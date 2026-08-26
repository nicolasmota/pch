# Data Model: Context Engine

**Feature**: `specs/004-context-engine/` · **Date**: 2026-08-26

All models are Pydantic response/request models in `packages/pcl-core/src/pcl_core/schema/contract.py`. None are vault object types — they are **not** added to `TYPE_MODELS` and never persisted (research D1). Field names below are normative for the MCP tool contract.

## ContextQuery (request)

What an agent submits. Read-only; never writes to the vault.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `purpose` | str | yes | Non-empty. What the agent is trying to do for the person now (e.g., "continue planning the trip"). |
| `subject_ref` | str \| null | no | Optional anchor hint: a vault object id (typically a Project). Must be in granted scope or it is ignored with an omission note. |
| `max_items` | int \| null | no | Optional client cap per category; the engine's own sufficiency caps still apply as upper bound. |

Requester identity is not a field — it comes from the authenticated connection (`actor_from_token`), same as every existing tool.

**Validation**: empty/whitespace `purpose` → validation error (mirrors `build_manifest`'s purpose requirement). `subject_ref` referencing a non-existent or out-of-scope object does not error; it is treated as no hint.

## ContextContract (response)

The unit the agent receives. The agent does not need to know where the data lives.

| Field | Type | Notes |
|-------|------|-------|
| `contract_id` | str | Ephemeral id (also written to the audit record for cross-reference). |
| `purpose` | str | Echo of the query. |
| `situation` | SituationRef \| null | Selected anchor, or null (minimal contract). |
| `candidates` | list[SituationRef] | Non-empty only when selection tied; refs only, no merged content. |
| `goals` | list[ContractItem] | Live goals of the anchor. |
| `preferences` | list[ContractItem] | Global + anchor-scoped preferences. |
| `memories` | list[ContractItem] | Ranked, capped (research D3). |
| `decisions` | list[ContractItem] | Includes rejected decisions (e.g., "dropped London"). |
| `constraints` | list[ContractItem] | Open commitments and constraint-like preferences. |
| `state` | list[ContractItem] | Non-expired `SharedState` visible to this connection, embedded verbatim. |
| `references` | list[ItemRef] | Beyond-cap items: id + type + title only, no body (SC-007). |
| `conflicts` | list[ConflictPair] | Pairs of item ids that contradict; no winner chosen (FR-012). |
| `granted_scope` | ScopeSummary | The grant under which assembly ran. |
| `omissions` | list[OmissionNote] | Always present (may be empty). |
| `assembled_at` | datetime | |

**Invariants**:
- Every inlined item passed `policy.evaluate()` → ALLOW under the requesting grant (FR-005).
- Every `ContractItem` has a non-empty `citation` (FR-003 / SC-004).
- `omissions` never contains content, titles, or ids of withheld items (research D4).
- Only live object versions are assembled; superseded versions never appear (FR-007).
- Imported/untrusted content keeps its `untrusted` flag; contract items are data, never instructions.

## ContractItem

One assembled piece of context.

| Field | Type | Notes |
|-------|------|-------|
| `ref` | ItemRef | `id`, `type` (existing `EntityType`), `title`/`key` summary. |
| `body` | dict | Type-appropriate content (e.g., `statement` for Memory, `key`/`value` for Preference). |
| `citation` | list[Citation] | From `citations_for` / `source_refs`; minimally the vault object id + version. |
| `authority` | str | Existing enum: `user_confirmed` / `source_imported` / `agent_inferred` / `proposed`. |
| `confidence` | float \| null | From `UniversalMetadata.confidence`. |
| `freshness` | datetime | The object's `updated_at`. |
| `untrusted` | bool | Propagated from Artifact-derived content. |

## OmissionNote

| Field | Type | Notes |
|-------|------|-------|
| `category` | enum | `scope_not_granted` \| `classification_ceiling` \| `capability_missing` \| `policy_exclusion` |
| `label` | str | Plain-language, content-free (e.g., "personal travel context withheld"). |
| `count` | int | Number of withheld items in this category. |

## SituationRef / ItemRef / ConflictPair / ScopeSummary

- **SituationRef**: `project_id`, `title`, `status`. Refs only.
- **ItemRef**: `id`, `type`, `summary` (title/key/short statement).
- **ConflictPair**: `item_ids: list[str]` (2+), `reason: str` (e.g., `"preference_key_collision"`).
- **ScopeSummary**: `grant_id`, `selectors`, `classification_ceiling`, `capabilities` — a redacted echo of the existing `Grant`, reusing its `summary_human`.

## Contract Issuance Record (audit)

Not a new table — a body shape for the existing append-only ledger under new `EventKind.CONTEXT_CONTRACT = "context.contract"` in `schema/audit.py`.

| Body field | Notes |
|------------|-------|
| `contract_id` | Matches the response. |
| `actor` | Connection id (or `owner`). |
| `purpose` | As requested. |
| `status` | `issued` \| `refused` |
| `situation` | Anchor project id or null. |
| `item_refs` | ids + types of inlined items (no bodies). |
| `omission_categories` | Category + count pairs. |

Hash-chained like every other event; readable via existing `GET /v1/events` (US3, FR-008).

## State transitions

None. Contracts are immutable snapshots; corrections happen on source objects through existing flows, and only affect contracts assembled afterwards (FR-007).

## Relationships to existing schema

```text
ContextQuery ──(anchor selection: FTS over)──> Project, Goal
ContextContract.goals/decisions/constraints ──(project_id FK)──> anchor Project
ContextContract.preferences ──> Preference (global + project-scoped)
ContextContract.memories ──> Memory (ranked by DefaultRanker + purpose overlap)
ContextContract.state ──> SharedState (name and semantics unchanged)
ContractItem.citation ──> source_refs / citations_for (001)
ScopeSummary ──> Grant (002; unchanged)
Issuance record ──> audit Ledger (001; new EventKind only)
```
