---

description: "Task list for Hub Plugin Framework & Marketplace"
---

# Tasks: Hub Plugin Framework & Marketplace

**Input**: Design documents from `/specs/003-hub-plugin-marketplace/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included — SC-001 and SC-003…SC-008 demand deterministic suites (migration, audit attribution, adversarial containment, package integrity, kill-switch, offline).

**Organization**: Tasks are grouped by user story so each story is an independently testable increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete sibling tasks)
- **[Story]**: US1 (plugin boundary + connector migration), US2 (developer kit + side-load), US3 (marketplace)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Directories, pytest markers, and bundled-plugin layout

- [x] T001 Create `packages/pcl-server/src/pcl_server/plugins/`, `packages/pcl-server/src/pcl_server/marketplace/`, `packages/pcl-sdk/src/pcl_sdk/plugin_runtime/`, `plugins/{google-calendar,gmail,example-rss}/`, and test dirs `packages/pcl-core/tests/plugins/`, `packages/pcl-server/tests/plugins/`, `packages/pcl-server/tests/marketplace/`, `packages/pcl-sdk/tests/plugin_kit/`
- [x] T002 [P] Register pytest marker `plugins` in root `pyproject.toml` alongside existing markers
- [x] T003 [P] Add a signed local catalog fixture (test Ed25519 key + `catalog.json` + tampered package) in `packages/pcl-server/tests/marketplace/fixtures/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schema, grants, protocol, and enforcement every story needs

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Implement `PluginManifest`, `ProducesPermission`, `PluginInstallation` models and lifecycle states in `packages/pcl-core/src/pcl_core/schema/plugin.py` and register `plugin` in `packages/pcl-core/src/pcl_core/schema/__init__.py`
- [x] T005 [P] Add audit kinds `plugin.install/consent/lifecycle/sync/denied/killswitch` and `marketplace.catalog_check` in `packages/pcl-core/src/pcl_core/schema/audit.py`
- [x] T006 Extend policy for principal type `plugin` (manifest-derived produce/host/schedule grant, deny undeclared writes) in `packages/pcl-core/src/pcl_core/policy.py` with unit tests in `packages/pcl-core/tests/plugins/test_plugin_grant.py`
- [x] T007 Add Hub service surface: create/get/list/patch plugin installations, consent grant, secret/state kv helpers (`plugin_secret:` / `plugin_state:`), provenance stamp `plugin:{id}` in `packages/pcl-core/src/pcl_core/service.py` with tests in `packages/pcl-core/tests/plugins/test_plugin_objects.py`
- [x] T008 Exclude `plugin_secret:*` and `plugin_state:*` kv entries from PCA export in `packages/pca/src/pca/` with test in `packages/pca/tests/test_plugin_secret_exclusion.py`
- [x] T009 Implement Plugin Host Protocol v1 dispatcher (JSON-RPC over stdio, capability methods, error codes) in `packages/pcl-server/src/pcl_server/plugins/protocol.py`
- [x] T010 Implement manifest enforcement (object types, hosts, payload/item caps, 3-denial abort) in `packages/pcl-server/src/pcl_server/plugins/enforcement.py`
- [x] T011 Implement mediated egress `hub.http.fetch` (https-only, exact host allowlist, size/time caps, redirect re-check) in `packages/pcl-server/src/pcl_server/plugins/egress.py`
- [x] T012 Implement plugin supervisor (spawn, timeout kill, optional `bwrap`/`unshare` sandbox, reduced-isolation flag) in `packages/pcl-server/src/pcl_server/plugins/host.py`
- [x] T013 Implement stdlib-only runtime shim (`hub.items/state/secrets/http/log/progress/oauth`) in `packages/pcl-sdk/src/pcl_sdk/plugin_runtime/__init__.py`

**Checkpoint**: A plugin process can be spawned, mediated, denied, killed — without any first-party plugin yet

---

## Phase 3: User Story 1 - Extend My Hub With Plugins (Priority: P1) 🎯 MVP

**Goal**: Calendar and Gmail run as bundled plugins behind consent/lifecycle UI; upgrade of a 002 vault loses no data.

**Independent Test**: Quickstart Scenarios 1 + 2 — migrated connectors stay enabled and re-sync without duplicates; a new bundled plugin stays inert until consent; pause kills the run; purge tombstones only that plugin's objects.

