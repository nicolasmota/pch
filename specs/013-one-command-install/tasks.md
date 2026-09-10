---
description: "Task list for One-Command Install"
---

# Tasks: One-Command Install

**Input**: Design documents from `/specs/013-one-command-install/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/install.md, quickstart.md

**Tests**: Required (constitution + plan SC→test map). Write tests FIRST; they MUST fail before the code that satisfies them. `packages/pcl-sdk/tests/test_module_entry.py` is a regression guard (F6c), not red-first.

**Organization**: By user story (P1–P3).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1–US3 from spec.md
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Workspace naming so the published distribution can be `personal-context-hub`

- [x] T001 Rename root `pyproject.toml` `name` to `pch-workspace` and set `[tool.uv] package = false`
- [x] T002 [P] Set version `0.2.0` and `==0.2.0` sibling pins on `packages/pcl-core/pyproject.toml`, `packages/pcl-server/pyproject.toml`, `packages/pcl-sdk/pyproject.toml`, `packages/pca/pyproject.toml` (pca distribution name `pcl-pca`), `apps/hub-desktop/pyproject.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Cipher probe, key-storage report, schema_version, packaged app factory flags

**⚠️ CRITICAL**: No user story work until this phase is complete

### Tests for Foundational

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T003 [P] Cipher probe tests in `packages/pcl-core/tests/test_cipher_available.py`
- [x] T004 [P] Key-storage tests in `packages/pcl-core/tests/test_key_storage.py`
- [x] T005 [P] Schema migration tests in `packages/pcl-core/tests/test_upgrade_preserves_vault.py` plus fixture via `scripts/make_prev_vault.py` → `packages/pcl-core/tests/fixtures/vault_prev.sqlite`
- [x] T006 [P] Sim-disabled contract tests in `packages/pcl-server/tests/contract/test_sim_disabled.py`
- [x] T007 [P] Setup status field tests in `packages/pcl-server/tests/contract/test_setup_status_fields.py`

### Implementation for Foundational

- [x] T008 Add `cipher_available()` in `packages/pcl-core/src/pcl_core/vault/engine.py`
- [x] T009 Add `key_storage(data_dir)` in `packages/pcl-core/src/pcl_core/vault/keys.py`
- [x] T010 Add `kv.schema_version` and ordered `MIGRATIONS` in `packages/pcl-core/src/pcl_core/vault/engine.py`
- [x] T011 Extend `Hub.setup_status()` with `encrypted` and `key_storage` in `packages/pcl-core/src/pcl_core/service.py`
- [x] T012 Add `sim_enabled` and `catalog_refresh` to `create_app` / `dev_app` / lifespan wiring in `packages/pcl-server/src/pcl_server/rest/app.py`
- [x] T013 Skip `refresh_catalog` when `catalog_refresh` is False in `packages/pcl-server/src/pcl_server/sync/scheduler.py`
- [x] T014 Router-level sim 404 (including `target=everyday`) and lazy `_sim_hub` in `packages/pcl-server/src/pcl_server/rest/routers/sim.py`
- [x] T015 Expose `encrypted` / `key_storage` on `GET /v1/setup` in `packages/pcl-server/src/pcl_server/rest/routers/setup.py`

**Checkpoint**: Foundation ready — packaged flags exist; cipher probe is import-only

---

## Phase 3: User Story 1 - Install and open the Hub with one command (Priority: P1) 🎯 MVP

**Goal**: `uvx personal-context-hub` launches the guided setup with bundled UI, encrypted vault, loopback only, offline after pin.

