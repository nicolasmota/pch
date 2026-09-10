# Research: One-Command Install

**Feature**: `specs/013-one-command-install/` | **Date**: 2026-09-07 | **Constitution**: 1.1.0

Facts were checked against the repository and against live registries on 2026-09-07. Where a
decision rests on an experiment, the experiment is recorded so a tasks agent can rerun it.

## Facts that constrain the design

| # | Fact | Where | Consequence |
|---|------|-------|-------------|
| F1 | Built UI goes to `packages/pcl-server/src/pcl_server/static/` and that path is in `.gitignore`; `create_app` mounts it only `if static.exists()` | `frontend/vite.config.ts`, `.gitignore:20`, `rest/app.py:132` | Anything installed from git or from a wheel built without the UI serves JSON at `/` and no interface. The release step must build the UI first and the wheel must include it. |
| F2 | Pairing recipes emit `{"command": "uv", "args": ["run", "pcl-sdk", "mcp-bridge"]}` | `pairing/catalog.py::_bridge` | Only works with cwd inside the checkout. Must change. |
| F3 | Recipe endpoint hardcodes `"http://127.0.0.1:8765"` as `PCH_BASE` | `rest/routers/connections.py:59` | FR-010 (actual port) is a live bug, not a hypothetical. |
| F4 | Desktop shell already: re-attaches to a running Hub via `/health`, hunts a free port in `+1..+20`, opens browser when no GTK/Qt | `apps/hub-desktop/src/hub_desktop/launch.py`, `main.py` | Preserve, do not reimplement. Tests exist in `apps/hub-desktop/tests/test_launch.py`. |
| F5 | Vault key: OS keyring first, else `~/.pch/vault.key` with `0o600` | `pcl_core/vault/keys.py` | FR-014 needs only reporting which storage is in use, not new storage. |
| F6 | `Engine` silently falls back to plaintext SQLite when `sqlcipher3` fails; on fallback it already `executescript(SCHEMA)`, `_migrate()`, `commit()`; `Hub.__init__` then writes `owner_token`. `create_app(hub=None)` is `Hub(..., plain=True)` | `vault/engine.py:158-178`, `service.py:56-57`, `rest/app.py:66` | Checking `engine.encrypted` **after** `Hub(...)` is too late: a plaintext `vault.db` already exists. The packaged path must call `cipher_available()` (import-only) and refuse **before** `Hub`/`Engine`/`load_or_create_key`. |
| F6b | `create_app` **always** constructs a second `Hub(hub.data_dir / "_sim", plain=True)` when `sim_hub` is not passed, and calls `migrate_connectors(hub)` on every start | `rest/app.py:67-71` | Packaged launch must not create `_sim/`. Simulation is opt-in. |
| F6c | `pcl_sdk/__main__.py` already ends with the `if __name__ == "__main__": main()` guard | `pcl_sdk/__main__.py:69-70` | `python -m pcl_sdk mcp-bridge` works today; regression guard, not red-first. |
| F6d | `Hub.__init__` always constructs `BlobStore(data_dir / "blobs")`, which `mkdir`s an empty `blobs/` | `service.py:55`, `vault/blobs.py:12` | First launch listing is `vault.db` + empty `blobs/` (+ `vault.key` if no keychain). Do not change BlobStore. |
| F6e | `POST /v1/sim/runs` with `target=everyday` uses `app.state.hub` and never calls `_sim_hub`; pause/resume/stop use the session | `rest/routers/sim.py:30,105-109` | Disabling sim by making only `_sim_hub` 404 leaves the 011 harness aimed at the real vault. The sim router must refuse **every** `/v1/sim/*` route when disabled (router-level dependency). There is no `/v1/sim/status`; the probe is `GET /v1/sim/runs`. |
| F6f | MCP `tools/list` is answered from a static list in the bridge; only `tools/call` hits the Hub (`call_hub`) | `pcl_sdk/mcp_bridge.py:242-257` | SC-004 "connect" requires `tools/call search_personal_context` (empty hits ok) against a live loopback server; `tools/list` alone cannot catch a wrong `PCH_BASE`/`PCH_TOKEN`. |
| F6g | Windows will not delete or replace a running `python.exe`; `pch uninstall`/`upgrade` from inside the pinned env would fail or half-remove the tool dir | Win32 file locking | Uninstall/upgrade on Windows must spawn a detached helper that waits for this PID to exit, then run `uv tool …`. POSIX can uninstall in-process. |
| F6h | `lifespan` starts `scheduler_loop`, which on the first tick calls `refresh_catalog` when `marketplace_catalog` kv is absent; that writes `kv.marketplace_catalog` and a `marketplace.catalog_check` event even with no `PCH_CATALOG_URL` (bundled catalog) | `rest/app.py:42-45`, `sync/scheduler.py:115-156`, `marketplace/catalog.py:110-120` | A construction-only first-launch test misses this. Packaged serve must skip automatic catalog refresh (`app.state.catalog_refresh=False`); marketplace still refreshes on an explicit UI action. The first-launch test must enter the ASGI lifespan (TestClient) so a scheduler tick happens. |
| F7 | `pcl-server --host` accepts any address | `pcl_server/__main__.py` | Constitution II: the installed command must refuse non-loopback. |
| F8 | `_migrate()` runs inside `Engine.__init__`, before any request is served; today it is one ad-hoc `ALTER TABLE` | `vault/engine.py:181` | Ordering already correct; needs a `schema_version` key and a test with a fixture vault to satisfy FR-011. |
| F9 | Root `pyproject.toml` is already `name = "personal-context-hub"` with no `[build-system]`; it is the uv workspace root | `pyproject.toml:2` | Renaming `hub-desktop` to `personal-context-hub` without renaming the root yields `Two workspace members are both named personal-context-hub` (uv 0.12.5). Root becomes `name = "pch-workspace"` and `[tool.uv] package = false`. |
| F10 | PyPI names: `pch` **taken**, `pca` **taken**; `personal-context-hub`, `pcl-core`, `pcl-server`, `pcl-sdk`, `hub-desktop`, `pcl-pca`, `pcl-hub` free | `https://pypi.org/pypi/<name>/json` (200 vs 404) | The command cannot be `uvx pch`. `pca` must publish under another distribution name. |
| F11 | `sqlcipher3` 0.6.2 ships cp314 wheels for macOS (x86_64, arm64, universal2), manylinux_2_28 (x86_64, aarch64, i686), musllinux, and Windows (win32, amd64, arm64) | PyPI file list | Encryption is installable on all three OSes with no compiler. |
| F12 | `argon2-cffi-bindings` 26.1.0 and `cryptography` 50.0.1 ship cp314/abi3 wheels; `pywebview` 6.2.1 is a pure-Python wheel whose platform-conditional extras (`pythonnet` on Windows, `pyobjc` on macOS, `pygobject`/`qtpy` on Linux) are optional and only needed for a native window | PyPI | No build toolchain on the person's machine. The release matrix (D12) is the check that the resolved set installs from wheels on each OS; a native window is never required (browser fallback, F4). |
| F13 | `uvx <pkg>` re-resolves on every run and **fails with no network** (`tcp connect error`) even when the environment is cached; `uv --offline tool run` and `UV_OFFLINE=1 uvx` reuse the cache; a binary from `uv tool install` runs with **no network at all** | Experiment with uv 0.12.5, `cowsay`, `UV_INDEX_URL=http://127.0.0.1:9/simple` | The documented command may be `uvx …` for the first run, but the Hub must end up as an installed tool for FR-004 (offline) to hold. |
| F14 | `uv tool install` creates `<UV_TOOL_DIR>/<name>/bin/python` and shims in `UV_TOOL_BIN_DIR`; both stable paths | Experiment | Recipes can reference the tool environment's interpreter with an absolute path. |
| F15 | No CI in the repo (`.github/workflows` absent); remote is `github.com/nicolasmota/pcl` | `ls .github`, `git remote -v` | A release workflow is new and is the honest place for the three-OS matrix. |
| F16 | `pch.spec` is a two-line PyInstaller skeleton | `apps/hub-desktop/src/hub_desktop/packaging/pch.spec` | Native installer is real future work; this spec leaves it untouched. |

