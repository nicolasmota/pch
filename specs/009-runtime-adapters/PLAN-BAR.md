# Gauntlet bar — Speckit plan pack `specs/009-runtime-adapters/`

**Frozen:** 2026-08-26  
**Role:** this file is the critic’s only quality bar. Do not move the bar to match the draft. Do not grade the author’s intent or the conversation that produced the files.

**Artifact under test (the pack, not a summary):**

- `specs/009-runtime-adapters/plan.md`
- `specs/009-runtime-adapters/research.md`
- `specs/009-runtime-adapters/data-model.md`
- `specs/009-runtime-adapters/contracts/` (all files)
- `specs/009-runtime-adapters/quickstart.md`

The critic MUST read those files as they are on disk. Ignore `spec.md` except to check the pack does not contradict it. Ignore this bar’s existence in the pack. Do not read agent transcripts, do not accept a builder recap, do not invent missing files.

The bar is **implementable and honest to E5**: a later `/speckit-tasks` agent can generate tasks without inventing a new protocol, and two real-use runtimes consume the same situation package without the person re-editing the trip.

## Who the reader is

A coding agent about to run `/speckit-tasks` then `/speckit-implement`. They have constitution 1.0.0, 001–008 code, and this pack. They are allergic to a new A2A protocol, to “adapter per model,” and to counting the demo-agent as a real runtime.

## Blind comparison (use when possible)

- **A** — this 009 plan pack
- **B** — `specs/004-context-engine/` plan pack as the named reference for density

If they pick B because A is thinner, vaguer, or a catalog bullet list without Hub operations, **A loses**.

Also contrast, in one sentence each, against:

- Cursor-only pairing from 002 (one real client is not E5)
- In-repo demo-agent / generic test runtime (not “uso real”)
- A new agent-to-agent protocol (constitution forbids it)

If a tasks agent cannot tell this plan apart from those three after Summary + first research decisions, it **loses**.

## Pass / fail criteria (all must pass to WIN)

1. **E5 result** — At least two real-use runtimes (Cursor plus Hermes and/or OpenClaw; Hermes and OpenClaw both catalogued) consume the same trip situation package. A stranger can retell: *I switched assistant; the trip did not move.*
2. **Named targets** — Hermes and OpenClaw are first-class catalog pairing targets with person-visible recipes. Cursor stays. Demo-agent is a named **non-example**.
3. **Where it lives** — Recipes and catalog entries on the existing pairing surface. No new protocol object. No per-model adapter when the runtime already uses the existing connection.
4. **E1 seam** — Runtimes call the existing situation-package request. No second “get context for OpenClaw” tool. Package shape is unchanged (E2–E4 fields still present when set).
5. **Person-visible** — US3 names which Hub page (Connections), picker, copy recipe, refuse unknown assistant.
6. **Constitution 1.0.0** — Loopback only; recipes must not bind a public server; no pcl-core I/O; imported content cannot widen grants; no Personal Agency; 001–003 not reopened; no A2A.
7. **Isolation** — `forbidden_context` test named: a work-scoped newly listed runtime gets 0 personal trip titles/ids.
8. **Switch does not rewrite** — Revoke A, pair B: Hub objects unchanged; B’s package still names Europe Trip without re-entry.
9. **Success criteria → tests** — SC-001…SC-007 map to named test files. Tests written first and must fail before satisfying code.
10. **Out of scope held** — No new A2A protocol; no adapter-per-model; no treating demo-agent as real-use; Complexity Tracking empty unless a real exception.
11. **Quickstart is the switch** — Catalog shows Hermes + OpenClaw → copy recipe → pair two real-use assistants → both trip packages agree → revoke one → the other still sees the trip.
12. **Shareable to tasks** — Density matches 004: numbered research with alternatives, tables, recipe/catalog contract, demo quickstart. No TOC hunt. No “add two strings to a list” without operations, audit, and tests.

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
