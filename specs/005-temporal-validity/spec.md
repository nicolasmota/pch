# Feature Specification: Temporal Validity

**Feature Branch**: `005-temporal-validity`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "E2 — Validade Temporal (docs/ROADMAP.md). Preferences and facts change. Version history and retention already exist, but there is no clear representation of what holds now versus what was true. Result: 'I didn't like X.' → 'I now like X.' Both remain; the engine returns the current one. In scope: validity start/end, current vs historical resolution, temporal filter on E1 assembly. Out of scope: sophisticated semantic merge; automatic forgetting without policy. Depends on E1."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The Current Preference Is What Agents Receive (Priority: P1)

A person once disliked spicy food and said so. Later they change their mind: they now like it. Both statements stay in their record — the old dislike is not erased. When an authorized agent asks for a situation package for meal planning, the package treats "likes spicy food" as current and does not present the old dislike as a live preference. A second authorized agent, given the same purpose after the change, receives the same current picture. The person can still see that they used to dislike spicy food.

**Why this priority**: This is the E2 result and the reason the epic exists. E1 already assembles a situation package and already applies a person's correction to the live object; it does not yet distinguish a change of mind (two successive truths) from a live-object edit. Without current-vs-historical resolution, agents keep acting on expired preferences, or history disappears into overwrite.

**Independent Test**: Seed a preference or factual memory that the person disliked X; record a later change of mind that they now like X; request a situation package with a purpose that depends on that preference; verify the package presents only the new statement as current; verify the old statement still exists as historical and is not treated as live; request the same purpose from a second authorized agent with the same grant and verify the same current picture.

**Acceptance Scenarios**:

1. **Given** a vault containing a person-confirmed statement that they disliked X, **When** the person records a change of mind that they now like X, **Then** both statements remain in the vault and the earlier statement is marked historical (no longer current) rather than deleted.
2. **Given** that change of mind has been recorded, **When** an authorized agent requests a situation package whose purpose depends on that preference, **Then** the package includes the new statement as current and does not present the old dislike as a live preference.
3. **Given** two authorized agents with the same grant, **When** each requests a situation package with the same purpose after the change of mind, **Then** both packages agree on which statement is current.
4. **Given** the old statement is historical, **When** the person reviews their record in the Hub, **Then** they can still read the old statement and see that it was true in the past, not now.

---

### User Story 2 - The Person Sets When Something Is True (Priority: P2)

The person can say not only *what* is true, but *when*. They set an end: "I am vegetarian until June." Until that end, situation packages treat vegetarian as current. After that end, the statement is historical unless they renew it. They can also set a start in the future: "Starting in September I work from Lisbon" is not current before September; whatever was true before remains current until then. They do not have to invent a second statement to close an interval — ending validity is enough.

**Why this priority**: Change-of-mind (US1) covers the common reversal. Explicit windows are how temporary and scheduled truths work without pretending the person changed their mind or deleting history. This is independently valuable even if the reversal demo already passes.

**Independent Test**: Create a preference or factual statement with a stated start and end; request packages before the start, during the window, and after the end; verify current/historical resolution matches the window; verify a future-dated statement does not replace the previous current statement before its start.

**Acceptance Scenarios**:

1. **Given** a statement with a validity end in the future, **When** an authorized agent requests a situation package before that end, **Then** the statement is presented as current.
2. **Given** the same statement, **When** an authorized agent requests a situation package after that end and no successor current statement exists, **Then** the statement is not presented as current and remains available as historical.
3. **Given** a statement whose validity start is in the future and a different current statement on the same subject, **When** a package is assembled before that start, **Then** the future statement is not presented as current and the existing current statement remains current.
4. **Given** a statement with no explicit end, **When** packages are assembled, **Then** it remains current until the person ends it or records a change of mind that closes it.

---

### User Story 3 - The Person Can See Current Versus Historical (Priority: P3)

The person opens the Hub and can tell, for the statements this feature covers, which are current and which were true in the past — including when each interval started and (if ended) when it ended. Nothing about that resolution is invisible. If they correct a window ("that actually ended in March, not June"), the next situation package uses the corrected interval. A mistake ("I never disliked X; that was a typo") does not turn the wrong statement into historical truth; a change of mind does.