## Decisions

### D1 — Distribution name and the one command

**Decision**: Publish the desktop shell as distribution **`personal-context-hub`** (rename of the
`hub-desktop` distribution; import package `hub_desktop` unchanged) with two console scripts:
`personal-context-hub` (so `uvx personal-context-hub` needs no `--from`) and `pch` (short alias).
The documented one command is:

```bash
uvx personal-context-hub
```

**Rationale**: `uvx` runs the console script whose name equals the package name; that removes
`--from`. `pch` is taken on PyPI (F10), so it can only be the alias, never the package. `uv` is the
single prerequisite; it fetches Python 3.14 itself (`uv python install` on demand), so the person
needs no Python.

**Alternatives considered**: `uvx --from personal-context-hub pch` (works, but is a sentence, not a
command); `pipx` (needs a Python already installed; uv does not); publishing `pch-hub` / `pcl-hub`
(shorter, but the distribution name is what people search; the product is called Personal Context
Hub); `uvx --from git+https://github.com/nicolasmota/pcl personal-context-hub` (the spec's
"direct-from-repository URL as fallback" — rejected as a stranger path: F1, a git install ships no
UI; it stays under Contributing); native installers (F16; next spec).

### D2 — Publish five distributions, pinned to one version

**Decision**: Publish `pcl-core`, `pcl-pca` (distribution name for the `pca` package; F10),
`pcl-sdk`, `pcl-server`, `personal-context-hub`, all at the same version (`0.2.0` for the first
release), each depending on the others with `==<version>`. Root `pyproject.toml` is renamed
`name = "pch-workspace"`, gets `[tool.uv] package = false`, and stays the workspace root and
dev-dependency holder (F9).

