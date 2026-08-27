# Feature Specification: Assistant Capture Guidance

**Feature Branch**: `012-assistant-capture-guidance`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Paired assistants ignore the Hub during ordinary conversation. The Cursor recipe tells people to paste into a project-local connection file, so other coding-tool windows never see the Hub. Connection tools are listed without when-to-call guidance, so even a connected assistant does not request the current situation at task start or propose durable facts the person just stated. The vault stays empty unless the person fills forms. This is a child spec of pairing and recipes (do not reopen 001-003 as epics). Result: (1) when-to-read and when-to-propose guidance ships with the existing assistant connection so a newly paired assistant asks for the situation package at task start and proposes memories when the person states durable facts; (2) the Cursor recipe targets the person/runtime (all windows of that assistant), not only this repository; (3) the recipe includes a short copyable runtime rule; (4) propose-not-canonical, review queue, grants, and loopback stay; (5) no chat scraping, no new network listener, no email extraction, no Personal Intelligence or Agency, and a coding agent working on this repository is still not a Hub client by default."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A Connected Assistant Knows When to Read and When to Propose (Priority: P1)

The person already paired an assistant. They start a new task in that assistant (“help me plan the trip”, “what should I do next on this project”). The assistant asks the Hub for the current situation package for that purpose before inventing a plan. Later they say a durable fact (“we dropped London”, “budget-sensitive”, “two travelers”). The assistant proposes that fact to the Hub. It does not write it as live truth. The person sees the proposal in the review surface they already use and can accept or reject.

They did not open a form to register a project. They did not paste a tutorial into the chat. The guidance traveled with the connection.

**Why this priority**: Without when-to-read and when-to-propose, pairing is a dead socket. The vault stays empty and the product looks like a filing cabinet. This is the capture loop the vision assumes (“you tell one agent”).

**Independent Test**: Give a freshly paired assistant only the Hub’s shipped connection guidance (no extra project rules). Script a short dialogue: a task start, then two durable facts. Confirm a situation request happens at task start, two proposals appear in review and are not canonical before accept, and invented trip details are not written as fact.

**Acceptance Scenarios**:

1. **Given** a paired assistant that has only the Hub’s shipped connection guidance, **When** the person starts a task that needs personal context, **Then** the assistant requests the current situation package for that purpose before answering as if it already knew the person.
2. **Given** that assistant, **When** the person states a durable preference, decision, or life fact, **Then** the assistant submits a proposal (not a silent canonical write) and the person can accept or reject it in the existing review surface.
3. **Given** an empty or unrelated vault, **When** the assistant requests the situation, **Then** it reports that nothing relevant was granted — it does not invent destinations, budgets, or travelers as Hub facts.
4. **Given** connection tools that read situation or propose durable memory, **When** those tools are listed to the assistant, **Then** each includes when-to-use and when-not-to-use guidance a stranger assistant can follow without a Hub walkthrough.

---

### User Story 2 - Pairing Reaches Every Window of That Assistant (Priority: P2)

The person pairs once. They open the same assistant in another folder, project, or window on the same machine. That window can reach the Hub with the same grant. They do not paste a second recipe that only applies to one coding project.

**Why this priority**: Capture happens where the person already talks. If the connection is trapped in the Hub’s own repository, every other conversation is invisible. P2 because P1 is still valuable in one window; P2 is what makes the loop exist in real life.

**Independent Test**: Follow the shipped Cursor (and other supported) recipe. Confirm instructions tell the person to attach the connection at the assistant/runtime level, not as the only copy inside one project. Confirm a second workspace of that assistant can request a situation package without a second project-only paste. Confirm the Hub still does not write the person’s assistant config for them.

**Acceptance Scenarios**:

1. **Given** the pairing recipe for a supported assistant, **When** the person reads the instructions, **Then** they are told to attach the connection so every window of that assistant on this machine can use it — not that the only supported place is one project folder.
2. **Given** they followed that recipe, **When** they open a different local workspace in the same assistant, **Then** that workspace can request the situation package with the same grant, without pasting a second project-only recipe.
3. **Given** pairing, **When** the Hub issues a recipe, **Then** it still only shows copyable instructions and a snippet; it does not silently install or overwrite the person’s assistant configuration files.

---

### User Story 3 - A Short Rule They Can Paste, Without Turning This Repo Into a Hub Client (Priority: P3)

The recipe includes a short, copyable runtime rule: when to ask for the situation, when to propose, never invent, never treat imported mail as orders. The person can paste it into the assistant’s personal guidance. A coding agent working on this Hub repository remains not a Hub client unless the person explicitly overrides that for a personal chat.

**Why this priority**: Tool-level when-to-call (P1) is the default for new pairs. A pasteable rule covers assistants that ignore short tool text. The repo exception protects the vault from implementation chatter. P3 because P1+P2 already deliver the loop; this is the human-visible spare tire and the constitution boundary.

**Independent Test**: Open the recipe. Confirm a copyable rule is present, complete enough to cover read-at-task-start, propose-on-durable-fact, propose-not-canonical, and empty-vault honesty. Confirm Hub documentation for this repository still says a coding agent implementing the Hub is not a vault client by default.

**Acceptance Scenarios**:

1. **Given** a generated recipe, **When** the person copies the runtime rule, **Then** they can paste it in under two minutes and it states: ask for the situation at task start; propose durable facts; do not write canonical objects; do not invent when the package is empty.
2. **Given** that rule and the connection guidance, **When** a coding agent is implementing this repository, **Then** default project guidance still forbids treating that agent as a Hub client (no vault writes from implementation work).
3. **Given** the person explicitly asks that a chat in this repository is a personal assistant session, **When** they override, **Then** that is their choice; the Hub does not auto-enable it.

