# Personal Context — Roadmap

**Status:** live · **Updated:** 2026-08-26  
Thesis and community demo: [`docs/VISION.md`](VISION.md).  
This is **not** a Speckit spec. One epic at a time becomes a local pack `specs/<nnn>-<name>/` (gitignored — not published) via `/speckit-specify` → plan → tasks → implement.

User and developer documentation: [`docs/README.md`](README.md).

---

## Principles

1. **Context belongs to the person.** No runtime owns it.
2. **Memory ≠ context.** Storing everything is not understanding the situation.
3. **Context is temporal.** Facts, preferences, and states change; history does not disappear.
4. **Provenance matters.** Without a source, it is not canonical.
5. **Context quality > context volume.** More context is not better context.
6. **Least privilege.** The agent receives what the task needs, not the whole vault.
7. **Explicit control.** The person's correction beats agent inference.
8. **Model-agnostic.** MCP first; runtime adapters after.
9. **Local-first.** Read, edit, and search work offline. Encrypted vault, loopback.
10. **Imported content is data, never instruction.** Email, calendar, and plugins do not expand grants or trigger action.
11. **Cross-cutting properties.** Identity, privacy, provenance, and policy accompany every layer.

Do not build: a foundation model of our own; a vector DB as the product; our own agent runtime; a personal agent that plans and acts alone; universal ingest of “everything the person has ever done”; a mandatory graph database; a new A2A protocol. Horizon items stay refused until this document is revised.

---

## Vocabulary (collisions)

In the Hub today, two names are **not** the Layer primitives:

| Layer term | What the Hub already has | Do not confuse |
|------------|--------------------------|----------------|
| **State** (operational condition: *Planning*, *Comparing itineraries*) | `SharedState` = TTL handoff | Do not rename SharedState. Operational State entered with E3. |
| **Intent** (what the person is trying to do now) | `ActionIntent` = approval for an external action | Do not rename ActionIntent. Situation intent entered with E3. |
| **Skill** (reusable capability) | `MemoryKind.procedural` | A Skill object is horizon; the engine must prove the need first. |

Three layers the product often mixes:

```text
Memory     — persisted information.  "I said I wanted to visit Amsterdam."
Context    — the relevant slice now. User is planning a 10-day Europe trip; Amsterdam is a candidate; budget-sensitive.
Situation  — operational frame.      Project: Europe Trip; Goal: plan 10-day trip; State: comparing itineraries; Intent: choose next itinerary.
```

> **Memory is persisted information. Context is the relevant information for a situation. Situation is the operational frame in which an agent is acting now.**

Conceptual primitives of the Layer (not all need to be persisted entities on day one; some start derived by the engine): Identity, Memory, State, Goals, Preferences, Relationships, Projects, Skills, Intent, Provenance.

---

## What 001–003 delivered

Closed chapters. Do not reopen as an epic. Evolve only via a child spec.

**001 — Personal Context Hub.** Encrypted vault, schema, UI, pairing, grants, memory proposals, approvals, append-only audit, search, project brief, PCA export/import, MCP (`search_personal_context`, `get_context_manifest`, `propose_memory`, shared state, actions).

Current primitives: Person, Profile, Preference, Project, Goal, Commitment, Decision, Memory, Artifact, SharedState, plus provenance as metadata (authority, source_refs, citations, audit) — not a separate entity type.

**002 — Connectors.** A real assistant (Cursor) via MCP recipe; calendar (`private`); selective Gmail (`sensitive`); assistant claims only by proposal; the Hub does not extract on its own.

**003 — Plugins and marketplace.** Kernel separated from isolated guests. Plugins: Calendar, Gmail, RSS. Kit: `pcl-sdk plugin` (sideload and catalog).

### What they still are not

The Hub stores, filters, searches, proposes, and presents briefs/manifests. It now also assembles a situation package (`get_context_contract`). The remaining era work is proving that package against the vision demo and evaluation harness — not inventing a second engine.

Also still in the era queue as spawned specs: temporal validity, operational situation fields, typed graph, extra runtime adapters, systematic quality evaluation.

---

## Mechanism (once)

The Context Engine exists to answer, before the agent acts:

1. What does this agent need to know?
2. What is relevant to the current situation?
3. What is still true?
4. What is historical?
5. What is inferred?
6. What is authoritative?
7. What can this agent access?
8. What should remain hidden?
9. What changed since the last interaction?
10. What context should be carried forward?

