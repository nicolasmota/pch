# Feature Specification: Context Engine

**Feature Branch**: `004-context-engine`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "E1 — Context Engine (docs/ROADMAP.md). The Hub stores, filters, searches, proposes, and presents briefs/manifests, but does not yet answer: what does this agent need to know about this person, for this task, right now? A request with intent plus the necessary scope must return a Context Contract: goal, preferences, relevant memories, constraints, available state, citations/provenance, granted scope, and deliberately omitted information. The 'continue planning the trip' demo must work using objects that already exist from 001."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Continue the Trip in a Second Agent (Priority: P1)

A person plans a ten-day trip for two in one authorized agent, comparing Amsterdam and London. They open a different authorized agent — different product, different runtime — and say only "continue planning the trip." That agent asks the Hub for context with a stated purpose, and receives a single situation package: the live goal, the travelers, the candidate destinations, the budget constraint, the decisions already made, and citations for each item — without having to guess what to search for. When the person drops London, every agent that later requests context for this situation sees Amsterdam as the live candidate; London appears only as a rejected decision, not a live option.

**Why this priority**: This is the killer demo from the vision and the reason E1 exists. Everything the Hub already ships (vault, grants, search, briefs) is only proven portable when a stranger agent can pick up a live situation from a purpose statement alone. E2–E6 all depend on this assembly step existing.

**Independent Test**: Can be fully tested with objects that already exist from 001 — seed a Project with a Goal, Preferences, Decisions, and Memories about the trip; pair two agents with the same granted scope; ask each for context with the purpose "continue planning the trip"; verify both receive the same package; record a correction ("dropped London") and verify subsequent packages reflect it.

**Acceptance Scenarios**:

1. **Given** a vault containing a trip Project with a Goal, Preferences, Decisions, and Memories created through existing Hub flows, **When** an authorized agent requests context with a purpose describing the trip-planning task, **Then** it receives one package containing the goal, relevant preferences, relevant memories, constraints, available shared state, and a citation to the source object for every item.
2. **Given** two different agents authorized with the same scope, **When** each requests context with the same purpose, **Then** both receive packages with the same substantive content, and neither had to issue its own searches to assemble it.
3. **Given** a package was previously issued, **When** the person records a correction (a decision rejecting London), **Then** any package issued afterward for that purpose presents Amsterdam as the live candidate and includes the rejection as a decision with its citation.
4. **Given** an agent requests context with a purpose that matches no project or goal in the granted scope, **When** the package is assembled, **Then** the agent receives an explicitly empty-but-valid package (identity-level context only, or nothing) rather than an error or an unscoped dump of the vault.

---

### User Story 2 - The Package Respects the Grant and Says What It Withheld (Priority: P2)

A person has both personal context (the trip, family, health) and work context (projects, commitments) in the vault. Their Work Agent holds a grant scoped to work only. When the Work Agent requests context — even with a purpose that brushes against personal life ("schedule around my travel") — the package contains only work-scoped items, and it explicitly states that information was withheld and under which category, without revealing the withheld content itself. The person can trust that pairing an agent never means handing over the whole vault.

**Why this priority**: Portability without indiscriminate sharing is the thesis's second demo. A context engine that leaks across grants is worse than no engine, because it centralizes the person's representation and then spills it. Omission disclosure is what lets an agent behave honestly about incomplete knowledge instead of hallucinating around gaps.

**Independent Test**: Seed personal and work objects in one vault; issue two grants (personal scope, work scope); request context with the same purpose from each; verify zero cross-scope items in each package and verify each package names its omitted categories.

**Acceptance Scenarios**:

1. **Given** a vault with personal and work objects and an agent granted work scope only, **When** that agent requests context for any purpose, **Then** the package contains zero items from outside the granted scope.
2. **Given** items relevant to the purpose exist outside the granted scope, **When** the package is assembled, **Then** the package includes an explicit omission note naming the withheld category (e.g., "personal travel context withheld") without exposing the withheld items' content.
3. **Given** an agent whose grant was revoked, **When** it requests context, **Then** no package is issued and the refusal is auditable.

---

### User Story 3 - The Person Can See What Was Assembled and Delivered (Priority: P3)

The person opens the Hub UI and reviews what context packages were issued: which agent asked, for what purpose, which items were included, what was omitted, and when. Nothing about assembly is invisible. If a package included something the person considers wrong or stale, they can trace each item back to its source object and correct it through existing Hub flows, and the correction wins over anything previously assembled.

**Why this priority**: Explicit control is a core principle — the person's correction beats the engine's selection. Without visibility, the engine becomes a black box deciding what agents learn about the person, which contradicts ownership. It is P3 because the engine can prove assembly and isolation without it, but the feature is not honest to the vision until the person can inspect it.

**Independent Test**: Issue several packages to different agents; open the Hub's audit/review surface; verify each issuance is listed with agent, purpose, included item references, and omission notes; correct a source object and verify the next package reflects the correction.

**Acceptance Scenarios**:

1. **Given** packages have been issued, **When** the person reviews the Hub, **Then** each issuance shows the requesting agent, the stated purpose, the included item references, the omission notes, and the timestamp.
2. **Given** the person corrects a source object (edits a preference, rejects an inferred memory), **When** any later package is assembled, **Then** the corrected version is used and the superseded version is not presented as live.

---

### Edge Cases

