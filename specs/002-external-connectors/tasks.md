---

description: "Task list for External Connectors (Real Agents, Calendar, Email)"
---

# Tasks: External Connectors (Real Agents, Calendar, Email)

**Input**: Design documents from `/specs/002-external-connectors/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included — the spec's success criteria (SC-002, SC-005…SC-008) demand deterministic suites, mirroring the 001 approach.

**Organization**: Tasks are grouped by user story so each story is an independently testable increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete sibling tasks)
- **[Story]**: US1 (real assistant), US2 (calendar), US3 (email)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Dependencies and test scaffolding for connector work

- [X] T001 Add `mcp`, `google-auth`, `google-auth-oauthlib`, `httpx` to the relevant `pyproject.toml` files (`packages/pcl-sdk` for mcp, `packages/pcl-server` for Google/httpx) and run `uv sync --all-packages`
- [X] T002 [P] Register pytest marker `connectors` in root `pyproject.toml` alongside existing `forbidden_context`/`perf` markers
- [X] T003 [P] Create Google API fake fixtures (httpx.MockTransport with recorded Calendar/Gmail response shapes, incremental-token behavior, 410 expiry) in `packages/pcl-server/tests/connectors/conftest.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Vault schema, object types, and policy plumbing every story needs

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add `source_key` TEXT column + unique partial index to `objects` (create-if-missing migration on startup) in `packages/pcl-core/src/pcl_core/vault/engine.py`
- [X] T005 [P] Implement `ConnectorAccount` model (provider, kind, selection, cadence_minutes, sync_cursor, last_sync, status lifecycle per data-model.md) in `packages/pcl-core/src/pcl_core/schema/connector.py`
- [X] T006 [P] Implement `Event` model (title, starts_at/ends_at, all_day, location, attendees, calendar_id, status) in `packages/pcl-core/src/pcl_core/schema/event.py`
- [X] T007 Extend email fields on Artifact (`kind="email"`: subject, sender, recipients, sent_at, body_text) in `packages/pcl-core/src/pcl_core/schema/memory.py` and register new types in `packages/pcl-core/src/pcl_core/schema/__init__.py` (`EntityType`, `TYPE_MODELS`)
- [X] T008 [P] Add audit kinds `connector.connected/disconnected/paused/sync` and `connection.recipe_issued` to `packages/pcl-core/src/pcl_core/schema/audit.py`
- [X] T009 Index event/email fields for FTS (`title`, `subject`, `body_text` in `_search_text`) in `packages/pcl-core/src/pcl_core/vault/objects.py` and map `event` → `memory.retrieve` in `_cap_for` in `packages/pcl-core/src/pcl_core/service.py`
- [X] T010 Add Hub service surface for connectors: create/get/list/patch connector objects, `source_key` upsert/tombstone helpers, encrypted token kv helpers under `connector_token:` prefix, in `packages/pcl-core/src/pcl_core/service.py` with unit tests in `packages/pcl-core/tests/test_connector_objects.py`
- [X] T011 Exclude `connector_token:*` kv entries from PCA export in `packages/pca/src/pca/` (export path) with test in `packages/pca/tests/test_token_exclusion.py` (SC-007)

**Checkpoint**: Vault knows connectors/events/email; tokens are storable and unexportable

---

## Phase 3: User Story 1 - Connect a Real AI Assistant (Priority: P1) 🎯 MVP

**Goal**: Cursor (primary target) answers real chat questions with cited vault context via a copy-paste MCP recipe; grants, refusals, revocation, and audit all hold.

**Independent Test**: Quickstart Scenario 1 — pair Cursor with the rendered `mcp.json` snippet, get a cited Atlas answer, get a refusal on finance, revoke and see the revocation error (SC-001…SC-003).

### Tests for User Story 1 ⚠️ write first, watch them fail

- [X] T012 [P] [US1] Contract tests for `GET /v1/catalog/assistants` and `POST /v1/connections/{id}/recipe` (supported/unsupported assistants, audit event emitted) in `packages/pcl-server/tests/contract/test_assistant_catalog.py`
- [X] T013 [P] [US1] MCP bridge conformance test driving stdio with the `mcp` SDK client against a temp Hub (tools/list parity, cited search round-trip, revocation error, unreachable-Hub error) in `packages/pcl-sdk/tests/test_mcp_bridge.py`

