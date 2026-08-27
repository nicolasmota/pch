---

description: "Task list for Situation State and Intent"
---

# Tasks: Situation State and Intent

**Input**: Design documents from `/specs/007-situation-state-intent/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/operational-state.md, quickstart.md

**Tests**: Included — constitution and SC-001…SC-007 demand deterministic suites (phase vs SharedState, intent vs ActionIntent, patch-then-contract, isolation, unset, two-agent MCP, perf). Write tests first; they MUST fail before implementation.

**Organization**: Tasks are grouped by user story so each story is an independently testable increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete sibling tasks)
- **[Story]**: US1 (phase on package), US2 (situation intent), US3 (Hub view/correct + agent propose)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Enum and schema fields every story copies onto `SituationRef`. No Hub operations yet.

- [x] T001 Add `OperationalPhase` enum (`planning`, `comparing_itineraries`, `waiting_for_approval`, `choosing_hotel`, `other`) plus optional `operational_phase`, `current_step` (max 200), `situation_intent` (max 200) on `Project` and `Goal` in `packages/pcl-core/src/pcl_core/schema/project.py`
- [x] T002 [P] Add the same three optional fields to `SituationRef` in `packages/pcl-core/src/pcl_core/schema/contract.py` (JSON `null` when unset; `status` remains ProjectStatus)
- [x] T003 Export `OperationalPhase` from `packages/pcl-core/src/pcl_core/schema/__init__.py`

**Checkpoint**: Models validate; assembly still ignores the new fields

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schema unit tests and proposal type. No silent agent writes.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Schema tests: defaults null; unknown phase rejected; step/intent max 200; `Project.status` independent of `operational_phase` in `packages/pcl-core/tests/test_operational_schema.py`
- [x] T005 Add `OperationalProposal` (`type=operational_proposal`, `target_id`, three optional fields, `ProposalStatus`, `submitted_by`) in `packages/pcl-core/src/pcl_core/schema/proposal.py` and export + `TYPE_MODELS` in `packages/pcl-core/src/pcl_core/schema/__init__.py`

**Checkpoint**: Proposal model exists; PATCH of Project fields still generic; no MCP tool yet

---

## Phase 3: User Story 1 - The Package Names Where the Work Stands (Priority: P1) 🎯 MVP

**Goal**: Owner PATCH sets `operational_phase` (and optional step). `get_context_contract` copies onto `SituationRef`. SharedState `trip.phase` stays in `state[]`. Two agents agree. Unset still assembles. Isolation holds. Perf stays < 2 s.

**Independent Test**: Seed trip; PATCH `comparing_itineraries`; two agents `get_context_contract` purpose `"continue planning the trip"` → `situation.operational_phase` is that enum; `trip.phase` in `state[]` is not that field (SC-001, SC-006). Unset → still assembles, null phase (SC-005). Work grant: 0 personal phase (SC-004). Perf: `test_contract_perf.py` still < 2 s (SC-007).

### Tests for User Story 1 ⚠️ write first, watch them fail

- [x] T006 [P] [US1] `test_phase_in_situation_not_shared_state`, `test_unset_assembles_without_inventing` in `packages/pcl-core/tests/test_operational_contract.py` (SC-001, SC-005)
- [x] T007 [P] [US1] Isolation: work-scoped package omits personal project phase/intent; omission has no titles/ids (SC-004) marked `forbidden_context` in `packages/pcl-server/tests/forbidden_context/test_operational_isolation.py`
- [x] T008 [P] [US1] Two MCP tokens agree on phase (SC-006) in `packages/pcl-server/tests/contract/test_operational_mcp.py`
- [x] T009 [P] [US1] Extend `packages/pcl-core/tests/test_contract_perf.py` so the trip project has operational fields set; still < 2 s; still `hub.get_context_contract` (SC-007)

### Implementation for User Story 1

- [x] T010 [US1] Copy `operational_phase` / `current_step` / `situation_intent` from the selected Project onto `SituationRef` (and candidates) in `packages/pcl-core/src/pcl_core/retrieval/contract.py`; Goal overlay when `subject_ref` is a Goal (data-model overlay rule)
- [x] T011 [US1] Confirm owner `PATCH /v1/projects/{id}` persists the three fields via existing `Hub.patch` in `packages/pcl-server/src/pcl_server/rest/routers/projects.py` (no new write path)

**Checkpoint**: Phase on package; SharedState handoff distinct; isolation + perf green

---

## Phase 4: User Story 2 - The Package Names What They Are Trying to Do Now (Priority: P2)

**Goal**: `situation_intent` is the short string on Project/Goal. ActionIntent objects are not presented as that intent. PATCH of intent is live on the next contract (SC-002, SC-003).

**Independent Test**: Set intent `"choose next itinerary"`; contract includes it; create an ActionIntent approval; contract still uses the string field, not the approval; PATCH a new intent; next contract shows only the new one.

### Tests for User Story 2 ⚠️ write first, watch them fail

- [x] T012 [P] [US2] `test_intent_not_action_intent` and `test_patch_then_next_contract` in `packages/pcl-core/tests/test_operational_contract.py` (SC-002, SC-003)

### Implementation for User Story 2

- [x] T013 [US2] Keep ActionIntent tools unchanged in `packages/pcl-server/src/pcl_server/mcp/tools_context.py`; do not copy ActionIntent summaries onto `situation_intent` in `packages/pcl-core/src/pcl_core/retrieval/contract.py`

**Checkpoint**: Intent is a field; approvals remain approvals

---

## Phase 5: User Story 3 - The Person Can See and Correct Phase and Intent (Priority: P3)

**Goal**: Projects page shows/edits the three fields. Agents `propose_operational_state`; Review Queue accept/reject; live fields unchanged until accept.

**Independent Test**: Open Projects; fields visible; edit phase; next package uses it; agent propose does not change live fields until Accept (quickstart §§3–4).

### Tests for User Story 3 ⚠️ write first, watch them fail

- [x] T014 [P] [US3] MCP `propose_operational_state` returns pending proposal and does not patch live fields; accept patches; reject does not, in `packages/pcl-server/tests/contract/test_operational_mcp.py`

### Implementation for User Story 3

- [x] T015 [US3] `Hub.propose_operational_state` / `list_operational_proposals` / `decide_operational_proposal` in `packages/pcl-core/src/pcl_core/service.py`
- [x] T016 [US3] Register MCP `propose_operational_state` in `packages/pcl-server/src/pcl_server/mcp/tools_context.py` and `TOOL_NAMES` + `TOOL_SCHEMAS` in `packages/pcl-sdk/src/pcl_sdk/mcp_bridge.py`
- [x] T017 [US3] REST `GET /v1/operational-proposals`, `POST …/accept`, `POST …/reject` in `packages/pcl-server/src/pcl_server/rest/routers/operational.py` and include the router in the FastAPI app
- [x] T018 [US3] Extend `Project` (and Goal if listed) types plus operational proposal type in `frontend/src/api/types.ts`
- [x] T019 [US3] Show/edit phase, step, intent on `frontend/src/pages/Projects.tsx` via PATCH
- [x] T020 [US3] List operational proposals with Accept/Reject on `frontend/src/pages/ReviewQueue.tsx` (do not coerce into `proposed_memory.statement`)

**Checkpoint**: Person-visible + propose/accept; agents cannot silent-write

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Quickstart coverage and repo-wide checks

- [x] T021 [P] Run `make test` and `make lint`; record loop evidence
- [x] T022 Confirm quickstart.md steps 1–6 against the SC map in `specs/007-situation-state-intent/contracts/operational-state.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: After Foundational — MVP
- **US2 (Phase 4)**: After US1 assembly copy exists (same `SituationRef` fields)
- **US3 (Phase 5)**: After Foundational proposal type; can overlap US2
- **Polish**: After US1–US3

### User Story Dependencies

- **US1 (P1)**: After Phase 2
- **US2 (P2)**: After US1 copy path (T010)
- **US3 (P3)**: After T005; UI independent of MCP once REST exists

### Parallel Opportunities

- T002 with T001
- T006, T007, T008, T009 together (tests, different files)
- T018 with T015–T017 (types vs backend)

---

## Parallel Example: User Story 1

```bash
# Tests first (must fail):
Task: "test_operational_contract.py SC-001/SC-005"
Task: "test_operational_isolation.py SC-004"
Task: "test_operational_mcp.py SC-006"
Task: "test_contract_perf.py SC-007"

# Then assembly copy in retrieval/contract.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Setup + Foundational schema
2. Fail-first tests T006–T009
3. Copy fields in assembly (T010)
4. Validate SC-001/004/005/006/007

### Incremental Delivery

1. US1 → phase on package
2. US2 → intent vs ActionIntent
3. US3 → Projects + propose/accept
4. Polish → lint/test evidence

---

## Notes

- Do not rename SharedState or ActionIntent
- Do not treat seed `trip.phase` as operational phase
- Do not add a second MCP read tool
- Do not auto-advance phase
- Commit only if the person asked
