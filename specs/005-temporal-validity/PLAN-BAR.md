# Gauntlet bar — Speckit plan pack `specs/005-temporal-validity/`

**Frozen:** 2026-08-26  
**Role:** this file is the critic’s only quality bar. Do not move the bar to match the draft. Do not grade the author’s intent or the conversation that produced the files.

**Artifact under test (the pack, not a summary):**

- `specs/005-temporal-validity/plan.md`
- `specs/005-temporal-validity/research.md`
- `specs/005-temporal-validity/data-model.md`
- `specs/005-temporal-validity/contracts/` (all files)
- `specs/005-temporal-validity/quickstart.md`

The critic MUST read those files as they are on disk. Ignore `spec.md` except to check the pack does not contradict it. Ignore this bar’s existence in the pack (the pack must stand alone for `/speckit-tasks`). Do not read agent transcripts, do not accept a builder’s recap, do not invent missing files.

This is not “make it longer” or “more complete.” Completeness already lost on vision docs. The bar is **implementable and honest to E2**: a later `/speckit-tasks` agent could generate tasks without inventing product, and the E2 result would survive contact with the existing Hub.

## Who the reader is

A coding agent about to run `/speckit-tasks` then `/speckit-implement` on this repo. They have the constitution, 001–004 code, and this pack. They will not re-litigate the vision. They are allergic to “add some timestamps” plans and to architecture novels that reopen the Hub.

## Blind comparison (use when possible)

Imagine two tabs, labels stripped:

- **A** — this 005 plan pack
- **B** — `specs/004-context-engine/` plan pack (plan.md + research.md + data-model.md + contracts/ + quickstart.md) as the named, fetchable reference for “what a child spec plan looks like in this repo”

The critic must say which they would **hand to `/speckit-tasks`**. If they pick B because A is thinner, vaguer, or a field list without operations, **A loses**. Density should match 004: numbered research decisions with alternatives, tables in the data model, a wire contract an implementer can test, a quickstart that is the demo not a migration.

Also contrast, in one sentence each, against:

- “Add `valid_from` / `valid_until` columns and filter live versions” (schema-only sketch; does not keep two truths)
- E1 object-version overwrite (correction of the live object; history is versions, not successive truths)
- SharedState TTL (handoff expiry, not when a preference was true of the person)

If a tasks agent cannot tell this plan apart from those three after the Summary + first research decisions, it **loses**.

## Pass / fail criteria (all must pass to WIN)

A tasks agent, after the **plan Summary plus research decisions** (not after hunting appendices):

1. **E2 result** — Can retell without looking at the roadmap: *both statements remain; the engine returns the current one.* The pack names change-of-mind as an operation, not as “edit the same row.”
2. **Four clocks** — Validity interval, retention, object `version`, and SharedState TTL are four different things. None is reused as another. `ActionIntent` is not situation intent and is not validity.
3. **001 key collision** — Preference “unique per key” vs two successive truths is a named research decision with alternatives. The chosen invariant is testable (at most one *current* preference per key; many historical with the same key).
4. **Change of mind ≠ mistake** — Two operations. Change of mind keeps the earlier statement as historical truth. Mistake (“never true”) is not presented as historical truth. If every PATCH is treated as a new historical truth, this criterion fails.
5. **E1 seam** — Assembly in the existing context-contract path filters to current-at-evaluation-time. Overlapping *current* statements still surface as conflicts (no silent winner, no semantic merge). Optional evaluation time rides the existing context request; no second MCP tool, no vector DB, no new listener.
6. **Constitution 1.0.0** — Gates map to concrete files/behaviors using the ratified constitution (not the 004 leftover “unratified template”). History must not disappear. Imported content cannot open or close validity. `pcl-core` stays free of I/O. Loopback only. Personal Intelligence / Personal Agency are not in scope. Closed chapters 001–003 are not reopened as epics.
7. **Isolation** — Historical personal statements cannot appear in a work-scoped package. A `forbidden_context` test is named. Omission notes still leak no withheld titles/ids.
8. **Person-visible** — US3 has a concrete Hub surface (which page, which fields, which actions). “They can look at audit extra” is not enough unless that extra actually shows current vs historical intervals on the source statements.
9. **Success criteria → tests** — SC-001…SC-007 each map to a named test location and marker. The plan states tests are written first and must fail before the implementation that satisfies them.
10. **Out of scope held** — No automatic forgetting, no semantic merge, no graph database, no E3 operational State/Intent primitives, no rename of `SharedState` / `ActionIntent`. Complexity Tracking is empty unless a real constitution exception is justified.
11. **Quickstart is the reversal** — A stranger can run: record dislike → record like → two agents get the current like → Hub still shows the old dislike as historical. Not a column-migration checklist.
12. **Shareable to tasks** — The pack is no longer than it needs to be and no shorter than 004’s standard. A document that requires a table of contents to reach the operations **fails**. A bullet list of Pydantic fields with no Hub operations **fails**.

## What “good” means here (inspectable)

Not: more primitives, a new policy engine, or a temporal database.

Yes: the smallest Hub change that makes “what is true now” a first-class fact the Context Engine already knows how to assemble.

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
