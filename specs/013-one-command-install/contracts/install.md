# Contract: Install, Launch, Recipes, Upgrade, Uninstall, Release

**Feature**: `specs/013-one-command-install/` | **Date**: 2026-09-07

This is the contract a tasks agent implements and tests against. Sections: CLI verbs, recipe
shape, `GET /v1/setup` fields, loopback and encryption refusals, release gate, workflow, README
section, and the test list with fail-first order.

## 1. Console scripts

| Script | Distribution | Entry | Audience |
|--------|--------------|-------|----------|
| `personal-context-hub` | `personal-context-hub` | `hub_desktop.cli:main` | the one command (`uvx personal-context-hub`) |
| `pch` | `personal-context-hub` | `hub_desktop.cli:main` | daily alias after pin |
| `hub-desktop` | `personal-context-hub` | `hub_desktop.main:main` | contributors (`--dev --reload`), unchanged |
| `pcl-server`, `pcl-sdk`, `pca` | respective | unchanged | contributors / bridge |

## 2. `pch` verbs

```text
pch                      # launch: pin if needed, open Hub (reuse if running), native window or browser
pch serve [--headless] [--port N] [--data-dir P] [--host 127.0.0.1]
pch doctor [--json]
pch smoke  [--port N] [--data-dir P]      # start packaged_app headless; GET /health and / (SPA title); POST /v1/setup, POST /v1/projects Atlas, GET /v1/search?q=Atlas, POST /v1/mcp/tools/get_context_manifest; stop; exit 0/1
pch upgrade                              # runs: uv tool upgrade personal-context-hub
pch uninstall [--purge-data] [--yes]
pch version
pch --help
```

Behavioural rules:

- **launch** (no verb): unless `--no-pin`: `ensure_pinned(__version__)`; on `installed` →
  `reexec_into_pinned(argv)` (§3) — the current process is replaced and the rules below run in the
  pinned interpreter. Then: `require_cipher_or_exit(data_dir)` (§5) **before any Hub/Engine/key
  write** → `packaged_app(data_dir)` (`require_cipher_or_exit` + `Hub` +
  `create_app(hub, sim_enabled=False, catalog_refresh=False)`)
  → `choose_port` → if a Hub already answers `/health`, open its URL and exit 0 → else serve on
  loopback, wait for health, open native window or browser (`launch.native_gui_available()`),
  block until closed.
- **serve**: same as launch without opening a window; `--host` accepted only if `is_loopback(host)`;
  `--sim` (dev convenience) passes `sim_enabled=True`, otherwise `False`.
- **`--no-pin`** (internal, all verbs): skip `ensure_pinned`/re-exec. Set by the re-exec itself so it cannot loop.
- **doctor**: fields per data-model; exit 0 only when `encrypted` (or plain requested) and `ui_bundled`.
- **smoke**: used by the release matrix under `UV_OFFLINE=1`; starts `packaged_app`, asserts SPA,
  then the four 001/004 HTTP calls; must not contact any index.
- **upgrade**: POSIX: `uv tool upgrade personal-context-hub`. Windows when `running_from_uv_tool()`:
  same deferred-helper pattern as uninstall with `uv tool upgrade …`. If `uv` missing, print the
  exact command and exit 1.
- **uninstall**: print data location first. POSIX: `uv tool uninstall personal-context-hub`.
  Windows when `running_from_uv_tool()`: detached helper waits for this PID, then uninstalls (F6g).
  Never removes the data directory without `--purge-data` **and** (typed `DELETE` or `--yes`).
- **No verb ever**: pairs an assistant, writes an object/proposal/connection, or opens a non-loopback socket.

Exit codes: `0` ok · `1` doctor/smoke failure or refused plaintext · `2` usage / non-loopback host.

## 3. Pin behaviour (`hub_desktop/pin.py`)

