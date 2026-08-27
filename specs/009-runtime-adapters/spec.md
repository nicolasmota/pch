# Feature Specification: Runtime Adapters

**Feature Branch**: `009-runtime-adapters`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "E5 — Adapters de Runtime (docs/ROADMAP.md). The thesis is portability. Today the real client is Cursor, plus a demo agent and a second test runtime. Result: at least two real-use runtimes consume the same situation package. Candidates: Hermes, OpenClaw. The person switches runtime without re-editing context. In scope: per-runtime recipes; pairing; catalog; existing assistant connection; killer-demo validation. Out of scope: a per-model adapter when the runtime already uses the existing connection; a new agent-to-agent protocol. Depends on E1."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A Second Real Assistant Gets the Same Trip Package (Priority: P1)

A person already pairs Cursor and gets a situation package for "continue planning the trip." They want a **second real assistant** — Hermes or OpenClaw — to see that same package: the Europe trip, the same goals and memories, the same operational phase and typed relations if those are set. They open Connections, pick that assistant from the catalog, copy the connection recipe, pair it with the same grant. Both assistants, same purpose, agree. They do not paste a different protocol or re-describe the trip.

**Why this priority**: This is the E5 result. Portability is the thesis; one real client is not enough. The demo agent and unnamed test runtime do not count as real-use runtimes.

**Independent Test**: Catalog lists Hermes and OpenClaw as supported pairing targets with recipes. Pair two real-use assistants (Cursor plus Hermes, or Hermes plus OpenClaw) with the same grant. Each requests the trip situation package. Verify the packages match on situation, goals, and (if present) relations. Verify no second connection protocol was introduced.

**Acceptance Scenarios**:

1. **Given** the catalog of pairing targets, **When** the person opens it, **Then** Hermes and OpenClaw appear as supported real-use assistants with a copy-paste connection recipe each, not as "coming soon" placeholders.
2. **Given** two paired real-use assistants with the same grant, **When** each requests a situation package for "continue planning the trip," **Then** both packages agree on the live situation (project, operational phase if set, current intent if set, typed relations if set).
3. **Given** those two assistants, **When** they request the package, **Then** they use the existing assistant connection surface — no new agent-to-agent protocol and no per-model special path.

---

### User Story 2 - Switching Runtime Does Not Mean Re-editing the Trip (Priority: P2)

The person stops using one assistant and starts another. The Europe trip, visa dependency, budget preference, and "comparing itineraries" phase stay in the Hub. They do not re-type facts into the new assistant's memory. After pairing the new runtime and granting the same project, the next package is still the trip — not an empty vault and not a rewrite of canonical objects.

**Why this priority**: Constitution: agents are replaceable. Switching runtime must not delete history or require re-entry of canonical facts. US1 proves two can read; US2 proves the person can **replace** one without editing context.

**Independent Test**: Seed the trip. Pair assistant A; confirm a package. Revoke or stop using A. Pair assistant B with the same grant. Confirm B's package still names the trip and does not ask the person to re-enter destinations, budget, or phase.

**Acceptance Scenarios**:

1. **Given** trip facts and operational state already in the Hub, **When** the person pairs a different supported runtime, **Then** that runtime's package includes those facts without the person editing them again.
2. **Given** assistant A is revoked, **When** assistant B requests the same purpose, **Then** B still receives the trip package; A's revocation does not delete Hub objects.
3. **Given** the person switches runtimes, **When** they inspect the Hub, **Then** projects, memories, relations, and phase are unchanged.

---

### User Story 3 - The Person Can See Which Runtimes Are Supported (Priority: P3)

On Connections, the person sees which assistants are supported for pairing and which are not. They pick Hermes or OpenClaw, get a recipe with instructions in plain language, and copy it. A nonsense assistant name does not mint a recipe. Cursor remains available; this feature does not remove it.

**Why this priority**: Explicit control. Recipes the person cannot find are not portability. P3 because US1 already requires the catalog entries; this story is the Hub surface and the reject path.

**Independent Test**: Open Connections; verify Hermes and OpenClaw in the picker; generate each recipe; verify instructions mention how to paste; request a recipe for an unknown assistant and verify it is refused; verify Cursor is still listed.

**Acceptance Scenarios**:

