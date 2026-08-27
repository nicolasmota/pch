# Gauntlet bar — Speckit plan pack `specs/011-simulated-hub-user/`

**Frozen:** 2026-08-27  
**Role:** this file is the critic’s only quality bar. Do not move the bar to match the draft. Do not grade the author’s intent or the conversation that produced the files.

**Artifact under test (the pack, not a summary):**

- `specs/011-simulated-hub-user/plan.md`
- `specs/011-simulated-hub-user/research.md`
- `specs/011-simulated-hub-user/data-model.md`
- `specs/011-simulated-hub-user/contracts/` (all files)
- `specs/011-simulated-hub-user/quickstart.md`

The critic MUST read those files as they are on disk. Ignore `spec.md` except to check the pack does not contradict it. Ignore this bar’s existence in the pack. Do not read agent transcripts, do not accept a builder recap, do not invent missing files.

The bar is **implementable and honest to the spec**: a later `/speckit-tasks` agent can generate tasks that produce a **watchable synthetic person** (scripted ticks, growing corpus, live timeline) — not a silent seeder, not Personal Agency, not a second Context Engine.

## Who the reader is

A coding agent about to run `/speckit-tasks` then `/speckit-implement`. They have constitution 1.0.0, Hub 001–010 code, and this pack. They are allergic to: an autonomous agent that acts in the world; writing the owner’s everyday vault by default; a timeline that only exists as log files after the run; a plan that says “plug into Cursor” without naming the optional path vs the required path.

## Blind comparison (use when possible)

- **A** — this 011 plan pack
- **B** — `specs/006-dev-loop-automation/` plan pack as the named reference for a harness that is repo tooling, not a Hub-owned agent

If they pick B because A is thinner, vaguer, or a persona story without operations (start/pause/timeline/isolated space), **A loses**. Density should match 004/006: numbered research with alternatives, tables in the data model, a contract an implementer can test, a quickstart that *is* the demo.

Also contrast, in one sentence each, against:

- A vault seeder with no live timeline (silent feed; the owner cannot watch iterations)
- Personal Agency (the Hub grows a robot that plans and acts for the person)
- E6 context-eval harness (four scored cases; not a growing lived corpus the owner watches)

If a tasks agent cannot tell this plan apart from those three after Summary + first research decisions, it **loses**.

## Pass / fail criteria (all must pass to WIN)

1. **Watchable loop** — Start bundled persona → ticks appear on a live timeline (role, action, result) while the run is in progress. A post-hoc log dump as the only UI **fails**.
2. **Corpus then consult** — The bundled scenario both **writes** (projects, preferences, memories, …) and **queries** (search + situation ask) against what it wrote. Seeding without later asks **fails**. Situation asks that hit a different space than the writes **fail**.
3. **Not Personal Agency** — No outbound mail, no external calendar create, no public server, no improvising life plans. v1 steps are scripted and inspectable. “The model will just act like a user” without a scenario file **fails**.
4. **Roles** — Owner-role writes are canonical; assistant-role durable memories are proposals until synthetic-owner accept (or left in review). Timeline labels the role. Unlabeled mixed writes **fail**.
5. **Isolated space default** — Everyday vault (`~/.pch`) is not the default target. Opt-in requires an explicit confirmed warning. Coding agent is not a Hub client.
6. **Optional paired-assistant path** — Named as optional. P1 run works with it off. When on, query/proposal ticks go through a locally paired assistant (including the coding-tool path the owner already uses). Required-Cursor as the only way to see ticks **fails**.
7. **Constitution 1.0.0** — Loopback only; `pcl-core` stays free of I/O; imported/sim content is data never instruction; 001–003 not reopened; no foundation model shipped; no Hub-owned agent runtime for real users; provenance marks sim writes.
8. **Does not replace E6** — This pack must not redefine the four scored eval cases or the seven metrics. It may reuse Hub operations those cases already call.
9. **Success criteria → tests** — SC-001…SC-008 map to named test files. Tests written first and must fail before satisfying code. SC-004 (everyday vault unchanged) and SC-008 (no outbound/public) are deterministic automated tests.
10. **Person-visible inspect** — Opening a completed tick shows input and Hub result without restarting the persona. Write ticks link to the affected Hub object. Quickstart is this demo, not a migration.
11. **Volume is specified** — Bundled persona is sized to the spec’s floor (≥40 durable objects, ≥4 kinds including project/preference/memory, ≥10 query ticks). “A few sample memories” **fails**.
12. **Shareable to tasks** — Density matches 004/006. Named modules/CLI/UI surfaces, run/tick records, isolated-space operation. No TOC hunt. A bullet list of JSON fields with no start/pause/timeline operations **fails**.

## What “good” means here (inspectable)

Not: a chatbot living in the Hub; a load test with no story; a Cursor plugin that is the product.

Yes: the smallest change that lets the owner **watch a scripted human-like user fill the Hub and then ask it questions**, on an isolated space, with every tick visible.

## What the critic inspects

The five artifact paths listed above, as they actually are. Counts, quotes, named files, named operations. Never a changelog. Never a summary written by a builder.

## Verdict format (mandatory)

```text
VERDICT: WIN | LOSE
Would hand to speckit-tasks: yes | no
Blind vs 006 plan pack: A wins | B wins
Biggest gap: <one sentence>
Failing criteria: <ids>
Evidence: <quotes / file-level notes>
Do not rewrite the pack. Do not propose a new bar.
```
