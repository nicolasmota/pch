# Feature Specification: Personal Context Hub (MVP)

**Feature Branch**: `001-personal-context-hub`

**Created**: 2026-08-21

**Status**: Draft

**Input**: User description: "Personal Context Hub (PCH) — a plug-and-play product that gives a person one private, durable home for their digital context (identity, memory, objectives, preferences, projects, relationships, capabilities and selected current state), with the Personal Context Layer (PCL) as the underlying platform. Users install the Hub, connect accounts and agents, and control what each agent may see or do. Agents are replaceable; personal context is a user-owned asset. Derived from product/architecture draft `personal-context-layer-spec.md` (Draft v0.1)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Manage My Personal Context (Priority: P1)

A person installs the Hub, completes a short guided setup, and gets a single private space for their personal context. They can create and edit their profile, preferences, projects, goals, commitments, decisions, and memories; browse and search them; and see where each piece of information came from. All of this works entirely on their own device with no cloud account and no agent connected.

**Why this priority**: This is the foundation of the product promise — "your personal context is an asset you own." Without a usable, private, inspectable context store, nothing else (agent connections, permissions, portability) has value. It is also a viable standalone product slice: a private, structured home for personal context.

**Independent Test**: Can be fully tested by installing the Hub on a clean machine, completing setup, creating a project with goals, commitments, decisions and memories, searching for them, editing one, and confirming everything persists locally after a restart — with no agent or external account involved.

**Acceptance Scenarios**:

1. **Given** a clean machine, **When** a non-technical user installs the Hub and follows the guided setup, **Then** a private personal context space is created and ready to use without any developer configuration.
2. **Given** an active personal space, **When** the user creates a project with goals, commitments, decisions and related memories, **Then** each object is saved, versioned, and browsable from the Hub interface.
3. **Given** stored memories and projects, **When** the user searches for a topic, **Then** results show matching items with their classification and the source each item came from.
4. **Given** a stored memory the user disagrees with, **When** the user edits or deletes it, **Then** the correction takes effect immediately, the change is recorded in the history, and the old value does not silently return.
5. **Given** the device is offline, **When** the user opens the Hub, **Then** all reading and editing of their context continues to work.

---

### User Story 2 - Connect an Agent With Scoped Access (Priority: P2)

A person connects an AI agent to their Hub by choosing it from a catalog or scanning/pasting a connection link. During connection they pick a simple, plain-language permission preset (for example "Can read my active projects", "Always ask before sending anything"). The connected agent can then request context for a stated purpose and receives only what its permissions allow, with citations to sources. The user can view and revoke the agent's access at any time.

**Why this priority**: Connecting agents is the product's reason to exist beyond a personal notebook. Scoped, revocable access is the core trust mechanism ("least context, least privilege") and is required before any agent-facing scenario can happen.

**Independent Test**: Can be tested by connecting one agent via the catalog, granting it read access to a single project, asking it about that project (receives grounded, cited context) and about an out-of-scope topic (receives nothing), then revoking access and confirming subsequent requests are denied.

**Acceptance Scenarios**:

1. **Given** an installed Hub, **When** the user selects an agent from the catalog or uses its connection link, **Then** the agent is connected without the user performing any manual technical configuration.
2. **Given** an agent connection in progress, **When** the user selects a permission preset, **Then** the granted access is displayed in plain language before the user confirms.
3. **Given** an agent with read access limited to one project, **When** the agent requests context for a stated purpose within that project, **Then** it receives only the in-scope information, together with source citations and notices for anything withheld.
4. **Given** the same agent, **When** it requests information outside its granted scope (e.g., personal finance memories), **Then** the request is denied or redacted and the denial is recorded.
5. **Given** a connected agent, **When** the user revokes its access, **Then** all subsequent requests from that agent are refused and any outstanding context snapshots stop working.

---

### User Story 3 - Continuity Across Different Agents (Priority: P3)

