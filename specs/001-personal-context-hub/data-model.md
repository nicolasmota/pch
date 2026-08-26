# Data Model: Personal Context Hub (MVP)

**Feature**: `specs/001-personal-context-hub/spec.md` · **Plan**: [plan.md](./plan.md) · **Decisions**: [research.md](./research.md)

All entities live in one SQLCipher-encrypted SQLite database per context space (MVP: one `personal` space). IDs are type-prefixed ULIDs. Pydantic v2 models in `packages/pcl-core/src/pcl_core/schema/` are the source of truth; this document is their design reference.

## Universal metadata (all durable entities)

Every durable entity embeds this envelope (spec FR-005):

| Field | Type | Notes |
|---|---|---|
| `id` | ULID with type prefix | `mem_…`, `prj_…`, `grant_…` |
| `space_id` | string | MVP: always `personal` |
| `type` | entity type discriminator | drives exhaustive handling |
| `labels` | string[] | user/agent-applied tags |
| `classification` | `public \| personal \| private \| sensitive` | policy ceiling input; `sensitive` covers financial/health/legal/relationship (FR-015) |
| `owner` | person id | MVP: the single user |
| `created_at`, `updated_at` | ISO-8601 UTC | |
| `source_refs` | artifact/memory ids[] | provenance links (citations) |
| `confidence` | 0..1 | 1.0 for user-declared |
| `authority` | `user_confirmed \| source_imported \| agent_inferred \| proposed` | inference never silently overwrites `user_confirmed` (FR-007) |
| `retention` | `{mode: until_revoked \| review_after \| expires, at?}` | |
| `policy_tags` | string[] | additional policy selectors |
| `version` | int, monotonic | optimistic concurrency (`If-Match`); prior versions kept in `object_versions` |

**Validation**: `classification`, `authority`, `retention.mode` are closed enums (Pydantic-validated; handled exhaustively in code). `confidence` required when `authority = agent_inferred`. `source_refs` required for any accepted memory that originated as a proposal.

## Entities

### Person
The vault owner. `name`, `time_zone`, `identities[]` (display identities only; no external IdP in MVP). One row.

### ContextSpace
Access/ownership boundary. `name`, `kind` (`personal` only in MVP), key metadata for the space's encryption. All other entities carry its `space_id`.

### Profile & Preference
- **Profile**: singleton structured facts about the person (contact norms, working hours). Fields editable in UI; edits set `authority = user_confirmed`.
- **Preference**: `key` (namespaced, e.g. `communication.style`), `value` (JSON), `rationale?`. Unique per (`space_id`, `key`). Agent-proposed preference changes go through MemoryProposal, never direct write.

### Project / Goal / Commitment / Decision
Structured intent objects:

| Entity | Key fields | Relationships |
|---|---|---|
| **Project** | `title`, `status (active \| paused \| done \| archived)`, `charter`, `stakeholders[]` | has many goals, commitments, decisions, memories (via `project_id`) |
| **Goal** | `title`, `outcome`, `horizon?`, `measure?`, `status` | belongs to project (optional) |
| **Commitment** | `title`, `due_at?`, `counterparty?`, `status (open \| done \| cancelled \| overdue)` | belongs to project/goal (optional) |
| **Decision** | `title`, `chosen_option`, `alternatives[]`, `rationale`, `decided_at` | belongs to project; `source_refs` cite evidence |

**Validation**: status enums closed; `Commitment.due_at` required if `status = overdue` is ever derived; deleting a Project soft-archives children (nothing silently destroyed).

### Artifact
Source material or external reference: `kind (document \| message_thread \| conversation \| file \| url)`, `title`, `content_hash?` (blob-store key when content is stored), `external_ref?`, `untrusted = true` by default for imported content (FR-026 — untrusted content can never carry authority).

### Memory
Durable claim/observation/summary/episode: `kind (semantic \| episodic \| procedural \| summary)`, `statement` (canonical text), `subject_ref?` (entity + attribute path it makes a claim about — drives conflict detection), `project_id?`, `sensitivity_flags[]` (`financial`, `health`, `legal`, `relationship`). Full-text indexed (FTS5).

**State transitions** (via MemoryProposal, FR-014):

```text
(agent) proposal:pending ──policy──► auto_accepted ─► canonical (authority=agent_inferred)
                         ├─────────► needs_review ─► user accept ─► canonical
                         │                        └► user edit+accept ─► canonical (authority=user_confirmed)
                         │                        └► user reject ─► rejected (never canonical)
                         └─────────► rejected
(user)  direct create/edit ─► canonical (authority=user_confirmed)
canonical ─► corrected (new version) / deleted (tombstone; FTS purged)
```

### MemoryProposal
`proposed_memory` (Memory payload), `evidence_refs[]` (≥ 1 artifact/memory), `submitted_by` (connection id), `status (pending \| auto_accepted \| accepted \| rejected \| superseded)`, `policy_verdict`, `conflict_ids[]`.