**Rationale**: uv workspace `sources = { workspace = true }` are for local resolution; the wheel
metadata carries only the `[project.dependencies]` string, so exact pins keep a released set
coherent. Renaming only the `pca` *distribution* avoids touching imports. Renaming the root avoids
the duplicate-name lock break.

**Alternatives considered**: one fat wheel (breaks `pcl-core` isolation and plugin kit reuse);
unpinned deps (a person could get `pcl-server 0.3` with `pcl-core 0.2`); leaving the root named
`personal-context-hub` (F9).

### D3 — UI inside the `pcl-server` wheel

**Decision**: `packages/pcl-server/pyproject.toml` adds
`[tool.hatch.build.targets.wheel] artifacts = ["src/pcl_server/static/**"]` so the git-ignored
build output is included when present. `make release` runs, in order: `npm ci && npm run build`
(maintainer machine or CI only) → `uv build --all-packages` → `scripts/check_release.py` (opens each
wheel, asserts `pcl_server/static/index.html` and `pcl_server/static/assets/*.js` exist in the
`pcl-server` wheel, asserts all five wheels share one version) → `uv publish`.

**Rationale**: hatch `artifacts` is the documented way to ship VCS-ignored files. The check step is
what makes "UI ships inside the release" a gate rather than a hope; a wheel without the UI never
reaches PyPI.

**Alternatives considered**: committing `static/` (binary churn on every UI change); a
`build.py` hook that runs npm during wheel build (drags Node into the build, breaks `uv build` on
machines without it); serving the UI from a CDN (constitution II).

### D4 — Self-pin on first launch so offline holds

**Decision**: When `personal-context-hub` (no subcommand) starts and detects it is not running from
a `uv tool` environment (`sys.prefix` not under `uv tool dir`), it runs
`uv tool install personal-context-hub==<own version>` once (subprocess, `uv` resolved with
`shutil.which`), prints one line — `Installed for offline use. Next time run: pch` — and then
**re-executes itself inside the pinned environment**: `os.execv(<tool_dir>/personal-context-hub/bin/python,
[python, "-m", "hub_desktop.cli", "--no-pin", *argv])` on POSIX; on Windows,
`subprocess.run([...\Scripts\python.exe, "-m", "hub_desktop.cli", "--no-pin", *argv])` followed by
`sys.exit(returncode)`. The interpreter path comes from `uv tool dir` (`uv tool dir --bin` for the
shim, `<uv tool dir>/personal-context-hub` for the env). `--no-pin` is an internal flag that skips
the pin step so the re-executed process cannot loop. If `uv` is not found, or the install or re-exec
fails, the launch continues in the current process and the line says offline use requires
`uv tool install personal-context-hub`; `pch doctor` then reports `pinned: false`.

