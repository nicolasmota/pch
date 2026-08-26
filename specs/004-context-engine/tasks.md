---

description: "Task list for Context Engine"
---

# Tasks: Context Engine

**Input**: Design documents from `/specs/004-context-engine/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/context-contract.md

**Tests**: Included — SC-001…SC-007 demand deterministic suites (killer demo, correction propagation, isolation, citations, audit, perf, sufficiency). Write tests first; they MUST fail before implementation.

**Organization**: Tasks are grouped by user story so each story is an independently testable increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete sibling tasks)
- **[Story]**: US1 (trip handoff + assembly), US2 (grant bounding + omissions), US3 (audit review)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: New module files and a reusable trip-demo seed used by later tests

- [ ] T001 Create empty modules `packages/pcl-core/src/pcl_core/schema/contract.py` and `packages/pcl-core/src/pcl_core/retrieval/contract.py` (no logic yet)
- [ ] T002 [P] Add trip-demo seed helper (Project + Goal + Preferences + Decisions Amsterdam/London + Memories + SharedState) in `packages/pcl-core/tests/helpers/trip_seed.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Request/response models and audit kind every story needs. Contracts remain ephemeral — not added to `TYPE_MODELS`.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Implement Pydantic models `ContextQuery`, `ContextContract`, `ContractItem`, `OmissionNote`, `SituationRef`, `ItemRef`, `ConflictPair`, `ScopeSummary` in `packages/pcl-core/src/pcl_core/schema/contract.py` matching `specs/004-context-engine/data-model.md` (empty `purpose` fails validation; `citation` min length 1; omission has category/label/count only)
- [ ] T004 [P] Add `EventKind.CONTEXT_CONTRACT = "context.contract"` in `packages/pcl-core/src/pcl_core/schema/audit.py`
- [ ] T005 Export contract models from `packages/pcl-core/src/pcl_core/schema/__init__.py` without adding them to `TYPE_MODELS`
- [ ] T006 Schema unit tests (empty purpose rejected; citation required; omission fields cannot carry item ids/titles) in `packages/pcl-core/tests/test_contract_schema.py`

**Checkpoint**: Models validate; `context.contract` is a legal event kind; no vault table or TYPE_MODELS change

---

## Phase 3: User Story 1 - Continue the Trip in a Second Agent (Priority: P1) 🎯 MVP

**Goal**: An authorized agent submits a purpose and receives one Context Contract assembled from live 001 objects — citations on every item, empty-but-valid when nothing matches, correction ("dropped London") visible in the next contract. Exposed as MCP tool `get_context_contract`.

**Independent Test**: Seed the trip vault; pair two agents with the same grant; both call `get_context_contract` with purpose `"continue planning the trip"` and receive the same substantive package (goal, travelers, live candidate, budget, decisions, citations) without issuing searches; record a Decision rejecting London; subsequent contracts show Amsterdam live and London as rejected.

### Tests for User Story 1 ⚠️ write first, watch them fail

- [ ] T007 [P] [US1] Assembly unit tests (anchor selection, FTS fallback, tie → candidates not merged, ranking + caps, conflicts listed not resolved, empty/minimal contract, citations present, live versions only) in `packages/pcl-core/tests/test_contract_assembly.py`
- [ ] T008 [P] [US1] MCP/HTTP contract tests vs `specs/004-context-engine/contracts/context-contract.md` (request schema, 200 empty contract, 422 empty purpose, response required fields, B4/B5/B6/B12) in `packages/pcl-server/tests/contract/test_mcp_contract.py`
- [ ] T009 [P] [US1] Killer-demo integration test: two agents, same purpose, identical substance, then "dropped London" correction reflected (SC-001, SC-002, SC-004) in `packages/pcl-server/tests/contract/test_trip_handoff.py`

### Implementation for User Story 1

- [ ] T010 [US1] Implement situation selection + category assembly + sufficiency caps + conflict pairing in `packages/pcl-core/src/pcl_core/retrieval/contract.py` (reuse FTS5, `DefaultRanker`, `significant_tokens`, `citations_for`; D2/D3/D5/D6)
- [ ] T011 [US1] Add `Hub.get_context_contract()` in `packages/pcl-core/src/pcl_core/service.py`: call assembly, append `EventKind.CONTEXT_CONTRACT` with `status: issued`, `contract_id`, purpose, item refs (no bodies), omission categories
- [ ] T012 [US1] Register MCP tool `get_context_contract(purpose, subject_ref=None, max_items=None)` in `packages/pcl-server/src/pcl_server/mcp/tools_context.py` using `mcp._current_actor`
- [ ] T013 [US1] Add `get_context_contract` to `TOOL_NAMES` and `TOOL_SCHEMAS` in `packages/pcl-sdk/src/pcl_sdk/mcp_bridge.py` (request schema from the contract doc); extend `packages/pcl-sdk/tests/test_mcp_bridge.py` so `tools/list` parity includes the new tool

**Checkpoint**: Killer demo passes through MCP; two agents get the same package; empty purpose 422; no-match returns a valid empty contract, not a dump

---

## Phase 4: User Story 2 - The Package Respects the Grant and Says What It Withheld (Priority: P2)

**Goal**: Every candidate item passes `policy.evaluate()` under the requesting grant. Cross-scope items never appear. Omission notes name category + count only. Revoked grant refuses with an auditable `status: refused` event.

**Independent Test**: Seed personal + work objects; two scoped grants; same purpose from each agent → 0 cross-scope items and omission notes when withheld material existed; revoked token → 401/403 plus one `context.contract` refused event.

### Tests for User Story 2 ⚠️ write first, watch them fail