**Validation**: any `sensitivity_flags` present ⇒ status can never be `auto_accepted` (FR-015). Exact-duplicate hash ⇒ `superseded`. Same `subject_ref` with different value than a `user_confirmed` memory ⇒ Conflict record, proposal held (FR-007, FR-016).

### Conflict
`memory_id`, `proposal_id`, `kind (duplicate \| contradiction)`, `status (open \| resolved_keep_existing \| resolved_accept_new \| resolved_merged)`. Only the user resolves contradictions against `user_confirmed` values.

### SharedState
Short-lived operational facts (FR-017): `key`, `value` (JSON, user-inspectable), `ttl_seconds`, `expires_at`, `visibility (private_to_connection \| shared)`, `created_by` (connection id). Hard-expired by sweep; **never** promoted to Memory automatically. Not exported in PCA.

### AgentConnection
A paired agent runtime: `name`, `runtime_info` (declared version/capabilities), `status (pending \| active \| revoked)`, `credential_hash` (pairing secret, hashed), `paired_at`, `revoked_at?`.

**Transitions**: `pending` (link minted) → `active` (pairing completed) → `revoked` (FR-012; terminal — reconnection creates a new connection). Revocation cascades: all grants of the connection → `revoked`, all outstanding ContextManifests → invalidated, active MCP sessions terminated.

### Grant
Scoped permission (FR-009): `connection_id`, `capabilities[]` (closed set: `project.read`, `commitment.read`, `memory.retrieve`, `memory.propose`, `state.write`, `action.propose`, …), `selectors` (e.g. `{project: prj_…}`), `classification_ceiling` (max classification disclosable), `purpose_constraint?`, `expires_at?`, `status (active \| expired \| revoked)`. Preset bundles ("Can read my active projects") are named sets of grants (FR-010).

### ContextManifest
Immutable, expiring disclosure snapshot (FR-011): `connection_id`, `purpose`, `requested_capabilities[]`, `selectors`, `disclosed_refs[]` (object id + version disclosed), `redaction_notices[]`, `expires_at`, `status (active \| expired \| invalidated)`. Serves as the citation anchor for everything an agent was shown.

### ActionIntent
Proposed external-effect action (FR-018): `connection_id`, `kind`, `summary_human` (plain-language, FR-019), `payload`, `basis_refs[]` (what it's based on), `idempotency_key` (unique per connection — duplicate submission returns the existing intent, FR-020), `status (pending \| approved \| declined \| executed \| failed \| expired)`.

**Transitions**: `pending` → (`approved` → `executed | failed`) | `declined` | `expired`. MVP: every intent requires explicit approval; a retry after `declined` creates a new intent that references the declined one and is auto-flagged.

### Approval
User decision record: `intent_ref` (ActionIntent or MemoryProposal), `decision (approved \| declined)`, `decided_at`, `context_shown` (what the user saw). Immutable.

### AuditEvent
Append-only, hash-chained (FR-021, research D8): `seq` (per-space monotonic), `kind` (closed enum: `context.request`, `context.disclose`, `policy.decision`, `memory.proposed/accepted/rejected`, `state.write`, `approval.decided`, `action.intent/executed/failed`, `grant.created/revoked`, `connection.paired/revoked`, `export.created`, `import.staged/applied`), `actor` (user | connection id | system), `refs[]`, `summary_human`, `prev_hash`, `hash`. **No raw conversation content** by default (FR-022). Never updated or deleted; PCA export includes it as lineage.

### ExportRecord / ImportStaging
- **ExportRecord**: `filters` (space/project/date/classification), `pca_version`, `manifest_hash`, `created_at`.
- **ImportStaging**: quarantine for an opened archive (FR-025): `archive_manifest`, `item_resolutions[]` (`merge | replace | keep_separate` per conflicting id), `status (staged \| applied \| discarded)`. Imported `agent_inferred` records keep that authority.

## Relationship overview

```text
Person 1─1 ContextSpace
ContextSpace 1─* {Profile, Preference, Project, Goal, Commitment, Decision,
                  Artifact, Memory, AgentConnection, AuditEvent}
Project 1─* {Goal, Commitment, Decision, Memory}
Memory *─* Artifact (source_refs)          MemoryProposal ─► Memory (on accept)
AgentConnection 1─* Grant                  MemoryProposal ─* Conflict
AgentConnection 1─* {ContextManifest, SharedState, ActionIntent}
ActionIntent 1─0..1 Approval               ContextManifest ─* disclosed object versions
Everything ─► AuditEvent (append-only, hash-chained)
```

## Retrieval & indexing

- FTS5 virtual table over `Memory.statement`, `Project.charter`/`title`, `Decision.rationale`, `Artifact.title` with (`space_id`, `type`, `classification`, `project_id`, labels) as filterable columns.
- Query pipeline: structured filter → FTS/BM25 → recency + authority re-rank → **policy filter (grants + classification ceiling) before any disclosure** → citation assembly from `source_refs` (FR-006, FR-013).
- Ranking sits behind a `Ranker` interface; a derived local vector index may be added post-MVP without schema change (research D4).
