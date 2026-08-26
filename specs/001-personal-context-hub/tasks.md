---
description: "Task list template for feature implementation"
---

# Tasks: Personal Context Hub (MVP)

**Input**: Design documents from `/specs/001-personal-context-hub/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/)

**Tests**: Included. Contracts mark REST, MCP, and PCA tests as **normative**, and SC-003 / SC-005 / SC-007 require deterministic automated suites.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

uv workspace layout from [plan.md](./plan.md): `apps/hub-desktop/`, `frontend/`, `packages/pcl-core/`, `packages/pcl-server/`, `packages/pca/`, `packages/pcl-sdk/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create uv workspace layout with packages `pcl-core`, `pcl-server`, `pca`, `pcl-sdk`, app `hub-desktop`, and `frontend/` per `specs/001-personal-context-hub/plan.md`
- [x] T002 Initialize Python 3.14 workspace in `pyproject.toml` and `uv.lock` with workspace members and `requires-python = ">=3.14"`
- [x] T003 [P] Add FastAPI, uvicorn, Pydantic v2, SQLAlchemy 2, Alembic, sqlcipher3, cryptography, keyring, pyrage, mcp, pywebview, pytest, schemathesis, playwright to workspace dependencies in `pyproject.toml`
- [x] T004 [P] Scaffold `frontend/package.json` with React 19 + Vite TypeScript app outputting to `packages/pcl-server/src/pcl_server/static/`
- [x] T005 [P] Configure Ruff + mypy in `pyproject.toml` and `ruff.toml` for the four Python packages
- [x] T006 [P] Configure pytest (`pytest.ini` or `[tool.pytest.ini_options]`) with markers `forbidden_context`, `perf`, `e2e`, and per-package `tests/` directories
- [x] T007 [P] Add `.gitignore` covering `.venv/`, `node_modules/`, vault files, `dist/`, and SQLCipher databases
- [x] T008 Write root `README.md` with Python 3.14 + uv + Node 22 prerequisites matching `specs/001-personal-context-hub/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 Implement universal metadata Pydantic envelope (id prefixes, classification, authority, retention, version) in `packages/pcl-core/src/pcl_core/schema/metadata.py`
- [x] T010 [P] Implement Person and ContextSpace models in `packages/pcl-core/src/pcl_core/schema/person.py` and `packages/pcl-core/src/pcl_core/schema/space.py`
- [x] T011 [P] Implement Grant and Capability closed-set models in `packages/pcl-core/src/pcl_core/schema/grant.py`
- [x] T012 Implement SQLCipher engine factory and Alembic env in `packages/pcl-core/src/pcl_core/vault/engine.py` and `packages/pcl-core/src/pcl_core/vault/migrations/`
- [x] T013 Implement OS-keychain vault-key storage with optional Argon2id passphrase in `packages/pcl-core/src/pcl_core/vault/keys.py`
- [x] T014 [P] Implement ChaCha20-Poly1305 content-addressed blob store in `packages/pcl-core/src/pcl_core/vault/blobs.py`
- [x] T015 Implement `object_versions` persistence and optimistic `If-Match` helpers in `packages/pcl-core/src/pcl_core/vault/versions.py`
- [x] T016 Implement hash-chained append-only audit ledger (same-transaction commit) in `packages/pcl-core/src/pcl_core/audit/ledger.py`
- [x] T017 Implement ABAC policy evaluator (`allow` / `redact` / `deny` / `require_approval`) in `packages/pcl-core/src/pcl_core/policy/evaluator.py`
- [x] T018 Create FastAPI app bound to `127.0.0.1` with `/v1` prefix and generated OpenAPI 3.1 in `packages/pcl-server/src/pcl_server/rest/app.py`
- [x] T019 [P] Implement bearer auth (owner token vs connection token) in `packages/pcl-server/src/pcl_server/rest/auth.py`
- [x] T020 [P] Implement RFC 9457 problem+json errors (`policy_denied`, `version_conflict`, `approval_required`, `revoked`, `not_found`, `validation_failed`) in `packages/pcl-server/src/pcl_server/rest/errors.py`
- [x] T021 Implement `Idempotency-Key` middleware and replay store in `packages/pcl-server/src/pcl_server/rest/idempotency.py`
- [x] T022 Implement `GET /v1/events/verify` hash-chain verification in `packages/pcl-server/src/pcl_server/rest/routers/events.py`
- [x] T023 Implement `uv run pcl-server --headless` entrypoint in `packages/pcl-server/src/pcl_server/__main__.py`
- [x] T024 Implement pywebview window + in-process FastAPI startup and keychain unlock in `apps/hub-desktop/src/hub_desktop/main.py`
- [x] T025 [P] Generate typed frontend OpenAPI client pipeline in `frontend/src/api/`
- [x] T026 [P] Add unit tests for metadata validation and policy evaluator in `packages/pcl-core/tests/test_metadata.py` and `packages/pcl-core/tests/test_policy.py`
- [x] T027 [P] Add unit tests for audit hash chain and version conflict in `packages/pcl-core/tests/test_audit.py` and `packages/pcl-core/tests/test_versions.py`
- [x] T028 Add vault integration tests using temp-dir SQLCipher databases in `packages/pcl-core/tests/test_vault.py`

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and Manage My Personal Context (Priority: P1) 🎯 MVP

**Goal**: A non-technical user installs the Hub, completes guided setup, and CRUD/searches profile, preferences, projects, goals, commitments, decisions, memories, and artifacts entirely locally and offline.

**Independent Test**: Clean machine → setup → create project Atlas with goals/commitments/decisions/memories → search → edit one memory → restart offline → data still present with citations and version history.

### Tests for User Story 1

> Write these tests FIRST and ensure they FAIL before implementation

- [x] T029 [P] [US1] Contract tests for `POST /v1/setup`, `GET /v1/spaces`, and context CRUD/search in `packages/pcl-server/tests/contract/test_setup_and_context.py`
- [x] T030 [P] [US1] Integration test for resumable setup and offline persistence in `packages/pcl-core/tests/test_setup_resume.py`
- [x] T031 [P] [US1] Playwright journey for setup + Atlas project + search + edit in `frontend/tests/us1_manage_context.spec.ts`

### Implementation for User Story 1

- [x] T032 [P] [US1] Implement Profile and Preference models in `packages/pcl-core/src/pcl_core/schema/profile.py` and `packages/pcl-core/src/pcl_core/schema/preference.py`
- [x] T033 [P] [US1] Implement Project, Goal, Commitment, Decision models in `packages/pcl-core/src/pcl_core/schema/project.py`
- [x] T034 [P] [US1] Implement Memory and Artifact models in `packages/pcl-core/src/pcl_core/schema/memory.py` and `packages/pcl-core/src/pcl_core/schema/artifact.py`
- [x] T035 [US1] Add Alembic tables for US1 entities, FTS5 virtual table, and tombstones in `packages/pcl-core/src/pcl_core/vault/migrations/`
- [x] T036 [US1] Implement vault CRUD with versioning, user_confirmed authority, and same-transaction audit writes in `packages/pcl-core/src/pcl_core/vault/objects.py`
- [x] T037 [US1] Implement FTS5 search + BM25/recency/authority ranking behind `Ranker` in `packages/pcl-core/src/pcl_core/retrieval/search.py`
- [x] T038 [US1] Implement citation assembly from `source_refs` in `packages/pcl-core/src/pcl_core/retrieval/citations.py`
- [x] T039 [US1] Implement resumable `POST /v1/setup` and `GET /v1/spaces` in `packages/pcl-server/src/pcl_server/rest/routers/setup.py`
- [x] T040 [US1] Implement owner CRUD routers for projects/goals/commitments/decisions in `packages/pcl-server/src/pcl_server/rest/routers/projects.py`
- [x] T041 [P] [US1] Implement owner CRUD routers for memories, artifacts, preferences, and profile in `packages/pcl-server/src/pcl_server/rest/routers/memories.py`
- [x] T042 [US1] Implement `GET /v1/{type}/{id}/versions` and correction/delete tombstone behavior (FR-007) in `packages/pcl-server/src/pcl_server/rest/routers/versions.py`
- [x] T043 [US1] Implement policy-filtered `GET /v1/search` returning citations and classification in `packages/pcl-server/src/pcl_server/rest/routers/search.py`
- [x] T044 [US1] Implement `GET /v1/projects/{id}/brief` with citations in `packages/pcl-server/src/pcl_server/rest/routers/briefs.py`
- [x] T045 [US1] Build guided setup page (resume/restart, no cloud account) in `frontend/src/pages/Setup.tsx`
- [x] T046 [P] [US1] Build projects/goals/commitments/decisions pages in `frontend/src/pages/Projects.tsx`
- [x] T047 [P] [US1] Build memories/artifacts/preferences pages with provenance and history in `frontend/src/pages/Memories.tsx`
- [x] T048 [US1] Build search results UI showing classification and sources in `frontend/src/pages/Search.tsx`
- [x] T049 [US1] Wire owner token + static UI serving in `packages/pcl-server/src/pcl_server/rest/app.py` and `frontend/src/api/client.ts`
- [x] T050 [US1] Package PyInstaller spec (NSIS/dmg skeleton) in `apps/hub-desktop/src/hub_desktop/packaging/`
- [x] T051 [US1] Add integration tests that search/edit survive process restart with networking disabled in `packages/pcl-server/tests/integration/test_offline.py`
- [x] T052 [US1] Add unit tests that user edits never silently revert in `packages/pcl-core/tests/test_memory_authority.py`

**Checkpoint**: User Story 1 is fully functional and testable with no agent connected

---

## Phase 4: User Story 2 - Connect an Agent With Scoped Access (Priority: P2)

**Goal**: Pair an agent via catalog or one-time link, apply a plain-language permission preset, serve purpose-bound context with citations/redactions, and revoke access immediately.

**Independent Test**: Pair one agent, grant read on project Atlas only, in-scope query returns cited context, out-of-scope query returns nothing, revoke → subsequent requests refused.

### Tests for User Story 2

- [x] T053 [P] [US2] REST contract tests for pairing, grants, manifests, and revoke (including unscoped 422) in `packages/pcl-server/tests/contract/test_connections.py`
- [x] T054 [P] [US2] MCP conformance tests for `search_personal_context` and `get_context_manifest` in `packages/pcl-server/tests/contract/test_mcp_context.py`
- [x] T055 [P] [US2] Seeded forbidden-context suite (SC-003, 100% block) in `packages/pcl-server/tests/forbidden_context/test_project_scope.py`
- [x] T056 [P] [US2] Playwright journey for catalog/link pairing + preset + revoke in `frontend/tests/us2_connect_agent.spec.ts`

### Implementation for User Story 2

- [x] T057 [P] [US2] Implement AgentConnection and ContextManifest models in `packages/pcl-core/src/pcl_core/schema/connection.py` and `packages/pcl-core/src/pcl_core/schema/manifest.py`
- [x] T058 [US2] Add Alembic tables for connections, grants, and manifests in `packages/pcl-core/src/pcl_core/vault/migrations/`
- [x] T059 [US2] Implement pairing link mint/redeem and hashed credentials in `packages/pcl-server/src/pcl_server/pairing/links.py`
- [x] T060 [US2] Implement grant service (presets, selectors, classification ceiling, expiry) in `packages/pcl-core/src/pcl_core/policy/grants.py`
- [x] T061 [US2] Implement context-manifest builder (purpose required, TTL, redaction notices) in `packages/pcl-core/src/pcl_core/retrieval/manifests.py`
- [x] T062 [US2] Implement revoke cascade (grants, manifests, sessions) in `packages/pcl-core/src/pcl_core/policy/revoke.py`
- [x] T063 [US2] Implement REST routers for connections, grants, and manifests in `packages/pcl-server/src/pcl_server/rest/routers/connections.py`
- [x] T064 [US2] Implement FastMCP server (Streamable HTTP loopback + stdio launcher) with session=connection identity in `packages/pcl-server/src/pcl_server/mcp/server.py`
- [x] T065 [US2] Implement MCP resources `pcl://spaces/{id}/profile`, `pcl://projects/{id}/brief`, `pcl://connection/self` in `packages/pcl-server/src/pcl_server/mcp/resources.py`
- [x] T066 [US2] Implement MCP tools `search_personal_context` and `get_context_manifest` in `packages/pcl-server/src/pcl_server/mcp/tools_context.py`
- [x] T067 [US2] Implement `pcl-sdk` pairing + MCP client helpers in `packages/pcl-sdk/src/pcl_sdk/client.py`
- [x] T068 [US2] Implement `uv run pcl-sdk demo-agent` reference client in `packages/pcl-sdk/src/pcl_sdk/demo_agent.py`
- [x] T069 [US2] Build Connections page (catalog, link, presets in plain language, revoke) in `frontend/src/pages/Connections.tsx`
- [x] T070 [US2] Build Grants/access summary page in `frontend/src/pages/Access.tsx`
- [x] T071 [US2] Add revocation timing test (SC-004: subsequent calls 401 revoked, manifests 410) in `packages/pcl-server/tests/integration/test_revoke.py`
- [x] T072 [US2] Add unit tests that unscoped manifest requests raise `validation_failed` in `packages/pcl-core/tests/test_manifest_purpose.py`