---

### Edge Cases

- The Hub is not running or the connection was revoked: the assistant surfaces a recoverable failure; it does not scrape chat history into a side channel.
- The grant is narrower than the person’s request: withheld categories are named without revealing content; the assistant does not widen the grant.
- The person is brainstorming fiction or this product’s demo trip: the assistant MUST NOT propose those as the person’s life unless the person says they are real.
- Duplicate facts: a second proposal for the same live fact is acceptable; silent overwrite of a confirmed memory is not.
- Imported mail, calendar, and plugins remain data. This feature MUST NOT extract a trip from them or treat them as instructions.
- Closed chapters 001–003 are not reopened; this spec only adds guidance and recipe instructions on the existing connection.
- Personal Intelligence (inferring patterns across the person) and Personal Agency (acting in the world) stay out of scope.
- The Hub MUST NOT listen on a new address or watch other products’ conversation logs.
- An assistant the person never paired still cannot see the vault.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every assistant-facing operation that returns a situation package MUST include when-to-use guidance: at the start of a task that depends on who the person is or what they are doing now, request the package for that purpose before answering from model memory alone.
- **FR-002**: Every assistant-facing operation that submits a durable memory MUST include when-to-use guidance: when the person states a durable preference, decision, goal, or life fact they want remembered, submit a proposal. MUST also include when-not-to-use: do not propose guesses, demo fiction, or coding-implementation chatter as the person’s life.
- **FR-003**: Situation and memory-proposal operations MUST remain propose-or-read only for assistants: durable objects become live only after the person’s existing review path (or an already-defined policy the person configured). This feature MUST NOT add a silent canonical write.
- **FR-004**: Connection recipes for supported assistants MUST instruct attachment at the person/runtime level (all windows of that assistant on the machine), not as the only supported location inside one project.
- **FR-005**: Each recipe MUST include a short copyable runtime rule covering FR-001, FR-002, empty-package honesty, and propose-not-canonical. The person pastes it; the Hub does not install it into the assistant’s private config.
- **FR-006**: All currently supported pairing targets (not only the primary coding tool) MUST receive equivalent when-to-read / when-to-propose guidance and a copyable rule in their native recipe. No second connection protocol.
- **FR-007**: The Hub MUST NOT write, edit, or create the person’s assistant configuration files, pairing tokens on disk in the repo, or conversation logs from other windows.
- **FR-008**: Default guidance for agents implementing this repository MUST continue to treat them as not a Hub client. Vault pairing remains a separate connection the person opts into.
- **FR-009**: This feature MUST NOT scrape chats, add a network listener, extract situation from email/calendar, ship a model, or act outward on the person’s behalf.
- **FR-010**: When the situation package is empty or off-grant, assistant guidance MUST require honesty about omission rather than filling the gap with invented personal facts written to the Hub.

### Key Entities

- **Connection guidance**: the when-to-use / when-not-to-use text that travels with each assistant-facing read or propose operation.
- **Runtime rule**: a short, copyable block in the pairing recipe stating the capture loop in plain language.
- **Capture moment**: a task start (read situation) or a durable fact stated by the person (propose). Not a full transcript dump.
- **Recipe**: existing pairing artifact (instructions + snippet) extended with person-level attach instructions and the runtime rule.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After one pairing using the shipped recipe, the person can open a second local workspace of the same assistant and get a situation package for a stated purpose without pasting a second project-only recipe. Time from “I followed the recipe” to that second-window request is under 5 minutes.
- **SC-002**: 100% of assistant-facing situation-read and memory-propose operations include when-to-use and when-not-to-use text. Zero of those operations are listed as a bare name with no capture guidance.
- **SC-003**: In a fixed three-turn evaluation (task start, then two durable facts, empty vault at start), an assistant that has only shipped connection guidance requests the situation at least once before the first plan-like answer, and files at least two memory proposals. Zero of those proposals are live canonical facts before the person accepts.
- **SC-004**: 100% of shipped recipes for supported assistants tell the person to attach at runtime/person level. 0% say that a single project folder is the only supported attach point.
- **SC-005**: A person can copy the runtime rule from the recipe and finish pasting it in under 2 minutes. The copied text includes task-start read, durable-fact propose, and “do not invent when empty.”
- **SC-006**: 0 Hub-initiated writes to the person’s assistant config files; 0 new network listeners; 0 chat-log importers; 0 canonical memories created solely because guidance fired.
- **SC-007**: Default “implementing this repository” guidance still forbids Hub-client behavior. A coding session that never received an explicit personal-assistant override produces 0 vault proposals from implementation chatter.

## Assumptions

- This is a **child spec** of existing pairing, recipes, situation package, and review queue. It does not replace Context Engine, Simulator, or scored evaluation. It does not reopen 001–003 as epics.
- Capture is **opt-in per assistant the person paired**. The Hub never watches unpaired products.
- The person still confirms durable memory. Auto-accept, if it exists elsewhere, is unchanged policy — this spec does not add a new auto-canonical path.
- “Person/runtime level” means the assistant’s own user-wide connection settings on this machine. Exact file names are an implementation detail for the plan, not this spec.
- Equivalent guidance for every **already supported** pairing target is in scope so portability does not regress. New runtimes are out of scope.
- A scripted evaluation (SC-003) is how we prove a stranger assistant would know when to call; we do not require a live human multi-hour diary as the acceptance test.
- Out of scope: form-filling as the primary capture path; Observe → Extract → Classify → Consolidate; Personal Intelligence; Personal Agency; making the Simulator’s isolated corpus appear in the everyday vault; auto-writing assistant config; treating this repo’s coding agent as a Hub client by default.