- Purpose is vague or overly broad ("help me"): the engine must still bound the package to the granted scope and rank for relevance rather than returning everything; an over-broad result is a quality failure, not a crash.
- Two live objects conflict (a preference says "no red-eye flights", a memory says the person booked one): the package includes both with provenance so the agent can see the conflict; the engine does not silently pick a winner (temporal resolution is E2).
- The purpose matches several projects: the package must either select the best match with its rationale visible in audit, or present candidate situations, never merge unrelated projects into one package.
- Requested purpose is in scope, but every relevant item is stale or unverified: items still appear, each carrying its provenance and freshness so the agent can weigh them.
- Very large situation (hundreds of memories): the package respects a size discipline — smallest sufficient context — rather than inlining the entire history; less relevant items are referenced, not inlined.
- Imported content (email, calendar, plugin data) appearing inside a package is data with provenance, never instructions to the agent.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The Hub MUST accept a context request from an authorized agent consisting of at least a stated purpose (what the agent is trying to do for the person now), and optionally a subject hint (e.g., a project reference).
- **FR-002**: The Hub MUST respond to a context request with a single Context Contract containing, when available within scope: the live goal(s), relevant preferences, relevant memories, constraints, decisions, available shared state, and the granted scope under which it was assembled.
- **FR-003**: Every item in a Context Contract MUST carry a citation to its source object in the vault, and MUST expose the source's provenance, freshness (when it was last asserted or updated), and whether it is person-confirmed or assistant-proposed.
- **FR-004**: The Context Contract MUST include an explicit omission section naming categories of information that were withheld because of scope or policy, without revealing the withheld content.
- **FR-005**: Assembly MUST be bounded by the requesting agent's existing grant: no item outside the granted scope may appear in the contract, regardless of relevance to the purpose.
- **FR-006**: The Hub MUST rank candidate items by relevance to the stated purpose and include only the smallest sufficient set, using the vault's existing search and object relationships; items beyond the sufficiency threshold are excluded or referenced rather than inlined.
- **FR-007**: A person's correction to a source object MUST take effect in all contracts assembled after the correction; superseded content MUST NOT be presented as live.
- **FR-008**: Every contract issuance and refusal MUST be recorded in the existing append-only audit with the requesting agent, purpose, included item references, and omission notes.
- **FR-009**: The context request MUST be available through the Hub's existing MCP connection surface so any paired MCP runtime can use it without a runtime-specific adapter.
- **FR-010**: Assembly MUST work entirely locally and offline, using only objects already in the vault; it MUST NOT trigger imports, external calls, or plugin syncs.
- **FR-011**: When nothing in the granted scope matches the purpose, the Hub MUST return a valid, explicitly minimal contract rather than an error or an unscoped result.
- **FR-012**: Conflicting live items MUST both be included with their provenance; the engine MUST NOT silently discard one side (temporal resolution is deferred to E2).

### Key Entities

- **Context Query**: what an agent submits — the requesting agent's identity (existing pairing), a stated purpose, and an optional subject hint. It is a read request; it never writes to the vault.
- **Context Contract**: the unit the agent receives — subject/situation, purpose echoed back, the assembled items (goals, preferences, memories, decisions, constraints, shared state), granted scope, omission notes, and per-item citation/provenance/freshness/confidence. The agent does not need to know where the data lives.
- **Omission Note**: a named category of withheld information inside a contract (e.g., scope not granted, policy exclusion), with no content from the withheld items.
- **Contract Issuance Record**: the audit entry for each assembled or refused contract — agent, purpose, included item references, omissions, timestamp.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The killer demo passes: a second authorized agent, given only "continue planning the trip" as purpose, receives a contract containing the trip goal, travelers, live candidate, budget constraint, and prior decisions — with zero agent-issued searches — and can state the live candidate correctly.
- **SC-002**: After the person records the "dropped London" correction, 100% of contracts issued afterward for that purpose present Amsterdam as the live candidate and London only as a rejected decision.
- **SC-003**: In the isolation test (personal + work vault, two scoped grants), 0 items cross scope across all issued contracts, and 100% of contracts that withheld in-scope-relevant material include an omission note.
- **SC-004**: Every item in every issued contract carries a resolvable citation to a vault object; 0 uncited items.
- **SC-005**: 100% of contract issuances and refusals appear in the audit trail with agent, purpose, and item references.
- **SC-006**: Contract assembly completes locally with no network egress, within 2 seconds on a typical personal vault (thousands of objects), so an agent can request context at conversation start without noticeable delay.
- **SC-007**: For the fixed demo scenarios, contracts stay within the smallest-sufficient discipline: no contract inlines the full vault or full project history; reviewers can verify every inlined item is relevant to the stated purpose.

## Assumptions

- The existing grant/scope model from 001–002 is sufficient to bound assembly; E1 adds no new grant types, only enforces existing ones during assembly.
- Relevance ranking uses the vault's existing search capabilities and object relationships (project membership, goal linkage); no vector database or embedding store is introduced.
- The context request is exposed as an addition to the existing MCP surface, complementing (not replacing) `search_personal_context` and `get_context_manifest`.
- Purpose interpretation may be lexical/structural in v1 (matching against projects, goals, and object text); semantic inference from imported content (e.g., deriving intent from email) is explicitly out of scope per the roadmap.
- Temporal validity resolution ("what is true now" vs "what was true") is out of scope — E2 depends on this feature and will add it; E1 surfaces conflicts with provenance instead of resolving them.
- Operational project state and situation intent as first-class objects are out of scope — E3; in E1, "available state" means existing SharedState and object status fields.
- Existing `SharedState` and `ActionIntent` keep their names and meanings; this feature does not rename or repurpose them.
- Grant issuance/approval UX is unchanged: holding a valid grant is sufficient authorization for contract requests; no per-request human approval is added.
- Personal Intelligence (pattern inference) and Personal Agency (acting on behalf) remain horizon items and are not part of this feature.