**Checkpoint**: User Stories 1 and 2 both work independently; one paired agent can read only granted context

---

## Phase 5: User Story 3 - Continuity Across Different Agents (Priority: P3)

**Goal**: Two independently implemented agents receive the same canonical, cited project brief; shareable TTL state is visible only when marked shared; replacing an agent does not lose context.

**Independent Test**: Pair two demo-agent instances with distinct credentials, both fetch Atlas brief, disconnect one, the other still works and SharedState marked `shared` is visible.

### Tests for User Story 3

- [x] T073 [P] [US3] Contract tests for `PUT/GET /v1/state/{key}` visibility rules in `packages/pcl-server/tests/contract/test_shared_state.py`
- [x] T074 [P] [US3] Two-runtime brief consistency test (SC-002) in `packages/pcl-server/tests/integration/test_two_agents.py`
- [x] T075 [P] [US3] Playwright journey pairing two agents and comparing briefs in `frontend/tests/us3_continuity.spec.ts`

### Implementation for User Story 3

- [x] T076 [US3] Implement SharedState model (TTL, visibility, never auto-promoted) in `packages/pcl-core/src/pcl_core/schema/state.py`
- [x] T077 [US3] Add SharedState table and expiry sweep in `packages/pcl-core/src/pcl_core/vault/state.py`
- [x] T078 [US3] Implement REST state routes in `packages/pcl-server/src/pcl_server/rest/routers/state.py`
- [x] T079 [US3] Implement MCP tools `set_shared_state` and `get_shared_state` in `packages/pcl-server/src/pcl_server/mcp/tools_state.py`
- [x] T080 [US3] Add a second independently implemented MCP client fixture (SDK vs raw HTTP) in `packages/pcl-sdk/tests/test_second_runtime.py`
- [x] T081 [US3] Ensure project brief is identical across connections (canonical object versions) in `packages/pcl-core/src/pcl_core/retrieval/briefs.py`
- [x] T082 [US3] Show shareable handoff state in the Hub UI in `frontend/src/pages/Handoff.tsx`

