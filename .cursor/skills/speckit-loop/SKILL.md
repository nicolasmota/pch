---
name: speckit-loop
description: >-
  Runs the full Speckit plus Gauntlet development loop from one start
  (specify, freeze bar, plan, critics, tasks, analyze, implement, tests,
  delivery). Use when the user says /speckit-loop, wants to automate specify
  through delivery, advance the roadmap, or avoid driving each Speckit stage
  by hand.
---

# Speckit Loop

The person issues **one** start. You do not ask “shall I run plan next?” after a pass. You stop only on `blocked_on_person`, refuse, or exhausted budget.

## Start

From repo root, exactly one source:

```bash
uv run pch-lab loop start --mode full --desc "…"
uv run pch-lab loop start --mode full --epic E3
uv run pch-lab loop start --mode full --dir specs/005-temporal-validity --resume
uv run pch-lab loop start --mode full --roadmap
uv run pch-lab loop start --mode design-only --dir specs/… --resume
```

Then repeat until `loop status` shows `complete`, `failed`, `stopped`, or `blocked_on_person`:

1. `uv run pch-lab loop next`
2. Execute the named skill/stage (table below)
3. `uv run pch-lab loop record --stage <id> --outcome pass|fail|blocked_on_person`

Never implement `docs/VISION.md` or `docs/ROADMAP.md` (local, gitignored). Never reopen 001–003 as epics. Never skip Gauntlet. Never commit unless the person asked.

## Stages

| `next.skill` / stage | What you do |
|----------------------|-------------|
| `speckit-specify` | Follow `.cursor/skills/speckit-specify/SKILL.md` |
| `speckit-clarify` | Follow speckit-clarify; pause if the person must choose |
| `gauntlet-bar` | Write `PLAN-BAR.md` (or `SPEC-BAR.md`) **before** pack files. Then `loop record --stage freeze_bar --outcome pass` |
| `speckit-plan` | Follow speckit-plan. Do not edit the frozen bar |
| `gauntlet-critics` | See **Critics** below |
| `speckit-tasks` | Follow speckit-tasks |
| `speckit-analyze` | Follow speckit-analyze |
| `speckit-implement` | Follow speckit-implement; tests fail before satisfying code |
| `make-test` | Run `make test` and `make lint` as appropriate; `uv run pch-lab loop evidence --command "make test" --exit-code N --summary "…"` then record `test` |
| `delivery-validate` | Map each SC to executed checks; constitution gates; `red_before_green`. Record `delivery` with outcomes. Do not report complete without evidence |
| `speckit-converge` | Follow speckit-converge if unmet items remain |

## Critics

Dispatch **two** independent subagents with **fresh** context. They read **only** the frozen bar file and the pack files on disk. Give them **no** builder recap.

Each must return:

```text
VERDICT: WIN | LOSE
…
```

Then:

```bash
uv run pch-lab loop record-verdict --critic A --verdict WIN|LOSE --round N [--failing 1,2]
uv run pch-lab loop record-verdict --critic B --verdict WIN|LOSE --round N [--failing 1,2]
```

If the sequencer returns the run to `plan`, revise the **pack**, not the bar, and continue. Two critics in disagreement is not WIN.

## Status

`uv run pch-lab loop status` — show this instead of asking the person what ran.

`uv run pch-lab loop stop` — person asked to stop.

`--roadmap` starts the next unfinished era epic (E1–E6). It does not treat the roadmap file as a feature to implement. After one epic `complete`, if the person asked to advance until the era is done, `loop start --roadmap` again.

## Constitution

Loopback only. Not a Hub client. No vault writes. `pch-core` stays free of I/O from this skill.
