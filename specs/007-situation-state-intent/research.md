# Research: Situation State and Intent

**Feature**: `specs/007-situation-state-intent/` · **Date**: 2026-08-26

No NEEDS CLARIFICATION markers remained in the Technical Context; the decisions below resolve the open design choices against the existing codebase (mapped 2026-08-26: `Project`/`Goal` in `pcl_core/schema/project.py`, `SituationRef` in `pcl_core/schema/contract.py`, assembly in `pcl_core/retrieval/contract.py` ~191–207, `Hub.patch` in `service.py`, MCP in `pcl_server/mcp/tools_context.py`, bridge in `pcl_sdk/mcp_bridge.py`, Projects + Review Queue UI).

## D1 — Fields on Project and Goal, not SharedState, not ActionIntent

**Decision**: Add `operational_phase`, `current_step`, `situation_intent` to `Project` and `Goal`. Canonical write is owner `Hub.patch` via existing `PATCH /v1/projects/{id}` and `PATCH /v1/goals/{id}`. Do **not** store phase in SharedState. The E1 seed SharedState key `trip.phase` stays a TTL handoff and is a **named non-example**: tests may still see `{ "key": "trip.phase", … }` in `state[]`; that is not `situation.operational_phase`. ProjectStatus remains `active|paused|done|archived` on `situation.status`. ActionIntent remains the external-action approval object (`request_approval` / `propose_action`); situation intent is a string field, not an ActionIntent.

**Rationale**: Spec FR-003/FR-004. SharedState expires; operational phase must not vanish when TTL fires. Reusing ActionIntent would mix “may I send this email” with “choose next itinerary.”

**Alternatives considered**: (a) SharedState `trip.phase` — rejected: already used in E1 tests as handoff; TTL would clear “comparing itineraries.” (b) New vault type Situation — rejected: extra object; situation is the E1 frame, not a store. (c) Memory kind — rejected: durable memory ≠ operational now. (d) Reuse ActionIntent — rejected: that object is approval to act externally, not situation intent. (e) Encode phase as ProjectStatus — rejected: `active|paused|done|archived` is object lifecycle, not “comparing itineraries.”

## D2 — SituationRef carries operational fields; `state[]` stays SharedState

**Decision**: Extend `SituationRef` with `operational_phase`, `current_step`, `situation_intent` (all optional; JSON `null` when unset). Assembly in `packages/pcl-core/src/pcl_core/retrieval/contract.py` copies from the selected Project when building `SituationRef` (today ~lines 191–207). If `subject_ref` is a Goal and that Goal has step/intent set, those overlay; phase falls back to the Project when the Goal phase is unset. Empty fields are omitted (`null`), never inferred from memories, artifacts, or email.

**Rationale**: FR-002, FR-007. Agents already read `situation`. Putting phase into `state[]` would mix TTL handoffs with operational now. No second MCP read tool (E1 seam).

**Alternatives considered**: (a) New top-level `operational` object on the contract — rejected: extra shape; SituationRef is the situation. (b) New MCP tool `get_operational_state` — rejected: E1 seam is one contract; a second read would fork clients. (c) Infer phase from recent memories — rejected: constitution + SC-005; missing is omitted, not invented.

## D3 — Phase vocabulary

**Decision**: `OperationalPhase` enum: `planning`, `comparing_itineraries`, `waiting_for_approval`, `choosing_hotel`, `other`. `current_step` and `situation_intent` are free-text (max 200 chars). `other` + step covers unnamed phases. Unknown enum on PATCH → 422.

**Rationale**: Roadmap examples become testable enums; free-text step avoids a second enum explosion. SC-001 needs a stable “comparing itineraries” value (`comparing_itineraries`).

**Alternatives considered**: (a) Free-text phase only — rejected: SC-001 needs a stable comparable value. (b) Large workflow engine / auto-advance — rejected: Personal Agency / planner; out of scope. (c) Nested state machine per project type — rejected: overkill for five named phases.

## D4 — Owner PATCH is canonical; agents propose

**Decision**: Owner `PATCH /v1/projects/{id}` and `PATCH /v1/goals/{id}` (existing routers in `packages/pcl-server/src/pcl_server/rest/routers/projects.py`) accept the three fields because `Hub.patch` is already generic. MCP `propose_operational_state` writes an `OperationalProposal` (`type=operational_proposal`) pending on Review Queue; accept applies `Hub.patch` on the target; reject leaves live fields unchanged. Agents cannot `Hub.patch` projects (owner-only REST unchanged). Do not fake this as `propose_memory`.

**Rationale**: FR-005. Reuse Review Queue, not a new Hub product. A fake Memory would pollute memory lineage and US3 (“not as memories”).

**Alternatives considered**: (a) Agents PATCH via MCP — rejected: silent canonical write. (b) `propose_memory` with a fake Memory — rejected: pollutes memory lineage; Review Queue title is “Memory review” today and must grow a second row type, not a fake statement. (c) New Hub page for operational review — rejected: one queue; add a type discriminator.

## D5 — Isolation and imports

**Decision**: Grant filter already applied to the Project before `SituationRef` is built. Out-of-scope project → `situation` is the in-scope project or `null`; **zero** personal `operational_phase` / `current_step` / `situation_intent` in a work-scoped package. Omission notes keep existing E1 shape: category + count + label, never the withheld project title or id. Imported artifacts / plugin sync never call `Hub.patch` or `propose_operational_state` for these fields.

**Rationale**: FR-007, FR-008, constitution V and isolation demo. Phase/intent on a leaked SituationRef would be a new side channel even if memories are withheld.

**Alternatives considered**: (a) Redact fields but keep project title on SituationRef — rejected: title leak is already forbidden; fields must not be a second leak. (b) Infer “safe” phase from in-scope memories when the project is withheld — rejected: SC-005 + import-is-data. (c) Separate isolation MCP tool — rejected: same `get_context_contract` path.

## D6 — Tests fail first; trip.phase remains a handoff

**Decision**: Named SC map in plan.md. NEW files: `test_operational_contract.py` (SC-001, SC-002, SC-003, SC-005), `forbidden_context/test_operational_isolation.py` (SC-004), `contract/test_operational_mcp.py` (SC-006). EDIT `test_contract_perf.py` for SC-007 (same `< 2 s` assertion, trip project has operational fields set, still `hub.get_context_contract`, no egress). Trip seed may still set SharedState `trip.phase`; tests assert `situation.operational_phase` is **not** derived from that key (handoff remains in `state[]` only).

**Rationale**: Constitution “tests fail first.” SC-007 is the E1 budget, not a new assembly pipeline — extending the existing perf file makes that enforceable.

**Alternatives considered**: (a) One catch-all `test_e3.py` — rejected: SC map would still invent files at tasks time. (b) New perf harness / second assembly entry — rejected: SC-007 says stay on E1 path. (c) Treat seed `trip.phase` as the operational phase in tests — rejected: that is the bug E3 exists to stop.

## D7 — Performance: copy in memory, no extra I/O

**Decision**: After E1 has already loaded the selected Project (and Goal if `subject_ref` is a goal), copy three optional fields in memory. No extra FTS pass, no extra `store.list`, no plugin sync, no network. SC-007 verified by extending `packages/pcl-core/tests/test_contract_perf.py`.

**Rationale**: Spec SC-007: operational state available offline; package time stays within the E1 budget.

**Alternatives considered**: (a) Separate vault query for operational fields — rejected: they live on the Project/Goal already loaded. (b) Cache/index of “current phase” — rejected as premature; same as E1 D8.