```python
def running_from_uv_tool() -> bool: ...              # sys.prefix under `uv tool dir`
def ensure_pinned(version: str) -> PinAction: ...     # none | installed | skipped_no_uv | failed
def pinned_interpreter() -> Path | None: ...          # <uv tool dir>/personal-context-hub/bin/python | ...\Scripts\python.exe
def reexec_into_pinned(argv: list[str]) -> NoReturn | None: ...  # os.execv (POSIX) / subprocess+exit (Windows); returns None only on failure
```

- `ensure_pinned` returns `none` immediately when `running_from_uv_tool()`. Otherwise runs
  `[uv, "tool", "install", f"personal-context-hub=={version}"]` with `check=False`, captured output,
  120 s timeout. On success prints exactly: `Installed for offline use. Next time run: pch`
- `uv tool dir` is resolved by `subprocess.run([uv, "tool", "dir"])` (respects `UV_TOOL_DIR`).
- `reexec_into_pinned(argv)`: `[pinned_interpreter(), "-m", "hub_desktop.cli", "--no-pin", *argv]`.
  POSIX: `os.execv`. Windows: `subprocess.run(...)` then `sys.exit(rc)`. If `pinned_interpreter()`
  is `None` or exec fails, print `Could not switch to the installed copy; continuing.` and return.
- On `skipped_no_uv` prints: `uv was not found; the Hub runs now but offline use needs: uv tool install personal-context-hub`
- Never blocks launch; never prompts; never runs when `--no-pin` is present.

## 4. Recipe shape (all six assistants)

```json
{
  "command": "/home/me/.local/share/uv/tools/personal-context-hub/bin/python",
  "args": ["-m", "pcl_sdk", "mcp-bridge"],
  "env": {"PCH_TOKEN": "<token>", "PCH_BASE": "http://127.0.0.1:8765"}
}
```

- `command` = `sys.executable` of the process that served the recipe request. Because launch
  re-execs into the pinned environment (§2/§3), this is `<uv tool dir>/personal-context-hub/bin/python`
  from the first session onward; in a source checkout it is `.venv/bin/python`.
- `PCH_BASE` = `f"{request.url.scheme}://{request.url.hostname}:{request.url.port}"`; loopback by construction.
- Wrapper keys unchanged: `mcpServers` (Cursor, Claude Code, Claude Desktop, ChatGPT), `mcp_servers` (Hermes), `mcp.servers` (OpenClaw).
- `python -m pcl_sdk mcp-bridge` already works (`pcl_sdk/__main__.py:69-70`); `test_module_entry.py` guards it.

## 5. Refusals

| Condition | Where | Exit | Message (exact first line) |
|-----------|-------|------|----------------------------|
| `--host` not loopback | `pch serve`, `pcl-server` | 2 | `The Hub is not a public server; it binds loopback only.` |
| `cipher_available()` is False and `PCH_PLAIN_SQLITE != "1"` | `pch` launch/serve/smoke | 1 | `Refusing to start: the encrypted database driver (sqlcipher3) did not load on this platform.` |

`is_loopback(host)` accepts `localhost`, any `127.0.0.0/8` address, `::1`; rejects everything
else including `0.0.0.0`, `::`, and LAN addresses. Packaged serve always **binds** `127.0.0.1`
(`AF_INET`); `--host ::1` is accepted as loopback policy but mapped to `127.0.0.1` for bind
(`launch.port_free` is IPv4-only today).

`require_cipher_or_exit` runs **before** `Hub`/`Engine`/`load_or_create_key`. After a refusal the
data dir has no `vault.db`, no `blobs/`, no `vault.key`. Second line of stderr:
`Your vault was not opened in plaintext. Set PCH_PLAIN_SQLITE=1 only if you accept an unencrypted vault.`

```python
def cipher_available() -> bool: ...   # pcl_core.vault.engine; import sqlcipher3 only
def require_cipher_or_exit(data_dir: Path) -> None: ...  # hub_desktop.cli
```

### 5a. Simulation disabled in the packaged app

`create_app(hub, sim_enabled: bool | None = None, sim_hub: Hub | None = None, sim_dir: Path | None = None, catalog_refresh: bool | None = None)`:

- `sim_enabled is None` → `os.environ.get("PCH_SIM_ENABLED") == "1"`; a non-`None` `sim_hub` implies enabled.
- `catalog_refresh is None` → `os.environ.get("PCH_CATALOG_REFRESH") == "1"`; packaged `pch` passes False.
- `app.state.sim_enabled` and `app.state.catalog_refresh` are always set. `scheduler_loop` skips
  `refresh_catalog` when `catalog_refresh` is False (F6h).
- The sim router has a **router-level** dependency: when
  disabled, **every** `/v1/sim/*` handler — including `POST /sim/runs` with `target=everyday` —
  returns `404 {"detail": "simulation disabled; run hub-desktop --dev or set PCH_SIM_ENABLED=1"}`
  before `require_owner`. Probe: `GET /v1/sim/runs` (no `/v1/sim/status` route exists).
- Enabled: `app.state.sim_dir` is set; `routers/sim.py::_sim_hub(request)` opens `Hub(sim_dir, plain=True)`
  on first use and caches it on `app.state.sim_hub`.
- Disabled: `app.state.sim_hub = None`, `app.state.sim_dir = None`.
- `dev_app()` passes `sim_enabled=True, catalog_refresh=True`. `pch` / `packaged_app` pass both False.
  `tests/conftest.py` (`create_app(hub)`) therefore gets sim disabled and catalog refresh off;
  `test_sim_rest.py` passes `sim_hub` and keeps working.
- The sim `Engine` is never constructed on the packaged path: `test_packaged_entry_never_plain.py`
  records every `Engine.__init__` call.

## 6. `GET /v1/setup` (extended)

```json
{"initialized": false, "in_progress": false, "name": null, "encrypted": true, "key_storage": "keychain"}
```

`key_storage` ∈ `{"keychain", "file"}`. `frontend/src/pages/Setup.tsx` shows one line derived from it.

## 7. Schema versioning (`pcl_core/vault/engine.py`)

```python
MIGRATIONS: list[tuple[int, Callable[[SerializedConnection], None]]] = [
    (1, _m1_add_source_key),
]
```

`_migrate()` reads `kv.schema_version` (absent → 0), applies each `(n, fn)` with `n > current` in
a transaction, writes `n` after each. Called from `Engine.__init__` before the constructor
returns; therefore before `create_app` and before uvicorn binds.

## 8. Release gate (`scripts/check_release.py`)

Input: `dist/`. Asserts, else exit 1:

1. Exactly five wheels: `pcl_core`, `pcl_pca`, `pcl_sdk`, `pcl_server`, `personal_context_hub`.
2. All five share one version string.
3. `pcl_server` wheel contains `pcl_server/static/index.html` and at least one `pcl_server/static/assets/*.js`.
4. `personal_context_hub` wheel's `entry_points.txt` declares `personal-context-hub` and `pch`.
5. Each wheel's `METADATA` `Requires-Dist` pins sibling packages with `==<version>`.

`make release` = `frontend` → `uv build --all-packages` → `python scripts/check_release.py` → `uv publish`.

## 9. Release workflow (`.github/workflows/release.yml`)

Trigger: push of tag `v*`.

| Job | Runner(s) | Steps |
|-----|-----------|-------|
| `build` | ubuntu-latest | checkout · setup Node 22 · `npm ci && npm run build` (in `frontend/`) · install uv · `uv build --all-packages` · `python scripts/check_release.py` · upload `dist/` |
| `matrix` | ubuntu-latest, macos-latest, windows-latest | download `dist/` · install uv · `uv tool install --find-links dist personal-context-hub==<v>` · `pch doctor --json` (assert `encrypted==true`, `ui_bundled==true`) · `UV_OFFLINE=1 pch smoke --data-dir <tmp>` (SPA + four 001/004 HTTP calls) · `pch uninstall --yes` · **Windows: wait ≤30s until `pch` is gone from PATH** · assert `<tmp>` still exists |
| `publish` | ubuntu-latest, needs `matrix` | download `dist/` · `uv publish` via PyPI trusted publishing (`id-token: write`), no secrets in repo |

