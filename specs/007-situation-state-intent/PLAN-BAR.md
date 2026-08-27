# Gauntlet bar — Speckit plan pack `specs/007-situation-state-intent/`

**Frozen:** 2026-08-26  
**Role:** this file is the critic’s only quality bar. Do not move the bar to match the draft. Do not grade the author’s intent or the conversation that produced the files.

**Artifact under test (the pack, not a summary):**

- `specs/007-situation-state-intent/plan.md`
- `specs/007-situation-state-intent/research.md`
- `specs/007-situation-state-intent/data-model.md`
- `specs/007-situation-state-intent/contracts/` (all files)
- `specs/007-situation-state-intent/quickstart.md`

The critic MUST read those files as they are on disk. Ignore `spec.md` except to check the pack does not contradict it. Ignore this bar’s existence in the pack. Do not read agent transcripts, do not accept a builder recap, do not invent missing files.

The bar is **implementable and honest to E3**: a later `/speckit-tasks` agent can generate tasks without inventing product, and operational phase/intent survive contact with the existing Hub without renaming SharedState or ActionIntent.

## Who the reader is

A coding agent about to run `/speckit-tasks` then `/speckit-implement`. They have constitution 1.0.0, 001–005 code, and this pack. They are allergic to “stash the phase in SharedState `trip.phase`” and to a planner that advances the project by itself.

## Blind comparison (use when possible)

- **A** — this 007 plan pack
- **B** — `specs/004-context-engine/` plan pack as the named reference for density

If they pick B because A is thinner, vaguer, or a field list without Hub operations, **A loses**.

Also contrast, in one sentence each, against:

- SharedState key `trip.phase` (already in E1 tests; TTL handoff, not operational phase)
- ProjectStatus `active|paused|done|archived` (lifecycle of the project object, not “comparing itineraries”)
- ActionIntent (approval to act externally, not “choose next itinerary”)

If a tasks agent cannot tell this plan apart from those three after Summary + first research decisions, it **loses**.

## Pass / fail criteria (all must pass to WIN)

1. **E3 result** — Package includes current phase, optional step, and short situation intent. A stranger can retell: *the agent sees where the work stands and what they are trying to do now.*
2. **Three names stay three names** — SharedState, ActionIntent, and ProjectStatus are not reused as operational phase or situation intent. The pack names the existing `trip.phase` SharedState seed as a **non-example**.
3. **Where it lives** — Phase/step/intent are fields on Project (and Goal when goal-scoped), not a new vault type and not a SharedState key.
4. **E1 seam** — Assembly copies those fields onto the existing situation object in `get_context_contract`. No second MCP tool. The `state` array remains SharedState items.
5. **Person-visible** — US3 names which Hub page and which fields/actions. Patching is owner-canonical; agents propose, they do not silent-write.
6. **Constitution 1.0.0** — No new listener, no pcl-core I/O, loopback, imported content cannot set phase, no Personal Agency planner, 001–003 not reopened.
7. **Isolation** — `forbidden_context` test named: work-scoped package gets 0 personal project phase/intent; omissions leak no titles/ids.
8. **Missing is omitted, not invented** — Empty phase/intent: E1 still assembles; no inference from email/memories.
9. **Success criteria → tests** — SC-001…SC-007 map to named test files. Tests written first and must fail before satisfying code.
10. **Out of scope held** — No rename of SharedState/ActionIntent; no autonomous phase advancement; no E4 graph; Complexity Tracking empty unless a real exception.
11. **Quickstart is the trip** — Set phase comparing itineraries + intent choose next itinerary → two agents’ packages agree → Hub Projects page shows it → SharedState `trip.phase` is still a handoff, not the phase field.
12. **Shareable to tasks** — Density matches 004: numbered research with alternatives, tables, wire contract, demo quickstart. No TOC hunt. No field list without operations.

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