**Checkpoint**: Two agents share continuity without owning the vault

---

## Phase 6: User Story 4 - Review and Control Agent-Proposed Memories (Priority: P4)

**Goal**: Agents submit memory proposals with evidence; users accept/edit/reject; sensitive flags always require confirmation; contradictions against user_confirmed never silently overwrite.

**Independent Test**: Agent proposes three memories (normal, financial-flagged, contradicting user_confirmed); review queue handles each correctly; accepted memory has provenance; rejected never becomes canonical.

### Tests for User Story 4

- [x] T083 [P] [US4] REST contract tests for proposals accept/reject and conflicts in `packages/pcl-server/tests/contract/test_memory_proposals.py`
- [x] T084 [P] [US4] MCP conformance: `propose_memory` never auto-accepts `financial` in `packages/pcl-server/tests/contract/test_mcp_propose_memory.py`
- [x] T085 [P] [US4] Playwright review-queue journey in `frontend/tests/us4_memory_review.spec.ts`

### Implementation for User Story 4

- [x] T086 [P] [US4] Implement MemoryProposal and Conflict models in `packages/pcl-core/src/pcl_core/schema/proposal.py` and `packages/pcl-core/src/pcl_core/schema/conflict.py`
- [x] T087 [US4] Add proposal/conflict tables in `packages/pcl-core/src/pcl_core/vault/migrations/`
- [x] T088 [US4] Implement proposal pipeline (policy verdict, duplicate hash, subject_ref contradiction) in `packages/pcl-core/src/pcl_core/memory/pipeline.py`
- [x] T089 [US4] Enforce FR-015: any sensitivity flag blocks `auto_accepted` in `packages/pcl-core/src/pcl_core/memory/sensitivity.py`
- [x] T090 [US4] Implement REST proposal and conflict routers in `packages/pcl-server/src/pcl_server/rest/routers/proposals.py`
- [x] T091 [US4] Implement MCP tool `propose_memory` in `packages/pcl-server/src/pcl_server/mcp/tools_memory.py`
- [x] T092 [US4] Build review queue UI (content, evidence, confidence, accept/edit/reject) in `frontend/src/pages/ReviewQueue.tsx`
- [x] T093 [US4] Build conflict resolution UI in `frontend/src/pages/Conflicts.tsx`
- [x] T094 [US4] Prompt user to review derived memories whose sources were deleted in `packages/pcl-core/src/pcl_core/memory/orphans.py`
- [x] T095 [US4] Add tests that two concurrent contradictory proposals both stay non-canonical in `packages/pcl-core/tests/test_concurrent_proposals.py`
- [x] T096 [US4] Add tests that post-correction retrieval returns the new version in `packages/pcl-core/tests/test_correction_propagation.py`