**Why this priority**: Explicit control is a constitution principle. If only agents see the current slice, the person cannot check that history was kept or that a window is wrong. It is P3 because US1/US2 can prove resolution without a dedicated review surface, but the feature is not honest to ownership until the person can inspect current vs historical.

**Independent Test**: Record a change of mind and an explicit window; open the Hub's review surface for those objects; verify each shows current vs historical and its interval; correct an end date; verify the next package respects the correction; record a "never true" correction and verify the false statement does not appear as historical truth.

**Acceptance Scenarios**:

1. **Given** current and historical statements exist, **When** the person reviews them in the Hub, **Then** each is labeled as current or historical and shows the interval during which it was (or is) true.
2. **Given** the person corrects a validity interval, **When** any later situation package is assembled, **Then** resolution uses the corrected interval.
3. **Given** the person corrects a statement as never having been true (a mistake, not a change of mind), **When** they review history and when later packages are assembled, **Then** that false statement is not presented as a historical truth and is not presented as current.

---

### Edge Cases

- A statement with no explicit validity interval is current from when it was asserted until it is ended or replaced by a change of mind; missing interval is not an error.
- Two current statements on the same subject whose intervals overlap: both appear with provenance as a conflict; the engine does not silently pick a winner or merge them.
- Validity end is before validity start: the Hub rejects the interval rather than inventing a current statement.
- Evaluation time for a package is a single instant for the whole package (the moment of the request, unless the request states another evaluation time); items are not mixed across different clocks.
- Retention (how long the record is kept) is not validity (when the statement was true). Ending validity MUST NOT delete the record. Retention expiry, if it fires, follows existing retention policy and is out of scope to redesign here.
- Imported content (email, calendar, plugin data) that appears to announce a change of mind is data, never an instruction: it MUST NOT close or open validity by itself.
- Grant and policy still bound every package: a historical personal statement MUST NOT appear in a work-scoped package, and omission notes still name withheld categories without revealing withheld content.
- SharedState remains a short-lived handoff with a time-to-live; it is not a validity interval and MUST NOT be reused as one. ActionIntent remains approval of an external action.
- Object version history (typo fix, field edit) is not automatically a new historical truth. Only a change of mind or an explicit validity interval creates current-vs-historical statements.
- A very large history of closed intervals is not inlined into every package; the package still returns the smallest sufficient current set. Historical review happens in the Hub, not by dumping every past interval into the agent package.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Durable preferences and factual claims MUST carry a validity interval: a start (when the statement became true of the person) and an optional end (when it stopped being true). A missing end means the statement is still current.
- **FR-002**: When the person records a change of mind on a subject that already has a current statement, the Hub MUST keep the earlier statement, end its validity at the change, and record the new statement as current. History MUST NOT disappear.
- **FR-003**: When the person (or an existing confirmation flow they approve) sets or edits a validity interval, the Hub MUST persist that interval on the statement and use it for all later resolution.
- **FR-004**: Context assembly (the E1 situation package) MUST resolve each candidate item as current or historical at a single evaluation time and MUST present only current items as live. Historical items MUST NOT be presented as live preferences, facts, or constraints.
- **FR-005**: The default evaluation time for assembly is the moment of the request. If the request states an evaluation time, resolution MUST use that time so a past (or scheduled) moment can be reconstructed without changing what is current now.
- **FR-006**: A statement whose interval does not contain the evaluation time MUST be treated as not current. A future-dated start MUST NOT make the statement current before that start.
- **FR-007**: Ending a validity interval MUST NOT delete the statement, MUST NOT by itself create a successor statement, and MUST NOT be treated as automatic forgetting.
- **FR-008**: Two or more statements that are current at the evaluation time on the same subject MUST both be included with provenance as a conflict. The engine MUST NOT silently discard one side or merge their meaning.
- **FR-009**: A correction that a statement was never true (mistake) MUST remove it from both current and historical truth. A change of mind MUST NOT be treated as a mistake, and a mistake MUST NOT be treated as a historical truth.
- **FR-010**: Validity is distinct from retention and from object version numbers. Retention policy, version concurrency, and audit remain as they are; this feature MUST NOT redefine them as validity.
- **FR-011**: Every current/historical resolution used in a situation package MUST remain bounded by the requesting agent's existing grant and policy. Historical status MUST NOT bypass scope. Omission notes still name withheld categories without revealing withheld content.
- **FR-012**: Assembly with temporal resolution MUST work entirely locally and offline, using only objects already in the vault. It MUST NOT trigger imports, external calls, or plugin syncs, and imported content MUST NOT open or close validity by itself.
- **FR-013**: The person MUST be able to see, in the Hub, which covered statements are current versus historical and the interval for each, and MUST be able to correct an interval through existing ownership flows.
- **FR-014**: Invalid intervals (end before start) MUST be rejected with a clear error and MUST NOT be stored as current truth.
- **FR-015**: Situation packages MUST still follow smallest-sufficient discipline: historical intervals are not inlined into the live package; they remain in the person's record for review.