Goal: **the smallest sufficient context for the situation.** Source ≠ Truth: a source can be wrong, stale, incomplete, or only an inference. Provenance, confidence, authority, and freshness enter the slice. Each source operates inside a grant — having a connector does not put the data in every contract.

**Context Contract** — the unit the agent receives. It does not need to know where the data lives.

```text
Context Contract
  Subject / Situation / Intent
  Required context (goals, preferences, decisions, project state, …)
  Granted scope     (personal, travel, project:123, …)
  Omitted           (other projects, private work, …)
  Provenance / Freshness / Confidence
```

**Context Quality** — maximize Relevant + Current + Authorized + Sufficient. Future metrics: was the right context retrieved? did irrelevant items leak? was it fresh? were conflicts resolved? did the agent have enough? how much context was needed to improve the task?

**Context Debt** — future concept, not MVP. Like technical debt: stale items, conflicting preferences, abandoned projects, inferences never confirmed, data without provenance, duplication, unclear authority. “Context Health” (freshness, provenance, conflicts, stale, unverified) only makes sense at scale.

**Isolation (second demo).** Portability without indiscriminate sharing: a Personal Agent sees personal scope; a Work Agent does not receive personal context it does not need. The thesis is not “one dump for every agent.”

---

## Next era — E1–E6

Ordered queue. One epic at a time becomes a spec. Each child spec must be testable on its own. The next era proves the killer demo in [`VISION.md`](VISION.md).

```text
001 Hub → 002 Connectors → 003 Plugins
        → E1 Context Engine
        → E2 Temporal → E3 Situation/State/Intent → E4 Graph → E5 Adapters → E6 Evaluation
        → (horizon) Personal Intelligence → Personal Agency
```

### E1 — Context Engine

**Spec:** `specs/004-context-engine/`

**Problem.** The agent needs to know what to fetch. The Hub returned hits and briefs, but did not yet produce a complete situation package.

**Outcome.** A request with intent + needed slice → Context Contract containing: goal; preferences; relevant memories; constraints; available state; citations/provenance; granted scope; information deliberately omitted. The “continue planning the trip” demo must work using objects that already exist in 001.

**In scope.** Context Query; context read; relevance ranking; context assembly; grant slicing; Context Contract.

**Out of scope.** Automatic inference from email; vector DB; Personal Intelligence; Personal Agency.

**Depends on.** 001–003.

### E2 — Temporal validity

**Spec:** `specs/005-temporal-validity/`

**Problem.** Preferences and facts change. Versioning and retention exist, but “what holds now” vs “what was true” was not clearly represented.

**Outcome.** `"I didn't like X."` → `"I now like X."` Both remain; the engine returns the live one.

**In scope.** `valid_from`; `valid_until`; current vs historical resolution; temporal filter on E1.

**Out of scope.** Sophisticated semantic merge; automatic forgetting without policy.

**Depends on.** E1.

### E3 — Project state and situation intent

**Spec:** `specs/007-situation-state-intent/`

**Problem.** `SharedState` is a TTL handoff. `ActionIntent` is an approval. Missing: phases (`Planning`, `Comparing itineraries`, `Waiting for approval`, `Choosing hotel`) and “what is the person trying to do now?”

**Outcome.** The Context Contract includes current phase, current step, short intent, and operational state.

**In scope.** Operational state on Project/Goal; situation intent; visibility for the person; separation from durable memory.

**Out of scope.** Renaming SharedState; renaming ActionIntent; autonomous planner.

**Depends on.** E1.

### E4 — Light graph

**Spec:** `specs/008-light-graph/`

**Problem.** Relationships were mostly FKs. No typed relations (`owned_by`, `depends_on`, `blocked_by`, `related_to`).

**Outcome.** The Context Engine includes useful relations in the Context Contract (e.g. Project A → depends_on → Project B → blocked_by → Person C).

**In scope.** Typed relations; query from an anchor object; respect grants.

**Out of scope.** Graph database; A2A; social graph.

**Depends on.** E1.

### E5 — Runtime adapters

**Spec:** `specs/009-runtime-adapters/`

**Problem.** The thesis is portability. The real client was Cursor, plus demo-agent and a second test runtime.

**Outcome.** At least two real-use runtimes consume the same Context Contract. Candidates: Hermes, OpenClaw. The user switches runtime without re-editing context.

**In scope.** Per-runtime recipes; pairing; catalog; existing MCP contract; validation of the killer demo.

**Out of scope.** Per-model adapters when the runtime already speaks MCP; a new protocol.

