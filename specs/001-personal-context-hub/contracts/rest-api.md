# Contract: REST Control Plane (v1)

**Consumers**: Hub desktop UI (primary client), local adapters/SDK, advanced users.
**Server**: `pcl-server` (FastAPI on uvicorn), bound to `127.0.0.1` only. OpenAPI 3.1 generated from Pydantic v2 models; the generated document is the normative artifact — this file is its design contract.

## Conventions

- Base path `/v1`. JSON bodies; entity payloads follow [data-model.md](../data-model.md) including universal metadata.
- **Auth**: bearer token per client. The Hub UI holds the `owner` token (full user authority); each agent connection's token maps to its `AgentConnection` and is policy-scoped. Owner-only routes are marked 👤.
- **Writes**: require `Idempotency-Key` header; mutations of versioned objects require `If-Match: <version>` and return the new `version`. Replayed idempotency keys return the original result.
- **Errors**: RFC 9457 problem+json with stable `type` codes (`policy_denied`, `version_conflict`, `approval_required`, `revoked`, `not_found`, `validation_failed`).
- **Audit**: every policy-relevant request emits an AuditEvent; consequential writes commit their event in the same transaction.

## Routes

### Setup & space (👤)

| Method / route | Purpose |
|---|---|
| `POST /v1/setup` | initialize vault + `personal` space (guided setup backend; resumable — FR-001) |
| `GET /v1/spaces` | list spaces (MVP: one) |

### Context objects (👤 full CRUD; agents: read via manifests/search only)

| Method / route | Purpose |
|---|---|
| `GET/POST /v1/{projects\|goals\|commitments\|decisions\|preferences\|memories\|artifacts}` | list (filterable) / create |
| `GET/PATCH/DELETE /v1/…/{id}` | read / edit (If-Match) / delete (tombstone; corrections set `authority=user_confirmed` — FR-007) |
| `GET /v1/…/{id}/versions` | full version history ("why does the system believe this") |
| `GET /v1/projects/{id}/brief` | grounded project brief: charter, decisions, open commitments, top memories — every item with citations |

### Search & retrieval

| Method / route | Purpose |
|---|---|
| `GET /v1/search?q=&type=&project=&classification=` | FTS + filters; results carry citations and classification; **policy-filtered by caller's grants** (FR-006, FR-013) |
| `POST /v1/context-manifests` | purpose-bound disclosure snapshot (body: `purpose`, `requested_capabilities`, `selectors`, `ttl_seconds`); response: manifest id, disclosed entities + citations, redaction notices. Unscoped requests → `422 validation_failed` (FR-011) |
| `GET /v1/context-manifests/{id}` | re-read an unexpired manifest (immutable) |

### Memory pipeline

| Method / route | Purpose |
|---|---|
| `POST /v1/memories/proposals` | agent submits MemoryProposal with `evidence_refs` (FR-014) |
| `GET /v1/memories/proposals?status=pending` 👤 | review queue |
| `POST /v1/memories/proposals/{id}/accept` 👤 | accept (optional inline edit ⇒ `authority=user_confirmed`) |
| `POST /v1/memories/proposals/{id}/reject` 👤 | reject |
| `GET /v1/conflicts` / `POST /v1/conflicts/{id}/resolve` 👤 | surface / resolve contradictions (FR-016) |

### Shared state

| Method / route | Purpose |
|---|---|
| `PUT /v1/state/{key}` | create/update TTL state (`value`, `ttl_seconds`, `visibility`) (FR-017) |
| `GET /v1/state/{key}` | read if owner, creator, or `visibility=shared` + grant |

### Connections, grants, approvals

| Method / route | Purpose |
|---|---|
| `POST /v1/connections/links` 👤 | mint one-time pairing link/code (catalog or manual — FR-008) |
| `POST /v1/connections/pair` | agent redeems link → credential (connection becomes `active`) |
| `GET /v1/connections` 👤 / `POST /v1/connections/{id}/revoke` 👤 | list / revoke — cascades to grants, manifests, sessions (FR-012) |
| `POST /v1/grants` 👤 / `POST /v1/grants/{id}/revoke` 👤 | create scoped grant (or preset bundle) / revoke |
| `GET /v1/grants?connection=` 👤 | plain-language access summary source (FR-010) |
| `POST /v1/actions/intents` | agent proposes external action (`summary_human`, `payload`, `basis_refs`, idempotency — FR-018/019/020) |
| `GET /v1/approvals?status=pending` 👤 / `POST /v1/approvals/{id}/decide` 👤 | pending queue / approve-decline |
| `POST /v1/actions/intents/{id}/result` | adapter reports execution outcome (`executed \| failed`) |

### Audit & portability (👤)

| Method / route | Purpose |
|---|---|
| `GET /v1/events?kind=&actor=&from=&to=` | audit timeline, plain-language summaries (FR-021) |
| `GET /v1/events/verify` | verify hash chain integrity |
| `POST /v1/export` | create PCA archive (body: filters + passphrase) → file path (FR-023/024) |
| `POST /v1/import/stage` | open archive into quarantine staging (FR-025) |
| `GET /v1/import/staging/{id}` / `POST /v1/import/staging/{id}/apply` | inspect conflicts / apply with per-item `merge\|replace\|keep_separate` |

## Contract tests (normative)

1. Agent token with `project.read` on project A: `GET /v1/search` never returns objects outside A or above its classification ceiling (SC-003 seed suite).
2. `POST /v1/context-manifests` without `purpose` or with empty `requested_capabilities` → `422`.
3. Replayed `Idempotency-Key` on `POST /v1/actions/intents` returns the same intent, no duplicate (FR-020).
4. `PATCH` with stale `If-Match` → `409 version_conflict`.
5. After `POST /v1/connections/{id}/revoke`: all requests with that connection's token → `401 revoked`; its unexpired manifests → `410` (FR-012, SC-004).
6. Every route above, when exercised, produces exactly the audit events listed for it in the OpenAPI `x-audit-events` extension (FR-021, SC-005).
