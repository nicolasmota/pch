# Gauntlet bar — Speckit plan pack `specs/006-dev-loop-automation/`

**Frozen:** 2026-08-26  
**Role:** this file is the critic’s only quality bar. Do not move the bar to match the draft. Do not grade the author’s intent or the conversation that produced the files.

**Artifact under test (the pack, not a summary):**

- `specs/006-dev-loop-automation/plan.md`
- `specs/006-dev-loop-automation/research.md`
- `specs/006-dev-loop-automation/data-model.md`
- `specs/006-dev-loop-automation/contracts/` (all files)
- `specs/006-dev-loop-automation/quickstart.md`

The critic MUST read those files as they are on disk. Ignore `spec.md` except to check the pack does not contradict it. Ignore this bar’s existence in the pack (the pack must stand alone for `/speckit-tasks`). Do not read agent transcripts, do not accept a builder’s recap, do not invent missing files.

This is not “make it longer.” The bar is **implementable and honest to the loop**: a later `/speckit-tasks` agent could generate tasks that produce a start instruction, a testable sequencer, and Gauntlet as a gate — not a checklist the person still drives by hand.

## Who the reader is

A coding agent about to run `/speckit-tasks` then `/speckit-implement` on this repo. They have the constitution, existing Speckit skills, and this pack. They will not reopen the Hub. They are allergic to “just remember to run specify then plan then implement” and to architecture novels that add a workflow engine, a new listener, or Hub pairing.

## Blind comparison (use when possible)

Imagine two tabs, labels stripped:

- **A** — this 006 plan pack
- **B** — `specs/004-context-engine/` plan pack (plan.md + research.md + data-model.md + contracts/ + quickstart.md) as the named, fetchable reference for “what a child spec plan looks like in this repo”

The critic must say which they would **hand to `/speckit-tasks`**. If they pick B because A is thinner, vaguer, or a field list without operations, **A loses**. Density should match 004: numbered research decisions with alternatives, tables in the data model, a wire contract an implementer can test, a quickstart that is the demo not a migration.

Also contrast, in one sentence each, against:

- “Document the loop in AGENTS.md and hope the agent follows it” (habit, not a gate)
- Speckit’s built-in `workflow.yml` (specify → human review → plan → human review → tasks → implement; no Gauntlet, no tests, no resume, mandatory pauses)
- A cloud automation that commits and pushes when green (violates FR-017 and local-first)

If a tasks agent cannot tell this plan apart from those three after the Summary + first research decisions, it **loses**.

## Pass / fail criteria (all must pass to WIN)

A tasks agent, after the **plan Summary plus research decisions** (not after hunting appendices):

1. **One trigger** — The pack names the start instruction and the program that computes the next stage. “The agent will just keep going” without a named command and a named sequencer **fails**.
2. **Sequencer is testable without a model** — Next-stage, refuse, resume, retry budget, and complete-requires-evidence are functions/CLI a pytest can call. If the only artifact is a skill that tells the model to remember the order, this criterion fails.
3. **Gauntlet freeze-before-draft** — `freeze_bar` is a real stage: the bar file must exist and its hash recorded **before** plan-pack files are written. A LOSE retry must be specified as rewriting artifacts, not the bar. Skipping Gauntlet is a defect, not a flag.
4. **Resume** — Pointing at an existing spec folder continues from the last completed stage. Specify is not redone unless redo is requested. Two runs on the same folder do not clobber; they resume or refuse.
5. **Refusals** — Implement against `docs/VISION.md` or `docs/ROADMAP.md` is refused. Reopening 001–003 as epics is refused. Empty start is refused. These are named operations with test locations.
6. **Constitution 1.0.0** — No new network listener, no Hub client pairing, no writes to canonical vault memory, `pcl-core` untouched (no I/O there), no auto-commit/push, no Personal Agency / Personal Intelligence product work. Gates map to concrete files.
7. **Success criteria → tests** — SC-001…SC-008 each map to a named test path. The plan states those tests are written first and must fail before the implementation that satisfies them.
8. **Design-only** — A start mode that stops after plan Gauntlet WIN, before tasks/implement, is a first-class operation, not a comment.
9. **Delivery is evidence** — `complete` is impossible without recorded fresh test/delivery results in the run record. Unmet spec items cannot be marked complete. Converge/close-gaps is named when implementation finishes thin.
10. **Out of scope held** — Does not replace Speckit commands; does not add a public server or cloud account; does not move a frozen bar to match a LOSE; Complexity Tracking is empty unless a real constitution exception is justified.
11. **Quickstart is the demo** — A stranger can: start one instruction → see stages advance → see a bar frozen before the plan pack → see tests recorded before “complete”. Not a “install Speckit” checklist.
12. **Shareable to tasks** — The pack is no longer than it needs to be and no shorter than 004’s standard. A document that requires a table of contents to reach the operations **fails**. A bullet list of JSON fields with no CLI operations **fails**.

## What “good” means here (inspectable)

Not: a new agent runtime, a workflow SaaS, or Hub features disguised as DX.

Yes: the smallest repo change that makes specify → Gauntlet → tasks → implement → tests one start, with gates the person cannot skip by forgetting.

## What the critic inspects

The five artifact paths listed above, as they actually are. Counts, quotes, named files, named operations. Never a changelog. Never a summary written by a builder.

## Verdict format (mandatory)

```text
VERDICT: WIN | LOSE
Would hand to speckit-tasks: yes | no
Blind vs 004 plan pack: A wins | B wins
Biggest gap: <one sentence>
Failing criteria: <ids>
Evidence: <quotes / file-level notes>
Do not rewrite the pack. Do not propose a new bar.
```