**Checkpoint**: Memory integrity is user-controlled; inferences cannot silently win

---

## Phase 7: User Story 5 - Approve External Actions and Audit Everything (Priority: P5)

**Goal**: External actions require per-action approval; declined retries are recorded not executed; the audit timeline is plain-language, append-only, and complete.

**Independent Test**: Propose action → approve → executed; propose second → decline → nothing happens; replay idempotency key returns same intent; timeline shows the chain; `GET /v1/events/verify` passes.

### Tests for User Story 5

- [x] T097 [P] [US5] REST contract tests for intents, approvals, and idempotent replay in `packages/pcl-server/tests/contract/test_actions.py`
- [x] T098 [P] [US5] MCP conformance for `propose_action`, `check_action_status`, `request_approval` in `packages/pcl-server/tests/contract/test_mcp_actions.py`
- [x] T099 [P] [US5] SC-005 suite: every durable write/action has an audit event in `packages/pcl-server/tests/integration/test_audit_completeness.py`
- [x] T100 [P] [US5] Playwright approve/decline + timeline journey in `frontend/tests/us5_approvals.spec.ts`

### Implementation for User Story 5

- [x] T101 [P] [US5] Implement ActionIntent and Approval models in `packages/pcl-core/src/pcl_core/schema/action.py` and `packages/pcl-core/src/pcl_core/schema/approval.py`
- [x] T102 [US5] Add action/approval tables and unique `(connection_id, idempotency_key)` in `packages/pcl-core/src/pcl_core/vault/migrations/`
- [x] T103 [US5] Implement action-intent service (always `pending` in MVP, duplicate detection) in `packages/pcl-core/src/pcl_core/policy/actions.py`
- [x] T104 [US5] Implement REST intent/approval/result routers in `packages/pcl-server/src/pcl_server/rest/routers/actions.py`
- [x] T105 [US5] Implement MCP tools `propose_action`, `check_action_status`, `request_approval` in `packages/pcl-server/src/pcl_server/mcp/tools_actions.py`
- [x] T106 [US5] Implement `GET /v1/events` filtered timeline with `summary_human` (no raw conversation by default) in `packages/pcl-server/src/pcl_server/rest/routers/events.py`
- [x] T107 [US5] Implement MCP resource `pcl://audit/recent` (own events only) in `packages/pcl-server/src/pcl_server/mcp/resources.py`
- [x] T108 [US5] Build Approvals page (who, what, basis) in `frontend/src/pages/Approvals.tsx`
- [x] T109 [US5] Build Audit timeline page in `frontend/src/pages/Audit.tsx`
- [x] T110 [US5] Add tests that declined retries create a new flagged intent and never execute in `packages/pcl-core/tests/test_declined_retry.py`