### Implementation for User Story 1

- [X] T014 [P] [US1] Implement assistant catalog + recipe templates (Cursor, Claude Code, Claude Desktop, ChatGPT per research R5) in `packages/pcl-server/src/pcl_server/pairing/catalog.py`
- [X] T015 [US1] Add `GET /catalog/assistants` and `POST /connections/{connection_id}/recipe` routes (owner-only, `connection.recipe_issued` audit) in `packages/pcl-server/src/pcl_server/rest/routers/connections.py`
- [X] T016 [US1] Implement MCP stdio bridge (static tool declarations per contracts/mcp-bridge.md, REST forwarding with bearer token, error mapping table, startup health check) in `packages/pcl-sdk/src/pcl_sdk/mcp_bridge.py`
- [X] T017 [US1] Wire `mcp-bridge` subcommand (env `PCH_TOKEN`/`PCH_BASE`, flag overrides) into `packages/pcl-sdk/src/pcl_sdk/__main__.py`
- [X] T018 [US1] Extend Connections page with assistant catalog picker and copy-to-clipboard recipe block in `frontend/src/pages/Connections.tsx`
- [X] T019 [US1] Validate Quickstart Scenario 1 end-to-end with Cursor on this machine and record outcome in `specs/002-external-connectors/quickstart.md`

**Checkpoint**: A real assistant uses the vault — the product's headline moment works

---

## Phase 4: User Story 2 - Calendar as a Context Source (Priority: P2)

**Goal**: Google Calendar connects via consent, syncs every 15 minutes into `private` `event` objects with provenance, and granted assistants answer schedule questions with citations.

**Independent Test**: Quickstart Scenario 2 — consent, first sync visible, "what's my week?" answered with event citations within 5 minutes, disconnect stops syncing (SC-004, SC-005).

### Tests for User Story 2 ⚠️ write first, watch them fail

- [X] T020 [P] [US2] Contract tests for connector lifecycle (`POST /v1/connectors` consent flow with mocked provider, `GET`, `PATCH` selection/cadence, `sync now` 409 on concurrent run, pause/resume, `DELETE` with/without purge) in `packages/pcl-server/tests/connectors/test_connector_lifecycle.py`
- [X] T021 [P] [US2] Sync correctness tests (dedup by `source_key` across double-sync, update-in-place version bump, provider deletion → tombstone, syncToken 410 → bounded full re-sync, `connector.sync` audit events) in `packages/pcl-server/tests/connectors/test_calendar_sync.py`

### Implementation for User Story 2

- [X] T022 [P] [US2] Implement installed-app OAuth (loopback redirect + PKCE, `calendar.readonly`/`gmail.readonly` scopes, encrypted token storage via T010 helpers) in `packages/pcl-server/src/pcl_server/sync/oauth.py`
- [X] T023 [P] [US2] Define `Connector` protocol (plan_sync/fetch/map/dedup, no network in pcl-core) in `packages/pcl-core/src/pcl_core/connectors/base.py`
- [X] T024 [US2] Implement Google Calendar sync (events.list + syncToken, recurrence flattened within window, map to `event` objects: private classification, imported authority, `source_key`) in `packages/pcl-core/src/pcl_core/connectors/google_calendar.py`
- [X] T025 [US2] Implement background scheduler (lifespan task, per-connector cadence + asyncio lock, reconnect_needed on auth failure) in `packages/pcl-server/src/pcl_server/sync/scheduler.py` and register it in `packages/pcl-server/src/pcl_server/rest/app.py`
- [X] T026 [US2] Implement connectors REST router per contracts/connectors-rest.md in `packages/pcl-server/src/pcl_server/rest/routers/connectors.py` and include it in `packages/pcl-server/src/pcl_server/rest/app.py`
- [X] T027 [US2] Add `type=event` + `from`/`to` range filtering to search in `packages/pcl-core/src/pcl_core/retrieval/search.py` and `packages/pcl-server/src/pcl_server/rest/routers/search.py`
- [X] T028 [US2] Build Connectors page (consent launch, calendar selection, sync status/last_sync, sync-now, pause, disconnect keep-or-purge dialog) in `frontend/src/pages/Connectors.tsx` and add the route in `frontend/src/App.tsx`
- [X] T029 [US2] Validate Quickstart Scenario 2 against a real Google account and record outcome in `specs/002-external-connectors/quickstart.md`

