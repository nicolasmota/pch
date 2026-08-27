# Feature Specification: Context Quality Evaluation

**Feature Branch**: `010-context-eval`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "E6 — Avaliação de Qualidade de Contexto (docs/ROADMAP.md). We do not yet measure whether the slice is correct, fresh, precise, or cheap. Result: a small set of cases — killer demo; temporal conflict; context isolation; runtime switch. Metrics: context retrieval accuracy; context precision; freshness; conflict resolution; portability; user correction rate; context assembly cost. In scope: harness; fixed cases; observable criteria. Out of scope: public benchmark; token optimization as a product. Depends on E1; stronger with E2 and E5."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The Person Can See Whether the Trip Package Is Right (Priority: P1)

A person (or the person working with a coding agent on this Hub) wants to know if the situation package for the Europe trip is actually selecting the trip, citing live goals, and staying cheap enough. They run a local evaluation on the four fixed cases. The killer-demo case reports whether the trip was retrieved accurately and at what assembly cost. They do not publish a leaderboard.

**Why this priority**: This is the E6 result. Without a named case and numbers, “quality” is a feeling.

**Independent Test**: Run the local harness. Killer-demo case: trip purpose selects Europe Trip; assembly cost is reported. Fail if the package names the wrong project or omits the cost.

**Acceptance Scenarios**:

1. **Given** a vault seeded with the Europe trip, **When** the killer-demo case runs with purpose “continue planning the trip,” **Then** retrieval accuracy is a pass only if that trip is the situation.
2. **Given** that run, **When** the report is produced, **Then** it includes assembly cost as an observable number (not “felt fast”).
3. **Given** the harness, **When** it finishes, **Then** results stay on the person’s machine — not a public benchmark.

---

### User Story 2 - Freshness, Conflict, and Correction Are Visible (Priority: P2)

The same report covers: a preference that changed over time (freshness); two live preferences that collide (conflict resolution); the person dropping London (correction). The package after correction must not present London as the live destination choice.

**Why this priority**: E2 already stores validity; E6 makes those behaviors **scored**, not only unit-tested in isolation.

**Independent Test**: Temporal-conflict case: historical vs current preference; conflict pair listed when two current values share a key; after the person corrects (drop London), correction score is a pass only if the next package reflects it.

**Acceptance Scenarios**:

1. **Given** a preference that was true then superseded, **When** the freshness check asks as-of the old time vs now, **Then** only the then-true value is current at that time and the live value is current now.
2. **Given** two current preferences with the same key, **When** the package is assembled, **Then** the conflict is listed (not silently dropped).
3. **Given** the person records that London is dropped, **When** the next package is assembled, **Then** the correction is counted as applied (London is not the live chosen destination).

---

### User Story 3 - Isolation and Switching Runtime Are Scored (Priority: P3)

The harness includes context isolation (work-scoped assistant does not see the personal trip) and runtime switch (two real-use connections agree; revoke does not erase the trip). Precision fails if personal titles leak into the work package. Portability fails if the two packages disagree.

**Why this priority**: E1 isolation and E5 switch already exist; E6 puts them on the same scorecard as the killer demo.

**Independent Test**: Isolation case: 0 personal trip titles/ids in the work package. Runtime-switch case: two assistants agree; after revoke, trip objects remain.

**Acceptance Scenarios**:

1. **Given** a work-scoped assistant, **When** isolation runs, **Then** precision is a pass only if the personal trip is absent from that package.
2. **Given** two real-use connections with the same grant, **When** portability runs, **Then** it is a pass only if situation packages agree.
3. **Given** one connection is revoked, **When** Hub objects are listed, **Then** the trip is still there.

---

### Edge Cases

- Public leaderboard or uploaded scores are out of scope; refuse rather than add a hosted bench.
- Token-count optimization as a product is out of scope; assembly cost is time (and maybe item counts), not a tokenizer race.
- Closed chapters 001–003 are not reopened; this is a child spec that **scores** E1–E5 behavior.
- Personal Intelligence / Agency stay horizon.
- Empty vault: killer-demo case fails retrieval accuracy rather than inventing a trip.
- Coding agent is not a Hub client; the harness uses a temporary local vault in tests/CLI, not the person’s `~/.pch` unless they opt in.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A local evaluation harness MUST run four fixed cases: killer demo, temporal conflict, isolation, runtime switch.
- **FR-002**: The report MUST include: retrieval accuracy, precision (isolation), freshness, conflict resolution, portability, user correction, assembly cost.
- **FR-003**: Each metric MUST be observable from the situation package or from timed assembly — not from model self-report.
- **FR-004**: Results MUST remain local (stdout and/or a file the person chose). The Hub MUST NOT publish a public benchmark.
- **FR-005**: The harness MUST NOT treat token minimization as a scored product goal.
- **FR-006**: Isolation and portability cases MUST reuse grant and pairing rules already in the Hub (no weaker test doubles that skip policy).
- **FR-007**: The person MUST be able to run the harness from the existing CLI without a cloud account.

### Key Entities

- **Eval case**: a named scenario with a fixture, a purpose (or grant), and a pass/fail.
- **Eval report**: local document with per-case outcomes and the seven metrics.
- **Situation package**: the existing E1 contract the metrics read; not a new package format.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of killer-demo runs that seed Europe Trip report retrieval accuracy pass iff the package situation is that trip.
- **SC-002**: 100% of isolation runs report precision pass iff 0 personal trip titles/ids appear in the work-scoped package.
- **SC-003**: Freshness: 100% of temporal cases distinguish then-true vs live preference via as-of vs now.
- **SC-004**: Conflict: 100% of dual-current same-key cases list a conflict on the package.
- **SC-005**: Correction: after drop-London, 100% of subsequent packages do not present London as the live chosen destination.
- **SC-006**: Portability: two same-grant assistants agree in 100% of switch-case trials; revoke deletes 0 trip objects.
- **SC-007**: Assembly cost is reported as a duration for the killer-demo package; the case fails if assembly exceeds the existing 2 s budget.

## Assumptions

- Depends on E1–E5 behavior already in the Hub. This epic scores it; it does not reopen those epics.
- CLI lives in pcl-sdk beside `loop` and `mcp-bridge`.
- Default harness vault is ephemeral (temp dir) so running eval does not touch `~/.pch` unless the person passes a data dir later (out of this spec’s required path).
- 006 (dev loop) is tooling; this spec is product epic E6.
- Horizon items stay out of scope. No public benchmark.