Linux runner is expected to report `native_window: browser`; macOS and Windows `native`. A
`browser` result on macOS/Windows is not a failure but is printed in the job summary.

## 10. README install section (exact text)

```markdown
## Install

Needs [uv](https://docs.astral.sh/uv/getting-started/installation/) (one line to install). Then:

    uvx personal-context-hub

The Hub opens on your machine. No account, no API key, nothing leaves your device.

Next time: `pch` · Upgrade: `uv tool upgrade personal-context-hub` · Remove: `pch uninstall`
(your data stays in `~/.pch` unless you add `--purge-data`).
```

Everything currently under Prerequisites/Setup/Tests moves below a `## Contributing (from source)`
heading. `test_readme_install_section.py` enforces: heading `## Install` present; ≤ 25 lines until
the next `##`; exactly one indented/fenced command line and it is `uvx personal-context-hub`; none
of `git clone`, `npm`, `make install`, `uv sync` appear above `## Contributing`.

## 11. Tests (write first; each must fail before its satisfying change)

| Order | File | Asserts | SC/FR |
|-------|------|---------|-------|
| 1 | `apps/hub-desktop/tests/test_cli_dispatch.py` | `test_verbs_route`; `test_no_verb_launches`; `test_refuses_non_loopback` (`--host 0.0.0.0` → exit 2 + message); `test_launch_never_prompts` (no stdin reads, no key/account strings); `test_reattach_when_running` | FR-006, FR-007, SC-002 |
| 2 | `apps/hub-desktop/tests/test_launch.py` (edit) | `is_loopback` table: `127.0.0.1`, `127.5.5.5`, `localhost`, `::1` true; `0.0.0.0`, `::`, `192.168.1.2` false | FR-006 |
| 3 | `apps/hub-desktop/tests/test_entry_refuses_plaintext.py` | monkeypatch `cipher_available` → False (do **not** construct Hub); exit 1; both message lines; temp data dir has no `vault.db`, no `blobs/`, no `vault.key`; with `PCH_PLAIN_SQLITE=1` the probe is skipped and launch may proceed | FR-005 |
| 4 | `apps/hub-desktop/tests/test_pin.py` | fake `uv` on PATH: `test_first_launch_installs_once` (`tool install personal-context-hub==<v>`, prints the line); `test_reexec_into_pinned_interpreter` (monkeypatch `os.execv`/`subprocess.run`, assert argv `[<tool_dir>/…/python, "-m", "hub_desktop.cli", "--no-pin", …]`); `test_no_pin_flag_skips`; `test_pin_targets_user_tool_dir` (path under `uv tool dir`, no elevation); missing uv → `skipped_no_uv`, still launches | FR-004, FR-015, SC-002 |
| 5 | `apps/hub-desktop/tests/test_doctor.py` | fields present incl. `pinned`, `pinned_interpreter`; exit 1 when `ui_bundled` false; `--json` parses | FR-003, FR-014 |
| 6 | `apps/hub-desktop/tests/test_uninstall.py` | default keeps data + prints location; `--purge-data` w/o `DELETE` → data untouched, exit 1; with `DELETE` or `--yes` removes; `--yes` alone removes nothing; `test_windows_self_uninstall_defers_helper` (`sys.platform` patched to `win32`, `running_from_uv_tool` True: `uv tool uninstall` is **not** called in-process; `Popen` argv is the helper; helper text contains `uv tool uninstall personal-context-hub` and this PID) | SC-006, FR-012 |
| 7 | `apps/hub-desktop/tests/test_first_launch_writes_nothing.py` | `TestClient(packaged_app(tmp))` (lifespan ticks scheduler once): 0 objects, 0 events, 0 connections, 0 proposals; no `marketplace_catalog` kv; `set(listdir(data_dir)) ⊆ {"vault.db", "blobs", "vault.key"}`; `blobs/` empty; no `_sim/` | FR-018, SC-007 |
| 8 | `apps/hub-desktop/tests/test_packaged_entry_never_plain.py` | wrap `Engine.__init__`; packaged construction path; exactly one `Engine`, `encrypted is True`; `data_dir/"_sim"` absent | FR-005 |
| 9 | `apps/hub-desktop/tests/test_readme_install_section.py` | §10 rules | SC-008, FR-016 |
| 10 | `apps/hub-desktop/tests/test_check_release.py` | `scripts/check_release.py` fails on missing `index.html`, on version mismatch, on missing entry point, on unpinned sibling; passes on a synthetic good `dist/` | FR-003 |
| 11 | `packages/pcl-core/tests/test_key_storage.py` | `file` when `vault.key` exists; `keychain` otherwise | FR-014 |
| 11b | `packages/pcl-core/tests/test_cipher_available.py` | True when import works; False when `sqlcipher3` import patched to fail | FR-005 |
| 12 | `packages/pcl-core/tests/test_upgrade_preserves_vault.py` | open `fixtures/vault_prev.sqlite` copy with new `Engine`; counts equal for objects, versions, events, **connections**; sha256 of canonical JSON equal per table (kv compared minus `schema_version`); audit chain verifies; `schema_version` advanced; migration ran before first query | SC-005, FR-011 |
| 13 | `packages/pcl-server/tests/contract/test_assistant_catalog.py` (edit) | call `render_recipe` / `_bridge` with an explicit `http://127.0.0.1:<port>` (do not use TestClient's `testserver`); command absolute + exists; no `uv run` | FR-009, FR-010 |
| 14 | `packages/pcl-server/tests/contract/test_recipe_from_anywhere.py` | start `create_app(hub, sim_enabled=False)` under uvicorn on a free loopback port in a thread; issue pairing + recipes for all six assistants; for each: `Popen(command+args, cwd=tmp, env={**os.environ, **recipe.env})`; MCP `initialize`; then `tools/call` name=`search_personal_context` arguments=`{query: Atlas, purpose: test}`; assert JSON-RPC `result` is a tool payload and the serialized body does **not** contain `Hub unreachable` → `test_all_supported_assistants_connect_from_tmp`; `test_recipe_command_is_pinned_interpreter` | SC-004, FR-009 |
| 15 | `packages/pcl-server/tests/contract/test_setup_status_fields.py` | `GET /v1/setup` has `encrypted`, `key_storage` present and typed | FR-014 |
| 16 | `packages/pcl-server/tests/contract/test_sim_disabled.py` | `create_app(hub)` (default) → `GET /v1/sim/runs` and `POST /v1/sim/runs {"target":"everyday"}` both 404 with the message (no owner token needed); no `_sim/`; `create_app(hub, sim_hub=...)` → GET 200 after a run; `PCH_SIM_ENABLED=1` → lazy open on first **enabled** request only | FR-005, FR-018 |
| 17 | `apps/hub-desktop/tests/test_offline_guard.py` | `from hub_desktop.cli import packaged_app` (file/symbol absent today → collection-red; **not** a copy of `packages/pcl-server/tests/integration/test_offline.py`); socket guard; POST `/v1/setup`, POST `/v1/projects` Atlas, GET `/v1/search?q=Atlas`, POST `/v1/mcp/tools/get_context_manifest`; any non-loopback connect fails | SC-003, SC-007 |
| 18 | `packages/pcl-server/tests/integration/test_existing_vault_reuse.py` | source-created vault opened by packaged path; same object ids; no second dir | FR-013 |
| 19 | `frontend/tests/setup_key_storage.spec.ts` | guided setup shows "system keychain" or "private file in ~/.pch" | FR-014 |

Regression guard, **not** red-first (behavior exists today, F6c): `packages/pcl-sdk/tests/test_module_entry.py`
— `python -m pcl_sdk mcp-bridge --help` exits 0 from a tmp cwd.

Delivery evidence (not pytest): timed clean-machine run per OS (SC-001), 30-second README read
(SC-008), release matrix logs (FR-017).
