# Feature Specification: Simulated Hub User

**Feature Branch**: `011-simulated-hub-user`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Queria criar um robot que se comporte como se fosse um usuario humano da minha ferramenta e que ele fosse gerando memorias, contextos, etc, alimentando a base dele e fazendo consultas etc... queria conseguir visualizar essas iterações e resultados. Isso pode acontecer plugado no Cursor se for necessario. Minha intenção e conseguir ver como a ferramenta se comporta com mais dados por tras."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Watch a Synthetic Person Fill and Query the Hub (Priority: P1)

The Hub owner wants to see how the product behaves once it is no longer empty. They start a bundled synthetic person (a named life situation, not a blank vault) and watch that person use the Hub the way a human owner would: create projects and goals, record preferences and memories, then search and ask for the current situation. Each step appears on a live timeline with what was done and what came back. They can pause, resume, or stop without losing the objects already written.

This is a local observation harness. It is not a personal agent that plans trips, sends mail, or acts in the world.

**Why this priority**: Without a growing corpus and a visible loop of write-then-ask, the owner cannot judge ranking, assembly, and “enough context” against a realistic pile of data. The timeline is the product of this feature; a silent seeder would not answer the request.

**Independent Test**: Start the bundled persona on an isolated Hub space. Confirm objects accumulate across several kinds, searches and situation requests run against that space, and every step is listed with its result. Confirm the owner’s everyday Hub space is untouched.

**Acceptance Scenarios**:

1. **Given** the Hub is running locally and no synthetic run is active, **When** the owner starts the bundled persona, **Then** a chronological timeline begins and the first steps appear without a cloud account or a second product to install.
2. **Given** a run in progress, **When** the synthetic person records a project, a preference, and a memory, **Then** those objects exist in the isolated space and the timeline shows each write and its outcome.
3. **Given** those objects exist, **When** the synthetic person searches and asks for the current situation of the active project, **Then** the timeline shows the question and a result that cites objects from that persona (not an empty miss caused by writing to a different space).
4. **Given** a run in progress, **When** the owner pauses or stops it, **Then** already-written objects remain inspectable, no half-applied step is left as canonical, and the timeline marks where it stopped.
5. **Given** a default start, **When** the run finishes or is stopped, **Then** the owner’s everyday personal space is unchanged.

---

### User Story 2 - Follow Each Iteration as Owner vs Assistant (Priority: P2)

A human uses the Hub in two ways: as the owner (canonical writes, reviews, corrections) and with a connected assistant (search, situation package, proposed memories). The synthetic person can play both roles in the same run so the owner sees the difference on the timeline: owner writes become canonical; assistant writes stay proposals until the synthetic owner accepts them (simulating a human clicking approve). Results of assistant asks are shown as what that assistant was allowed to see, including withheld categories when a grant is narrower than the whole space.

**Why this priority**: The owner asked to see behavior with more data *and* how consultation works. Mixing roles without labeling them would hide whether the Hub treated a step as a person or as an agent. This story is independent of Cursor: it uses the Hub’s existing owner and assistant surfaces.

**Independent Test**: Run a scenario that includes owner writes, an assistant situation ask, an assistant memory proposal, and a synthetic-owner accept. Confirm the timeline labels the role, the proposal is not canonical before accept, and the post-accept situation result reflects the accepted memory.

**Acceptance Scenarios**:

1. **Given** a run with both roles, **When** the timeline is viewed, **Then** each step is labeled as owner or assistant.
2. **Given** an assistant proposes a durable memory, **When** the synthetic owner has not yet accepted, **Then** that memory is not treated as live canonical fact in the next situation ask.
3. **Given** the synthetic owner accepts that proposal, **When** the next situation ask for the same project runs, **Then** the accepted fact can appear, and the timeline shows both the accept and the later result.
4. **Given** an assistant granted only one project, **When** it asks about another project’s private items, **Then** those items are absent from the result, withheld categories are named without revealing content, and the denial is visible on the timeline.

---

