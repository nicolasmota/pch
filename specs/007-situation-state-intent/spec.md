# Feature Specification: Situation State and Intent

**Feature Branch**: `007-situation-state-intent`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "E3 — Estado de Projeto e Intent de Situação (docs/ROADMAP.md). SharedState is a TTL handoff. ActionIntent is approval. The Hub still lacks project phases (Planning, Comparing itineraries, Waiting for approval, Choosing hotel) and an answer to 'what is the person trying to do now?'. Result: the situation package includes current phase, current step, short intent, and operational state. In scope: operational state of Project/Goal; situation intent; person-visible; keep durable memory separate. Out of scope: renaming SharedState or ActionIntent; autonomous planner. Depends on E1."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The Package Names Where the Work Stands (Priority: P1)

A person is planning a trip. The Hub already stores the project, goals, and (from E1) can assemble a situation package. What it cannot yet say is the **operational phase**: they are comparing itineraries, not still kicking off planning, not yet choosing a hotel. When an authorized agent asks for context with purpose "continue planning the trip," the package includes that phase (and the current step, if one is set) so the agent does not restart the project or skip ahead. A second authorized agent with the same grant receives the same phase.

**Why this priority**: This is the E3 result. E1 packages goals and memories; without operational state, agents treat every request as a cold start. SharedState already exists and must not be reused — it is a short-lived handoff, not "Planning vs Comparing itineraries."

**Independent Test**: Seed a project with a goal; set operational phase to "comparing itineraries"; request a situation package for "continue planning the trip"; verify the package states that phase (and does not present SharedState TTL as the phase); request the same purpose from a second authorized agent and verify agreement.

**Acceptance Scenarios**:

1. **Given** a project whose operational phase is "comparing itineraries," **When** an authorized agent requests a situation package whose purpose continues that project, **Then** the package includes that phase as operational state, not as a durable memory and not as SharedState.
2. **Given** two authorized agents with the same grant, **When** each requests that package after the phase is set, **Then** both packages agree on the phase.
3. **Given** SharedState exists for a handoff, **When** the package is assembled, **Then** SharedState remains a TTL handoff field if present and is not labeled as the project's operational phase.

---

### User Story 2 - The Package Names What They Are Trying to Do Now (Priority: P2)

The person is trying to choose the next itinerary. That **situation intent** is short-lived operational framing ("choose next itinerary"), not an approval to send email (ActionIntent) and not a life goal ("visit Europe"). The situation package includes that short intent when one is set. When they change it ("now pick a hotel"), later packages use the new intent; the old one is not presented as current.

**Why this priority**: Phase without intent still leaves the agent guessing the next move. It is P2 because US1 already stops cold-start; intent is the finer "now."

**Independent Test**: Set situation intent "choose next itinerary"; request a package; verify the short intent is present and ActionIntent approvals are not used as that intent; change the intent; verify the next package shows the new one.

**Acceptance Scenarios**:

1. **Given** a current situation intent "choose next itinerary" on the project, **When** a package is assembled for a matching purpose, **Then** the package includes that short intent.
2. **Given** an ActionIntent (external-action approval) also exists, **When** the package is assembled, **Then** situation intent and ActionIntent remain distinct; approval objects are not presented as "what the person is trying to do now."
3. **Given** the person replaces the situation intent, **When** a later package is assembled, **Then** only the current intent is presented as live.

---

### User Story 3 - The Person Can See and Correct Phase and Intent (Priority: P3)

The person opens the Hub on the project (or goal) and sees current phase, current step, and situation intent. They can set or correct them. The next situation package uses the correction. Agents may propose a phase or intent; they do not silently write it as canonical.

**Why this priority**: Explicit control. Without a person-visible surface, operational state is invisible inference.

**Independent Test**: Set phase and intent; open the Hub project/goal surface; verify they are shown; correct the phase; verify the next package uses the correction; submit an agent proposal and verify it does not become canonical until the person confirms.

**Acceptance Scenarios**:

1. **Given** phase, step, and intent are set, **When** the person views the project in the Hub, **Then** those fields are visible and labeled as operational (not as memories).
2. **Given** the person corrects the phase, **When** any later package is assembled, **Then** assembly uses the corrected phase.
3. **Given** an agent proposes a new intent, **When** the person has not confirmed, **Then** the live intent is unchanged.

---

### Edge Cases

- Missing phase: the package still assembles (E1 behavior); operational state is omitted or marked unknown — it is not invented from email or memories.
- Missing situation intent: same; do not substitute a Goal title or ActionIntent.
- SharedState TTL expiry does not clear operational phase.
- Imported content that looks like "we are now choosing hotels" is data, never an instruction that changes phase/intent.
- Grant isolation: a work-scoped agent does not receive a personal project's phase or intent; omission notes leak no titles/ids.
- Closed chapters 001–003 are not reopened; this is a child spec on E1's contract.
- Personal Agency (autonomous planner that advances phase by itself) is out of scope.
- Vocabulary: do not rename SharedState or ActionIntent.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A Project (and a Goal when the situation is goal-scoped) MUST be able to carry operational phase, optional current step, and optional situation intent, distinct from durable memories and from SharedState / ActionIntent.
- **FR-002**: Situation packages MUST include current phase, step (if set), and situation intent (if set) when the assembled situation is that project/goal.
- **FR-003**: SharedState MUST remain a TTL handoff and MUST NOT be reused as operational phase.
- **FR-004**: ActionIntent MUST remain external-action approval and MUST NOT be reused as situation intent.
- **FR-005**: The person MUST be able to view and set/correct phase, step, and intent in the Hub; agent writes are proposals until confirmed.
- **FR-006**: A change of current intent or phase MUST appear in subsequent packages; the previous current intent is not presented as live.
- **FR-007**: Missing phase or intent MUST NOT be inferred from imported content or filled by an autonomous planner.
- **FR-008**: Grant and omission rules from E1 still apply to operational state.
- **FR-009**: E2 current-vs-historical filtering still applies to preferences/memories in the same package; operational state is "now," not a historical truth interval.

### Key Entities

- **Operational Phase**: named stage of a project/goal (e.g. Planning, Comparing itineraries). Not SharedState.
- **Current Step**: optional finer grain inside a phase (e.g. "rank two remaining itineraries").
- **Situation Intent**: short description of what the person is trying to do now. Not ActionIntent, not a Goal.
- **Context Contract**: E1 package; this feature adds operational fields to it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After phase is set to "comparing itineraries," 100% of later packages for that trip purpose include that phase; 0% treat SharedState TTL as the phase.
- **SC-002**: After situation intent is set, 100% of matching packages include it; 0% use an ActionIntent as that intent.
- **SC-003**: After the person corrects phase or intent, 100% of subsequent packages reflect the correction.
- **SC-004**: Isolation test: 0 operational-state fields from a personal project appear in a work-scoped package.
- **SC-005**: With no phase/intent set, 100% of packages still assemble (E1); 0 packages invent a phase from mail or memories.
- **SC-006**: A second authorized agent with the same grant agrees on phase and intent in 100% of paired trials.
- **SC-007**: Operational state is available offline; package time stays within the existing E1 budget the person already accepts.

## Assumptions

- Depends on E1 (Context Engine). E2 temporal filter remains for preferences/memories.
- Phase vocabulary can start as a small controlled set plus an "other" free-text step; exact enum is a plan decision.
- Situation intent is a short string, not a planner task graph.
- Horizon items (Personal Intelligence, Personal Agency) stay out of scope.
- 006 (dev loop) is tooling; this spec is the product epic E3.
