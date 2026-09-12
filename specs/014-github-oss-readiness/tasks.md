# Tasks: GitHub Open-Source Readiness

**Input**: Design documents from `/specs/014-github-oss-readiness/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/oss-readiness.md, quickstart.md

**Tests**: Required (constitution + plan SC→test map). Write OSS tests FIRST; they MUST fail before the script/docs that satisfy them.

**Organization**: By user story (P1–P3).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1–US3 from spec.md
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Test package directory for OSS contract tests

- [ ] T001 Create `packages/pcl-sdk/tests/oss/` with `__init__.py` (empty)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Secrets deny-list checker + ignore alignment (SC-002) — blocks public flip safety

**⚠️ CRITICAL**: No user story docs work that claims SC-002 until this phase is green

### Tests for Foundational

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T002 [P] Secrets checker tests in `packages/pcl-sdk/tests/oss/test_secrets_check.py` (clean tree exit 0; tracked `.env` fails; tracked `.pch/` or `.pch-sim/` path fails; deny-list covers contract patterns)

### Implementation for Foundational

- [ ] T003 Implement `scripts/check_secrets.py` per `contracts/oss-readiness.md` deny-list (incl. Hub data dirs `.pch/` / `.pch-sim/`)
- [ ] T004 Add `check-secrets` target to `Makefile` invoking the script
- [ ] T005 Align `.gitignore` with deny-list (`pairing_token*`, `.pch/`, `.pch-sim/`, existing vault/env/oauth/mcp rules)

**Checkpoint**: `make check-secrets` exits 0 on clean tree; pytest secrets module green

---

## Phase 3: User Story 1 - Stranger opens the public repo (Priority: P1) 🎯 MVP

**Goal**: LICENSE, package license metadata, README front door, secrets hygiene visible

**Independent Test**: `uv run pytest packages/pcl-sdk/tests/oss/test_community_files.py packages/pcl-sdk/tests/oss/test_secrets_check.py -k "license or readme or secrets"` plus cold README walk (SC-001)

### Tests for User Story 1

- [ ] T006 [P] [US1] Community/license/README assertions in `packages/pcl-sdk/tests/oss/test_community_files.py` (LICENSE MIT markers; five pyprojects `license = "MIT"`; README answers four questions + links)

### Implementation for User Story 1

- [ ] T007 [P] [US1] Add root `LICENSE` (MIT full text)
- [ ] T008 [P] [US1] Set `license = "MIT"` on `packages/pcl-core/pyproject.toml`, `packages/pcl-server/pyproject.toml`, `packages/pcl-sdk/pyproject.toml`, `packages/pca/pyproject.toml`, `apps/hub-desktop/pyproject.toml`
- [ ] T009 [US1] Edit `README.md` for SC-001 front door (purpose, local-first/`~/.pch`, install + from-source pointer, MIT, links to Contributing/Security/CoC)

**Checkpoint**: Cold visitor can answer four README questions; SC-002/SC-003 license portion green

---

## Phase 4: User Story 2 - Contributor knows how to help safely (Priority: P2)

**Goal**: CONTRIBUTING + issue/PR templates

**Independent Test**: Follow CONTRIBUTING → `make install` (if needed), `make check-secrets`, `make lint`, `make test`; template warning tests pass

### Tests for User Story 2

- [ ] T010 [P] [US2] Extend `packages/pcl-sdk/tests/oss/test_community_files.py` for CONTRIBUTING presence/sections and template secrets warnings (SC-005)

### Implementation for User Story 2

- [ ] T011 [P] [US2] Write `CONTRIBUTING.md` (prerequisites, make install/test/lint/check-secrets, PR expectations, must-not-commit, loopback, imported-is-data, coding-agent-not-client)
- [ ] T012 [P] [US2] Add `.github/ISSUE_TEMPLATE/bug.yml` (+ optional `config.yml`) with secrets warning checkbox
- [ ] T013 [P] [US2] Add `.github/PULL_REQUEST_TEMPLATE.md` with summary, test/lint evidence, no-secrets confirmation

**Checkpoint**: Contributor path documented; templates warn against vault dumps

---

## Phase 5: User Story 3 - Security reports and community norms (Priority: P3)

**Goal**: SECURITY.md + CODE_OF_CONDUCT.md + PR CI

**Independent Test**: Docs present; `ci.yml` references lint/test/check-secrets; community file tests green

### Tests for User Story 3

- [ ] T014 [P] [US3] Extend `packages/pcl-sdk/tests/oss/test_community_files.py` for SECURITY, CoC, and `.github/workflows/ci.yml` gates

### Implementation for User Story 3

- [ ] T015 [P] [US3] Write `SECURITY.md` (supported versions, GitHub private reporting, in/out of scope)
- [ ] T016 [P] [US3] Write `CODE_OF_CONDUCT.md` (Contributor Covenant adaptation + enforcement contact)
- [ ] T017 [US3] Add `.github/workflows/ci.yml` (PR + push main: Node build as needed, uv, `make lint`, `make test`, `make check-secrets`)

**Checkpoint**: Community health complete; CI gates-only

---

## Phase 6: Polish & Delivery

- [ ] T018 Run quickstart.md rehearsal checklist; record SC-001 timed README walk notes in delivery evidence
- [ ] T019 Confirm diff scope is hygiene-only (SC-006); no VISION/ROADMAP product implement
- [ ] T020 Mark all tasks complete; `make check-secrets && make lint && make test`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup**: immediate
- **Foundational**: after Setup — BLOCKS claiming SC-002
- **US1**: after Foundational (README may land with US2/US3 links stubbed then filled)
- **US2 / US3**: after Foundational; can parallelize after US1 README skeleton if links updated once
- **Polish**: after US1–US3

### Parallel Opportunities

- T002 tests before T003–T005
- T007 / T008 parallel
- T011 / T012 / T013 parallel
- T015 / T016 parallel; T017 after Makefile target exists

### MVP

Complete Setup + Foundational + US1 → safe public front door + secrets check. Then US2/US3 before flip.
