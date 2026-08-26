---

description: "Task list for Temporal Validity"
---

# Tasks: Temporal Validity

**Input**: Design documents from `/specs/005-temporal-validity/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/temporal-validity.md

**Tests**: Included — constitution and SC-001…SC-007 demand deterministic suites (reversal demo, historical remains, explicit windows, isolation, conflicts, retract vs supersede, perf). Write tests first; they MUST fail before implementation.

**Organization**: Tasks are grouped by user story so each story is an independently testable increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete sibling tasks)
- **[Story]**: US1 (supersede + current-only package), US2 (explicit intervals + `as_of`), US3 (Hub review + retract)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Interval helper and a reusable spicy-preference seed used by later tests

- [x] T001 Add `parse_instant` and `interval_contains` (half-open `[start, end)`, missing end = still current) in `packages/pcl-core/src/pcl_core/timeutil.py`
- [x] T002 [P] Add spicy-reversal seed helper (current Preference `food.spicy` = dislike, optional matching Memory) in `packages/pcl-core/src/pcl_core/testing/spicy_seed.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schema fields every story needs. No Hub operations yet. No vault table.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Add `valid_from`, `valid_until`, `never_true` to `Preference` in `packages/pcl-core/src/pcl_core/schema/preference.py` with validator `valid_from < valid_until` when both set (FR-014)
- [x] T004 [P] Add `valid_from`, `valid_until`, `never_true` to `Memory` in `packages/pcl-core/src/pcl_core/schema/memory.py` with the same interval validator
- [x] T005 Add optional `as_of: str | None` to `ContextQuery` in `packages/pcl-core/src/pcl_core/schema/contract.py` (ISO-8601 UTC; unparseable fails validation)
- [x] T006 Schema unit tests (defaults: missing `valid_from` allowed on the model; end-before-start rejected; `never_true` defaults false; `as_of` empty-ok) in `packages/pcl-core/tests/test_validity_schema.py`
- [x] T007 [P] Interval math tests (open-ended current, future start not current, half-open boundary, evaluation instant) in `packages/pcl-core/tests/test_validity_resolution.py`

**Checkpoint**: Models validate; interval helper is tested; `as_of` exists on the query model; no Hub writes yet

---

## Phase 3: User Story 1 - The Current Preference Is What Agents Receive (Priority: P1) 🎯 MVP

**Goal**: Owner `supersede` ends the current statement and creates a successor; both remain. `get_context_contract` at now inlines only current Preference/Memory. Two agents agree. `Hub.create("preference")` rejects a second *current* row with the same `key`. Overlapping currents still surface as `preference_key_collision`.

**Independent Test**: Seed dislike; `POST /v1/preferences/{id}/supersede` with like; two agents call `get_context_contract` with purpose `"plan dinner this week"` → live `food.spicy` = like, 0 live dislike; GET still returns the dislike row with `valid_until` set (SC-001, SC-002).

### Tests for User Story 1 ⚠️ write first, watch them fail

- [x] T008 [P] [US1] Unit tests for `Hub.supersede` (predecessor kept, `valid_until` set, successor current, same key; PATCH of `value` alone does not create a second object) in `packages/pcl-core/tests/test_change_mind.py`
- [x] T009 [P] [US1] Killer-demo integration: two agents, same purpose, like is live and dislike is not; GET lists still return historical dislike (SC-001, SC-002) in `packages/pcl-server/tests/contract/test_preference_reversal.py`
- [x] T010 [P] [US1] Assembly tests: after supersede only current prefs/memories inlined; historical absent from `references`; two current same-key prefs → `preference_key_collision` neither dropped (SC-005) in `packages/pcl-core/tests/test_contract_assembly.py`
- [x] T011 [P] [US1] Isolation: historical personal preference absent from work-scoped contract, omission has no titles/ids (SC-004) marked `forbidden_context` in `packages/pcl-server/tests/forbidden_context/test_contract_isolation.py`

### Implementation for User Story 1