**Independent Test**: `uv run pytest apps/hub-desktop/tests/test_cli_dispatch.py apps/hub-desktop/tests/test_entry_refuses_plaintext.py apps/hub-desktop/tests/test_pin.py apps/hub-desktop/tests/test_doctor.py apps/hub-desktop/tests/test_first_launch_writes_nothing.py apps/hub-desktop/tests/test_offline_guard.py apps/hub-desktop/tests/test_packaged_entry_never_plain.py apps/hub-desktop/tests/test_readme_install_section.py packages/pcl-server/tests/contract/test_setup_status_fields.py packages/pcl-server/tests/contract/test_sim_disabled.py`

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T016 [P] [US1] CLI dispatch / loopback / no-prompt / reattach tests in `apps/hub-desktop/tests/test_cli_dispatch.py`
- [x] T017 [P] [US1] `is_loopback` table in `apps/hub-desktop/tests/test_launch.py`
- [x] T018 [P] [US1] Plaintext refusal tests in `apps/hub-desktop/tests/test_entry_refuses_plaintext.py`
- [x] T019 [P] [US1] Pin + re-exec tests in `apps/hub-desktop/tests/test_pin.py`
- [x] T020 [P] [US1] Doctor tests in `apps/hub-desktop/tests/test_doctor.py`
- [x] T021 [P] [US1] First-launch writes-nothing tests in `apps/hub-desktop/tests/test_first_launch_writes_nothing.py`
- [x] T022 [P] [US1] Packaged Engine never-plain tests in `apps/hub-desktop/tests/test_packaged_entry_never_plain.py`
- [x] T023 [P] [US1] Offline 001/004 guard tests in `apps/hub-desktop/tests/test_offline_guard.py`
- [x] T024 [P] [US1] README install-section tests in `apps/hub-desktop/tests/test_readme_install_section.py`
- [x] T025 [P] [US1] Release-gate self-test in `apps/hub-desktop/tests/test_check_release.py`
- [x] T026 [P] [US1] Setup key-storage UI test in `frontend/tests/setup_key_storage.spec.ts`

### Implementation for User Story 1

- [x] T027 [US1] Rename `apps/hub-desktop/pyproject.toml` distribution to `personal-context-hub` with scripts `personal-context-hub` and `pch` → `hub_desktop.cli:main`; keep `hub-desktop` → `hub_desktop.main:main`
- [x] T028 [US1] Hatch `artifacts = ["src/pcl_server/static/**"]` in `packages/pcl-server/pyproject.toml`
- [x] T029 [US1] Implement `hub_desktop/pin.py` (`running_from_uv_tool`, `ensure_pinned`, `pinned_interpreter`, `reexec_into_pinned`) in `apps/hub-desktop/src/hub_desktop/pin.py`
- [x] T030 [US1] Implement `packaged_app`, `require_cipher_or_exit`, argparse verbs (launch/serve/doctor/smoke/upgrade/uninstall/version) in `apps/hub-desktop/src/hub_desktop/cli.py`
- [x] T031 [US1] Extract `launch_hub` from `apps/hub-desktop/src/hub_desktop/main.py`; add `is_loopback` and WebKit/WebView2 probe in `apps/hub-desktop/src/hub_desktop/launch.py`
- [x] T032 [US1] Implement doctor report in `apps/hub-desktop/src/hub_desktop/doctor.py`
- [x] T033 [US1] Loopback host guard in `packages/pcl-server/src/pcl_server/__main__.py`
- [x] T034 [US1] Setup screen key-storage sentence in `frontend/src/pages/Setup.tsx` and `frontend/src/api/types.ts`
- [x] T035 [US1] `scripts/check_release.py` and Makefile `release` / `smoke` targets in `scripts/check_release.py` and `Makefile`
- [x] T036 [US1] README Install section per `contracts/install.md` §10 (include uv one-liner) in `README.md`

**Checkpoint**: US1 independently testable; `packaged_app` is the single factory

---

## Phase 4: User Story 2 - Pair an assistant from anywhere (Priority: P2)

**Goal**: Recipes use the installed interpreter and actual port; MCP `tools/call` from `/tmp` reaches the Hub.