A person uses two different agents (for example, one for planning and one for messaging). Both can be granted access to the same projects and preferences, so either agent can pick up work with full awareness of the project's charter, decisions, and commitments — but neither agent owns the context. Switching or replacing an agent never means losing history or re-entering personal information.

**Why this priority**: Cross-agent continuity is the differentiating proposition ("your personal context, connected to any agent"). It depends on Stories 1 and 2 being in place, which is why it is P3 despite being the headline value.

**Independent Test**: Can be tested by connecting two independently implemented agents, creating a project once, asking each agent for a project brief, and verifying both receive consistent, correctly cited context; then disconnecting one agent and confirming the context remains intact and usable by the other.

**Acceptance Scenarios**:

1. **Given** a project created once in the Hub, **When** two different connected agents each request a brief on that project, **Then** both receive consistent context reflecting the same canonical objects, each with citations.
2. **Given** one agent has recorded shareable working state for a task, **When** the user continues the task with a second authorized agent, **Then** the second agent can see the explicitly shared state and continue the work.
3. **Given** an agent is disconnected or replaced, **When** the user connects a different agent, **Then** no personal history is lost and the new agent can be granted access without re-creating any context.

---

### User Story 4 - Review and Control Agent-Proposed Memories (Priority: P4)

When an agent learns something durable about the user (a preference, a summary, a decision), it proposes the memory rather than writing it directly. The user reviews proposals, accepts or rejects them, and can always see why the system believes something — its source, when it was added, and how confident it is. User-confirmed facts always win over agent inferences.

**Why this priority**: Trustworthy memory is what makes people willing to keep their context in one place. It requires an agent connection (Story 2) to be meaningful, and protects the integrity of everything created in Story 1.

**Independent Test**: Can be tested by having a connected agent submit memory proposals, reviewing them in the Hub queue, accepting one and rejecting another, and verifying the accepted one appears with provenance while the rejected one never enters canonical memory.

**Acceptance Scenarios**:

1. **Given** a connected agent, **When** it submits a durable memory proposal, **Then** the memory does not become canonical until the applicable review policy is satisfied.
2. **Given** a pending proposal, **When** the user reviews it, **Then** they can see the proposed content, its source evidence, and its confidence, and can accept, edit-then-accept, or reject it.
3. **Given** a proposal that concerns sensitive topics (financial, health, legal, or relationship information), **When** it is submitted, **Then** it always requires explicit user confirmation before acceptance.
4. **Given** a user-confirmed fact, **When** an agent proposes a conflicting inference, **Then** the user-confirmed value is never silently overwritten and the conflict is surfaced for the user to resolve.
5. **Given** an accepted memory the user later corrects, **When** any agent retrieves related context afterwards, **Then** it receives the corrected value.

---

### User Story 5 - Approve External Actions and Audit Everything (Priority: P5)

When an agent wants to do something with external effect (like sending a message), it must submit the intended action for the user's explicit approval. The user sees a clear summary of what will happen, approves or declines, and can later review a complete, plain-language timeline of everything agents read, wrote, requested, and did.

**Why this priority**: Controlled delegation and observability are essential to trust but only matter once agents are connected and using context. In the MVP, every external action requires approval — no standing automation.

**Independent Test**: Can be tested by having a connected agent submit an external action intent, approving it in the Hub, verifying the action proceeds only after approval, declining a second intent and verifying nothing happens, then reviewing the full sequence in the audit timeline.

**Acceptance Scenarios**:

1. **Given** a connected agent, **When** it proposes an action with external effect, **Then** the action does not proceed until the user explicitly approves that specific action.
2. **Given** a pending approval, **When** the user views it, **Then** the request shows who is asking, what will happen, and what information it is based on, in plain language.
3. **Given** the user declines an action, **When** the agent retries the same action, **Then** it is not executed and the retry is recorded.
4. **Given** any context read, memory write, approval or action, **When** the user opens the audit timeline, **Then** the event appears with the acting agent, time, and outcome, and the record cannot be silently altered.

