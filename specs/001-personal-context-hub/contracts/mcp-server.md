# Contract: MCP Server Surface (v0)

**Consumers**: agent runtimes via generic MCP adapter (spec assumption: generic adapter + two real runtimes).
**Server**: `pcl-server` MCP module (official `mcp` Python SDK / FastMCP, mounted alongside the FastAPI app). Transport: **Streamable HTTP on `127.0.0.1`** (primary); stdio launcher wrapping the same server for stdio-only agents.

## Identity & session rules

- Every MCP session authenticates with the credential minted at pairing (`POST /v1/connections/pair`). The session **is** an `AgentConnection`: it holds exactly that connection's grants and nothing more — connecting never confers authority (FR-009).
- Revocation (`connection` or `grant`) terminates affected sessions and invalidates outstanding manifests within seconds (FR-012, SC-004).
- Every tool result that discloses context includes `citations[]`, `classification`, and `redactions[]` — uncertainty and withholding are explicit, never silent (FR-011, FR-013).
- Tool errors use stable codes matching REST problem types (`policy_denied`, `approval_required`, `revoked`, `validation_failed`).

## Resources

| URI | Content |
|---|---|
| `pcl://spaces/{space_id}/profile` | policy-filtered profile + readable preferences |
| `pcl://projects/{project_id}/brief` | grounded project brief with citations (mirror of `GET /v1/projects/{id}/brief`) |
| `pcl://connection/self` | the session's own identity, grants and their expiry (agent can introspect what it may do) |
| `pcl://audit/recent` | this connection's own recent audit events (transparency, not surveillance of others) |

## Tools

All input/output schemas are the same Pydantic v2 models as the REST layer (single source of truth).

### `search_personal_context`
`{ query, scope?: {project?, types?}, purpose }` → `{ results: [{id, type, excerpt, classification, citations[]}], redactions[] }`
Policy-filtered FTS retrieval (FR-006). `purpose` is mandatory and audited.

### `get_context_manifest`
`{ purpose, requested_capabilities[], selectors, ttl_seconds? }` → `{ manifest_id, expires_at, entities[], citations[], redaction_notices[] }`
Purpose-bound snapshot; refuses unscoped "everything" requests with `validation_failed` (FR-011). May return `approval_required` challenge when policy demands it.

### `propose_memory`
`{ memory: {kind, statement, subject_ref?, sensitivity_flags[], project_id?}, evidence_refs[], retention? }` → `{ proposal_id, status: pending|auto_accepted, policy_verdict, conflicts[] }`
Never a direct write (FR-014). Sensitive flags force user confirmation (FR-015). Duplicates/contradictions reported back (FR-016).

### `set_shared_state`
`{ key, value, ttl_seconds, visibility: private_to_connection|shared }` → `{ key, expires_at }`
TTL working state; `shared` requires `state.write` grant with share permission (FR-017).

### `get_shared_state`
`{ key }` → `{ value, expires_at, created_by }` — own state, or `shared` state permitted by grants.

### `request_approval`
`{ intent_summary, rationale, impact }` → `{ approval_id, status: pending }`
Generic user-decision request (e.g. context-escalation challenge follow-up).

### `propose_action`
`{ kind, summary_human, payload, basis_refs[], idempotency_key }` → `{ intent_id, status: pending, approval_required: true }`
External-effect actions always start `pending` in MVP (FR-018). Duplicate `idempotency_key` returns the existing intent (FR-020). The adapter polls `check_action_status` (or receives session notification) and only executes after `approved`, then reports the result.

### `check_action_status`
`{ intent_id }` → `{ status: pending|approved|declined|executed|failed|expired, decided_at? }`

## Conformance tests (normative)

1. Session with grant scoped to project A calling `search_personal_context` about project B receives empty results + `redactions` notice — never content (SC-003).
2. `get_context_manifest` without `purpose` → `validation_failed`.
3. `propose_memory` with `sensitivity_flags: [financial]` never returns `auto_accepted` (FR-015).
4. `propose_action` twice with the same `idempotency_key` returns the same `intent_id` (FR-020).
5. After owner revokes the connection: any tool call → `revoked`; session is closed (FR-012).
6. Every tool invocation appears in the audit ledger with actor = connection id (FR-021).
7. A second, differently-implemented MCP client passes 1–6 unchanged (two-runtime compatibility bar, SC-002).