**Checkpoint**: The vault feeds itself; schedule questions work without hand-typed memories

---

## Phase 5: User Story 3 - Email as a Selective Context Source (Priority: P3)

**Goal**: Gmail imports only user-selected slices as `sensitive` email artifacts; the Hub extracts nothing; claims arrive solely as assistant proposals with message evidence.

**Independent Test**: Quickstart Scenario 3 — one label imported, preset-grant search gets redaction notice, sensitive-grant assistant's claim lands in Review citing messages, injection suite passes (SC-006, SC-008).

### Tests for User Story 3 ⚠️ write first, watch them fail

- [X] T030 [P] [US3] Selective import tests (empty selection rejected 422, only matching label/sender/range imported, sensitive default, attachments/HTML excluded) in `packages/pcl-server/tests/connectors/test_gmail_sync.py`
- [X] T031 [P] [US3] Policy tests: preset grant (private ceiling) search over email topics → withheld + redaction notice; sensitive-ceiling grant retrieves with citations (SC-006) in `packages/pcl-server/tests/connectors/test_email_ceiling.py`
- [X] T032 [P] [US3] Forbidden-context fixtures: prompt-injection payloads in event/message bodies → retrieval-as-data only, zero grant/policy/action changes (SC-008) in `packages/pcl-server/tests/forbidden_context/test_connector_injection.py`

### Implementation for User Story 3

- [X] T033 [US3] Implement Gmail sync (messages.list with label/sender/date query, historyId incremental with bounded fallback, text/plain extraction, map to sensitive email artifacts) in `packages/pcl-core/src/pcl_core/connectors/gmail.py`
- [X] T034 [US3] Enforce non-empty email selection at create/patch (422 per contract) in `packages/pcl-server/src/pcl_server/rest/routers/connectors.py`
- [X] T035 [US3] Add email selection editor (labels, senders, date range) to `frontend/src/pages/Connectors.tsx`
- [X] T036 [US3] Integration test: assistant proposes a claim citing email artifacts via `propose_memory`, proposal appears in review queue non-canonical (FR-017) in `packages/pcl-server/tests/connectors/test_email_claim_proposal.py`

**Checkpoint**: All three stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T037 [P] Regenerate OpenAPI contract via `make openapi` into `specs/001-personal-context-hub/contracts/openapi.json` and verify new routes appear
- [X] T038 [P] Update `README.md` (bridge usage, connector setup) and `Makefile` (`bridge` convenience target)
- [X] T039 Run `make lint` and `uv run pytest` full suite; fix regressions
- [X] T040 Execute all quickstart.md scenarios end-to-end and mark task checkboxes/outcomes in `specs/002-external-connectors/tasks.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)** → **Foundational (Phase 2)** → user stories
- **US1 (Phase 3)**: only needs Phase 2 (uses 001's existing pairing/tool facade) — pure MVP path
- **US2 (Phase 4)**: needs Phase 2; T022 (OAuth) and T025 (scheduler) also serve US3
- **US3 (Phase 5)**: needs T022/T025/T026 from US2 (shared OAuth/scheduler/router); otherwise independent
- **Polish (Phase 6)**: after desired stories complete

### Parallel Opportunities

- T002/T003 in parallel after T001; T005/T006/T008 in parallel after T004
- US1 is fully parallel to US2/US3 (different packages/files) once Phase 2 lands
- Within stories: both test tasks of each story run in parallel before implementation

## Implementation Strategy

**MVP first**: Phases 1–3 only, then stop and validate Scenario 1 with Cursor. That alone delivers the product's core promise. US2 next (daily utility), US3 last (highest sensitivity).