---

### User Story 6 - Export and Re-import My Context (Priority: P6)

A person can export their entire personal space — or a selected project — to a documented, portable archive that they own. The archive includes their structured objects, memory provenance, and policy labels. They can later import it into a fresh Hub installation without losing anything, with conflicts surfaced for their decision rather than silently resolved.

**Why this priority**: Portability is the proof of ownership and the exit guarantee ("portable exit"). It is deliberately part of the MVP so portability is tested early, but it depends on the context model (Story 1) being complete.

**Independent Test**: Can be tested by exporting a populated personal space to an archive, installing a clean Hub on another machine, importing the archive, and verifying that typed objects, memory lineage, and access classifications all survive the round trip.

**Acceptance Scenarios**:

1. **Given** a populated personal space, **When** the user requests an export, **Then** an encrypted, documented archive is produced containing all user-owned objects, their provenance, and their classifications.
2. **Given** an export request, **When** the user selects a subset (by project, date range, or classification), **Then** only the selected content is included.
3. **Given** an archive, **When** it is imported into a clean Hub, **Then** the content first appears in a staging view and the user chooses to merge, replace, or keep it separate.
4. **Given** an import that conflicts with existing content, **When** the import runs, **Then** conflicts are presented to the user rather than resolved silently, and imported agent-inferred memories keep their original (non-user-confirmed) standing.
5. **Given** an exported archive, **When** it is inspected without any Hub account or connected agent, **Then** its contents are readable per the documented format.

---

### Edge Cases

- What happens when an agent requests "everything about the user"? Requests must be purpose-bound; unscoped requests are rejected and the agent receives only what its grant allows.
- What happens when access is revoked while an agent holds an unexpired context snapshot? Snapshots are time-limited, and revocation invalidates outstanding snapshots.
- What happens when two agents propose contradictory memories at nearly the same time? Both remain proposals; the conflict is surfaced to the user, and neither silently becomes canonical.
- What happens when imported or connected content contains instructions aimed at manipulating an agent (prompt injection)? Imported content is treated as untrusted data, never as user authority; it cannot expand permissions or trigger actions.
- What happens when the user deletes a memory that an accepted summary was derived from? The derived item's provenance shows the missing source, and the user is prompted to review the derived item.
- What happens when the personal vault grows large (on the order of 100,000 memories and artifact references)? Everyday browsing and retrieval must remain responsive.
- What happens when the device loses network connectivity? All local reading, editing and searching continues; only externally dependent operations wait.
- What happens if the user abandons setup partway through? No partial context space is left in an ambiguous state; setup can be resumed or restarted cleanly.
- What happens when an agent submits the same action intent twice (e.g., after a timeout)? Duplicate submissions are recognized and do not cause the action to execute twice.
- What happens to sensitive fields when context is disclosed to an agent? Fields classified as sensitive are withheld or redacted before disclosure unless the grant explicitly covers them, and the response notes that redaction occurred.

## Requirements *(mandatory)*

### Functional Requirements

**Setup and context space**

- **FR-001**: The system MUST be installable by a non-technical user and provide a guided first-run setup that creates (or imports) a single private personal context space without any manual technical configuration.
- **FR-002**: The system MUST store all personal context on the user's own device, encrypted at rest, and MUST NOT require any cloud account to operate.
- **FR-003**: The system MUST remain fully functional for reading, editing, and searching local context while the device is offline.

**Context management**

- **FR-004**: Users MUST be able to create, view, edit, and delete their profile, preferences, projects, goals, commitments, decisions, and memories through the Hub interface.
- **FR-005**: Every durable object MUST carry ownership, classification, provenance (source, time, author), confidence, an authority level distinguishing user-confirmed facts from imported facts and agent inferences, and a version history.
- **FR-006**: The system MUST provide search and retrieval over stored context that returns results with source citations, classifications, and only content the requester is permitted to see.
- **FR-007**: A user correction or deletion MUST take effect immediately, be recorded, and MUST NOT be silently reverted by any later agent inference; an inference MUST never overwrite a user-confirmed value without user resolution.

