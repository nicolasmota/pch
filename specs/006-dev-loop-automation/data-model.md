# Data Model: Development Loop Automation

**Feature**: `specs/006-dev-loop-automation/` · **Date**: 2026-08-26

No vault types. Records are files in the spec folder. Field names below are normative for `RUN.json` and the CLI.

## WorkflowRun (`RUN.json`)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `schema_version` | int | yes | `1` |
| `feature_dir` | str | yes | Repo-relative, e.g. `specs/006-dev-loop-automation` |
| `mode` | str | yes | `full` \| `design-only` |
| `source` | str | yes | `desc` \| `epic` \| `dir` \| `roadmap` |
| `source_value` | str \| null | no | Description text, epic id (`E2`), or path |
| `current_stage` | str | yes | See Stage id table |
| `status` | str | yes | `running` \| `blocked_on_person` \| `failed` \| `stopped` \| `complete` |
| `stop_reason` | str \| null | no | `person_stop` \| `budget_exhausted` \| `refused` \| `unmet_items` \| null |
| `refuse_reason` | str \| null | no | `not_a_feature` \| `closed_chapter` \| `empty_start` \| `in_flight` \| null |
| `bar_path` | str \| null | no | Repo-relative bar file |
| `bar_sha256` | str \| null | no | Frozen hash; plan may not start until set |
| `gauntlet_round` | int | yes | Default `0`; max `3` |
| `test_repair_round` | int | yes | Default `0`; max `2` |
| `stages` | object | yes | Map of stage id → StageRecord |
| `unmet_items` | list[str] | yes | Spec/plan/task ids still open after delivery |
| `updated_at` | str | yes | ISO-8601 UTC |

**Invariants**:
- `complete` implies (design-only ∧ gauntlet pass) ∨ (full ∧ test pass ∧ delivery pass ∧ `unmet_items` empty).
- `bar_sha256` is immutable once set for a run, unless `--redo freeze_bar`.
- If `status=running` and `current_stage=plan`, `bar_sha256` is non-null.
- A second `start` on the same `feature_dir` with an existing non-terminal run does not replace the file (`refuse_reason=in_flight`) unless `--resume` (default for `--dir`) or `--redo`.

## StageRecord

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | str | yes | Stage id |
| `outcome` | str \| null | no | `pass` \| `fail` \| `blocked_on_person` \| null (not started) |
| `started_at` | str \| null | no | |
| `ended_at` | str \| null | no | |
| `evidence` | object \| null | no | Stage-specific (verdicts, test command, SC map) |

## Stage ids (order)

| id | Gate to pass | Next |
|----|--------------|------|
| `specify` | `spec.md` exists and requirements checklist has no `[NEEDS CLARIFICATION]` **or** those markers exist → `clarify` | `clarify` or `freeze_bar` |
| `clarify` | Markers resolved or person answers recorded | `freeze_bar` |
| `freeze_bar` | Bar file exists; `bar_sha256` recorded | `plan` |
| `plan` | Pack files exist (`plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`) | `gauntlet` |
| `gauntlet` | Two critic verdicts `WIN`; bar hash unchanged | `tasks` or `complete` if design-only |
| `tasks` | `tasks.md` exists with T-ids | `analyze` |
| `analyze` | Consistency report `pass` (no spec/plan/task contradictions that drop FRs) | `implement` |
| `implement` | `tasks.md` checkboxes for in-scope stories | `test` |
| `test` | Recorded command exit 0 | `delivery` |
| `delivery` | SC map all pass; `red_before_green` true per code SC; constitution gates pass | `converge` if unmet else `complete` |
| `converge` | New tasks appended and then implement/test/delivery re-run, or person accepts stop | `implement` or `failed` |
| `complete` | Derived terminal | — |

## QualityBar (file, not JSON type)

Existing practice: `PLAN-BAR.md` (plan pack) or `SPEC-BAR.md` (spec, when present). The sequencer only stores path + sha256. It does not parse criteria. Critics read the file.

**Invariant**: After freeze, `sha256(bar file) == bar_sha256` or the run fails (`bar_moved`).

## CriticVerdict (inside `stages.gauntlet.evidence.verdicts`)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `critic_id` | str | yes | `A` \| `B` (two required) |
| `round` | int | yes | Matches `gauntlet_round` |
| `verdict` | str | yes | `WIN` \| `LOSE` |
| `failing_criteria` | list[str] | yes | Empty on WIN |
| `evidence_note` | str | no | Quote/file pointers; not a builder recap |

**Invariants**:
- WIN requires both critics WIN in the same round with identical `round`.
- Disagree → not WIN; round increments; back to `plan`.
- LOSE → round increments; back to `plan`; bar hash unchanged.

## DeliveryEvidence (inside `stages.test` / `stages.delivery`)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `command` | str | yes | e.g. `make test` / `make lint` |
| `exit_code` | int | yes | |
| `summary` | str | yes | Counts or last lines; not “should pass” |
| `recorded_at` | str | yes | Freshness; complete must cite this timestamp |
| `sc_results` | object | delivery only | `{ "SC-001": "pass" \| "fail" \| "missing" }` |
| `red_before_green` | object | delivery only | `{ "SC-001": true \| false }` |

## State transitions

```text
(start) ──► specify ──► freeze_bar ──► plan ──► gauntlet ──┬──► tasks ──► … ──► complete
                │                         │               └──► complete (design-only)
                └── clarify ──────────────┘
gauntlet LOSE/disagree ──► plan (bar hash kept)
test/delivery fail ──► implement (test_repair_round++) or failed
blocked_on_person ──► (person answers) ──► same stage retry or next
stop ──► status=stopped; resume continues from current_stage
refuse ──► status=failed, no spec dir created for vision/roadmap
```

## Hub operations

None. The coding agent MUST NOT pair, write memories, or call Hub tools as part of this feature.