**Independent Test**: `uv run pytest packages/pcl-server/tests/contract/test_assistant_catalog.py packages/pcl-server/tests/contract/test_recipe_from_anywhere.py packages/pcl-sdk/tests/test_module_entry.py`

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T037 [P] [US2] Catalog recipe shape tests in `packages/pcl-server/tests/contract/test_assistant_catalog.py`
- [x] T038 [P] [US2] Connect-from-tmp MCP `tools/call` tests in `packages/pcl-server/tests/contract/test_recipe_from_anywhere.py`
- [x] T039 [P] [US2] Regression `python -m pcl_sdk mcp-bridge --help` in `packages/pcl-sdk/tests/test_module_entry.py`

### Implementation for User Story 2

- [x] T040 [US2] `_bridge()` emits `sys.executable -m pcl_sdk mcp-bridge` in `packages/pcl-server/src/pcl_server/pairing/catalog.py`
- [x] T041 [US2] `PCH_BASE` from `request.url` in `packages/pcl-server/src/pcl_server/rest/routers/connections.py`

**Checkpoint**: US2 independently testable via recipe spawn + `tools/call`

---

## Phase 5: User Story 3 - Upgrade and uninstall without losing the vault (Priority: P3)

**Goal**: Upgrade migrates then serves; uninstall never deletes `~/.pch` by default; existing vault reused.

**Independent Test**: `uv run pytest apps/hub-desktop/tests/test_uninstall.py packages/pcl-core/tests/test_upgrade_preserves_vault.py packages/pcl-server/tests/integration/test_existing_vault_reuse.py`

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T042 [P] [US3] Uninstall + Windows deferred-helper tests in `apps/hub-desktop/tests/test_uninstall.py`
- [x] T043 [P] [US3] Existing-vault reuse tests in `packages/pcl-server/tests/integration/test_existing_vault_reuse.py`

### Implementation for User Story 3

- [x] T044 [US3] Uninstall (POSIX in-process, Windows deferred helper, `--purge-data` + `DELETE`) in `apps/hub-desktop/src/hub_desktop/uninstall.py`
- [x] T045 [US3] Wire `pch upgrade` / `pch uninstall` in `apps/hub-desktop/src/hub_desktop/cli.py`

**Checkpoint**: US3 independently testable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Release matrix, docs, existing-vault path used by packaged entry

- [x] T046 [P] Release workflow `build` → `matrix` (ubuntu/macos/windows-latest) → `publish` in `.github/workflows/release.yml`
- [x] T047 [P] Contributor setup moved under `## Contributing (from source)` in `README.md`
- [x] T048 Run `make test` and `make lint`; record loop evidence

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — MVP
- **US2 (Phase 4)**: Depends on Foundational; uses `packaged_app` from US1 for live-server tests
- **US3 (Phase 5)**: Depends on Foundational and US1 CLI verbs
- **Polish (Phase 6)**: Depends on US1–US3

### User Story Dependencies

- **User Story 1 (P1)**: After Foundational
- **User Story 2 (P2)**: After Foundational; recipe connect test needs a running packaged app (US1)
- **User Story 3 (P3)**: After US1 CLI exists

### Parallel Opportunities

- T003–T007 (foundational tests)
- T016–T026 (US1 tests)
- T037–T039 (US2 tests)
- T042–T043 (US3 tests)

---

## Parallel Example: User Story 1 tests

```bash
# After T015, write US1 tests together:
Task: CLI dispatch tests in apps/hub-desktop/tests/test_cli_dispatch.py
Task: Pin tests in apps/hub-desktop/tests/test_pin.py
Task: Offline guard in apps/hub-desktop/tests/test_offline_guard.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 + 2
2. Phase 3 tests (must fail)
3. Phase 3 implementation until those tests pass
4. Validate: `packaged_app` + doctor + smoke HTTP

### Incremental Delivery

1. Setup + Foundational
2. US1 → one-command launch
3. US2 → recipes from `/tmp`
4. US3 → upgrade/uninstall
5. Polish → workflow + README

---

## Notes

- [P] tasks = different files, no dependencies
- Fail-first except T039 (F6c already green)
- Do not pair the Hub or write vault content during implement
- Do not commit unless the person asked