**Checkpoint**: No external action without explicit approval; audit chain is complete and verifiable

---

## Phase 8: User Story 6 - Export and Re-import My Context (Priority: P6)

**Goal**: Export a full or filtered PCA v0 archive (age + zip + JSONL + schemas) that is readable without the Hub; import stages in quarantine with merge/replace/keep-separate; authority and lineage survive.

**Independent Test**: Export populated space → open with generic age+unzip → import into clean vault via staging → 100% typed objects, lineage, and policy labels match (SC-007).

### Tests for User Story 6

- [x] T111 [P] [US6] REST contract tests for export/stage/apply in `packages/pcl-server/tests/contract/test_export_import.py`
- [x] T112 [P] [US6] PCA round-trip fidelity suite (SC-007) in `packages/pca/tests/test_roundtrip.py`
- [x] T113 [P] [US6] Tests that archives open with age+unzip and integrity mismatches abort in `packages/pca/tests/test_format.py`
- [x] T114 [P] [US6] Playwright export/import staging journey in `frontend/tests/us6_portability.spec.ts`

### Implementation for User Story 6

- [x] T115 [P] [US6] Implement ExportRecord and ImportStaging models in `packages/pcl-core/src/pcl_core/schema/portability.py`
- [x] T116 [US6] Implement PCA writer (canonical JSON, schemas from Pydantic, exclude secrets/state) in `packages/pca/src/pca/export.py`
- [x] T117 [US6] Implement PCA reader (age decrypt, hash verify, quarantine staging) in `packages/pca/src/pca/import_.py`
- [x] T118 [US6] Implement merge/replace/keep_separate resolver preserving imported `authority` in `packages/pca/src/pca/resolve.py`
- [x] T119 [US6] Mark imported artifacts `untrusted` (FR-026) in `packages/pca/src/pca/untrusted.py`
- [x] T120 [US6] Implement REST export/import routers in `packages/pcl-server/src/pcl_server/rest/routers/portability.py`
- [x] T121 [US6] Add `uv run pca verify-roundtrip` CLI in `packages/pca/src/pca/cli.py`
- [x] T122 [US6] Build Export page (filters + passphrase) in `frontend/src/pages/Export.tsx`
- [x] T123 [US6] Build Import staging/conflict UI in `frontend/src/pages/Import.tsx`
- [x] T124 [US6] Add tests that project-filtered exports contain zero out-of-scope records and no credentials in `packages/pca/tests/test_filters_and_secrets.py`

