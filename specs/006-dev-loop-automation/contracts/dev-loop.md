# Contract: Development Loop CLI

**Feature**: `specs/006-dev-loop-automation/`  
**Surface**: `pcl-sdk loop` (stdio, repo-root cwd). No HTTP. No MCP. No Hub.

Implementer tests live in `packages/pcl-sdk/tests/devloop/` and MUST be written first (fail before the CLI satisfies them).

## Commands

| Command | Purpose | Exit |
|---------|---------|------|
| `pcl-sdk loop start` | Create or refuse a run | 0 start/resume; 2 refuse |
| `pcl-sdk loop next` | Print the current stage and what the agent must run | 0; 1 if blocked/failed/complete |
| `pcl-sdk loop record --stage <id> --outcome pass\|fail\|blocked_on_person` | Persist StageRecord; may advance `current_stage` | 0; 1 on invariant break |
| `pcl-sdk loop record-verdict --critic A\|B --verdict WIN\|LOSE --round N [--failing id,id]` | Append CriticVerdict | 0; 1 if bar hash drifted |
| `pcl-sdk loop status` | Print run summary (stage, outcomes, latest verdicts, evidence timestamps) | 0; 1 if no run |
| `pcl-sdk loop stop` | `status=stopped`, `stop_reason=person_stop` | 0 |
| `pcl-sdk loop evidence --command <cmd> --exit-code N --summary <text>` | Record test evidence | 0 |

`--dir <feature_dir>` is optional on all commands except `start` when `source=dir`; default is `.specify/feature.json`’s `feature_directory`.

### `start` flags

```text
pcl-sdk loop start --mode full|design-only
  (--desc "…" | --epic E2 | --dir specs/005-temporal-validity | --roadmap)
  [--resume] [--redo <stage>]
```

Exactly one source flag. `--roadmap` selects the next era epic in `docs/ROADMAP.md` order (E1…E6) whose spec is missing or whose `RUN.json` is not `complete`. It does **not** open `docs/ROADMAP.md` as the feature to implement.

### `next` stdout (JSON)

```json
{
  "feature_dir": "specs/006-dev-loop-automation",
  "stage": "freeze_bar",
  "command": "write PLAN-BAR.md then loop record --stage freeze_bar --outcome pass",
  "skill": "speckit-plan",
  "status": "running",
  "gauntlet_round": 0
}
```

`skill` is a Speckit/loop skill name the agent runs (`speckit-specify`, `speckit-plan`, `speckit-tasks`, `speckit-analyze`, `speckit-implement`, `speckit-converge`, `speckit-clarify`, or `gauntlet-critics` for the critic dispatch). `command` is human-readable; the sequencer does not shell out to the model.

## Refusals (exit 2)

| Condition | `refuse_reason` | Spec |
|-----------|-----------------|------|
| No source / empty `--desc` | `empty_start` | FR-001 |
| Source path is `docs/VISION.md` or `docs/ROADMAP.md`, or `--desc` asks to implement those files as the spec | `not_a_feature` | FR-015, SC-007 |
| `--epic` / `--dir` targets 001–003 as a **new** epic reopen | `closed_chapter` | FR-015 |
| Second start on in-flight RUN without `--resume`/`--redo` | `in_flight` | edge case |
| `plan` record while `bar_sha256` is null | (exit 1, not refuse) | FR-006 |

Closed-chapter check: feature dir basename matching `001-`, `002-`, or `003-` is allowed only as `--dir` resume of existing work, never as `--epic` spawn.

## Gauntlet record rules

1. `record --stage freeze_bar --outcome pass` hashes the bar file (`PLAN-BAR.md` preferred; else `SPEC-BAR.md`) into `bar_sha256`.
2. `record --stage plan --outcome pass` fails if pack files missing **or** `bar_sha256` is null **or** bar file hash ≠ stored hash.
3. `record-verdict` fails if bar hash drifted (`bar_moved`).
4. After two WIN in the same round: `record` may mark `gauntlet` pass and advance.
5. LOSE or disagree: `gauntlet_round += 1`; if `> 3`, `status=failed`, `stop_reason=budget_exhausted`; else `current_stage=plan` (bar hash kept).

## Complete rules

`status` becomes `complete` only when the sequencer’s `complete_allowed(run)` is true (data-model invariant). `loop record --stage complete` is not a free-form write; it is derived. A client that POSTs complete without evidence is not applicable (no HTTP); tests call `complete_allowed` directly.

## Status stdout (person-visible)

Plain text, no need to ask:

```text
feature: specs/006-dev-loop-automation
mode: full
status: running
stage: gauntlet (round 1/3)
passed: specify, freeze_bar, plan
latest verdicts: A=LOSE B=LOSE
test evidence: none
```

## Fixture contract tests (must fail first)

| Test file | Asserts |
|-----------|---------|
| `packages/pcl-sdk/tests/devloop/test_refuse.py` | SC-007 vision/roadmap; closed chapter; empty start |
| `packages/pcl-sdk/tests/devloop/test_sequence.py` | SC-001 stage order; design-only stops after gauntlet WIN; later stage blocked until prior pass |
| `packages/pcl-sdk/tests/devloop/test_resume.py` | SC-006 resume after specify; in_flight; `--redo` |
| `packages/pcl-sdk/tests/devloop/test_gauntlet.py` | SC-002 freeze before plan; LOSE does not change bar hash; disagreement is not WIN; budget 3 |
| `packages/pcl-sdk/tests/devloop/test_delivery.py` | SC-003 stop on budget; SC-004 complete needs evidence; SC-005 unmet refuses complete; red_before_green |
| `packages/pcl-sdk/tests/devloop/test_status.py` | status lists stages and latest verdicts without extra flags |

## Out of contract

Git commit/push/PR. Hub HTTP. Editing Speckit core skill files except adding `speckit-loop`. Changing vault schema.