**Agent connection and permissions**

- **FR-008**: Users MUST be able to connect an agent from a catalog entry or a secure connection link, and to disconnect it, without manual technical configuration.
- **FR-009**: Each connected agent MUST have its own authenticated identity, and its access MUST be defined by explicit, scoped, time-boundable grants — never by default access to everything.
- **FR-010**: The system MUST offer plain-language permission presets at connection time (e.g., "Can read my active projects", "Always ask before sending"), with finer-grained adjustment available afterwards.
- **FR-011**: Agents MUST request context for a stated purpose and receive a time-limited, scope-filtered snapshot with citations and explicit notices of anything redacted or withheld; unscoped "give me everything" requests MUST be refused.
- **FR-012**: Users MUST be able to revoke any agent's access at any time; revocation MUST take effect promptly, including invalidating outstanding context snapshots.
- **FR-013**: Sensitive fields MUST be filtered or redacted according to classification and grant scope before any disclosure to an agent.

**Memory proposals and shared state**

- **FR-014**: Agents MUST NOT write durable memory directly; they MUST submit memory proposals carrying evidence, which are auto-accepted, queued for review, or rejected according to the user's review policy.
- **FR-015**: Proposals concerning financial, health, legal, or relationship-sensitive information MUST always require explicit user confirmation before acceptance.
- **FR-016**: The system MUST detect duplicate and conflicting proposals against existing memories and surface conflicts to the user rather than resolving them silently.
- **FR-017**: The system MUST support short-lived, expiring working state that agents can record for task continuity, shared with other agents only when explicitly marked shareable, and never automatically promoted into durable memory.

**Actions, approvals and audit**

- **FR-018**: Any agent action with external effect MUST be submitted as an explicit intent and MUST NOT execute until the user approves that specific action; in this release there are no standing pre-authorizations for external actions.
- **FR-019**: Approval requests MUST present, in plain language, who is asking, what will happen, and the basis for the request.
- **FR-020**: The system MUST recognize repeated submissions of the same action intent and prevent duplicate execution.
- **FR-021**: The system MUST maintain a tamper-evident, append-only audit timeline of context reads, memory proposals and outcomes, state changes, approvals, grant changes, actions, and exports/imports — viewable by the user in plain language; a consequential action MUST NOT be acknowledged before its audit record is persisted.
- **FR-022**: Audit records MUST NOT store raw private conversation content by default; sensitive diagnostic capture MUST be opt-in and separately protected.

**Portability**

- **FR-023**: Users MUST be able to export their personal space — in full or filtered by project, date range, or classification — to an encrypted archive in a documented, versioned, open format that is readable without any active product account.
- **FR-024**: Exports MUST include all user-owned canonical objects with their provenance, ownership, and classification, and MUST exclude third-party secrets by default.
- **FR-025**: Imports MUST land in a staging view where the user chooses merge, replace, or keep-separate; conflicts MUST be surfaced for user decision, and imported agent-inferred memories MUST retain their original authority level.

**Safety**

- **FR-026**: Content imported from external sources MUST be treated as untrusted data: it MUST NOT be able to expand permissions, alter policy, or trigger actions by itself.
- **FR-027**: Access decisions MUST be evaluated by the system's own policy rules — outside any agent's reasoning — based on the requesting identity, the context space, the purpose, the resource, and the grant's constraints.

### Key Entities

