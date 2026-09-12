# MCP tools

The Hub exposes **eleven** tools over the stdio bridge (`pcl-sdk mcp-bridge`) and over HTTP (`POST /v1/mcp/tools/{name}`).

Auth: connection token (`PCH_TOKEN`) or owner Bearer token. Policy is applied per actor. A revoked connection returns an error the bridge maps to *Connection revoked by the user in the Hub.*

Stdio MCP **does not** list resources. HTTP resources: [below](#resources).

## Catalog

| Tool | Required arguments | Role |
|---|---|---|
| `get_context_contract` | `purpose` | Situation package — start here |
| `search_personal_context` | `query`, `purpose` | Ranked hits inside the grant |
| `get_context_manifest` | `purpose`, `requested_capabilities` | Short-lived capability receipt |
| `propose_memory` | `memory`, `evidence_refs` | Queue a memory; not live until accept |
| `propose_operational_state` | `target_id` | Queue phase / step / situation intent |
| `propose_relation` | `from_id`, `to_id`, `relation_type` | Queue a typed edge |
| `set_shared_state` | `key`, `value`, `ttl_seconds`, `visibility` | TTL handoff object |
| `get_shared_state` | `key` | Read handoff |
| `propose_action` | `kind`, `summary_human`, `payload`, `basis_refs`, `idempotency_key` | Queue an external action |
| `request_approval` | `intent_summary`, `rationale`, `impact` | Convenience `kind=approval` |
| `check_action_status` | `intent_id` | `{ status, decided_at }` |

Guide: [Situation package](../guides/situation-package.md). Capture rules: [Pair an agent](../guides/pair-an-agent.md#runtime-rule-paste-into-personal-guidance).

---

### `get_context_contract`

Assembles the smallest sufficient package for `purpose`.

```json
{
  "purpose": "continue planning the ten-day trip",
  "subject_ref": null,
  "max_items": null,
  "as_of": null
}
```

| Field | Type | Notes |
|---|---|---|
| `purpose` | string, minLength 1 | Required |
| `subject_ref` | string \| null | Project id |
| `max_items` | integer ≥ 1 \| null | Per-category cap; engine caps still apply |
| `as_of` | string \| null | ISO-8601 UTC instant; null = now |

Returns a [Context Contract](data-model.md#context-contract). Additional properties are rejected on the bridge schema.

---

### `search_personal_context`

```json
{
  "query": "Amsterdam",
  "purpose": "status_update",
  "scope": { "project": "<project-id>", "types": ["memory"] }
}
```

`scope.project` and `scope.types` (first type only is applied today) are optional. Returns a search result dict (hits + policy metadata), not a contract.

---

### `get_context_manifest`

```json
{
  "purpose": "status_update",
  "requested_capabilities": ["project.read"],
  "selectors": { "project": "<project-id>" },
  "ttl_seconds": 900
}
```

Creates a time-boxed manifest of what this connection may see. Default TTL 900 seconds. HTTP twin for agents: `POST /v1/context-manifests` (connection actor only).

---

### `propose_memory`

```json
{
  "memory": {
    "kind": "semantic",
    "statement": "Amsterdam is the live city for the trip.",
    "project_id": "<project-id>"
  },
  "evidence_refs": [],
  "retention": null
}
```

If `retention` is set, it is merged into `memory`. The object is a **proposal**. Do not treat it as canonical. Do not propose guesses, demo fiction, or imported mail as orders.

Memory kinds: `semantic`, `episodic`, `procedural`, `summary`.

---

### `propose_operational_state`

```json
{
  "target_id": "<project-or-goal-id>",
  "operational_phase": "comparing_itineraries",
  "current_step": "shortlist flights",
  "situation_intent": "choose next itinerary"
}
```

`operational_phase` enum: `planning`, `comparing_itineraries`, `waiting_for_approval`, `choosing_hotel`, `other`, or null. `current_step` and `situation_intent` max length 200. Person accepts under `/v1/operational-proposals`.

This is **not** `SharedState` and **not** `ActionIntent`.

---

### `propose_relation`

```json
{
  "from_id": "<id>",
  "to_id": "<id>",
  "relation_type": "depends_on"
}
```

`relation_type`: `owned_by` | `depends_on` | `blocked_by` | `related_to`. Self-links are forbidden. Person accepts under `/v1/relation-proposals`.

---

### `set_shared_state` / `get_shared_state`

Handoff with TTL. Visibility: `private_to_connection` | `shared`.

```json
{ "key": "trip-draft", "value": { "city": "Amsterdam" }, "ttl_seconds": 900, "visibility": "shared" }
```

Do not use this as long-term memory. Durable facts go through `propose_memory`.

---

### `propose_action` / `request_approval` / `check_action_status`

External actions need a person in **Approvals**.

`request_approval` is `propose_action` with `kind=approval` and payload `{ rationale, impact }`.

`check_action_status` returns `{ "status": "…", "decided_at": "…" }`.

---

## Resources (HTTP only)

`GET /v1/mcp/resources?uri=`

| URI contains | Payload |
|---|---|
| `/profile` | Profile + preferences |
| `/projects/{id}/brief` | Project brief |
| `/connection/self` or `/self` | Grants for this actor |
| `audit` | Audit events for this actor |

Python: `Client.resource(uri)`.

---

## Bridge environment

| Variable | Meaning |
|---|---|
| `PCH_TOKEN` | Connection token (`--token` overrides) |
| `PCH_BASE` | Hub base URL, default `http://127.0.0.1:8765` |

The stdio serverInfo version string may still report `0.1.0`; the product packages are **0.2.0**. Prefer package version / `pch version`.
