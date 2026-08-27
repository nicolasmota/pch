---
description: "Task list for Simulated Hub User"
---

# Tasks: Simulated Hub User

**Input**: Design documents from `/specs/011-simulated-hub-user/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/sim-harness.md, quickstart.md

**Tests**: Included — SC-001…SC-008. Write tests first; they MUST fail before implementation. Constitution 1.0.0: no `pcl-core` I/O, no new listener, no Personal Agency, everyday vault untouched by default.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Package skeleton so tests can import

- [x] T001 Create `packages/pcl-sdk/src/pcl_sdk/sim/` with `__init__.py`, `persona.py`, `runner.py`, `records.py`, `cli.py` placeholders and `personas/` directory
- [x] T002 [P] Create `packages/pcl-sdk/tests/sim/` package (`__init__.py` if required by pytest layout)
- [x] T003 [P] Wire `sim` subparser in `packages/pcl-sdk/src/pcl_sdk/__main__.py` calling `pcl_sdk.sim.cli` (dump/run/status/pause/resume/stop)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Records, compile invariants, isolated Hub construction, CLI refuse paths. Blocks all stories.

**⚠️ CRITICAL**: No user story work until this phase is complete

- [x] T004 Implement `run.json` / `ticks.jsonl` load-save and Run/Tick shapes in `packages/pcl-sdk/src/pcl_sdk/sim/records.py` (data-model.md)
- [x] T005 Implement persona load + compile invariants (volume floors, forbidden actions) in `packages/pcl-sdk/src/pcl_sdk/sim/persona.py`
- [x] T006 Isolated Hub helper: default person dir `~/.pch-sim` (`PCH_SIM_DIR`); tests pass `--data-dir` temp; never open everyday vault unless confirm `WRITE_EVERYDAY_VAULT` in `packages/pcl-sdk/src/pcl_sdk/sim/runner.py`
- [x] T007 CLI refuse: unknown persona, `in_flight`, everyday without confirm (exit 2) in `packages/pcl-sdk/src/pcl_sdk/sim/cli.py`

**Checkpoint**: Foundation ready — dump can fail on missing persona; run refuses everyday without confirm

---

## Phase 3: User Story 1 - Watch a synthetic person fill and query the Hub (Priority: P1) 🎯 MVP

**Goal**: Bundled `lived-stretch` writes a growing corpus, queries it, live timeline (CLI + Hub `/sim`). Isolated by default. Pause/stop consistent.

**Independent Test**: `pcl-sdk sim run --persona lived-stretch --delay-ms 0` on a temp dir completes with ≥40 objects and ≥10 queries; first tick < 2 min; everyday vault unchanged; REST `current_seq` increases before complete.

### Tests for User Story 1 (MUST fail first)

- [x] T008 [P] [US1] `test_first_tick_under_two_minutes` in `packages/pcl-sdk/tests/sim/test_run.py` (SC-001)
- [x] T009 [P] [US1] `test_lived_stretch_volume` in `packages/pcl-sdk/tests/sim/test_run.py` (SC-002)
- [x] T010 [P] [US1] `test_every_create_has_tick` and `test_tick_input_output` in `packages/pcl-sdk/tests/sim/test_timeline.py` (SC-003, SC-006)
- [x] T011 [P] [US1] `test_everyday_vault_unchanged` and `test_everyday_refused_without_confirm` in `packages/pcl-sdk/tests/sim/test_isolation.py` (SC-004, FR-007)
- [x] T012 [P] [US1] `test_situation_asks_hit_trip` in `packages/pcl-sdk/tests/sim/test_queries.py` (SC-005)
- [x] T013 [P] [US1] `test_no_outbound_actions` in `packages/pcl-sdk/tests/sim/test_refuse.py` (SC-008)
- [x] T014 [P] [US1] `test_seq_increases_before_complete` in `packages/pcl-server/tests/test_sim_rest.py` (bar 1 live)

### Implementation for User Story 1

- [x] T015 [US1] Author declarative `packages/pcl-sdk/src/pcl_sdk/sim/personas/lived-stretch.json` that compiles to ≥40 owner-creates (project, preference, memory, + goal/commitment/decision), a preference supersede, and ≥10 search/situation-ask ticks over 14 simulated days
- [x] T016 [US1] Implement tick executor for `create`, `supersede`, `search`, `get_context_contract`, `brief` with labels `sim`/`persona:lived-stretch` in `packages/pcl-sdk/src/pcl_sdk/sim/runner.py`
- [x] T017 [US1] Implement `sim dump` and blocking `sim run` / `status` / `pause` / `resume` / `stop` in `packages/pcl-sdk/src/pcl_sdk/sim/cli.py`
- [x] T018 [US1] Add `packages/pcl-server/src/pcl_server/rest/routers/sim.py` (`POST/GET /v1/sim/runs`, pause/resume/stop, ticks, objects) using `app.state.sim_hub` (isolated), not everyday hub
- [x] T019 [US1] Hook `sim_hub` + background tick task in `packages/pcl-server/src/pcl_server/rest/app.py` (existing loopback lifespan; no new bind)
- [x] T020 [US1] Add `/sim` page `frontend/src/pages/Sim.tsx` (start, pause, resume, stop, polling timeline role/action/result, tick inspector input+result, object panel via `/v1/sim/objects/{id}`)
- [x] T021 [US1] Register route and “Simulator” nav in `frontend/src/App.tsx`, `frontend/src/components/Sidebar.tsx`, types in `frontend/src/api/types.ts`

**Checkpoint**: US1 independently demoable via CLI and `/sim`. Everyday vault unchanged.

---

## Phase 4: User Story 2 - Owner vs assistant roles (Priority: P2)

**Goal**: Timeline labels role. Assistant proposes; not canonical until accept. Narrow grant withholds.

**Independent Test**: `--leave-proposals` leaves memory non-canonical; auto-accept path appears in next contract; work-scoped grant omits other project.

### Tests for User Story 2 (MUST fail first)

- [x] T022 [P] [US2] `test_proposal_not_canonical_before_accept` in `packages/pcl-sdk/tests/sim/test_roles.py` (FR-005)
- [x] T023 [P] [US2] `test_narrow_grant_withholds` in `packages/pcl-sdk/tests/sim/test_pair.py` (US2.4)

### Implementation for User Story 2

- [x] T024 [US2] Mint pair + grant on sim Hub; assistant ticks use `actor=connection_id`; owner `decide_proposal` auto-accept unless `--leave-proposals` in `packages/pcl-sdk/src/pcl_sdk/sim/runner.py`
- [x] T025 [US2] Add `propose_memory` / `decide_proposal` actions and role labels on every tick in `packages/pcl-sdk/src/pcl_sdk/sim/runner.py` and `lived-stretch.json`
- [x] T026 [US2] Timeline shows role; REST tick payload includes `role` and `withheld` in `packages/pcl-server/src/pcl_server/rest/routers/sim.py` and `frontend/src/pages/Sim.tsx`

**Checkpoint**: US1+US2: mixed-role run is labeled; proposals respect review.

---

## Phase 5: User Story 3 - Inspect, replay, optional Cursor path (Priority: P3)

**Goal**: Open any tick’s input/output without re-run. Optional `--paired-assistant` labels `via` and prints MCP recipe (does not write `.cursor/mcp.json`).

**Independent Test**: GET last 20 ticks have input+result; flag off completes with `via=in_process_pair`; flag on labels `via=paired_assistant`.

### Tests for User Story 3 (MUST fail first)

- [x] T027 [P] [US3] `test_via_label_optional_path` in `packages/pcl-sdk/tests/sim/test_pair.py` (SC-007)

### Implementation for User Story 3

- [x] T028 [US3] `--paired-assistant` / `--print-mcp-recipe` in `packages/pcl-sdk/src/pcl_sdk/sim/cli.py` (stdout recipe only; never write `.cursor/mcp.json`)
- [x] T029 [US3] Set tick `via` from run flag in `packages/pcl-sdk/src/pcl_sdk/sim/runner.py`
- [x] T030 [US3] UI checkbox for paired-assistant start; tick inspector shows `via` in `frontend/src/pages/Sim.tsx`

**Checkpoint**: All three stories independently testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T031 Align CLI default data dir with contract: person CLI `~/.pch-sim`, tests always pass temp `--data-dir` (fix D2/contract wording drift in `packages/pcl-sdk/src/pcl_sdk/sim/cli.py` and `specs/011-simulated-hub-user/research.md` D2)
- [x] T032 [P] Ensure compile rejects `propose_action` / connector / plugin outbound in `packages/pcl-sdk/src/pcl_sdk/sim/persona.py`
- [x] T033 Run `make test` and `make lint`; `uv run pcl-sdk loop evidence` then record test stage

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: start immediately
- **Foundational (Phase 2)**: depends on Setup — BLOCKS stories
- **US1 (Phase 3)**: after Foundational — MVP
- **US2 (Phase 4)**: after US1 runner exists (same `runner.py`; sequential)
- **US3 (Phase 5)**: after US2 pair exists
- **Polish**: after stories

### User Story Dependencies

- **US1**: no other stories
- **US2**: extends US1 runner (same files; do not start in parallel on `runner.py`)
- **US3**: extends US2 `via` field

### Parallel Opportunities

- T002/T003 after T001
- T008–T014 (all US1 tests) in parallel before T015–T021
- T022/T023 in parallel before T024
- T032 with T031

---

## Parallel Example: User Story 1 tests

```bash
# After T007, write failing tests together:
# packages/pcl-sdk/tests/sim/test_run.py
# packages/pcl-sdk/tests/sim/test_timeline.py
# packages/pcl-sdk/tests/sim/test_isolation.py
# packages/pcl-sdk/tests/sim/test_queries.py
# packages/pcl-sdk/tests/sim/test_refuse.py
# packages/pcl-server/tests/test_sim_rest.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1–2
2. Failing US1 tests
3. Persona + runner + CLI + REST + `/sim`
4. Validate SC-001…SC-006, SC-008, isolation

### Incremental Delivery

1. US1 → watch feed+query on isolated space
2. US2 → roles and proposals
3. US3 → inspect + optional Cursor recipe
4. Polish + `make test`

### Notes

- Do not commit unless the person asked
- Do not write `.cursor/mcp.json`
- Do not modify `pcl-core` except by calling existing Hub methods
- Do not modify `pcl-sdk/eval/` (E6)
- Tests fail before satisfying code
