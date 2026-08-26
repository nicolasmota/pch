# Quickstart: Development Loop Automation

**Feature**: `specs/006-dev-loop-automation/`  
One start instruction runs the remaining stages. Gauntlet is a gate. Complete cites tests.

From the repo root, with the workspace installed (`uv sync`). Do **not** type `/speckit-plan` or `/speckit-implement` yourself in this demo.

## 1. Start (the only instruction)

Full loop on a new description:

```bash
uv run pcl-sdk loop start --mode full --desc "tiny in-scope fixture: add a changelog note that the loop exists"
```

Or resume an existing spec folder:

```bash
uv run pcl-sdk loop start --mode full --dir specs/006-dev-loop-automation --resume
```

Or design-only (stop after plan WIN):

```bash
uv run pcl-sdk loop start --mode design-only --dir specs/005-temporal-validity --resume
```

Then tell the coding agent: **`/speckit-loop`** (it reads `loop next` and keeps going).

Expect: `RUN.json` appears in the feature directory. `loop status` shows `specify` or the next incomplete stage. You are not asked “run plan next?”.

## 2. Bar before pack

When `loop next` says `freeze_bar`, the agent writes `PLAN-BAR.md` **before** `plan.md`. Then:

```bash
uv run pcl-sdk loop record --stage freeze_bar --outcome pass
uv run pcl-sdk loop status
```

Expect: `bar_sha256` set. A `plan` record before this step **fails**.

## 3. Gauntlet

After the plan pack is on disk, two critics read the bar and the pack (not a recap). Record:

```bash
uv run pcl-sdk loop record-verdict --critic A --verdict WIN --round 1
uv run pcl-sdk loop record-verdict --critic B --verdict WIN --round 1
```

Expect: `gauntlet` pass, next stage `tasks` (or `complete` in design-only). If both LOSE, `plan` is current again and `bar_sha256` is **unchanged**.

## 4. Tests before complete

After implement, the agent runs `make test` (and `make lint` when the change includes Python/UI) and records evidence:

```bash
uv run pcl-sdk loop evidence --command "make test" --exit-code 0 --summary "N passed"
```

Expect: `loop status` shows test evidence with a timestamp. Marking the run complete without this **fails**.

## 5. Refusals (must not ship a spec)

```bash
uv run pcl-sdk loop start --mode full --dir docs/VISION.md
uv run pcl-sdk loop start --mode full --dir docs/ROADMAP.md
```

Expect: exit 2, `refuse_reason=not_a_feature`, no implementation tasks against those files.

## 6. Roadmap advance (one epic per run)

```bash
uv run pcl-sdk loop start --mode full --roadmap
```

Expect: the next unfinished era epic (E2 if 005 is not `complete`, else E3, …). Not a run whose feature_dir is `docs/ROADMAP.md`.
