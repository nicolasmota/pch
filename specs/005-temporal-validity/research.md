# Research: Temporal Validity

**Feature**: `specs/005-temporal-validity/` · **Date**: 2026-08-26

No NEEDS CLARIFICATION markers remained in the Technical Context. Decisions resolve open design choices against the Hub as of 004 (`pcl_core/schema/preference.py`, `memory.py`, `retrieval/contract.py`, `service.py` create/patch/decide_proposal, MCP `get_context_contract`).

## D1 — Validity is on Preference and Memory only, not UniversalMetadata

**Decision**: Add `valid_from: str` (ISO-8601 UTC) and `valid_until: str | null` to `Preference` and `Memory`. Do **not** put them on `UniversalMetadata`. SharedState keeps `expires_at` / TTL. Decisions keep `decided_at` / status. Profile stays a singleton without intervals. Missing `valid_from` on existing rows means `created_at`. Missing `valid_until` means still current.

**Rationale**: Spec covered types are preferences and factual claims. Putting intervals on the envelope would imply Projects, Grants, and SharedState are temporally valid statements about the person — they are not. Four clocks stay distinct: validity (this feature), retention (`Retention.mode` / `at`), object `version` (optimistic concurrency + typo history), SharedState TTL (handoff). `ActionIntent` is none of these — it remains approval of an external action.

**Alternatives considered**: (a) Envelope fields on `UniversalMetadata` — rejected: conflates clocks and invites treating TTL as validity. (b) Only Preference — rejected: spec US1/FR-001 include factual memories. (c) A new `ValidityWindow` vault type — rejected: successive truths *are* the statements; a join table is a second source of truth.

## D2 — Change of mind is a new Hub operation, not PATCH-in-place

**Decision**: `Hub.supersede(obj_id, body) -> dict` (owner): in one transaction, set `valid_until` on the current object to now (if still current), then `create` a successor Preference or Memory copying classification/key/subject_ref as appropriate, with `valid_from = now` and `valid_until = null`. The earlier object is **not** tombstoned and **not** version-overwritten. REST: `POST /v1/memories/{id}/supersede` and `POST /v1/preferences/{id}/supersede`. Ledger: existing `object.write` for both ids, extra may name `supersedes` / `superseded_by`.

**Rationale**: E1 already uses live `version` for corrections of the same object (FR-007 there). If E2 reused PATCH, "I now like X" would erase "I didn't like X" from the live document and bury it in `object_versions` — that fails SC-002 and constitution "history MUST NOT disappear." Two first-class objects with intervals *are* the E2 result.

**Alternatives considered**: (a) Append a version and treat version history as historical truth — rejected: versions are edits (typos), not successive truths; Hub "History" today is versions, not "was true until." (b) Overwrite value on the same id and stash the old value in `rationale` — rejected: one object cannot be both current and historical. (c) Automatic supersede on any PATCH of `value`/`statement` — rejected: that turns every typo fix into a change of mind (fails FR-009 / criterion "change of mind ≠ mistake").

## D3 — Mistake is retract, not a historical interval

**Decision**: `Hub.retract_never_true(obj_id) -> dict` (owner): set `never_true: true` on Memory (and Preference, same field added for symmetry) and tombstone the object so FTS/search skip it. Assembly and Hub current/historical lists **exclude** `never_true` rows. Version history and `object.write` remain for forensic audit. REST: `POST /v1/{memories|preferences}/{id}/retract`.

**Rationale**: Spec FR-009 / SC-006: a statement that was never true must not appear as historical truth. Tombstone-only without `never_true` would collide with ordinary delete of a still-true fact the person no longer wants stored — keep `never_true` as the discriminator so a later "undelete" cannot resurrect a lie as history.

**Alternatives considered**: (a) Empty interval (`valid_until <= valid_from`) — rejected: looks like a data error (FR-014 already rejects end-before-start). (b) Ordinary `delete` without a flag — rejected: cannot tell "never true" from "remove from vault." (c) Keep the row visible as historical with a badge "false" — rejected: spec says it is not historical truth.

## D4 — At most one *current* Preference per key; many historical

**Decision**: 001's "unique per (`space_id`, `key`)" is **replaced** by: at most one Preference with that `key` whose interval contains *now* and `never_true` is false. Historical rows may share the key. `Hub.create("preference", …)` rejects (validation error) if a current preference with that key already exists — caller must `supersede`. Overlap can still occur via concurrent writes or patched intervals; assembly then emits `conflicts` with reason `preference_key_collision` (E1 D5), no silent winner.

**Rationale**: Code today does **not** enforce 001 uniqueness (`Hub.create` always inserts). E1 D5 already treats same-key live prefs as conflicts. E2 needs two successive truths with one key. Enforcing uniqueness on current-only preserves 001's "one live value" without destroying history.