**Rationale**: F13. Plain `uvx` cannot satisfy FR-004; a pinned tool can. Doing the pin from inside
the first launch keeps the README at one command. Re-executing into the pinned environment is what
makes the *running* Hub the installed one from the very first session, so `sys.executable` (used by
recipes, D5) is the stable tool-env interpreter and never uv's ephemeral cache. The exact-version
pin means the pin and the running process are the same release.

**Alternatives considered**: documenting `uv tool install personal-context-hub && pch` (two
commands; bar criterion 1); recipes and README using `uvx --offline` (fails on the *first* bridge
launch if the ephemeral env was pruned; also freezes the version forever); pinning but continuing
in the `uvx` process (rejected: first-session recipes would embed a prunable cache path — the very
failure mode above); having the recipe renderer look up the pinned interpreter instead of
`sys.executable` (works, but leaves the Hub itself running from the cache and adds a second source
of truth); a login daemon (out of scope).

### D5 — Recipes reference the running Hub's interpreter, not `uv run`

**Decision**: `catalog._bridge()` emits
`{"command": sys.executable, "args": ["-m", "pcl_sdk", "mcp-bridge"], "env": {...}}` and
`connections.connection_recipe` passes the request's actual scheme/host/port as `PCH_BASE`
(F3 fix). `python -m pcl_sdk mcp-bridge` already works (F6c); no change there.

**Rationale**: After D4's re-exec the Hub runs from `<uv tool dir>/personal-context-hub/bin/python`
(or `Scripts\python.exe`), a stable absolute path (F14) that exists after install, needs no PATH
(GUI-launched assistants often have no shell PATH), works from any cwd, and works offline. In a
source checkout the same code yields `.venv/bin/python`, so contributors keep working. Identical
for Cursor, Claude Code, Claude Desktop, ChatGPT, Hermes, OpenClaw: only the wrapper shape differs,
as today.

**Alternatives considered**: `{"command": "pch", "args": ["bridge"]}` (PATH-dependent; fails
under macOS GUI apps); `uvx personal-context-hub bridge` (F13: dies offline);
`uv tool run --offline` (first-run failure mode above).

### D6 — Encryption is checked at the packaged entry point, and reported

**Decision**: Packaged `pch` never constructs `Hub` until cipher is known good.

1. `pcl_core.vault.engine.cipher_available() -> bool` tries `import sqlcipher3` and returns False
   on any exception (no file I/O, no fallback). Engine's silent fallback stays for tests, `plain=True`,
   and `dev_app`.
2. `hub_desktop.cli.require_cipher_or_exit(data_dir)`: if `PCH_PLAIN_SQLITE != "1"` and not
   `cipher_available()`, print the two-line refusal and `sys.exit(1)` **before**
   `load_or_create_key` / `Hub` / `Engine`. Message:
   `Refusing to start: the encrypted database driver (sqlcipher3) did not load on this platform.`
   `Your vault was not opened in plaintext. Set PCH_PLAIN_SQLITE=1 only if you accept an unencrypted vault.`
3. Then `Hub(data_dir)` (never `create_app(hub=None)`). If somehow `engine.encrypted is False`
   and plain was not requested, exit 1 with the same message (belt; the probe is the contract).
4. Then `create_app(hub, sim_enabled=False, catalog_refresh=False)`.

