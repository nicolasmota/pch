---

description: "Task list for Context Quality Evaluation"
---

# Tasks: Context Quality Evaluation

**Input**: Design documents from `/specs/010-context-eval/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/eval-report.md, quickstart.md

**Tests**: Included — SC-001…SC-007. Write tests first; they MUST fail before implementation.

## Phase 1: Setup

- [x] T001 Add `packages/pcl-sdk/src/pcl_sdk/eval/` package (harness module placeholder)

## Phase 2: Foundational

- [x] T002 CLI `eval run` in `packages/pcl-sdk/src/pcl_sdk/__main__.py` calling the harness (stdout JSON, exit 1 if not all_pass)

## Phase 3: US1 Killer demo

- [x] T003 [P] `test_killer_demo_accuracy` and `test_assembly_cost_reported` in `packages/pcl-sdk/tests/eval/test_harness.py`
- [x] T004 Implement killer_demo case + retrieval_accuracy + assembly_cost_seconds in `packages/pcl-sdk/src/pcl_sdk/eval/harness.py`

## Phase 4: US2 Freshness / conflict / correction

- [x] T005 [P] `test_freshness_as_of`, `test_conflict_listed`, `test_correction_drop_london` in `packages/pcl-sdk/tests/eval/test_harness.py`
- [x] T006 Implement temporal_conflict + drop_london correction metrics in the harness

## Phase 5: US3 Isolation / portability

- [x] T007 [P] `test_isolation_precision`, `test_portability_and_revoke` in `packages/pcl-sdk/tests/eval/test_harness.py`
- [x] T008 Implement isolation and runtime_switch with real pairing/grants (no policy stub)

## Phase 6: Polish

- [x] T009 `run_eval` returns the report contract (four cases, seven metrics, all_pass); default temp vault
- [x] T010 Run `make test`; record loop evidence

## Notes

- Do not upload scores. Do not score token counts. Do not assemble a second contract.
- Commit only if the person asked
