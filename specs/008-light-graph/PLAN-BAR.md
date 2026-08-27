# Gauntlet bar — Speckit plan pack `specs/008-light-graph/`

**Frozen:** 2026-08-26  
**Role:** this file is the critic’s only quality bar. Do not move the bar to match the draft. Do not grade the author’s intent or the conversation that produced the files.

**Artifact under test (the pack, not a summary):**

- `specs/008-light-graph/plan.md`
- `specs/008-light-graph/research.md`
- `specs/008-light-graph/data-model.md`
- `specs/008-light-graph/contracts/` (all files)
- `specs/008-light-graph/quickstart.md`

The critic MUST read those files as they are on disk. Ignore `spec.md` except to check the pack does not contradict it. Ignore this bar’s existence in the pack. Do not read agent transcripts, do not accept a builder recap, do not invent missing files.

The bar is **implementable and honest to E4**: a later `/speckit-tasks` agent can generate tasks without inventing product, and typed relations survive contact with the existing Hub without a graph database or auto-promoting foreign keys.

## Who the reader is

A coding agent about to run `/speckit-tasks` then `/speckit-implement`. They have constitution 1.0.0, 001–007 code, and this pack. They are allergic to Neo4j, to walking the whole vault, and to “goal.project_id is already owned_by.”

## Blind comparison (use when possible)

- **A** — this 008 plan pack
- **B** — `specs/004-context-engine/` plan pack as the named reference for density

If they pick B because A is thinner, vaguer, or a type list without Hub operations, **A loses**.

Also contrast, in one sentence each, against:

- Goal/Memory `project_id` (membership FK, not `owned_by`)
- Project `stakeholders` (a string list, not `related_to`)
- E3 `operational_phase` (where the work stands, not how objects hang together)

If a tasks agent cannot tell this plan apart from those three after Summary + first research decisions, it **loses**.

## Pass / fail criteria (all must pass to WIN)

1. **E4 result** — Package includes typed relations from the situation anchor (and one hop). A stranger can retell: *the trip depends on the visa; the visa is blocked by a person.*
2. **Four types stay four types** — `owned_by`, `depends_on`, `blocked_by`, `related_to`. FKs and stakeholders are named **non-examples**. They are not auto-promoted.
3. **Where it lives** — Relations are explicit vault objects (from, to, type), not a graph database and not a SharedState key.
4. **E1 seam** — Assembly copies visible relations onto the existing context contract. No second MCP read tool. Depth is anchor + one hop, not a full walk.
5. **Person-visible** — US3 names which Hub page and which fields/actions. Creating is owner-canonical; agents propose, they do not silent-write.
6. **Constitution 1.0.0** — No new listener, no pcl-core I/O, loopback, imported content cannot create relations, no Personal Agency, 001–003 not reopened, no A2A/social graph.
7. **Isolation** — `forbidden_context` test named: work-scoped package gets 0 personal relation types/endpoints/titles/ids; omissions leak no titles/ids.
8. **Missing is empty, not invented** — No relations: E1/E3 still assemble; no inference from email/memories/phase.
9. **Success criteria → tests** — SC-001…SC-007 map to named test files. Tests written first and must fail before satisfying code.
10. **Out of scope held** — No graph DB; no A2A; no social graph; no auto-FK promotion; Complexity Tracking empty unless a real exception.
11. **Quickstart is the trip** — Record trip `depends_on` visa and visa `blocked_by` a person → two agents’ packages agree → Hub shows the links → removing a link drops it from the next package.
12. **Shareable to tasks** — Density matches 004: numbered research with alternatives, tables, wire contract, demo quickstart. No TOC hunt. No type list without operations.

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
