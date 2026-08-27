# Interface Contract: Operational state on context + proposals

**Feature**: `specs/007-situation-state-intent/` · **Date**: 2026-08-26
**Surfaces**: existing MCP tool `get_context_contract` (additive `SituationRef` fields); new MCP tool `propose_operational_state`; existing owner PATCH; new REST for operational proposals.

## Tool registration

| Surface | Location | Contract |
|---------|----------|----------|
| In-process MCP (read) | `attach_tools` in `packages/pcl-server/src/pcl_server/mcp/tools_context.py` | Existing `get_context_contract` — response `situation` / `candidates[]` gain three optional fields. **No new read tool.** |
| In-process MCP (write propose) | same `attach_tools` | New tool `propose_operational_state` next to `propose_memory` |
| Stdio bridge | `TOOL_NAMES` + `TOOL_SCHEMAS` in `packages/pcl-sdk/src/pcl_sdk/mcp_bridge.py` | Add `propose_operational_state`. `get_context_contract` request schema unchanged. |
| HTTP tools | `POST /v1/mcp/tools/get_context_contract` and `POST /v1/mcp/tools/propose_operational_state` | Bearer / `x-pch-token`; actor from token |
| Owner PATCH | `PATCH /v1/projects/{id}`, `PATCH /v1/goals/{id}` in `packages/pcl-server/src/pcl_server/rest/routers/projects.py` | Owner-only; body may include the three fields |
| Proposals REST | NEW router `packages/pcl-server/src/pcl_server/rest/routers/operational.py` | Owner-only list / accept / reject |

Authentication and pairing are unchanged (002). `propose_operational_state` is available to any paired connection that can already call `propose_memory`. Owner PATCH remains owner-only.

## Additive `situation_ref` (response of `get_context_contract`)

E1 required fields stay required. The three operational fields are optional; JSON `null` or omitted when unset. `status` remains ProjectStatus (`active|paused|done|archived`), never an OperationalPhase.

```json
{
  "type": "object",
  "required": ["project_id", "title", "status"],
  "additionalProperties": false,
  "properties": {
    "project_id": { "type": "string" },
    "title": { "type": "string" },
    "status": {
      "type": "string",
      "enum": ["active", "paused", "done", "archived"],
      "description": "ProjectStatus. Not operational phase."
    },
    "operational_phase": {
      "type": ["string", "null"],
      "enum": ["planning", "comparing_itineraries", "waiting_for_approval", "choosing_hotel", "other", null]
    },
    "current_step": { "type": ["string", "null"], "maxLength": 200 },
    "situation_intent": { "type": ["string", "null"], "maxLength": 200 }
  }
}
```

Example (set):

```json
{
  "project_id": "prj_…",
  "title": "Europe Trip",
  "status": "active",
  "operational_phase": "comparing_itineraries",
  "current_step": "rank two remaining itineraries",
  "situation_intent": "choose next itinerary"
}
```

Example (unset — E1 still assembles):

```json
{
  "project_id": "prj_…",
  "title": "Europe Trip",
  "status": "active",
  "operational_phase": null,
  "current_step": null,
  "situation_intent": null
}
```

SharedState items stay in `state[]`. A seed such as `{ "ref": { "id": "…", "type": "state" }, "body": { "key": "trip.phase", "value": "comparing itineraries" } }` is **not** `operational_phase`.

## Owner PATCH body (canonical write)

Existing endpoints. Unknown keys still follow `Hub.patch` extra-forbid / ignore rules already in force; unknown `operational_phase` enum → 422.

```json
{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "operational_phase": {
      "type": ["string", "null"],
      "enum": ["planning", "comparing_itineraries", "waiting_for_approval", "choosing_hotel", "other", null]
    },
    "current_step": { "type": ["string", "null"], "maxLength": 200 },
    "situation_intent": { "type": ["string", "null"], "maxLength": 200 }
  }
}
```

## MCP `propose_operational_state` request schema

```json
{
  "type": "object",
  "required": ["target_id"],
  "additionalProperties": false,
  "properties": {
    "target_id": {
      "type": "string",
      "description": "Project or Goal id to patch on accept."
    },
    "operational_phase": {
      "type": ["string", "null"],
      "enum": ["planning", "comparing_itineraries", "waiting_for_approval", "choosing_hotel", "other", null]
    },
    "current_step": { "type": ["string", "null"], "maxLength": 200 },
    "situation_intent": { "type": ["string", "null"], "maxLength": 200 }
  }
}
```