- [x] T012 [US1] Implement `Hub.supersede(obj_id, body)` in `packages/pcl-core/src/pcl_core/service.py`: one transaction, close predecessor `valid_until=now`, create successor `valid_from=now`, both `object.write` (research D2)
- [x] T013 [US1] Reject `Hub.create("preference", …)` when a current (not `never_true`, interval contains now) row already has that `key` (422; caller must supersede) in `packages/pcl-core/src/pcl_core/service.py` (research D4)
- [x] T014 [US1] Filter Preference/Memory in `assemble_contract` to `never_true` false, not tombstoned, and `interval_contains` at evaluation time (default now); include `valid_from`/`valid_until` in `_body`; keep E1 grant filter first (research D5/D6) in `packages/pcl-core/src/pcl_core/retrieval/contract.py`
- [x] T015 [US1] Owner REST `POST /v1/preferences/{id}/supersede` and `POST /v1/memories/{id}/supersede` per `specs/005-temporal-validity/contracts/temporal-validity.md` in `packages/pcl-server/src/pcl_server/rest/routers/memories.py`
- [x] T016 [US1] On `decide_proposal(accept=True)`, if proposed memory `subject_ref` matches a current memory, call `supersede` instead of inserting a second current row in `packages/pcl-core/src/pcl_core/service.py` (research D7)
- [x] T017 [US1] Keep the E1 overlapping `flights.red_eye` conflict fixture without a second `Hub.create` of a current same key (insert/patch so two currents exist for SC-005) in `packages/pcl-core/src/pcl_core/testing/trip_seed.py`

**Checkpoint**: Reversal demo green through REST + MCP; historical dislike still listed; work grant cannot see it; create second current key fails

---

## Phase 4: User Story 2 - The Person Sets When Something Is True (Priority: P2)

**Goal**: Explicit `valid_from` / `valid_until` via PATCH. Optional `as_of` on the existing context request reconstructs a past (or scheduled) instant. Ending an interval does not delete or auto-create a successor. Future start is not current before that start.

**Independent Test**: Create a preference with an end date; contracts before the end treat it as current; after the end, not current and still GET-able; `as_of` before supersede returns the old dislike; future-dated start does not replace the previous current statement (SC-003).

### Tests for User Story 2 ⚠️ write first, watch them fail

- [x] T018 [P] [US2] Resolution tests: current before end / not after; future `valid_from` not current; open-ended stays current; `as_of` selects the statement whose interval contains that instant in `packages/pcl-core/tests/test_validity_resolution.py`
- [x] T019 [P] [US2] MCP/HTTP contract tests vs `specs/005-temporal-validity/contracts/temporal-validity.md`: `as_of` omitted = now; valid `as_of`; unparseable `as_of` → 422 no issuance in `packages/pcl-server/tests/contract/test_mcp_contract.py`
- [x] T020 [P] [US2] Assembly + PATCH tests: explicit window respected in the package; PATCH `valid_until` without successor does not delete; end-before-start 422 (FR-007, FR-014) in `packages/pcl-core/tests/test_contract_assembly.py`

### Implementation for User Story 2

- [x] T021 [US2] Pass `as_of` through `Hub.get_context_contract` in `packages/pcl-core/src/pcl_core/service.py` and `get_context_contract(..., as_of=None)` in `packages/pcl-server/src/pcl_server/mcp/tools_context.py`
- [x] T022 [US2] Add `as_of` to `TOOL_SCHEMAS["get_context_contract"]` in `packages/pcl-sdk/src/pcl_sdk/mcp_bridge.py`; extend `packages/pcl-sdk/tests/test_mcp_bridge.py` tools/list parity
- [x] T023 [US2] Use `query.as_of` as the single evaluation time in `packages/pcl-core/src/pcl_core/retrieval/contract.py` (null → now); do not mix clocks in one package (FR-005)
- [x] T024 [US2] Validate interval on `Hub.patch` (end before start → `ValidationFailed`); add missing `PATCH /v1/preferences/{id}` (and GET-by-id if needed) in `packages/pcl-server/src/pcl_server/rest/routers/memories.py`

**Checkpoint**: Explicit windows and `as_of` reconstruct past/future without deleting history; 422 on bad intervals

---

## Phase 5: User Story 3 - The Person Can See Current Versus Historical (Priority: P3)

**Goal**: Memories page lists memories **and** preferences with `current` | `historical` badge and interval. Actions: Supersede, Retract (never true), Edit interval. Retract sets `never_true` + tombstone; excluded from current and historical truth (SC-006). Version History modal stays typo versions, labeled as such.

**Independent Test**: After US1 supersede, open Memories — dislike historical, like current, intervals visible; PATCH end date; next contract uses it; retract a false statement — it does not appear as historical and not in later packages.

### Tests for User Story 3 ⚠️ write first, watch them fail

- [x] T025 [P] [US3] Retract tests: `never_true` + tombstone; excluded from Hub list used by the UI and from assembly; supersede pair still has historical predecessor (SC-006) in `packages/pcl-core/tests/test_change_mind.py`

### Implementation for User Story 3