- **Person**: The human owner of the Hub — canonical profile, identities, and time zone. All context belongs to a person.
- **Context Space**: The ownership and access boundary for context (the MVP has one `personal` space per user). Every object lives in exactly one space.
- **Project / Goal / Commitment / Decision**: Structured, durable intent objects — a sustained effort, a desired outcome, a promise or deadline, and a chosen alternative with rationale. They link to each other and to supporting memories and artifacts.
- **Memory**: A durable claim, observation, summary, or episode, with provenance, confidence, sensitivity classification, authority level (user-confirmed vs. inferred vs. imported), retention policy, and version history.
- **Artifact**: Source material or an external reference (document, message thread, conversation) that memories and decisions cite as evidence.
- **Preference**: An editable user default or rule (e.g., communication style) that agents can be permitted to read.
- **Shared State**: Short-lived, expiring operational facts about work in progress (current focus, handoff notes), distinct from durable memory and shareable across agents only by explicit choice.
- **Agent Connection**: A registered, authenticated agent with its identity, capabilities, and current standing (connected, revoked).
- **Grant**: A scoped permission — subject, space, resource/action, purpose, constraints, and expiry — that defines exactly what a connection may see or do.
- **Memory Proposal**: An agent-submitted candidate memory with evidence, awaiting policy evaluation and/or user review.
- **Action Intent**: A proposed external-effect action awaiting explicit user approval, with its outcome recorded.
- **Audit Event**: An immutable record of a read, write, proposal, approval, action, grant change, or export/import.
- **Portable Archive**: A documented, versioned export of a space or subset, carrying objects, provenance, classifications, and integrity verification.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A non-technical user can install the Hub, complete setup, and create their first project in under 15 minutes without external help or developer configuration.
- **SC-002**: A pilot user can create a project context once and retrieve a correctly cited, grounded brief about it from each of two independently implemented agents.
- **SC-003**: 100% of seeded forbidden-context tests are blocked: an agent granted access to one project can never retrieve context outside its grant.
- **SC-004**: Revoking an agent's access takes effect within seconds, after which 100% of that agent's requests are refused.
- **SC-005**: 100% of external actions in pilot use are preceded by an explicit user approval, and zero actions or durable writes occur without a corresponding audit record.
- **SC-006**: A user can find, understand, and correct any stored memory — including seeing why the system believed it — and the correction persists across all subsequent agent interactions.
- **SC-007**: A full export/import round trip into a clean installation preserves 100% of typed objects, memory lineage, and policy labels.
- **SC-008**: At least 80% of pilot task interactions are rated by users as factually useful (the agent had the right context).
- **SC-009**: Common context searches over a vault of up to 100,000 memories and artifact references return results in under 1 second on a typical personal computer.
- **SC-010**: All user-facing controls (setup, permissions, review, audit) are operable by keyboard and screen reader, and pilot users can correctly explain what access an agent has after reading its permission summary.

## Assumptions

- **MVP scope**: This specification covers the local-first, single-user MVP (the source document's P0 scope). Later-phase capabilities — multi-device sync, additional named agent adapters, organization/team spaces, skill registry and catalog, agent-to-agent delegation, hosted deployment, and external account connectors (calendar/email/files) beyond basic consent-led connection — are out of scope for this feature.
- **Deployment model**: Local-first with an encrypted on-device vault and no mandatory cloud account, per the source document's recommended first decisions.
- **Single context space**: The MVP supports one `personal` context space per user; work/family/organization spaces come later.
- **Approval posture**: In the MVP, every external action and every sensitive durable memory requires explicit human approval; standing pre-authorizations are deferred.
- **Compatibility bar**: The MVP targets a generic agent integration plus two real, independently implemented agent runtimes for validating cross-agent continuity; no bespoke agent is built as part of this feature.
- **Source systems remain authoritative**: The Hub stores normalized references and selected derived context; connected source systems keep ownership of their native records unless the user explicitly makes the Hub canonical for a field.
- **No autonomous high-stakes actions**: Financial, legal, medical, or other high-impact autonomous decision-making is out of scope.
- **Agent reasoning quality is out of scope**: The product guarantees what context an agent receives and what it may do — not that the agent reasons correctly with it.
- **Synthetic test data**: Evaluation and test fixtures use synthetic or explicitly consented data.