**Checkpoint**: Portability is proven; ownership does not depend on a running Hub

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T125 [P] Keyboard and screen-reader pass on setup, permissions, review, and audit pages in `frontend/src/` (SC-010)
- [x] T126 [P] Seed 100k memories/artifact refs and assert search < 1 s and manifest p95 < 500 ms in `packages/pcl-core/tests/perf/test_search_scale.py` (SC-009)
- [x] T127 [P] Treat imported content as non-authoritative (prompt-injection fixtures) in `packages/pcl-core/tests/test_untrusted_content.py`
- [x] T128 Schemathesis sweep of the generated OpenAPI document in `packages/pcl-server/tests/contract/test_schemathesis.py`
- [x] T129 Confirm MCP tools emit audit events with actor = connection id in `packages/pcl-server/tests/integration/test_mcp_audit.py`
- [x] T130 [P] PyInstaller Windows/macOS packaging and Linux AppImage best-effort in `apps/hub-desktop/src/hub_desktop/packaging/`
- [x] T131 [P] Document adapter authoring in `packages/pcl-sdk/README.md`
- [x] T132 Run the six quickstart scenarios in `specs/001-personal-context-hub/quickstart.md` and record results
- [x] T133 [P] Generate OpenAPI JSON artifact from the running app into `specs/001-personal-context-hub/contracts/openapi.json`
- [x] T134 Redact sensitive fields before disclosure and include redaction notices (FR-013) coverage in `packages/pcl-core/tests/test_redaction.py`
- [x] T135 Code cleanup: remove unused stubs, lock uv dependencies, and verify `uv run pytest` is green from repo root

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - Sequential in priority order is the default (P1 → P6)
  - US2–US5 assume pairing/MCP from US2; US3–US5 should not start until US2 pairing works
  - US6 can start after US1 (portability of user-owned objects) but import of agent-inferred memories needs US4 authority fields
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: After Foundational — no other story dependencies. **MVP slice.**
- **User Story 2 (P2)**: After Foundational; uses US1 objects as grant targets. Independently testable with seeded Atlas data.
- **User Story 3 (P3)**: After US2 pairing/MCP identity. Independently testable with two demo-agent processes.
- **User Story 4 (P4)**: After US2 (agents submit proposals). Independently testable against the review queue.
- **User Story 5 (P5)**: After US2. Independently testable with action intents; audit ledger already exists from Phase 2.
- **User Story 6 (P6)**: After US1 for export of typed objects; after US4 if testing imported `agent_inferred` authority. Independently testable via `pca verify-roundtrip`.

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before migrations/services
- Services before REST/MCP endpoints
- Endpoints before UI
- Story complete before moving to next priority (unless staffed in parallel after US2)

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- Foundational models (T010, T011), blob store (T014), auth/errors (T019, T020), frontend client (T025), and unit tests (T026, T027) can run in parallel after T009/T012 land
- Once Foundational completes, US1 is the critical path; after US1+US2, US3/US4/US5 can proceed in parallel
- US6 PCA package work (T116–T118) can overlap with US5 if US1 objects exist
- All tests marked [P] within a story can be authored in parallel