### Key Entities

- **Validity Interval**: the period during which a statement was (or is) true of the person — a start, and an optional end. Distinct from retention (how long the Hub keeps the record) and from object version (edit concurrency / typo history).
- **Current Statement**: a preference or factual claim whose interval contains the evaluation time. This is what situation packages present as live.
- **Historical Statement**: a preference or factual claim that was true for an interval that does not contain the evaluation time. It remains in the person's record and is inspectable; it is not live context.
- **Change of Mind**: a person-confirmed event that ends the current statement on a subject and records a new current statement, keeping the earlier one as historical.
- **Mistake Correction**: a person-confirmed event that a statement was never true; it is not added to historical truth.
- **Evaluation Time**: the instant used to classify statements as current or historical for one situation package (default: now).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After the person records "I didn't like X" and later "I now like X," 100% of situation packages issued afterward for a purpose that depends on that preference present the new statement as current and 0% present the old dislike as a live preference.
- **SC-002**: After that change of mind, the person can retrieve the old statement as historical in 100% of Hub review checks; it is never missing because it was overwritten.
- **SC-003**: For a statement with an explicit end, 100% of packages issued before the end (and after the start) treat it as current, and 100% of packages issued after the end treat it as not current.
- **SC-004**: In the isolation test (personal + work record, two scoped grants), 0 historical or current items cross scope, including after a change of mind on a personal preference.
- **SC-005**: When two current statements on the same subject overlap at the evaluation time, 100% of issued packages include both with provenance as a conflict, and 0 packages silently drop or merge one side.
- **SC-006**: In a paired fixture, 100% of "never true" mistake corrections stay out of historical truth and out of live packages, and 100% of change-of-mind pairs keep the earlier statement as historical.
- **SC-007**: Temporal resolution does not require network access. On the same personal-scale vault used for E1, a situation package still completes without a wait the person would notice beyond what they already accept for E1 (target: still within two seconds).

## Assumptions

- This feature depends on E1 (Context Engine). Situation packages, grants, citations, omissions, and audit of issuances already exist; E2 adds validity and filters assembly. It does not reopen 001–003 as epics.
- Covered objects are preferences and factual claims (memories that state something about the person). Project/goal/commitment *status* lifecycles stay as they are. SharedState TTL and ActionIntent approvals are unchanged and not reused as validity.
- Default evaluation time is now. Stating an evaluation time on the request is in scope so history is usable, not only stored; it is not a new product surface beyond the existing context request.
- The person records change of mind and intervals through existing Hub confirmation/edit flows (including accepting an agent proposal). Agents still propose; they do not silently write canonical validity.
- No semantic merge: overlapping current statements are conflicts, not a blended preference. Automatic forgetting, decay, or "context health" cleanup is out of scope.
- Time zones: the person's profile time zone is used to interpret dates they enter; a package uses one evaluation instant so resolution is consistent.
- Existing object version history continues to store edits of the same record. This feature does not require treating every version as a historical truth.
- Personal Intelligence (inferring that a preference expired from email or patterns) and Personal Agency remain horizon items.
- E3 (operational project state / situation intent) is out of scope; validity does not invent those primitives.