**Alternatives considered**: (a) Keep hard unique index on key — rejected: cannot store the old dislike. (b) Allow many current prefs per key always — rejected: meal-planning agents would get both like and dislike as live (the E2 failure mode). (c) Auto-close the previous current on create — rejected: silent change of mind; person must use `supersede`.

## D5 — Evaluation time on the existing context request

**Decision**: Add optional `as_of: str | null` (ISO-8601 UTC instant) to `ContextQuery`. Default `null` → `now` at assembly. `assemble_contract` computes one `evaluation_time` and keeps Preference/Memory rows only when `never_true` is false, not tombstoned, **and** `valid_from <= evaluation_time` and (`valid_until` is null or `evaluation_time < valid_until`). Half-open `[start, end)`. Goals, decisions, commitments, SharedState are **not** filtered by validity (not covered types). Pass `as_of` through MCP `get_context_contract` and `Hub.get_context_contract`; update `TOOL_SCHEMAS`. No new tool.

**Rationale**: Spec FR-005 / FR-006. Default now is the killer path. `as_of` makes history usable without a second product surface. Half-open avoids a statement being current at two evaluation times when one ends and another starts at the same instant.

**Alternatives considered**: (a) Now only, history only in UI — rejected: spec explicitly allows a stated evaluation time; without it the engine cannot prove "histórico" except by omission. (b) New MCP tool `get_historical_context` — rejected: FR says it rides the existing request. (c) Filter all entity types — rejected: would treat project status and SharedState TTL as validity.

## D6 — Live package stays current-only; interval is metadata on included items

**Decision**: Do not add a `historical[]` section to `ContextContract`. `ContractItem.body` for preference/memory includes `valid_from` and `valid_until` so the agent sees the window of the *included* (current-at-`as_of`) statement. Sufficiency caps unchanged. Historical review is the Hub Memories page, not the agent package (FR-015).

**Rationale**: Roadmap result: the engine returns the current one. Dumping closed intervals would violate smallest-sufficient and turn every package into a biography.

**Alternatives considered**: (a) Include last historical as a reference-only entry — rejected: leaks extra preference content into agent context by default. (b) Omit interval from body — rejected: agent cannot tell a temporary vegetarian window from an open-ended preference.

## D7 — Proposal accept supersedes when replacing a current claim

**Decision**: `Hub.decide_proposal(..., accept=True)`: if the proposed memory has `subject_ref` matching a current (not `never_true`) memory, call `supersede` on that memory instead of inserting a second current row. Preference changes proposed as memories still go through the existing proposal pipeline; owner-confirmed preference supersede stays the REST/UI path. Imported artifacts never call `supersede`.

**Rationale**: Constitution IV: agents propose, confirmation writes canonical. Accepting a "I now like X" proposal must not leave two current statements (D4) and must not PATCH-overwrite (D2).

**Alternatives considered**: (a) Always insert and rely on conflicts — weaker: person confirmed a replacement, not a coexistence. (b) Auto-accept imported mail as supersede — rejected: constitution V.

## D8 — Person-visible surface is Memories.tsx, not a new app

**Decision**: Extend `frontend/src/pages/Memories.tsx` (and `api/types.ts`) to list **memories and preferences**. Each row: statement/key+value, badge `current` | `historical`, interval dates, actions **Supersede**, **Retract (never true)**, **Edit interval** (PATCH). Object-version "History" modal stays for typo versions and is labeled so it is not confused with validity. No new route required if the page description states both; add a short Preferences heading on the same page.

**Rationale**: There is no Preferences page today (prefs are REST-only). US3 needs a Hub surface that shows current vs historical on the source statements. Audit `context.contract` extra is item refs of *issued packages*, not interval review — insufficient alone (bar criterion 8).

**Alternatives considered**: (a) Only Audit extra — rejected: does not show intervals on statements. (b) New Preferences.tsx route — extra nav for one list; same components, more files; acceptable later, not required. (c) Reuse version History modal as validity — rejected: D2, versions ≠ successive truths.

## D9 — Performance: filter in memory, no new index

**Decision**: After E1's per-category `store.list` and `policy.evaluate`, drop non-current Preference/Memory in the same loop. No SQL interval index in v1. SC-007: reuse/extend `test_contract_perf.py` so assembly still < 2 s with a few thousand objects including closed intervals. No egress.

**Rationale**: Personal-scale vault; historical rows are few relative to memories. A btree on `(type, key, valid_until)` is premature (004 D8).

**Alternatives considered**: Precomputed "current snapshot" table — rejected: second source of truth vs live objects.