`create_app` gains `sim_enabled: bool | None = None` (None → `PCH_SIM_ENABLED == "1"`; a non-None
`sim_hub` implies enabled) and `catalog_refresh: bool | None = None` (None → `PCH_CATALOG_REFRESH == "1"`;
packaged `pch` passes False; `dev_app` True). It sets `app.state.sim_enabled` and
`app.state.catalog_refresh`. `scheduler_loop` skips `refresh_catalog` when `catalog_refresh` is
False (F6h). The sim **router** gets a router-level
dependency: when not enabled, **every** `/v1/sim/*` route — including `POST /sim/runs` with
`target=everyday` (F6e) — returns `404 {"detail": "simulation disabled; run hub-desktop --dev or set PCH_SIM_ENABLED=1"}`
before `require_owner`. Probe route: `GET /v1/sim/runs` (there is no `/v1/sim/status`). When
enabled, `_sim_hub` opens `Hub(sim_dir, plain=True)` lazily on first use. `dev_app()` passes
`sim_enabled=True`; `test_sim_rest.py` already passes `sim_hub`.

`GET /v1/setup` (existing; not a new `/status` path) adds `encrypted` and `key_storage` via
`Hub.setup_status()`. `frontend/src/pages/Setup.tsx` renders one sentence:
"Key stored in your system keychain" or "Key stored in a private file in ~/.pch".
`frontend/src/api/types.ts` extends `SetupStatus`. `pcl_core.vault.keys.key_storage(data_dir)`.

`test_entry_refuses_plaintext.py` monkeypatches `cipher_available` → False (not
`Engine.encrypted`), asserts **no** `vault.db`, **no** `blobs/`, **no** `vault.key` under the temp
data dir, exit 1, both message lines. `test_packaged_entry_never_plain.py` records every
`Engine.__init__`: exactly one, `encrypted is True`, no `_sim/`.

`hub_desktop.cli.packaged_app(data_dir)` is the single factory used by launch, smoke, and the
offline/first-launch tests: `require_cipher_or_exit` → `Hub` →
`create_app(hub, sim_enabled=False, catalog_refresh=False)`. It does not exist today, so those
tests are collection-red until `cli.py` exists (not a copy of `test_offline.py`).

**Rationale**: F6, F6b, F6e. The probe is the only way the refusal sentence is true. Router-level
404 is the only way 011 cannot reach the everyday vault from a packaged Hub. FR-014 needs the
Setup page, not just JSON.

**Alternatives considered**: making `Engine` raise (breaks the test suite's plain mode and the sim
Hub); checking `encrypted` after `Hub(...)` (writes plaintext first; the previous draft); leaving
the sim Hub eager but encrypted (second vault; 011 chose plain for inspectability); 404 only from
`_sim_hub` (F6e).

### D7 — Loopback refusal in every installed entry point

**Decision**: `hub_desktop.cli` accepts `--host` only for parity and rejects anything not in
`{127.0.0.1, ::1, localhost}` (and other `127.0.0.0/8`) with exit code 2 and the message
`The Hub is not a public server; it binds loopback only.` The same guard is added to
`pcl_server/__main__.py`.

**Rationale**: Constitution II and 1.1.0 packaging clause; FR-006. The check is a pure function
(`hub_desktop.launch.is_loopback(host)`) with a unit test.

### D8 — Upgrade: `uv tool upgrade`, migration before serve, hash-verified

**Decision**: Documented upgrade is `uv tool upgrade personal-context-hub`; `pch upgrade` wraps it.
`Engine` gains `kv.schema_version` and a small ordered list `MIGRATIONS = [(1, add_source_key), …]`
run in `_migrate()`; still inside `Engine.__init__`, so before uvicorn binds. Test fixture:
`packages/pcl-core/tests/fixtures/vault_prev.sqlite` (plain SQLite, generated once by
`scripts/make_prev_vault.py` at the previous schema with 20 objects, versions, 3 grants, 2
connections, audit chain). The upgrade test opens the fixture with the new `Engine` and asserts
equality of counts and of `sha256` over canonical JSON for **objects, object versions, events,
connections (including their grants and tokens), and kv rows other than `schema_version`**, and
that the audit hash chain still verifies. Connections live as objects/kv in the same vault, so the
same canonical-JSON hash covers them; the test names them separately so a regression in either
table is attributable.

