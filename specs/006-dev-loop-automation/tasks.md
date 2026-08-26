---
description: "Task list for Development Loop Automation"
---

# Tasks: Development Loop Automation

**Input**: Design documents from `/specs/006-dev-loop-automation/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/dev-loop.md, quickstart.md

**Tests**: Required (constitution + plan SC→test map). Write tests FIRST; they MUST fail before the code that satisfies them.

**Organization**: By user story (P1–P4).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1–US4 from spec.md
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Package layout for the sequencer

- [x] T001 Create `packages/pcl-sdk/src/pcl_sdk/devloop/__init__.py` exporting start/next/record/status placeholders
- [x] T002 Create empty module files `packages/pcl-sdk/src/pcl_sdk/devloop/stages.py`, `runfile.py`, `refuse.py`, `cli.py`
- [x] T003 Create `packages/pcl-sdk/tests/devloop/` with `__init__.py` (empty)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: RUN.json IO and stage ids all stories share

**⚠️ CRITICAL**: No user story work until this phase is complete

- [x] T004 Implement RUN.json load/save and bar SHA-256 in `packages/pcl-sdk/src/pcl_sdk/devloop/runfile.py`
- [x] T005 Implement stage id order and `next_stage` / `complete_allowed` stubs with documented invariants in `packages/pcl-sdk/src/pcl_sdk/devloop/stages.py`

**Checkpoint**: Foundation ready

---

## Phase 3: User Story 1 - One Trigger Runs the Whole Loop (Priority: P1) 🎯 MVP

**Goal**: `loop start` + `loop next` + `loop record` walk specify → … → complete (or design-only stop); later stages blocked until prior pass; `--roadmap` picks next epic not the roadmap file.

**Independent Test**: `uv run pytest packages/pcl-sdk/tests/devloop/test_sequence.py packages/pcl-sdk/tests/devloop/test_refuse.py packages/pcl-sdk/tests/devloop/test_resume.py`

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T006 [P] [US1] Sequence tests SC-001 + design-only in `packages/pcl-sdk/tests/devloop/test_sequence.py`
- [x] T007 [P] [US1] Refusal tests SC-007 (vision/roadmap/empty/closed chapter) in `packages/pcl-sdk/tests/devloop/test_refuse.py`
- [x] T008 [P] [US1] Resume tests SC-006 + in_flight in `packages/pcl-sdk/tests/devloop/test_resume.py`

### Implementation for User Story 1

- [x] T009 [US1] Implement refusals in `packages/pcl-sdk/src/pcl_sdk/devloop/refuse.py`
- [x] T010 [US1] Implement start/resume/next/record stage advance in `packages/pcl-sdk/src/pcl_sdk/devloop/stages.py` and `packages/pcl-sdk/src/pcl_sdk/devloop/__init__.py`
- [x] T011 [US1] Wire argparse `loop start|next|record|stop` in `packages/pcl-sdk/src/pcl_sdk/devloop/cli.py` and `packages/pcl-sdk/src/pcl_sdk/__main__.py`

**Checkpoint**: US1 independently testable via pytest

---

## Phase 4: User Story 2 - Gauntlet Is a Gate, Not a Memory (Priority: P2)

**Goal**: freeze_bar before plan; LOSE/disagree rewrite plan not bar; two WINs required; budget 3.

**Independent Test**: `uv run pytest packages/pcl-sdk/tests/devloop/test_gauntlet.py`

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T012 [P] [US2] Gauntlet tests SC-002 in `packages/pcl-sdk/tests/devloop/test_gauntlet.py`

### Implementation for User Story 2

- [x] T013 [US2] Implement bar hash freeze, plan-reject-without-bar, `record-verdict`, LOSE/disagree, budget in `packages/pcl-sdk/src/pcl_sdk/devloop/stages.py` and `packages/pcl-sdk/src/pcl_sdk/devloop/cli.py`

**Checkpoint**: US2 independently testable

---

## Phase 5: User Story 3 - The Person Only Intervenes When a Human Must (Priority: P3)

**Goal**: `loop status` and `loop stop`; `blocked_on_person`; no extra confirm on pass.

**Independent Test**: `uv run pytest packages/pcl-sdk/tests/devloop/test_status.py`

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T014 [P] [US3] Status/stop/help tests SC-008 CLI help + status listing in `packages/pcl-sdk/tests/devloop/test_status.py`

### Implementation for User Story 3

- [x] T015 [US3] Implement `loop status` / `loop stop` / `--outcome blocked_on_person` in `packages/pcl-sdk/src/pcl_sdk/devloop/cli.py`

**Checkpoint**: US3 independently testable

---

## Phase 6: User Story 4 - Delivery Is Not Done Until Evidence Says So (Priority: P4)

**Goal**: evidence required for complete; unmet blocks complete; budget exhaust stops; red_before_green.

**Independent Test**: `uv run pytest packages/pcl-sdk/tests/devloop/test_delivery.py`

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T016 [P] [US4] Delivery tests SC-003, SC-004, SC-005 in `packages/pcl-sdk/tests/devloop/test_delivery.py`

### Implementation for User Story 4

- [x] T017 [US4] Implement `loop evidence`, `complete_allowed`, unmet_items, test_repair_round in `packages/pcl-sdk/src/pcl_sdk/devloop/stages.py` and `packages/pcl-sdk/src/pcl_sdk/devloop/cli.py`

**Checkpoint**: US4 independently testable

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Agent trigger + docs + full suite

- [x] T018 Write `/speckit-loop` skill including Gauntlet critic dispatch (two fresh-context critics, bar+pack only, no builder recap) in `.cursor/skills/speckit-loop/SKILL.md`
- [x] T019 Document `/speckit-loop` as the start instruction in `AGENTS.md`
- [x] T020 Run `uv run pytest packages/pcl-sdk/tests/devloop/` and `uv run ruff check packages/pcl-sdk` (quickstart validation)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Immediate
- **Foundational (Phase 2)**: After Setup — BLOCKS stories
- **US1 (Phase 3)**: After Foundational — MVP
- **US2 (Phase 4)**: After Foundational; uses US1 record/start
- **US3 (Phase 5)**: After Foundational; uses US1 runfile
- **US4 (Phase 6)**: After Foundational; uses US1 complete path
- **Polish (Phase 7)**: After desired stories

### User Story Dependencies

- **US1**: After Phase 2
- **US2**: After US1 CLI exists (same modules; sequential in one agent)
- **US3**: Can follow US1
- **US4**: Can follow US1

### Parallel Opportunities

- T006, T007, T008 in parallel (tests, different files)
- T012, T014, T016 in parallel after US1 tests exist if staffed; in one agent, after prior story impl

---

## Parallel Example: User Story 1

```bash
Task: "Sequence tests in packages/pcl-sdk/tests/devloop/test_sequence.py"
Task: "Refusal tests in packages/pcl-sdk/tests/devloop/test_refuse.py"
Task: "Resume tests in packages/pcl-sdk/tests/devloop/test_resume.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup
2. Phase 2 Foundational
3. Phase 3 US1 tests (fail) then impl
4. Validate pytest US1

### Incremental Delivery

1. US1 sequencer + refusals
2. US2 Gauntlet hash gate
3. US3 status/stop
4. US4 evidence/complete
5. Skill + AGENTS.md

## Notes

- Do not modify `pcl-core`, Hub REST, or frontend
- Do not auto-commit
- `docs/VISION.md` and `docs/ROADMAP.md` are never implement targets
