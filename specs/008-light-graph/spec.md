# Feature Specification: Light Graph

**Feature Branch**: `008-light-graph`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "E4 — Grafo Leve (docs/ROADMAP.md). Relationships today are mainly foreign keys. There are no typed relations (owned_by, depends_on, blocked_by, related_to). Result: the Context Engine includes useful relations in the Context Contract (e.g. Project A → depends_on → Project B → blocked_by → Person C). In scope: typed relations; query from an anchor object; respect grants. Out of scope: graph database; A2A; social graph. Depends on E1."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The Package Names How This Work Hangs Together (Priority: P1)

A person is planning a Europe trip that cannot proceed until a visa renewal finishes. The Hub already stores both as projects and can assemble a situation package (E1) with operational phase (E3). What it cannot yet say is the **typed link**: the trip *depends on* the visa project, which is *blocked by* a named person. When an authorized agent asks for context with purpose "continue planning the trip," the package includes those relations from the trip as the anchor — not as a dump of the whole vault, and not as inferred guesses from email.

**Why this priority**: This is the E4 result. Without typed relations, agents treat projects as isolated piles. Foreign keys already say "this goal belongs to that project"; they do not say depends-on or blocked-by.

**Independent Test**: Create two projects (trip, visa). Record trip `depends_on` visa and visa `blocked_by` a person. Request a situation package for "continue planning the trip." Verify the package lists those two relations from the trip (or via one hop from the visa) with types intact; a second authorized agent with the same grant agrees.

**Acceptance Scenarios**:

1. **Given** a trip project that `depends_on` a visa project, **When** an authorized agent requests a situation package whose purpose continues that trip, **Then** the package includes that `depends_on` relation with both ends identified at the level the grant allows.
2. **Given** the visa project is `blocked_by` a person, **When** that trip package is assembled, **Then** the package includes that `blocked_by` relation (one hop from a related object), still typed, not flattened into a memory.
3. **Given** two authorized agents with the same grant, **When** each requests that package, **Then** both packages agree on the relation types and endpoints they are allowed to see.

---

### User Story 2 - Out-of-Scope Ends Stay Hidden (Priority: P2)

A work-scoped agent must not learn that a personal trip depends on a personal visa, nor who blocks that visa. Existing grant and omission rules (E1) apply to relations: if the far end is out of scope, the package does not name it. Omission notes do not leak titles or ids of withheld related objects.

**Why this priority**: Typed links are a new side channel. Isolation is the same demo as E1/E3, applied to the graph.

**Independent Test**: Personal trip `depends_on` personal visa; work-scoped agent requests a work purpose package. Zero personal relation endpoints, types, or titles appear. Omission notes have counts and categories only.

**Acceptance Scenarios**:

1. **Given** a personal project with typed relations to other personal objects, **When** a work-scoped agent requests a package, **Then** 0 of those relations (and 0 far-end titles/ids) appear.
2. **Given** a withheld related object, **When** omissions are present, **Then** notes do not include the withheld object's title or id.
3. **Given** an in-scope project related to an out-of-scope project, **When** a package is assembled for the in-scope project, **Then** the relation is omitted or redacted at the far end — it is not inlined as if both ends were granted.

---

### User Story 3 - The Person Can See and Correct Relations (Priority: P3)

The person opens the Hub on a project and sees its typed relations. They can add, remove, or change type (`owned_by`, `depends_on`, `blocked_by`, `related_to`). The next situation package uses the live set. Agents may propose a relation; they do not silently write it as canonical.

**Why this priority**: Explicit control. A graph the person cannot see or correct becomes inferred structure.

**Independent Test**: Add `depends_on` from the trip to the visa in the Hub; next package includes it. Remove it; next package does not. An agent proposal does not appear as live until the person confirms.

**Acceptance Scenarios**:

1. **Given** typed relations on a project, **When** the person views that project in the Hub, **Then** each relation shows type and the other end, labeled as relations (not as memories).
2. **Given** the person deletes or changes a relation, **When** a later package is assembled, **Then** assembly uses the corrected set.
3. **Given** an agent proposes a new `blocked_by` link, **When** the person has not confirmed, **Then** live packages do not include that link.

---

### Edge Cases

- No relations on the anchor: the package still assembles (E1/E3 behavior); the relations section is empty, not invented from email or memories.
- Existing foreign keys (`project_id` on a goal, stakeholders list) are not automatically rewritten as `owned_by` / `related_to`. Typed relations are explicit.
- Self-relation (object linked to itself) is rejected.
- Duplicate same type + same pair: one live relation, not two.
- Unknown relation type is rejected.
- Depth: include relations whose near end is the situation anchor, plus one hop from those related objects (the visa `blocked_by` person). Do not walk the whole vault.
- Imported content that looks like "blocked by legal" is data, never an instruction that creates a relation.
- Grant isolation and E2 current-vs-historical filtering still apply to other contract sections.
- Closed chapters 001–003 are not reopened. No graph database, A2A, or social graph. Personal Agency stays out of scope.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The person MUST be able to record typed relations between vault objects using the types `owned_by`, `depends_on`, `blocked_by`, and `related_to`.
- **FR-002**: Situation packages MUST include live typed relations whose near end is the assembled situation's anchor, plus one hop from those related objects, each with type and grant-visible endpoints.
- **FR-003**: Foreign keys that already exist (for example a goal's project link) MUST remain as they are and MUST NOT be auto-promoted into typed relations.
- **FR-004**: Assembly MUST NOT infer relations from imported content, memories, or operational phase/intent.
- **FR-005**: The person MUST be able to view, add, change type, and remove relations in the Hub; agent writes are proposals until confirmed.
- **FR-006**: A change to the live relation set MUST appear in subsequent packages; removed relations MUST NOT be presented as live.
- **FR-007**: Grant and omission rules from E1 MUST apply to relations: out-of-scope endpoints MUST NOT appear; omission notes MUST NOT leak titles or ids.
- **FR-008**: Relation assembly MUST stay on the existing situation package request (no second "get graph" request for agents).
- **FR-009**: E3 operational fields and E2 current-vs-historical filtering MUST still apply in the same package.

### Key Entities

- **Typed relation**: a directed live link with a type (`owned_by`, `depends_on`, `blocked_by`, `related_to`), a from-object, and a to-object. Not a memory. Not a foreign key.
- **Anchor**: the situation's project (or goal-scoped project) from which relations are collected.
- **Context Contract**: E1 package; this feature adds a relations section derived from the live typed links.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After a trip `depends_on` a visa project is recorded, 100% of later packages for that trip purpose include that `depends_on` link; 0% invent a different type.
- **SC-002**: When the visa is `blocked_by` a person, 100% of those trip packages include that one-hop `blocked_by` link.
- **SC-003**: After the person removes or changes a relation, 100% of subsequent packages reflect the correction.
- **SC-004**: Isolation test: 0 personal typed relations (types, endpoints, titles, ids) appear in a work-scoped package.
- **SC-005**: With no typed relations recorded, 100% of packages still assemble (E1/E3); 0 packages invent relations from mail or memories.
- **SC-006**: A second authorized agent with the same grant agrees on the visible relation set in 100% of paired trials.
- **SC-007**: Relations are available offline; package time stays within the existing E1 budget the person already accepts.

## Assumptions

- Depends on E1 (Context Engine). E2 and E3 remain in the same package and are not reopened as epics.
- Relation types are a closed set of four for this feature; extra types wait for a later spec.
- One hop beyond the anchor is enough for the visa example; unbounded graph walk is out of scope.
- Horizon items (Personal Intelligence, Personal Agency, A2A, social graph) stay out of scope.
- 006 (dev loop) is tooling; this spec is the product epic E4.