Response: the pending `OperationalProposal` object (`id`, `type: "operational_proposal"`, `status: "pending"`, `target_id`, proposed fields, `submitted_by`). Does **not** patch live Project/Goal fields.

## REST proposals

| Method | Path | Auth | Body | Result |
|--------|------|------|------|--------|
| GET | `/v1/operational-proposals?status=pending` | owner | — | list of `operational_proposal` objects |
| POST | `/v1/operational-proposals/{id}/accept` | owner | — | proposal `accepted`; `Hub.patch` applied to `target_id` |
| POST | `/v1/operational-proposals/{id}/reject` | owner | — | proposal `rejected`; live fields unchanged |

Non-owner → 403. Unknown id → 404. Accept of already-resolved proposal → 409.

## Behavioral contract

| # | Guarantee | Spec ref |
|---|-----------|----------|
| B1 | `situation.operational_phase` is copied from the selected Project (or Goal overlay); it is never read from SharedState key `trip.phase`. That key, if present, stays under `state[]`. | SC-001, FR-003 |
| B2 | `situation.situation_intent` is the string field, never an ActionIntent object and never `Goal.title`. | SC-002 |
| B3 | After owner PATCH of phase/intent, the next `get_context_contract` for a matching purpose reflects the live values. No cache of operational fields. | SC-003 |
| B4 | Work-scoped grant: 0 personal-project `operational_phase` / `current_step` / `situation_intent` in the package. Omissions do not include withheld titles or ids. | SC-004 |
| B5 | Unset fields are `null` (or omitted). Assembly still returns a valid E1 contract. No inference from memories, artifacts, or email. | SC-005 |
| B6 | Two connections with the same grant, same purpose, same vault: identical `situation.operational_phase` and `situation.situation_intent`. | SC-006 |
| B7 | Assembly performs no network egress, no plugin syncs, no extra `store.list` for these fields. Offline identical to online. Copy is in-memory on objects E1 already loaded. | SC-007, FR-010 |
| B8 | Assembly stays on `Hub.get_context_contract` / `retrieval.contract`. No second read MCP tool. | E1 seam |
| B9 | `propose_operational_state` never mutates live Project/Goal fields. Only accept does `Hub.patch`. | FR-005 |
| B10 | Plugins and connectors never write these fields. Imported content is data. | FR-008 |
| B11 | `situation.status` remains ProjectStatus. OperationalPhase lives only in `operational_phase`. | Vocabulary |
| B12 | Invalid phase enum on PATCH or propose → 422. Empty `target_id` → 422. Invalid/revoked token → 401/403 as today. | Validation |

## Review surface (US3)

- **Projects** (`frontend/src/pages/Projects.tsx`): each project row shows `operational_phase`, `current_step`, `situation_intent` as editable fields (not memory cards). Save calls `PATCH /v1/projects/{id}`.
- **Review Queue** (`frontend/src/pages/ReviewQueue.tsx`): pending `operational_proposal` rows with proposed fields + Accept/Reject calling the REST above. Memory proposals remain; do not coerce operational rows into `proposed_memory.statement`.

## Fixture tests (fail first)

| SC | File::test | Marker |
|----|------------|--------|
| SC-001 | `packages/pcl-core/tests/test_operational_contract.py::test_phase_in_situation_not_shared_state` | (default) |
| SC-002 | `packages/pcl-core/tests/test_operational_contract.py::test_intent_not_action_intent` | (default) |
| SC-003 | `packages/pcl-core/tests/test_operational_contract.py::test_patch_then_next_contract` | (default) |
| SC-004 | `packages/pcl-server/tests/forbidden_context/test_operational_isolation.py::test_work_scope_omits_personal_phase` | `forbidden_context` |
| SC-005 | `packages/pcl-core/tests/test_operational_contract.py::test_unset_assembles_without_inventing` | (default) |
| SC-006 | `packages/pcl-server/tests/contract/test_operational_mcp.py::test_two_agents_agree` | (default) |
| SC-007 | `packages/pcl-core/tests/test_contract_perf.py::test_contract_assembly_under_two_seconds` | `perf` |
