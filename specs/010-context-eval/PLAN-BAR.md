# Gauntlet bar — Speckit plan pack `specs/010-context-eval/`

**Frozen:** 2026-08-26  
**Role:** this file is the critic’s only quality bar. Do not move the bar to match the draft. Do not grade the author’s intent or the conversation that produced the files.

**Artifact under test (the pack, not a summary):**

- `specs/010-context-eval/plan.md`
- `specs/010-context-eval/research.md`
- `specs/010-context-eval/data-model.md`
- `specs/010-context-eval/contracts/` (all files)
- `specs/010-context-eval/quickstart.md`

The critic MUST read those files as they are on disk. Ignore `spec.md` except to check the pack does not contradict it. Ignore this bar’s existence in the pack. Do not read agent transcripts, do not accept a builder recap, do not invent missing files.

The bar is **implementable and honest to E6**: a later `/speckit-tasks` agent can generate tasks without inventing a public benchmark, and four fixed cases score the existing situation package.

## Who the reader is

A coding agent about to run `/speckit-tasks` then `/speckit-implement`. They have constitution 1.0.0, 001–009 code, and this pack. They are allergic to a public leaderboard, to token-optimization as a product, and to “just run make test” without named metrics.

## Blind comparison (use when possible)

- **A** — this 010 plan pack
- **B** — `specs/004-context-engine/` plan pack as the named reference for density

If they pick B because A is thinner, vaguer, or a metric name list without Hub operations, **A loses**.

Also contrast, in one sentence each, against:

- `make test` as the only quality story (unnamed metrics)
- A public context-quality benchmark / leaderboard
- Token-count optimization as the scored goal

If a tasks agent cannot tell this plan apart from those three after Summary + first research decisions, it **loses**.

## Pass / fail criteria (all must pass to WIN)

1. **E6 result** — Four named cases (killer demo, temporal conflict, isolation, runtime switch) plus seven named metrics. A stranger can retell: *I can see if the trip package is right, fresh, isolated, and portable.*
2. **Scores the contract** — Metrics read the existing situation package (and timed assembly). No new package format; no model self-grade.
3. **Where it lives** — Local harness in pcl-sdk CLI; ephemeral vault by default; stdout/file the person chose. Not a hosted bench. Not inside pcl-core I/O.
4. **Four cases mapped** — Each case names fixture + assertion. Killer demo uses Europe Trip purpose. Isolation uses a work-scoped grant. Switch uses two connections + revoke.
5. **Person-visible** — Quickstart says how to run the harness and read the report. No Hub UI required if CLI is the surface; then say so.
6. **Constitution 1.0.0** — Loopback; no public server; imported content is data; no Personal Agency/Intelligence; 001–003 not reopened; coding agent not Hub client (`~/.pch` not the default target).
7. **Isolation is a scored case** — `forbidden_context`-compatible: 0 personal titles/ids in the work package; precision metric fails otherwise.
8. **No public benchmark / no token product** — Out of scope held in research and Complexity Tracking empty unless a real exception.
9. **Success criteria → tests** — SC-001…SC-007 map to named test files. Tests written first and must fail before satisfying code.
10. **Does not reopen E1–E5** — Harness calls existing Hub methods (`get_context_contract`, pairing, grants, as_of, trip seed). No second assembly engine.
11. **Quickstart is the scorecard** — Run harness → four cases → seven metrics on a local report. Killer demo cost < 2 s.
12. **Shareable to tasks** — Density matches 004: numbered research with alternatives, tables, report contract, demo quickstart. No TOC hunt. No metric list without operations.

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