1. **Given** the Connections pairing surface, **When** the person opens the assistant picker, **Then** Cursor, Hermes, and OpenClaw are listed as supported.
2. **Given** a paired connection, **When** they generate a Hermes or OpenClaw recipe, **Then** they receive copyable setup text and a snippet that uses the existing Hub bridge — not a second protocol.
3. **Given** an unknown assistant id, **When** they request a recipe, **Then** the Hub refuses and does not issue a pairing recipe.

---

### Edge Cases

- Demo-agent and generic "test runtime" are not counted toward the two real-use runtimes.
- An assistant that already uses the existing connection does not get a per-model adapter; one recipe family is enough.
- A new agent-to-agent protocol is out of scope; refuse rather than invent one.
- Closed chapters 001–003 are not reopened; this is a child spec on pairing, catalog, and the E1 situation package.
- Grant isolation still holds: a work-scoped assistant does not receive the personal trip package.
- Imported content is data; pairing a second runtime does not treat email as instructions.
- Personal Agency (the new runtime planning and acting alone) is out of scope.
- Horizon items (Personal Intelligence, A2A, Skills object) stay out of scope.
- Loopback-only: recipes still point at the local Hub, not a public server.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The Hub MUST list Hermes and OpenClaw as supported real-use pairing targets, in addition to keeping Cursor supported.
- **FR-002**: Each supported target MUST have a person-visible connection recipe (instructions + copyable snippet) issued from the existing pairing flow.
- **FR-003**: At least two real-use runtimes MUST be able to request the same situation package through the existing assistant connection; packages for the same grant and purpose MUST agree.
- **FR-004**: Switching or revoking a runtime MUST NOT delete Hub objects or require the person to re-enter canonical trip facts.
- **FR-005**: The Hub MUST NOT add a new agent-to-agent protocol, and MUST NOT add a per-model adapter when the runtime already uses the existing connection.
- **FR-006**: An unknown or unsupported assistant MUST NOT receive a recipe.
- **FR-007**: The killer-demo trip purpose MUST still assemble for each newly listed runtime the same way it does for Cursor (E1–E4 fields included when set).
- **FR-008**: Grant, omission, and loopback rules from E1 MUST still apply; pairing a second runtime MUST NOT widen grants.

### Key Entities

- **Runtime adapter (recipe)**: a person-facing pairing target (name, supported flag, instructions, copyable connection snippet). Not a new protocol. Not a model.
- **Real-use runtime**: an assistant a person actually runs (Cursor, Hermes, OpenClaw). Not the in-repo demo agent.
- **Situation package**: the E1 contract (with E2–E4 fields when present). Adapters consume it; they do not own it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of catalog listings used for this feature include Hermes and OpenClaw as supported pairing targets (Cursor remains listed).
- **SC-002**: For 100% of Hermes and OpenClaw recipe requests on a valid connection, the person receives instructions plus a copyable snippet; 0 unknown-assistant requests succeed.
- **SC-003**: Two real-use assistants with the same grant agree on the trip situation package in 100% of paired trials (situation, goals; relations and phase if set).
- **SC-004**: After switching from assistant A to B, 100% of B's trip packages still name the existing Europe Trip without the person re-entering destinations, budget, or phase.
- **SC-005**: Revoking A deletes 0 Hub projects, memories, relations, or phase fields.
- **SC-006**: Isolation still holds: 0 personal trip titles/ids in a work-scoped package from the newly listed runtimes.
- **SC-007**: Recipes and packages work offline on the local Hub; no public-server binding is introduced.

## Assumptions

- Depends on E1 (situation package) and 002 (pairing, catalog, recipes). E2–E4 stay in the package and are not reopened.
- Cursor already counts as one real-use runtime; this feature adds Hermes and OpenClaw so at least two real-use runtimes are catalogued and consumable.
- Hermes and OpenClaw consume the existing assistant connection the same way Cursor does; recipe text may differ; the package must not.
- Live paste into a running Hermes/OpenClaw desktop is a manual check; automated tests prove catalog, recipe, pairing, and identical packages via the same connection surface used in E1.
- Horizon items and a new A2A protocol stay out of scope.
- 006 (dev loop) is tooling; this spec is product epic E5.