---

## Parallel Example: User Story 1

```bash
# Tests first (failing):
Task: "Contract tests in packages/pcl-server/tests/contract/test_setup_and_context.py"
Task: "Setup resume integration in packages/pcl-core/tests/test_setup_resume.py"
Task: "Playwright journey in frontend/tests/us1_manage_context.spec.ts"

# Models in parallel:
Task: "Profile/Preference in packages/pcl-core/src/pcl_core/schema/profile.py"
Task: "Project family in packages/pcl-core/src/pcl_core/schema/project.py"
Task: "Memory/Artifact in packages/pcl-core/src/pcl_core/schema/memory.py"
```

## Parallel Example: User Story 2

```bash
# After pairing models exist:
Task: "REST contract tests in packages/pcl-server/tests/contract/test_connections.py"
Task: "MCP conformance in packages/pcl-server/tests/contract/test_mcp_context.py"
Task: "Forbidden-context suite in packages/pcl-server/tests/forbidden_context/test_project_scope.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: setup → Atlas project → search → edit → offline restart
5. Demo the Hub as a private context notebook before any agent work

### Incremental Delivery

1. Setup + Foundational → encrypted local service + desktop shell
2. US1 → inspectable personal context (MVP)
3. US2 → first paired agent with scoped access
4. US3 → two-runtime continuity
5. US4 → memory proposals and conflicts
6. US5 → approvals and audit timeline
7. US6 → portable exit
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. After Foundational: one developer on US1 (critical path)
3. After US1+US2:
   - Developer A: US3 continuity
   - Developer B: US4 memory pipeline
   - Developer C: US5 actions/audit UI
   - Developer D: US6 PCA package

---

## Notes

- [P] tasks = different files, no dependencies on incomplete sibling tasks
- [Story] label maps task to spec user stories US1–US6
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate the story independently
- Vector index, sync, A2A, org spaces, and named OpenClaw/Hermes adapters are out of scope (spec assumptions)
