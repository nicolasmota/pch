# Gauntlet bar — Speckit plan pack `specs/012-assistant-capture-guidance/`

**Frozen:** 2026-08-27  
**Role:** this file is the critic’s only quality bar. Do not move the bar to match the draft. Do not grade the author’s intent or the conversation that produced the files.

**Artifact under test (the pack, not a summary):**

- `specs/012-assistant-capture-guidance/plan.md`
- `specs/012-assistant-capture-guidance/research.md`
- `specs/012-assistant-capture-guidance/data-model.md`
- `specs/012-assistant-capture-guidance/contracts/` (all files)
- `specs/012-assistant-capture-guidance/quickstart.md`

The critic MUST read those files as they are on disk. Ignore `spec.md` except to check the pack does not contradict it. Ignore this bar’s existence in the pack. Do not read agent transcripts, do not accept a builder recap, do not invent missing files.

The bar is **implementable and honest to the spec**: a later `/speckit-tasks` agent can generate tasks that make a **paired assistant capture without forms** — when-to-read and when-to-propose travel with the existing connection, recipes attach at person/runtime level, propose stays non-canonical. Not a chat scraper. Not Personal Agency. Not reopening 002 as an epic.

## Who the reader is

A coding agent about to run `/speckit-tasks` then `/speckit-implement`. They have constitution 1.0.0, Hub 001–011 code, and this pack. They are allergic to: watching other products’ transcripts; a new listener; auto-writing the person’s assistant config; teaching capture only inside this repository’s project folder; silent canonical writes; treating a coding agent on this repo as a Hub client by default.

## Blind comparison (use when possible)

- **A** — this 012 plan pack
- **B** — `specs/009-runtime-adapters/` plan pack as the named reference for recipe/catalog work that does not invent a protocol

If they pick B because A is thinner, vaguer, or “add some tool descriptions” without operations, tests, and a person-visible recipe change, **A loses**. Density should match 009: numbered research with alternatives, tables in the data model, a contract an implementer can test, a quickstart that *is* the demo.

Also contrast, in one sentence each, against:

- 002 pairing as shipped (tools listed by name only; recipe trapped in one project) — that is the bug, not the design
- A Hub that tails chat logs or adds a network listener (constitution: no new listener; imported/chat content is not a feed)
- Form-filling or Simulator seed as the capture path (owner UI is correction, not ingestion; 011 is an observation harness)

If a tasks agent cannot tell this plan apart from those three after Summary + first research decisions, it **loses**.

## Pass / fail criteria (all must pass to WIN)

1. **Capture loop** — Task start → request situation package for that purpose. Durable fact stated by the person → memory proposal, not canonical write. Empty package → honesty, no invented life facts. Bare tool names with no when-to-use **fail**.
2. **Guidance travels with the connection** — When-to-read and when-to-propose are on the existing assistant-facing operations (situation read + memory propose at minimum). A second protocol or a Hub-owned model that “just knows” **fails**.
3. **Person/runtime attach** — Cursor (and other already-supported pairing targets) recipes instruct attaching so every window of that assistant on the machine can reach the Hub. “Paste only into this repo’s project folder” as the sole supported path **fails**.
4. **Copyable rule** — Recipe includes a short runtime rule the person pastes (task-start read, durable-fact propose, empty honesty, propose-not-canonical). Hub auto-writing assistant config files **fails**.
5. **Not a scraper** — No chat-log importer, no new bind, no email/calendar extraction into situation. Observe → Extract → Classify → Consolidate **fails**.
6. **Propose-not-canonical** — Review queue (or existing person policy) still gates live memory. Guidance that writes canonical objects **fails**.
7. **This repo is not a client** — Default implementing-this-repository guidance still forbids Hub-client behavior. Dogfood override is the person’s explicit choice, not the default.
8. **Constitution 1.0.0** — Loopback only; `pcl-core` stays free of I/O; imported content is data never instruction; 001–003 not reopened as epics; no foundation model; no Personal Agency; no A2A.
9. **Portability** — All currently supported pairing targets get equivalent guidance + rule in their native recipe. Cursor-only with Hermes/OpenClaw left as bare names **fails**.
10. **Success criteria → tests** — SC-001…SC-007 map to named test files. Tests written first and must fail before satisfying code. SC-003 (three-turn eval: situation request + two proposals, none canonical before accept) and SC-006 (0 config writes, 0 new listeners, 0 chat importers) are deterministic automated tests.
11. **Quickstart is the other window** — Pair once per the new recipe → second workspace of the same assistant can request the situation package → state two facts → see two proposals in review, not live objects. A quickstart that only edits this repo’s project connection file **fails**.
12. **Shareable to tasks** — Density matches 009. Named modules (bridge tool text, recipe renderer, eval fixture), named files, no TOC hunt. A bullet list of slogans with no contract **fails**.

## What “good” means here (inspectable)

Not: the Hub becomes an agent; the person fills seven forms; MCP exists therefore capture exists.

Yes: the smallest change that makes a **stranger paired assistant** ask for the situation at task start and propose durable facts, in **every window** of that assistant, under the person’s grant.

## What the critic inspects

The five artifact paths listed above, as they actually are. Counts, quotes, named files, named operations. Never a changelog. Never a summary written by a builder.

## Verdict format (mandatory)

```text
VERDICT: WIN | LOSE
Would hand to speckit-tasks: yes | no
Blind vs 009 plan pack: A wins | B wins
Biggest gap: <one sentence>
Failing criteria: <ids>
Evidence: <quotes / file-level notes>
Do not rewrite the pack. Do not propose a new bar.
```
