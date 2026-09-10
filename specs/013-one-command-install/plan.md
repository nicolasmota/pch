# Implementation Plan: One-Command Install

**Branch**: `013-one-command-install` | **Date**: 2026-09-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/013-one-command-install/spec.md`

## Summary

A stranger pastes **`uvx personal-context-hub`** and reaches the guided setup with the full UI, no
API key, no account, no build step, no checkout. The first launch pins the Hub as a `uv tool` and
**re-executes inside that pinned environment**, so the running Hub, every later launch (`pch`),
and every assistant bridge use the installed interpreter and work with no network (research F13,
D4). The `pcl-server` wheel carries the built UI (hatch `artifacts`, verified by
`scripts/check_release.py` before publish). Recipes stop emitting `uv run …` and instead reference
the running Hub's interpreter with an absolute path, plus the actual port. The packaged entry
point refuses to start if `sqlcipher3` cannot be imported — **before** `Hub` or `Engine` can write
a plaintext vault — refuses a non-loopback bind, and disables every `/v1/sim/*` route (including
`target=everyday`) so no second vault is created (research F6, F6e, D6). `pch doctor`,
`pch upgrade`, `pch uninstall` (Windows: deferred helper so the running `python.exe` is not locked)
and a three-OS release workflow make FR-011/FR-012/FR-017 checkable. Nothing new is written into
the vault; no listener, daemon, or telemetry is added.

## Technical Context

**Language/Version**: Python 3.14 (fetched by `uv` on the person's machine); TypeScript/Node 22 at **release time only** (maintainer or CI)

**Primary Dependencies**: existing `hub-desktop` (renamed distribution `personal-context-hub`), `pcl-server`, `pcl-sdk`, `pcl-core`, `pca` (distribution `pcl-pca`); `uv` ≥ 0.12 as the single prerequisite; `sqlcipher3` 0.6.2 wheels (cp314, three OSes — F11); `hatchling` `artifacts` for static files; GitHub Actions for the release matrix (F15)

**Storage**: unchanged `~/.pch` (`vault.db` encrypted, `vault.salt`/`vault.key`, `plugins/`); new `kv.schema_version`; uv's own tool directory for the pinned environment. No new tables, no vault content at install

**Testing**: pytest across `apps/hub-desktop/tests/`, `packages/pcl-server/tests/`, `packages/pcl-core/tests/`, `packages/pcl-sdk/tests/`; wheel inspection in `scripts/check_release.py`; release matrix runs `pch doctor --json` and `pch smoke` on ubuntu/macos/windows. All new tests written first and failing before satisfying code

**Target Platform**: macOS (arm64, x86_64), Linux (x86_64, aarch64; glibc ≥ 2.28 or musl), Windows 10/11 native. Native window on macOS/Windows, browser fallback on bare Linux

**Project Type**: packaging + CLI entry point + release pipeline over an existing desktop-shell/local-service monorepo

**Performance Goals**: SC-001 — paste to guided setup < 5 min on a warm index (wheel set ≈ 60 MB incl. `sqlcipher3`, `cryptography`, FastAPI stack); `pch` cold start to `/health` < 3 s; `pch doctor` < 1 s

**Constraints**: constitution 1.1.0 (loopback only; vault encrypted by default; `pcl-core` no network/plugin-host I/O; no new listener; coding agent not a Hub client; Speckit artifacts are repo files); FR-002 no key/account; FR-004 offline after first fetch; FR-015 no elevation; FR-018 no install-time vault writes/telemetry

**Scale/Scope**: one person, one machine, one data dir per OS user; five published distributions at one version; one release workflow; README top section rewritten

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` **v1.1.0** (ratified 2026-08-26, amended 2026-09-07). Gates:

| Gate | Status | Evidence |
|------|--------|----------|
| I. Person owns context; coding agent is not a Hub client | PASS | Install writes zero objects/events/connections/proposals and creates no `_sim/` or `plugins/`; empty `blobs/` is the existing Hub mkdir (F6d); packaged serve skips catalog refresh (F6h, D14, `test_first_launch_writes_nothing.py` via TestClient); `migrate_connectors` asserted no-op; no pairing by the installer; implementer never pairs |
| II. Local-first, loopback-only; not a public server; encrypted at rest | PASS | `is_loopback` guard in both entry points (D7, `test_cli_dispatch.py::test_refuses_non_loopback`); `cipher_available()` then refuse **before** `Hub` (D6, F6, `test_entry_refuses_plaintext.py` asserts no `vault.db`); packaged path constructs exactly one encrypted `Engine`, no `_sim/`; sim router-level 404 including `target=everyday` (F6e, `test_sim_disabled.py`); offline: socket-guard `packaged_app` **and** `UV_OFFLINE=1 pch smoke` with 001/004 HTTP (D15); no telemetry |
| III. Least privilege / least context | PASS | No grant or assembly change; recipes carry the same token/grant model; no `forbidden_context` delta |
| IV. Provenance / explicit control | PASS | Uninstall never deletes data without `--purge-data` + typed `DELETE` (D9); upgrade migrates before serve and is hash-verified (D8); `pch doctor` states key storage honestly (D6/D11) |
| V. Imported content is data | PASS | Feature imports nothing; connectors unchanged and optional |
| `pcl-core` free of network/plugin-host I/O | PASS | Core changes: `cipher_available()` (import-only), `key_storage()` (stat `vault.key`), `schema_version` + ordered `MIGRATIONS` in `Engine` (local SQLite, core's job per 1.1.0) |
| Allowed feature origin | PASS | Child of 001 (FR-001/SC-001) and 002/009 (recipes) + repository tooling; not a horizon item; 001–003 not reopened |
| Package boundaries | PASS | Entry point/CLI in `apps/hub-desktop`; recipe fix in `pcl-server`; bridge `-m` entry in `pcl-sdk`; no server code in core; `pca` import name unchanged |
| Speckit artifacts are repo files | PASS | `scripts/`, workflow, README; nothing written to vault |
| Tests fail before satisfying implementation | PASS | SC table below names every test; tasks must create them first |
| No new listener / cloud dependency / vector DB / policy engine / daemon | PASS | `uv tool install` is a local install, not a service; no autostart; no cloud |
| Secrets not committed | PASS | Release uses PyPI trusted publishing (OIDC), no token in repo; workflow never touches `~/.pch` |
| Runtime defaults | PASS | Cursor remains default Speckit integration; Hermes/OpenClaw recipes get the same bridge shape |

**Post-design re-check (Phase 1)**: PASS — contract adds no HTTP route except two fields on
`GET /v1/setup` and a router-level `404` on `/v1/sim/*` when simulation is disabled; `pch smoke`
binds loopback on a free port and exits; the D4 re-exec replaces the current process with the pinned
one; the Windows uninstall helper is a one-shot detached `uv tool uninstall` after this PID exits,
not a daemon; Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/013-one-command-install/
├── plan.md              # This file
├── research.md          # Phase 0 — facts F1–F16, decisions D1–D15
├── data-model.md        # Phase 1 — Release, Data directory, Recipe, Doctor report, Pin state
├── quickstart.md        # Phase 1 — the stranger's screen, start to Hermes recipe from /tmp
├── contracts/
│   └── install.md       # CLI verbs, recipe shape, GET /v1/setup fields, release gate, tests
├── PLAN-BAR.md          # Frozen before this pack (Gauntlet)
└── tasks.md             # Phase 2 (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
pyproject.toml                                  # EDIT: name = "pch-workspace"; [tool.uv] package = false; version 0.2.0
packages/pcl-core/
├── pyproject.toml                              # EDIT: version 0.2.0
├── src/pcl_core/vault/keys.py                  # EDIT: key_storage(data_dir) -> "keychain" | "file"
├── src/pcl_core/vault/engine.py                # EDIT: cipher_available(); kv.schema_version; ordered MIGRATIONS
├── src/pcl_core/service.py                     # EDIT: setup_status() adds encrypted, key_storage
└── tests/
    ├── fixtures/vault_prev.sqlite              # NEW: previous-schema fixture (generated by scripts/make_prev_vault.py)
    ├── test_cipher_available.py                # NEW: True when sqlcipher3 imports; False when import patched to fail (fail first)
    ├── test_key_storage.py                     # NEW: FR-014 (fail first)
    └── test_upgrade_preserves_vault.py         # NEW: SC-005 counts + hashes + audit chain (fail first)
packages/pca/
└── pyproject.toml                              # EDIT: name = "pcl-pca", version 0.2.0 (import `pca` unchanged)
packages/pcl-sdk/
├── pyproject.toml                              # EDIT: version 0.2.0, deps ==0.2.0
└── tests/test_module_entry.py                  # NEW: regression guard — `python -m pcl_sdk mcp-bridge --help` from a tmp cwd (guard exists today, F6c; not red-first)
packages/pcl-server/
├── pyproject.toml                              # EDIT: version 0.2.0, deps ==0.2.0, [tool.hatch.build.targets.wheel] artifacts static/**
├── src/pcl_server/__main__.py                  # EDIT: is_loopback guard on --host
├── src/pcl_server/pairing/catalog.py           # EDIT: _bridge() -> sys.executable -m pcl_sdk mcp-bridge
├── src/pcl_server/rest/app.py                  # EDIT: create_app(..., sim_enabled=None, catalog_refresh=None); app.state.sim_enabled, catalog_refresh; sim Hub lazy; dev_app sim_enabled=True catalog_refresh=True
├── src/pcl_server/sync/scheduler.py            # EDIT: scheduler_loop skips refresh_catalog when catalog_refresh is False (F6h)
├── src/pcl_server/rest/routers/sim.py          # EDIT: router-level require_sim; 404 every /v1/sim/* when disabled (incl. target=everyday); lazy _sim_hub when enabled
├── src/pcl_server/rest/routers/connections.py  # EDIT: PCH_BASE from request.url (F3 fix)
├── src/pcl_server/rest/routers/setup.py        # EDIT: GET /v1/setup exposes encrypted, key_storage (no new path)
└── tests/
    ├── contract/test_assistant_catalog.py      # EDIT: render_recipe with an explicit base URL (not TestClient host `testserver`); no "uv run"
    ├── contract/test_recipe_from_anywhere.py   # NEW: uvicorn thread + pairing; MCP initialize then tools/call search_personal_context; all 6 assistants (fail first)
    ├── contract/test_setup_status_fields.py    # NEW: GET /v1/setup FR-014 fields (fail first)
    ├── contract/test_sim_disabled.py           # NEW: GET and POST /v1/sim/runs 404 with the message, including target=everyday; no _sim dir; sim_hub still works (fail first)
    └── integration/test_existing_vault_reuse.py# NEW: FR-013 (fail first)
apps/hub-desktop/
├── pyproject.toml                              # EDIT: name = "personal-context-hub"; scripts personal-context-hub + pch -> hub_desktop.cli:main; version 0.2.0
├── src/hub_desktop/
│   ├── main.py                                 # EDIT: extract launch_hub(args) from main(); keep `hub-desktop` dev behavior
│   ├── cli.py                                  # NEW: argparse verbs; packaged_app(data_dir); require_cipher_or_exit
│   ├── launch.py                               # EDIT: is_loopback(host); native_gui_available() -> also WebKit/WebView2 probe
│   ├── pin.py                                  # NEW: running_from_uv_tool(), ensure_pinned(version), pinned_interpreter(), reexec_into_pinned(argv); uv discovery
│   ├── doctor.py                               # NEW: DoctorReport dataclass, collect(), exit code rule
│   ├── uninstall.py                            # NEW: POSIX in-process uv tool uninstall; Windows deferred helper (F6g); print data location; --purge-data + DELETE
└── tests/
    ├── test_launch.py                          # EDIT: keep; add is_loopback cases
    ├── test_cli_dispatch.py                    # NEW: verbs route; (none) launches; test_refuses_non_loopback; test_launch_never_prompts; test_reattach_when_running (fail first)
    ├── test_pin.py                             # NEW: fake `uv` on PATH records `tool install personal-context-hub==X`; test_reexec_into_pinned_interpreter; test_no_pin_flag_skips; test_pin_targets_user_tool_dir (fail first)
    ├── test_doctor.py                          # NEW: fields + exit code (fail first)
    ├── test_uninstall.py                       # NEW: SC-006 data untouched, purge needs both flag and DELETE; test_windows_self_uninstall_defers_helper (fail first)
    ├── test_entry_refuses_plaintext.py         # NEW: cipher_available False → exit 1, no vault.db/blobs/vault.key (fail first)
    ├── test_packaged_entry_never_plain.py      # NEW: every Engine on packaged path encrypted; no _sim/ (fail first)
    ├── test_first_launch_writes_nothing.py     # NEW: TestClient(packaged_app): 0 rows; listing ⊆ {vault.db, blobs, vault.key}; no marketplace_catalog kv; no _sim/ (fail first)
    ├── test_offline_guard.py                   # NEW: import packaged_app (collection-red today); socket guard; setup+Atlas+search+get_context_manifest (fail first)
    ├── test_readme_install_section.py          # NEW: SC-008 rules (fail first)
    └── test_check_release.py                   # NEW: self-test of scripts/check_release.py on synthetic dist/ (fail first)
frontend/
├── src/api/types.ts                            # EDIT: SetupStatus.encrypted, SetupStatus.key_storage
├── src/pages/Setup.tsx                         # EDIT: one sentence from key_storage on guided setup
└── tests/setup_key_storage.spec.ts             # NEW: guided setup shows "system keychain" or "private file" (fail first)
scripts/
├── check_release.py                            # NEW: wheel contains static/index.html + assets; one version across five wheels
└── make_prev_vault.py                          # NEW: generates tests/fixtures/vault_prev.sqlite at previous schema
.github/workflows/release.yml                   # NEW: build → matrix (ubuntu, macos, windows) → publish (trusted publishing)
Makefile                                        # EDIT: `release` target (frontend build → uv build → check → publish); `smoke`
README.md                                       # EDIT: Install section (D13); contributor setup moved to bottom
```

**Structure Decision**: Entry point and all install verbs live in `apps/hub-desktop` (already the
launcher; becomes the published `personal-context-hub`). `pcl-server` owns the recipe fix and wheel
artifacts. `pcl-core` receives `cipher_available`, `key_storage`, and versioned migrations. The
Setup page is the one frontend change (FR-014). No new package. Root distribution name changes so
the workspace can host `personal-context-hub` (F9).

## Success criteria → tests

| SC | Test / check (must fail first where automated) |
|----|------------------------------------------------|
| SC-001 | Timed manual run recorded as delivery evidence on one clean VM/container per OS (quickstart §1); release matrix `pch smoke` as the automated floor |
| SC-002 | `test_cli_dispatch.py::test_launch_never_prompts` (no stdin reads, no key/account strings); matrix job runs as unprivileged runner user; `test_pin.py::test_pin_targets_user_tool_dir` |
| SC-003 | `apps/hub-desktop/tests/test_offline_guard.py::test_001_scenarios_offline`, `::test_004_situation_package_offline` (import `packaged_app`; socket guard); matrix `UV_OFFLINE=1 pch smoke` which also runs those four HTTP calls on the installed wheel |
| SC-004 | `contract/test_recipe_from_anywhere.py::test_all_supported_assistants_connect_from_tmp` — uvicorn on a free loopback port; for each of six assistants spawn `command+args` with `cwd=tmp` and recipe `env`; MCP `initialize`, then `tools/call` `search_personal_context` with `query="Atlas"` `purpose="test"`; assert the JSON-RPC result is a tool result (empty hits ok) and **not** `Hub unreachable`; `::test_recipe_command_is_pinned_interpreter`; `test_assistant_catalog.py::test_recipe_has_no_uv_run` |
| SC-005 | `test_upgrade_preserves_vault.py::test_counts_and_hashes_equal` (objects, versions, events, **connections**, kv minus `schema_version`), `::test_audit_chain_verifies_after_migration`, `::test_migrations_run_before_first_request` |
| SC-006 | `test_uninstall.py::test_default_keeps_data_and_names_location`, `::test_purge_requires_flag_and_typed_delete`, `::test_yes_without_purge_does_nothing_extra` |
| SC-007 | `test_offline_guard.py` (non-loopback connect fails the test); matrix `UV_OFFLINE=1 pch smoke`; `test_first_launch_writes_nothing.py` (TestClient lifespan, zero `marketplace.catalog_check`) |
| SC-008 | `test_readme_install_section.py` (new, `apps/hub-desktop/tests/`): section ≤ 25 lines, contains exactly one fenced command line `uvx personal-context-hub`, no `git clone`/`npm`/`make` above `## Contributing`; timed 30-second read recorded as delivery evidence |

Additional FR coverage: FR-005/FR-006 → `test_entry_refuses_plaintext.py`, `test_cli_dispatch.py::test_refuses_non_loopback`, `test_packaged_entry_never_plain.py`, `test_sim_disabled.py`; FR-004 → `test_pin.py::test_reexec_into_pinned_interpreter`; FR-007/FR-008 → existing `test_launch.py` + `test_cli_dispatch.py::test_reattach_when_running`; FR-013 → `test_existing_vault_reuse.py`; FR-014 → `test_key_storage.py`, `test_setup_status_fields.py` (`GET /v1/setup`), `frontend/tests/setup_key_storage.spec.ts`; FR-003 → `scripts/check_release.py` (release gate) + `test_check_release.py` + `test_doctor.py::test_ui_bundled_field`. `test_module_entry.py` is a regression guard for behavior that already exists (F6c) and is excluded from the red-first requirement.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution-gate violations. No new listener, cloud dependency, vector index, policy engine,
daemon, or kernel I/O. The self-pin (D4) is a one-time local `uv tool install` plus an in-place
re-exec. The Windows uninstall helper exits after one `uv tool uninstall`; it is not a service.