### User Story 3 - Inspect, Replay, and Optionally Use the Real Assistant Path (Priority: P3)

After or during a run, the owner opens any step and sees the input (what the synthetic person tried to do) and the output (what the Hub returned) without re-running the whole persona. They can jump from a step to the affected objects in the Hub they already use (memories, projects, search, review). If they want the same loop through the assistant connection they already use from their coding tool, they can opt into that path so queries and proposals go through a real paired assistant rather than only the built-in owner surface.

**Why this priority**: Visualization after the fact is how they debug “why did it retrieve that?” The coding-tool path is optional; the P1 timeline must work without it.

**Independent Test**: After at least five completed steps, open one write and one query from the timeline and confirm input and output are both shown. With the optional assistant path off, the run still completes. With it on, at least one query step is visibly served through a paired assistant and still appears on the same timeline.

**Acceptance Scenarios**:

1. **Given** a run with completed steps, **When** the owner opens one write step and one query step, **Then** they see that step’s input and result without restarting the persona.
2. **Given** a write step that created or changed an object, **When** the owner follows the link from the timeline, **Then** they land on that object in the Hub.
3. **Given** the optional real-assistant path is off, **When** the bundled persona runs, **Then** feed and query still complete and the timeline is still populated.
4. **Given** the optional path is on and an assistant is already paired locally, **When** a query step runs, **Then** the timeline records that it used the paired assistant, and the result still respects that assistant’s grant.

---

### Edge Cases

- The synthetic person is not Personal Agency: it MUST NOT send mail, create external calendar events, export the vault to the network, or take high-stakes external actions.
- It is not Personal Intelligence: it MUST NOT infer new life patterns across the person and treat those inferences as canonical.
- Default runs MUST use an isolated space. Writing into the owner’s everyday vault is opt-in and MUST be an explicit, confirmed choice with a plain-language warning.
- A coding agent working on this repository is not a Hub client. Pairing the optional assistant path is a separate local connection.
- Empty or missing persona definition: the run MUST refuse to start with a named reason rather than inventing objects.
- Hub not running or isolated space locked: the timeline shows a failed step with a recoverable error; it MUST NOT silently skip writes.
- Pause during an in-flight step: that step either completes and is logged, or is not applied; no orphan canonical object without a timeline entry.
- Duplicate start: a second run against the same isolated space MUST NOT interleave unlabeled with the first; either it is refused or it is a named new run.
- Context quality evaluation (the separate scored harness with fixed cases) remains that other feature. This simulation populates and observes; it does not replace those scores.
- Closed Hub chapters are not reopened; the synthetic person uses objects and surfaces that already exist.
- Imported-looking content produced by the simulation remains data, never instructions to the Hub.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The owner MUST be able to start, pause, resume, and stop a named synthetic-person run locally, without a cloud account.
- **FR-002**: A bundled persona MUST ship with the feature so the owner can start without writing a scenario. That persona MUST produce a mix of projects, goals, preferences, and memories over simulated time, then issue searches and situation asks against what it wrote.
- **FR-003**: Every completed step MUST appear on a chronological timeline with: order, simulated time, role (owner or assistant), action summary, and result summary (success, empty, denied, or error).
- **FR-004**: Owner-role steps MUST create or update canonical Hub objects the same way a human owner would (including provenance that they came from this simulation).
- **FR-005**: Assistant-role durable memories MUST be proposed, not written as canonical. Canonicalization MUST wait for synthetic-owner accept (or the owner’s real review if they choose to review by hand).
- **FR-006**: Query steps MUST include at least search and a situation ask for the persona’s active project, and MUST record what was returned and what was withheld by grant.
- **FR-007**: The default target MUST be an isolated Hub space. The everyday vault MUST NOT be used unless the owner explicitly opts in and confirms a warning.
- **FR-008**: The owner MUST be able to open any completed step and see its input and its Hub result without re-running the persona.
- **FR-009**: The owner MUST be able to follow a successful write step to the affected object in the Hub they already use.
- **FR-010**: The timeline MUST update while the run is in progress so the owner can watch iterations live, not only after the run ends.
- **FR-011**: An optional path MUST allow query and proposal steps to go through a locally paired assistant (including the coding-tool assistant the owner already uses) when the owner turns that path on. The P1 run MUST work with that path off.
- **FR-012**: The simulation MUST NOT act outside the Hub (no outbound mail, no external event creation, no public hosting).
- **FR-013**: The simulation MUST NOT ship or require a foundation model of its own. Persona content is scripted and inspectable. Optional generative wording is out of v1.
- **FR-014**: Stopping or failing a run MUST leave the timeline and the isolated space consistent: applied steps are listed; unapplied steps are not canonical.
- **FR-015**: Each run MUST be identifiable (name or id) so two runs are not silently merged on the timeline.