**Depends on.** E1.

### E6 — Context quality evaluation

**Spec:** `specs/010-context-eval/`

**Problem.** We did not yet measure whether the slice is correct, fresh, precise, or cheap.

**Outcome.** A small case set: killer demo; temporal conflict; context isolation; runtime switch. Metrics: context retrieval accuracy; context precision; freshness; conflict resolution; portability; user correction rate; context assembly cost.

**In scope.** Harness; fixed cases; observable criteria.

**Out of scope.** Public benchmark; token optimization as a product.

**Depends on.** E1; stronger with E2 and E5.

---

## Horizon

Named. They do not enter the queue until promoted into the next era.

| Theme | Why wait |
|------|-----------------|
| Skills as a primitive | Procedural memory already exists; a Skill object only after the engine proves a need for discovery/slicing. |
| Observe → Extract → Classify → Consolidate loop | The Hub decided assistants propose; internal extraction is a different product. |
| Personal Intelligence | Needs stable, trustworthy context. *Without reliable context, intelligence predicts from noise.* |
| Personal Agency | Needs assembled context, policy, and authorization. |
| A2A / Context Agent | MCP covers the next era. |
| Context Debt / Context Health | Only makes sense with enough context at scale. |
| Anticipatory AI | Only after Personal Intelligence demonstrates real value. |

The next era ends when the system delivers: **the right context, to the right agent, for the right situation, at the right time — under the user's control.**

---

## The ladder (horizon, not the product)

```text
Memory → Personal Context → Context Engine → Personal Intelligence → Personal Agency
```

Cross every layer: Identity, Privacy, Provenance, Policy, User Ownership, Interoperability.

**Memory** — *AI remembers what happened.* Store, update, retrieve, forget.  
**Personal Context** — *AI understands what matters about the person.* Memory answers “what happened?”; Context answers **“what matters for this situation?”**  
**Context Engine** — *AI assembles the right context for the situation.* That is the next era.  
**Personal Intelligence** — *AI understands patterns across the person's context.* Patterns, conflicts, likely needs, next steps. Only after a trustworthy engine. This is not more retrieval: it is reasoning about the representation of the person.  
**Personal Agency** — *AI plans and acts continuously on behalf of the person.* Context → Understand → Predict → Plan → Act, with feedback into context. Any external action remains subordinate to identity, grants, policy, approval, and audit. **Not part of the next era.**

---

## How to use these files

- **Agent implementing a feature:** if there is no spec in `specs/`, do not invent an epic from the vision. Point at the epic in this roadmap and ask for `/speckit-specify`.
- **Agent unsure about product:** thesis and contrasts in [`VISION.md`](VISION.md) beat vector DB, autonomous agent, action marketplace.
- **Person who owns the repo:** only one epic in the queue becomes the active spec. Done → mark Spec → move to the next.
- **Speckit constitution:** copy the principles when the constitution is filled in; do not turn this roadmap into a spec.

## Speckit (when an epic is ready)

1. `/speckit-specify` with the epic's slice, **not** the vision document.
2. Fill the epic's **Spec** field with the path (`specs/<nnn>-…`).
3. Follow `plan → tasks → implement` only on that child spec.

The origin of the thesis is the draft `personal-context-layer-spec.md`. The Hub (specs 001–003) is already the product form of that thesis, local-first.

## Changelog

- **2026-08-26** — E6 spawned as `specs/010-context-eval/` via speckit-loop `--roadmap` after E5 delivery.
- **2026-08-26** — E5 spawned as `specs/009-runtime-adapters/` via speckit-loop `--roadmap` after E4 delivery.
- **2026-08-26** — E4 spawned as `specs/008-light-graph/` via speckit-loop `--roadmap` after E3 delivery.
- **2026-08-26** — E3 spawned as `specs/007-situation-state-intent/` via speckit-loop `--roadmap` after 006 sequencer shipped.
- **2026-08-26** — Gauntlet round 2 — VISION.md is only the shareable spine; this file holds operations.
- **2026-08-26** — Gauntlet round 1 — shareable spine; architecture after the fold.
- **2026-08-26** — First roadmap: thesis, 001–003 as past, E1–E6 as next era, explicit horizon.
- **2026-08-26** — Conceptual evolution: Product Evolution, Context Problem, Situation, Context Contract, Context Quality, Context Isolation, Personal Intelligence and Personal Agency as explicit vision layers.
- **2026-08-26** — E2 spawned as `specs/005-temporal-validity/` via speckit-specify.