- [x] T026 [US3] Implement `Hub.retract_never_true(obj_id)` in `packages/pcl-core/src/pcl_core/service.py` (research D3); `GET /v1/memories` and `GET /v1/preferences` omit `never_true` rows while `GET` by id remains owner-forensic
- [x] T027 [US3] Owner REST `POST /v1/preferences/{id}/retract` and `POST /v1/memories/{id}/retract` in `packages/pcl-server/src/pcl_server/rest/routers/memories.py`
- [x] T028 [US3] Extend `Memory` and add `Preference` in `frontend/src/api/types.ts` with `valid_from`, `valid_until`, `never_true`, `key`, `value`
- [x] T029 [US3] Render memories + preferences on `frontend/src/pages/Memories.tsx`: current/historical badge, interval, Supersede, Retract, Edit interval (PATCH); keep version History modal labeled as object versions not validity (research D8)

**Checkpoint**: Person can inspect and correct intervals; mistake ≠ change of mind

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: PCA round-trip, perf non-regression, lint/test after the three stories

- [x] T030 [P] Preserve `valid_from`, `valid_until`, `never_true` on preference/memory in PCA export/import (`packages/pca/src/pca/` and a test under `packages/pca/tests/`)
- [x] T031 [P] Extend perf test: assembly < 2 s with closed intervals in the vault, no network egress (SC-007) marked `perf` in `packages/pcl-core/tests/test_contract_perf.py`
- [x] T032 Confirm `specs/005-temporal-validity/quickstart.md` matches shipped routes and UI (supersede, two agents, Memories badges, optional retract)
- [x] T033 Run `make lint` and `make test`; fix regressions in touched packages (`pcl-core`, `pcl-server`, `pcl-sdk`, `pca`, `frontend`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — MVP
- **US2 (Phase 4)**: Depends on Foundational; uses US1 `supersede` + assembly filter but is independently testable via explicit windows / `as_of`
- **US3 (Phase 5)**: Needs US1 objects in the vault; independently testable via retract + Memories UI
- **Polish (Phase 6)**: Depends on desired stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: After Phase 2 — no dependency on US2/US3
- **User Story 2 (P2)**: After Phase 2 — `as_of` and PATCH interval; does not need Memories UI
- **User Story 3 (P3)**: Needs US1 supersede records to review; retract is new; richer after US2 interval PATCH

### Parallel Opportunities

- T001 then T002 can overlap with T002 marked [P]
- T003 and T004 in parallel (different schema files)
- T006 and T007 in parallel after T001+T003–T005
- T008, T009, T010, T011 in parallel (tests, different files)
- T018, T019, T020 in parallel
- T030, T031 in parallel after assembly exists

### Parallel Example: User Story 1

```bash
# After Phase 2, write failing tests in parallel:
Task: "Hub.supersede unit tests in packages/pcl-core/tests/test_change_mind.py"
Task: "Reversal integration in packages/pcl-server/tests/contract/test_preference_reversal.py"
Task: "Assembly current-only + conflict in packages/pcl-core/tests/test_contract_assembly.py"
Task: "Isolation historical leak in packages/pcl-server/tests/forbidden_context/test_contract_isolation.py"

# Then implement sequentially (service.py / contract.py would conflict if parallel):
Task: "Hub.supersede + create uniqueness in service.py"
Task: "assemble_contract temporal filter in retrieval/contract.py"
Task: "REST supersede + trip_seed conflict fixture"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup
2. Phase 2 Foundational
3. Phase 3 User Story 1
4. **STOP and VALIDATE**: reversal demo (`test_preference_reversal.py`)
5. Demo if ready — dislike → supersede like → two agents, current only

### Incremental Delivery

1. Setup + Foundational → interval math + schema
2. US1 → change of mind + current-only package (MVP)
3. US2 → explicit windows + `as_of`
4. US3 → person can see current vs historical; retract
5. Polish → PCA + perf + lint

### Parallel Team Strategy

1. Shared: Phase 1 + 2
2. Then: A implements US1 Hub/assembly/REST; B writes US2 `as_of` tests against the same query field; C wires Memories UI against GET lists once supersede writes intervals

---

## Notes

- [P] = different files, no dependency on incomplete siblings
- Do not add validity to `UniversalMetadata` or to SharedState
- Do not rename `SharedState` or `ActionIntent`
- Do not treat PATCH of `value`/`statement` as change of mind
- Do not tombstone on supersede
- Imported plugin/email content must not call `supersede`
- Commit after each task or logical group
- Stop at any checkpoint to validate the story independently