**Rationale**: FR-011/SC-005 need something stronger than "we did not delete anything".
`uv tool upgrade` keeps the tool's environment, so `sys.executable` in already-issued recipes stays
valid (F14).

**Alternatives considered**: Alembic (already a dependency but unused; heavier than the current
single-file schema needs; revisit if a migration ever needs data transforms); `pch upgrade`
re-running `uv tool install --reinstall` (same effect, less discoverable than uv's own verb).

### D9 — Uninstall never touches the vault by default

**Decision**: `pch uninstall` always prints
`Removed the Hub program. Your data is untouched at <data_dir> (vault.db, blobs/, vault.salt or vault.key,
plugins/). To also delete your data: pch uninstall --purge-data`
**before** touching the tool env. `--purge-data` requires typing `DELETE` (or `--yes` **together
with** `--purge-data`); then it removes `<data_dir>` and the keyring entry
`personal-context-hub/vault-key`. Without `--purge-data`, `--yes` does nothing extra. Purge of
`vault.db` is skipped with exit 1 if the file is locked (Hub still running).

Tool removal (F6g):

- POSIX: `uv tool uninstall personal-context-hub` in this process.
- Windows when `running_from_uv_tool()`: write `%TEMP%\pch-uninst-<pid>.cmd` that loops until
  this PID is gone, then runs `uv tool uninstall personal-context-hub`, then deletes itself;
  start it detached (`DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP`); print
  `The program will be removed after this window closes.`; `sys.exit(0)`.
- Windows when not in the tool env: uninstall in-process like POSIX.

`pch upgrade` on Windows in the tool env uses the same deferred helper with
`uv tool upgrade personal-context-hub`; POSIX upgrades in-process.

**Rationale**: FR-012/SC-006; Principle I. Two flags plus a typed word make silent deletion
impossible. The deferred helper is the only way the Windows matrix step `pch uninstall --yes`
can succeed while the command itself is the installed `python.exe`.

**Alternatives considered**: telling Windows users to run `uv tool uninstall` themselves (leaves
criterion 9's named step untrue on one of the three OSes); copying python.exe aside and uninstalling
in-process (fragile, still races).

### D10 — Existing vault is reused by construction

**Decision**: No code. Default data dir stays `~/.pch` (`PCH_DATA_DIR` override kept); key lookup
is unchanged (F5). A test opens a vault created by the source-checkout `Hub`, then opens the same
directory via `hub_desktop.cli`'s construction path and asserts the same objects and that no second
directory appeared.

### D11 — `pch doctor` as the verifiable install surface

**Decision**: `pch doctor [--json]` reports: version; data dir; `encrypted`; `key_storage`;
`ui_bundled` (does `pcl_server/static/index.html` exist inside the installed package);
`loopback_only: true`; `pinned` (running from a uv tool env); `uv` found; `native_window`
(GTK/Qt/WebKit/WebView2 probe result → `native` or `browser`). Exit code 0 only if `encrypted`
(or plain explicitly requested) and `ui_bundled`.

**Rationale**: It gives the CI matrix, the quickstart, and a person asking for help one
inspectable artifact, and it is how SC-002/SC-003/SC-007 are checked on each OS.

### D12 — Three operating systems, verified by a release workflow

**Decision**: New `.github/workflows/release.yml`, triggered by tag `v*`: job `build` (ubuntu):
`npm ci && npm run build`, `uv build --all-packages`, `python scripts/check_release.py`, upload
`dist/`. Job `matrix` (ubuntu-latest, macos-latest, windows-latest): download `dist/`,
`uv tool install dist/personal_context_hub-*.whl --find-links dist/`, `pch doctor --json` (assert
`encrypted`, `ui_bundled`), `pch smoke` (starts headless on a free port, GETs `/health` and `/`,
asserts the SPA `<title>`, stops), `pch uninstall --yes`, **on Windows wait up to 30s until `pch`
is gone from PATH** (deferred helper, F6g), then assert the temp data dir still exists.
Job `publish` (needs matrix green): `uv publish` with PyPI trusted publishing. Native window
expectations documented: macOS uses the system WebKit (native window); Windows uses WebView2
(present on Windows 10/11; falls back to browser if absent); Linux needs GTK or Qt bindings and is
expected to open the browser on a bare install. Windows in the matrix is `windows-latest` native,
not WSL.

**Rationale**: FR-017 and bar criterion 11 ask for per-OS verification, not names. The matrix runs
exactly the person's path (install the wheel, run `pch`). Publishing only after the matrix is green
is what makes "verified on three OSes" true for every release.

**Alternatives considered**: manual testing on three machines (not repeatable; not evidence);
only Linux CI (fails criterion 11).

### D13 — README becomes the product surface

**Decision**: README top section becomes exactly the text in `contracts/install.md` §10 (single
source; not repeated here to avoid drift). Everything that exists today (make targets, `uv sync`, npm, headless, demo agent, tests) moves to
`## Contributing (from source)` at the bottom. Pairing and Google sections stay, with the bridge
sentence updated to say the recipe already contains the right command.

**Rationale**: FR-016/SC-008. One screen, one command.

### D14 — Install writes nothing into the vault

**Decision**: First launch creates the empty encrypted vault, the key, `owner_token`,
`schema_version`, and the empty `blobs/` directory that `Hub.__init__` already mkdirs (F6d) — and
nothing else: zero objects, zero events, zero connections, zero proposals; `~/.pch` contains
`vault.db`, empty `blobs/`, and `vault.key` only when the keychain is unavailable — no `_sim/`,
no `plugins/`. `migrate_connectors(hub)` still runs inside `create_app` and is asserted to be a
no-op on the empty vault (events stay at zero). Packaged serve sets `catalog_refresh=False` so
the first scheduler tick does not write `marketplace_catalog` / `marketplace.catalog_check` (F6h).
A test asserts all of this after `TestClient(packaged_app(data_dir))` (lifespan runs one scheduler
tick). The pin step (D4) writes only under uv's tool directory. No telemetry exists and none is
added; the offline guard test (below) is the proof.

**Rationale**: FR-018. Changing BlobStore to be lazy would be an unrelated 001 change; naming
`blobs/` as expected empty infrastructure keeps the test green against the real `Hub`.

### D15 — Offline proof

**Decision**: Two checks, both named, because the bar allows either a packaged install with
network disabled **or** a loopback-only allow-list, and SC-003 asks for both 001 and 004:

1. `apps/hub-desktop/tests/test_offline_guard.py` (new file; importing
   `hub_desktop.cli.packaged_app` makes it collection-red today — it is **not** a rename of
   `packages/pcl-server/tests/integration/test_offline.py`, which stays). Installs a socket
   guard (`connect`/`getaddrinfo` raise unless loopback), opens `TestClient(packaged_app(tmp))`,
   then: POST `/v1/setup`, POST `/v1/projects` Atlas, GET `/v1/search?q=Atlas`, POST
   `/v1/mcp/tools/get_context_manifest` (004). Any non-loopback connect fails the test.
2. `pch smoke` on the **installed wheel** (release matrix, `UV_OFFLINE=1`) starts the packaged
   server, GETs `/health` and `/` (SPA title), **and** runs the same four HTTP calls as (1)
   against that loopback server, then stops. This is 001/004 against a packaged install with
   network disabled.

**Rationale**: F13 + bar criterion 4. The pytest is the allow-list variant and the red-first
gate (`packaged_app` does not exist). The matrix smoke is the packaged-install variant and
catches `uvx`/index use after pin.

**Alternatives considered**: only TestClient (misses F13 on the binary); network namespaces
(not portable to the three-OS matrix); copying `test_offline.py` (already green; not
red-before-green).

## Resolved unknowns

All Technical Context items are resolved above; no `NEEDS CLARIFICATION` remains.

## Out of scope, confirmed

Native `.dmg` / `.msi` / AppImage (F16, next spec); login autostart; cloud sync; connector
credentials (Calendar/Gmail keep `~/.pch/google_oauth.json`, optional); Alembic adoption.