### Tests for User Story 1 ⚠️ write first, watch them fail

- [x] T014 [P] [US1] Contract tests for plugins REST (`GET/POST /v1/plugins`, consent, enable/pause/disable, sync, DELETE purge) in `packages/pcl-server/tests/plugins/test_plugins_rest.py`
- [x] T015 [P] [US1] Host protocol + enforcement tests (upsert allowed type, deny undeclared type/host, timeout kill, 3-denial abort) in `packages/pcl-server/tests/plugins/test_host_protocol.py`
- [x] T016 [P] [US1] Migration test: populated 002-era vault → plugin installations, tokens remapped, `source_key` unchanged, zero duplicates after sync in `packages/pcl-server/tests/plugins/test_migration.py`
- [x] T017 [P] [US1] Adversarial containment tests (undeclared upsert, undeclared fetch, hang, crash isolation) in `packages/pcl-server/tests/plugins/test_adversarial.py`

### Implementation for User Story 1

- [x] T018 [P] [US1] Implement 002→plugin migration (`connector_account` → `plugin`, `connector_token:` → `plugin_secret:`, auto-consent, `source_key` preserved) in `packages/pcl-server/src/pcl_server/plugins/migrate.py` and invoke on Hub startup
- [x] T019 [P] [US1] Port Google Calendar sync to `plugins/google-calendar/` (`plugin.toml` + `src/sync.py` using only `pcl_sdk.plugin_runtime`)
- [x] T020 [P] [US1] Port Gmail sync to `plugins/gmail/` (`plugin.toml` + `src/sync.py` using only `pcl_sdk.plugin_runtime`)
- [x] T021 [US1] Add plugins REST router (`/v1/plugins` per `contracts/plugins-rest.md`) in `packages/pcl-server/src/pcl_server/rest/routers/plugins.py` and mount it
- [x] T022 [US1] Generalize scheduler to run enabled plugins by manifest schedule (keep 15m/60m cadences, per-plugin lock, catalog-check hook placeholder) in `packages/pcl-server/src/pcl_server/sync/scheduler.py`
- [x] T023 [US1] Add Plugins page (list, consent modal, lifecycle buttons, keep/purge removal, last-run) in `frontend/src/pages/Plugins.tsx` and route it from `frontend/src/App.tsx`
- [x] T024 [US1] Stop listing migrated connectors as built-in on `frontend/src/pages/Connections.tsx` / `frontend/src/pages/Connectors.tsx` (point to Plugins page)

**Checkpoint**: Existing calendar/email work as plugins; consent/pause/remove work from the UI

---

## Phase 4: User Story 2 - Build a Plugin Without Touching the Core (Priority: P2)

**Goal**: A developer scaffolds, validates, packs, and side-loads an import plugin using only the kit.

**Independent Test**: Quickstart Scenario 3 — `plugin new/dev/validate/pack` for `example-rss` (or a scaffolded clone), side-load shows unverified warning, items land with plugin provenance; validate rejects an undeclared host.

### Tests for User Story 2 ⚠️ write first, watch them fail

- [x] T025 [P] [US2] Kit tests: scaffold layout, validate pass/fail (undeclared host, non-stdlib import), pack produces `.pclplugin` + sha256 in `packages/pcl-sdk/tests/plugin_kit/test_plugin_kit.py`
- [x] T026 [P] [US2] Side-load contract test: `POST /v1/plugins` with package, consent preview includes unverified warning, sync imports artifacts in `packages/pcl-server/tests/plugins/test_sideload.py`

### Implementation for User Story 2

- [x] T027 [US2] Implement `pcl-sdk plugin new|dev|validate|pack` in `packages/pcl-sdk/src/pcl_sdk/plugin_kit.py` and wire subcommands in `packages/pcl-sdk/src/pcl_sdk/__main__.py`
- [x] T028 [US2] Write `plugins/example-rss/` (manifest + sync entry) and `plugins/README.md` (kit-only developer guide)
- [x] T029 [US2] Implement package install path (zip validate, sha256, unverified-source flag on consent) in `packages/pcl-server/src/pcl_server/plugins/package.py` and hook it from `plugins.py` router