### Key Entities

- **Persona**: a named synthetic life situation (who this simulated person is, which projects are active, what they care about). Bundled and inspectable.
- **Scenario**: the ordered list of steps the persona will take over simulated time (writes, reviews, searches, situation asks).
- **Step (iteration)**: one human-like action: role, action type, payload summary, result summary, simulated time, status (pending, applied, failed, skipped).
- **Timeline**: the owner-visible chronological log of steps for one run.
- **Run**: one execution of a scenario against one isolated space (or an explicitly opted-in everyday vault). Has start, pause, resume, stop.
- **Role**: owner (canonical) or assistant (grant-scoped ask / propose).
- **Isolated space**: a Hub data location used for simulation so the everyday vault stays untouched by default.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: From a cold start, the owner can begin the bundled persona and see the first timeline step within 2 minutes, with no cloud account.
- **SC-002**: One complete bundled-persona run produces at least 40 durable objects spanning at least four kinds (including project, preference, and memory), and at least 10 query steps (search or situation ask).
- **SC-003**: 100% of completed steps appear on the timeline with role, action, and result; 0% of canonical writes in that run lack a corresponding timeline entry.
- **SC-004**: In 100% of default runs, the everyday vault’s object count is unchanged.
- **SC-005**: After the corpus exists, at least 90% of the persona’s situation asks for the active project return a package that names that project and cites at least one object the persona wrote (not a generic empty miss).
- **SC-006**: The owner can open any of the last 20 completed steps and see that step’s input and output in under 10 seconds without restarting the run.
- **SC-007**: When the optional paired-assistant path is off, 100% of bundled-persona runs still complete feed and query. When it is on with a local pair, 100% of those query steps are labeled as using the paired assistant.
- **SC-008**: 0 synthetic-person runs send mail, create external calendar events, or make the Hub reachable from outside the owner's machine.

## Assumptions

- This is an **observation harness for the Hub owner**, not a roadmap epic that replaces Context Engine, temporal validity, or context-quality evaluation. It uses objects and asks those chapters already defined.
- The bundled persona is a dense “lived stretch” around a travel-planning life (compatible with the existing trip demo) plus everyday notes, so volume and mixed kinds are the point — not a single golden fixture.
- v1 steps are **scripted and deterministic**. The robot follows the scenario; it does not improvise a life plan. That keeps the feature on the safe side of Personal Agency and makes runs comparable.
- Simulated-owner auto-accept of the persona’s own proposals is on by default so the corpus actually grows; the owner can switch the run to leave proposals in the review queue instead.
- Visualization lives in the Hub the owner already opens locally (a timeline they can watch). A local start/stop control is enough; a separate analytics product is out of scope.
- Cursor (or any coding-tool assistant) is an **optional** paired-assistant path, not a requirement to see the timeline.
- Isolated space is a throwaway Hub space the owner can discard. Opt-in to the everyday vault is a later, warned action, not the first-run default.
- Provenance for simulated writes MUST mark them as coming from this harness so the owner can tell demo data from their own.
- Out of scope: Personal Agency; Personal Intelligence; replacing the scored evaluation harness; public benchmark; a Hub-owned foundation model; a Hub-owned agent that acts for real users; silent use of the everyday vault; reopening chapters 001–003.
