# Interface Contract: Typed relations on context + proposals

**Feature**: `specs/008-light-graph/` · **Date**: 2026-08-26
**Surfaces**: existing MCP tool `get_context_contract` (additive `relations`); new MCP tool `propose_relation`; owner REST; proposal accept/reject.

## Tool registration

| Surface | Location | Contract |
|---------|----------|----------|
| In-process MCP (read) | `attach_tools` in `packages/pcl-server/src/pcl_server/mcp/tools_context.py` | Existing `get_context_contract` — response gains required `relations` array. **No new read tool.** |
| In-process MCP (write propose) | same | New tool `propose_relation` |
| Stdio bridge | `packages/pcl-sdk/src/pcl_sdk/mcp_bridge.py` | Add `propose_relation` |
| HTTP tools | `POST /v1/mcp/tools/get_context_contract`, `POST /v1/mcp/tools/propose_relation` | Bearer / `x-pch-token` |
| Owner REST | NEW `packages/pcl-server/src/pcl_server/rest/routers/relations.py` | CRUD + proposals |

## Additive `relations` on `get_context_contract` response

E1 required keys stay required. `relations` is required and may be empty.

```json
{
  "type": "object",
  "required": ["id", "relation_type", "from", "to"],
  "additionalProperties": false,
  "properties": {
    "id": { "type": "string" },
    "relation_type": {
      "type": "string",
      "enum": ["owned_by", "depends_on", "blocked_by", "related_to"]
    },
    "from": {
      "type": "object",
      "required": ["id", "type", "summary"],
      "properties": {
        "id": { "type": "string" },
        "type": { "type": "string" },
        "summary": { "type": "string" }
      }
    },
    "to": {
      "type": "object",
      "required": ["id", "type", "summary"],
      "properties": {
        "id": { "type": "string" },
        "type": { "type": "string" },
        "summary": { "type": "string" }
      }
    }
  }
}
```

Example (trip depends_on visa; one hop visa blocked_by person):

```json
{
  "relations": [
    {
      "id": "rel_…",
      "relation_type": "depends_on",
      "from": { "id": "prj_trip", "type": "project", "summary": "Europe Trip" },
      "to": { "id": "prj_visa", "type": "project", "summary": "Visa renewal" }
    },
    {
      "id": "rel_…",
      "relation_type": "blocked_by",
      "from": { "id": "prj_visa", "type": "project", "summary": "Visa renewal" },
      "to": { "id": "per_…", "type": "person", "summary": "Consulate contact" }
    }
  ]
}
```

`project_id` on a Goal is **not** emitted as `owned_by`. `stakeholders` is **not** emitted as `related_to`.

## Owner REST

| Method | Path | Auth | Body | Result |
|--------|------|------|------|--------|
| POST | `/v1/relations` | owner | `{ "from_id", "to_id", "relation_type" }` | live relation |
| GET | `/v1/relations?from_id=` | owner | — | live relations |
| DELETE | `/v1/relations/{id}` | owner | — | no longer live |
| GET | `/v1/relation-proposals?status=pending` | owner | — | pending proposals |
| POST | `/v1/relation-proposals/{id}/accept` | owner | — | live relation created |
| POST | `/v1/relation-proposals/{id}/reject` | owner | — | live set unchanged |

Unknown type or self-link → 422. Duplicate live triple → 409. Missing endpoint → 404. Accept of resolved proposal → 409.

## MCP `propose_relation` request schema

```json
{
  "type": "object",
  "required": ["from_id", "to_id", "relation_type"],
  "additionalProperties": false,
  "properties": {
    "from_id": { "type": "string" },
    "to_id": { "type": "string" },
    "relation_type": {
      "type": "string",
      "enum": ["owned_by", "depends_on", "blocked_by", "related_to"]
    }
  }
}
```

Response: pending `relation_proposal`. Does **not** create a live Relation.

## Behavioral contract

| # | Guarantee | Spec ref |
|---|-----------|----------|
| B1 | `relations` includes `depends_on` from the trip when that live row exists. Type is not rewritten. | SC-001 |
| B2 | One hop: visa `blocked_by` person appears in the trip package. No third hop. | SC-002 |
| B3 | After owner delete/change, the next contract reflects the live set. | SC-003 |
| B4 | Work-scoped grant: 0 personal relation types, endpoint ids, or titles. Omissions have no titles/ids. | SC-004 |
| B5 | No live relations → `relations: []`. E1/E3 still assemble. No inference from memories/email/phase. | SC-005 |
| B6 | Two connections, same grant, same purpose: identical `relations` (order stable). | SC-006 |
| B7 | No network egress; one `store.list("relation")`; still `Hub.get_context_contract`. | SC-007 |
| B8 | No second read MCP tool. | E1 seam |
| B9 | `propose_relation` never creates a live row. Only accept / owner POST does. | FR-005 |
| B10 | Plugins never write relations. FKs are not auto-promoted. | FR-003, FR-004 |
| B11 | Self-link 422; unknown type 422; duplicate live 409. | Validation |
| B12 | `situation.operational_phase` (E3) is unchanged by this feature. | FR-009 |

## Review surface (US3)

- **Projects** (`frontend/src/pages/Projects.tsx`): each project lists live relations (type + other end). Add via type select + target id; remove via delete. Not memory cards.
- **Review Queue**: pending `relation_proposal` rows with Accept/Reject. Do not coerce into `proposed_memory.statement`.

## Fixture tests (fail first)

| SC | File::test | Marker |
|----|------------|--------|
| SC-001 | `packages/pcl-core/tests/test_relation_contract.py::test_depends_on_in_package` | (default) |
| SC-002 | `packages/pcl-core/tests/test_relation_contract.py::test_one_hop_blocked_by` | (default) |
| SC-003 | `packages/pcl-core/tests/test_relation_contract.py::test_remove_then_next_contract` | (default) |
| SC-004 | `packages/pcl-server/tests/forbidden_context/test_relation_isolation.py::test_work_scope_omits_personal_relations` | `forbidden_context` |
| SC-005 | `packages/pcl-core/tests/test_relation_contract.py::test_unset_assembles_without_inventing` | (default) |
| SC-006 | `packages/pcl-server/tests/contract/test_relation_mcp.py::test_two_agents_agree` | (default) |
| SC-007 | `packages/pcl-core/tests/test_contract_perf.py::test_contract_assembly_under_two_seconds` | `perf` |