**Checkpoint**: Third-party import plugin can be built and installed without reading Hub source

---

## Phase 5: User Story 3 - Discover and Install Plugins From a Marketplace (Priority: P3)

**Goal**: Signed static catalog, integrity-pinned install, permission-diff updates, withdrawn kill-switch, offline cache.

**Independent Test**: Quickstart Scenario 5 — browse fixture catalog, install, reject tampered zip, require re-consent on added host, pause on withdrawn, keep working offline.

### Tests for User Story 3 ⚠️ write first, watch them fail

- [x] T030 [P] [US3] Catalog verify/tamper/kill-switch/offline tests in `packages/pcl-server/tests/marketplace/test_catalog.py`
- [x] T031 [P] [US3] Marketplace REST contract tests (`GET catalog`, `POST refresh/install`, update preview + `ReconsentRequired`) in `packages/pcl-server/tests/marketplace/test_marketplace_rest.py`

### Implementation for User Story 3

- [x] T032 [US3] Implement catalog fetch, Ed25519 verify, kv cache, withdrawn handling in `packages/pcl-server/src/pcl_server/marketplace/catalog.py`
- [x] T033 [US3] Add marketplace REST router in `packages/pcl-server/src/pcl_server/rest/routers/marketplace.py` and mount it; wire 12h catalog check into `packages/pcl-server/src/pcl_server/sync/scheduler.py`
- [x] T034 [US3] Add Marketplace page (browse, publisher/verification/permissions before install, update banner, offline notice) in `frontend/src/pages/Marketplace.tsx` and route it from `frontend/src/App.tsx`

**Checkpoint**: Marketplace browse/install/update/kill-switch work against the signed catalog

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Docs, suite green, quickstart gates

- [x] T035 [P] Document plugin host, kit, and marketplace in `plugins/README.md` and point from root `README.md` if present
- [x] T036 Run `uv run pytest packages/pcl-core/tests/plugins/ packages/pcl-server/tests/plugins/ packages/pcl-server/tests/marketplace/ packages/pcl-sdk/tests/plugin_kit/` and `cd frontend && npm run build`; fix failures
- [x] T037 Validate Quickstart Scenarios 1–5 against a running Hub and record outcomes in `specs/003-hub-plugin-marketplace/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — MVP
- **US2 (Phase 4)**: Depends on Foundational; reuses US1 install/consent REST
- **US3 (Phase 5)**: Depends on Foundational; reuses US1/US2 package install path
- **Polish (Phase 6)**: Depends on the stories being delivered

### User Story Dependencies

- **User Story 1 (P1)**: After Foundational — no other story
- **User Story 2 (P2)**: After Foundational; independently testable via kit + side-load
- **User Story 3 (P3)**: After Foundational; independently testable via catalog fixture

### Parallel Opportunities

- T002/T003 after T001
- T005 parallel with T004
- T014–T017 after Phase 2
- T018–T020 after T014–T017 are written
- T025/T026 after US1 REST exists
- T030/T031 after package install path exists

---

## Parallel Example: User Story 1

```bash
# Tests first (after Phase 2):
Task: "Contract tests in packages/pcl-server/tests/plugins/test_plugins_rest.py"
Task: "Host protocol tests in packages/pcl-server/tests/plugins/test_host_protocol.py"
Task: "Migration test in packages/pcl-server/tests/plugins/test_migration.py"
Task: "Adversarial tests in packages/pcl-server/tests/plugins/test_adversarial.py"

# Then ports:
Task: "Port calendar plugin in plugins/google-calendar/"
Task: "Port gmail plugin in plugins/gmail/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup
2. Phase 2 Foundational
3. Phase 3 US1 (migrate Calendar/Gmail, Plugins UI)
4. Validate Quickstart 1+2

### Incremental Delivery

1. Foundation ready
2. US1 → plugins page + migrated connectors
3. US2 → kit + RSS example + side-load
4. US3 → marketplace + kill-switch
5. Polish + full pytest

---

## Notes

- [P] tasks = different files, no dependencies
- Plugin code must import only stdlib + `pcl_sdk.plugin_runtime`
- Keep `source_key` byte-identical during migration (SC-001)
- Nothing runs before consent (FR-003)