- [ ] T014 [P] [US2] Unit tests for grant bounding and aggregated omission notes (no withheld ids/titles/content in `omissions`) in `packages/pcl-core/tests/test_contract_grants.py`
- [ ] T015 [P] [US2] Isolation tests (personal vs work grants, 0 leakage, omission present when relevant material withheld, revoked grant refused) marked `forbidden_context` in `packages/pcl-server/tests/forbidden_context/test_contract_isolation.py`

### Implementation for User Story 2

- [ ] T016 [US2] Filter every candidate through `policy.evaluate()` and aggregate DENY/REDACT into `OmissionNote`s (`scope_not_granted`, `classification_ceiling`, `capability_missing`, `policy_exclusion`) in `packages/pcl-core/src/pcl_core/retrieval/contract.py` (D4; out-of-scope `subject_ref` ignored with an omission, not an error)
- [ ] T017 [US2] Append `context.contract` with `status: refused` on unauthenticated/revoked requests in `packages/pcl-core/src/pcl_core/service.py` (and the MCP/auth path that already returns 401/403); empty `purpose` stays 422 with no ledger event (B10)

**Checkpoint**: Isolation test green (SC-003); omissions never leak withheld content; revoked grant is auditable

---

## Phase 5: User Story 3 - The Person Can See What Was Assembled and Delivered (Priority: P3)

**Goal**: The existing Audit page shows each `context.contract` issuance/refusal: agent, purpose, status, item refs, omission categories, timestamp. Owner correction of a source object wins on the next assembly (already assembled by T010/T011; this phase makes it inspectable).

**Independent Test**: Issue several contracts; open Audit; each `context.contract` row shows agent, purpose, included refs, omissions, time; edit a preference; next contract uses the live version.

### Tests for User Story 3 ⚠️ write first, watch them fail

- [ ] T018 [P] [US3] Events API tests: `GET /v1/events?kind=context.contract` returns `extra` with `contract_id`, `purpose`, `status`, `item_refs`, `omission_categories` (SC-005) in `packages/pcl-server/tests/contract/test_contract_audit.py`

### Implementation for User Story 3

- [ ] T019 [US3] Extend `AuditEvent` in `frontend/src/api/types.ts` with `kind` (already present) and `extra` so the UI can read issuance fields
- [ ] T020 [US3] Render `context.contract` events in `frontend/src/pages/Audit.tsx` (agent, purpose, status, item refs, omission categories, timestamp) without a new endpoint

**Checkpoint**: Person can inspect every issuance from Audit; correction of a source object is visible in the next contract (covered by T009/T011)

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Quickstart, perf, and repo-wide checks after the three stories

- [ ] T021 Write `specs/004-context-engine/quickstart.md` covering seed trip vault, pair two agents, call `get_context_contract`, drop London, inspect Audit
- [ ] T022 [P] Perf test: assembly < 2 s on a seeded vault of a few thousand objects, no network egress during assembly (SC-006, B7) marked `perf` in `packages/pcl-core/tests/test_contract_perf.py`
- [ ] T023 [P] Sufficiency assertion on the trip fixture: inlined memories ≤ cap; overflow appears only in `references` (SC-007) in `packages/pcl-core/tests/test_contract_assembly.py`
- [ ] T024 Run `make lint` and `make test`; fix regressions in touched packages (`pcl-core`, `pcl-server`, `pcl-sdk`, `frontend`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — MVP
- **US2 (Phase 4)**: Depends on Foundational; integrates with US1 assembly (same `retrieval/contract.py` / `service.py`) but is independently testable via isolation suite
- **US3 (Phase 5)**: Depends on US1 issuance records existing; independently testable via events API + Audit UI
- **Polish (Phase 6)**: Depends on desired stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: After Phase 2 — no dependency on US2/US3
- **User Story 2 (P2)**: After Phase 2 — extends assembly with policy filter; isolation tests do not require Audit UI
- **User Story 3 (P3)**: Needs US1 ledger events; does not need US2 for the happy-path review, but omission columns are richer after US2

### Parallel Opportunities

- T001 then T002 can overlap with T002 marked [P]
- T004 can run in parallel with T003
- T007, T008, T009 in parallel (tests, different files)
- T014, T015 in parallel
- T022, T023 in parallel after assembly exists

### Parallel Example: User Story 1

```bash
# After Phase 2, write failing tests in parallel:
Task: "Assembly unit tests in packages/pcl-core/tests/test_contract_assembly.py"
Task: "MCP contract tests in packages/pcl-server/tests/contract/test_mcp_contract.py"
Task: "Killer-demo integration in packages/pcl-server/tests/contract/test_trip_handoff.py"

# Then implement sequentially (same files would conflict if parallel):
Task: "retrieval/contract.py assembly"
Task: "Hub.get_context_contract in service.py"
Task: "MCP tool + SDK schema"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup
2. Phase 2 Foundational
3. Phase 3 User Story 1
4. **STOP and VALIDATE**: killer demo via MCP (`test_trip_handoff.py`)
5. Demo if ready — two agents, one purpose, one package

### Incremental Delivery

1. Setup + Foundational → models + audit kind
2. US1 → portable situation package (MVP)
3. US2 → isolation + omission honesty
4. US3 → person can see what was delivered
5. Polish → quickstart + perf

### Parallel Team Strategy

1. Shared: Phase 1 + 2
2. Then: A implements US1 assembly/MCP; B writes US2 isolation tests against the same API; C wires Audit UI against ledger `extra` once T011 writes it

---

## Notes

- [P] = different files, no dependency on incomplete siblings
- Do not add `ContextContract` to `TYPE_MODELS` or persist contracts
- Do not rename `SharedState` or `ActionIntent`
- Assembly must not call plugins, HTTP, or imports
- Commit after each task or logical group
- Stop at any checkpoint to validate the story independently
