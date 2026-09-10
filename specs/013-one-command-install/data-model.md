# Data Model: One-Command Install

**Feature**: `specs/013-one-command-install/` | **Date**: 2026-09-07

No vault object types are added. The entities below are release artifacts, filesystem state, CLI
report shapes, and one extended read model (`GET /v1/setup`). All live outside the vault except the
single `kv.schema_version` row.

## Release

A published set of five distributions at one version.

| Field | Type | Rule |
|-------|------|------|
| `version` | `MAJOR.MINOR.PATCH` | Identical across all five wheels; `scripts/check_release.py` fails otherwise |
| `distributions` | list | `pcl-core`, `pcl-pca`, `pcl-sdk`, `pcl-server`, `personal-context-hub` |
| `console_scripts` | map | `personal-context-hub` → `hub_desktop.cli:main`; `pch` → same; `hub-desktop` (dev), `pcl-server`, `pcl-sdk`, `pca` unchanged |
| `ui_bundled` | bool | `pcl-server` wheel contains `pcl_server/static/index.html` and `pcl_server/static/assets/*.js`; gate before publish |
| `pins` | map | Each inter-package dependency is `==version` in `[project.dependencies]` |
| `python` | `>=3.14` | uv fetches it; no system Python required |

State: `built` → `checked` (wheel inspection passed) → `matrix_green` (three OS jobs passed) →
`published`. A Release never moves to `published` from `built` or `checked`.

## Data directory

The person's local home for everything durable. Unchanged layout; this feature adds one kv row.

| Path (under `PCH_DATA_DIR`, default `~/.pch`) | Owner | Install | Upgrade | Uninstall | Uninstall `--purge-data` |
|---|---|---|---|---|---|
| `vault.db` | Hub | created empty, encrypted | migrated in place | untouched | removed after typed `DELETE` |
| `blobs/` | Hub | created empty (`BlobStore.mkdir`, F6d) | untouched | untouched | removed |
| `vault.salt` (passphrase mode) / `vault.key` (file fallback, `0600`) | Hub | created if needed | untouched | untouched | removed |
| keyring entry `personal-context-hub` / `vault-key` | OS keychain | created if keychain available | untouched | untouched | removed |
| `plugins/`, `google_oauth.json` | Hub / person | not created | untouched | untouched | removed |
| `_sim/` (011 simulation vault, plaintext by design) | Hub (dev only) | **not created**: packaged launch passes `sim_enabled=False`; created lazily only by `hub-desktop --dev` / `PCH_SIM_ENABLED=1` on first `/v1/sim` request | untouched | untouched | removed |
| `kv.schema_version` (inside `vault.db`) | Engine | set to current | advanced by ordered `MIGRATIONS` | — | — |

Invariants:

- One data directory per OS user; the packaged entry point never creates a second one when
  `~/.pch` already exists (FR-013).
- After first launch: `objects = 0`, `events = 0`, `connections = 0`, `proposals = 0` (FR-018).
  `kv.owner_token` and `kv.schema_version` are the only rows written; `migrate_connectors` is a
  no-op on the empty vault. The directory listing is `vault.db`, empty `blobs/`, and `vault.key`
  only when the keychain is unavailable. Exactly one `Engine` is constructed, and it is encrypted.
  Packaged refusal (cipher missing) creates **none** of those paths. After `TestClient(packaged_app)`
  (one scheduler tick): still zero events and no `kv.marketplace_catalog` (F6h).
- `schema_version` is monotonic; `_migrate()` applies every `(n, fn)` with `n > current` in order
  inside `Engine.__init__`, before any request is served.

## Pin state

Whether the running Hub is the persistent `uv tool` install or an ephemeral `uvx` environment.

| Field | Type | Source |
|-------|------|--------|
| `pinned` | bool | `sys.prefix` is under `uv tool dir` (`running_from_uv_tool()`) |
| `uv_path` | `str \| None` | `shutil.which("uv")` |
| `pinned_interpreter` | `path \| None` | `<uv tool dir>/personal-context-hub/bin/python` (POSIX) or `…\Scripts\python.exe` (Windows), if it exists |
| `pin_action` | enum `none` / `installed` / `skipped_no_uv` / `failed` | Result of `ensure_pinned(version)` on launch |
| `reexec` | bool | Whether launch replaced the current process with `pinned_interpreter -m hub_desktop.cli --no-pin …` |

Transitions: `uvx` first run → `ensure_pinned` → `installed` (prints one line) → `reexec=true` →
the process that actually serves has `pinned=true`, `pin_action=none` (it was started with
`--no-pin`). Later runs via `pch` are `pinned=true` from the start. `skipped_no_uv` / `failed` →
`reexec=false`, launch continues in the current process; `doctor` reports `pinned=false` and the
offline caveat.

Invariant: whenever `pinned=true`, `sys.executable == pinned_interpreter`, so recipes (below)
reference the installed environment, never uv's ephemeral cache.

## Recipe (extended)

Existing pairing recipe; two fields change shape. Rendered by `pcl_server.pairing.catalog.render_recipe`.

| Field | Before | After |
|-------|--------|-------|
| `snippet.*.command` | `"uv"` | absolute path of the interpreter running the Hub (`sys.executable`) |
| `snippet.*.args` | `["run", "pcl-sdk", "mcp-bridge"]` | `["-m", "pcl_sdk", "mcp-bridge"]` |
| `snippet.*.env.PCH_BASE` | `"http://127.0.0.1:8765"` (hardcoded) | scheme + host + port of the request that issued the recipe |
| `snippet.*.env.PCH_TOKEN` | connection token | unchanged |
| `assistant`, `format`, `instructions`, `runtime_rule` | — | unchanged |

Validation rules (tested):

- `command` is absolute, exists, is executable, and contains no `uv run`.
- When `running_from_uv_tool()`, `command` is under `uv tool dir` (never under uv's cache).
- Spawning `command args…` with the recipe's `env` from an unrelated cwd against a live loopback
  Hub completes MCP `initialize` and `tools/call` `search_personal_context` (empty hits ok);
  a wrong `PCH_BASE` or token yields `Hub unreachable` and fails the test.
- `PCH_BASE` host is loopback; port equals the serving port.
- Identical `command`/`args` across all six supported assistants; only wrapper keys differ.

## Doctor report

Output of `pch doctor [--json]`.

| Field | Type | Meaning | Affects exit code |
|-------|------|---------|-------------------|
| `version` | str | Release version | no |
| `data_dir` | path | Resolved data directory | no |
| `encrypted` | bool | `Engine.encrypted` on the real vault | yes: `false` and `PCH_PLAIN_SQLITE!=1` → exit 1 |
| `key_storage` | `keychain` / `file` | From `pcl_core.vault.keys.key_storage` | no |
| `ui_bundled` | bool | `static/index.html` present in installed `pcl_server` | yes: `false` → exit 1 |
| `loopback_only` | `true` | Constant; documents the guarantee | no |
| `pinned` | bool | Pin state | no |
| `pinned_interpreter` | `str \| null` | `pin.pinned_interpreter()`; equals `sys.executable` when `pinned` | no |
| `sim_enabled` | `false` | Constant for the packaged entry point | no |
| `uv` | `str \| null` | Path to uv or null | no |
| `native_window` | `native` / `browser` | Result of toolkit probe | no |
| `port` | int | Port a launch would use now (`choose_port`) | no |

## Setup status (extended read model)

`GET /v1/setup` (existing) adds two fields, populated from `Hub.setup_status()`:

| Field | Type | Source |
|-------|------|--------|
| `encrypted` | bool | `hub.engine.encrypted` |
| `key_storage` | `keychain` / `file` | `key_storage(hub.data_dir)` |

The first-run screen renders one sentence from these; no other UI change.

## Simulation switch (extended app factory input)

| Input | Type | Effect |
|-------|------|--------|
| `create_app(..., sim_enabled=None)` | `bool \| None` | `None` → `PCH_SIM_ENABLED == "1"`; explicit `sim_hub=` implies enabled |
| enabled | — | `app.state.sim_dir` set; `sim_hub` opened lazily on first `/v1/sim/*` request (plaintext, as 011 designed) |
| disabled (packaged `pch`) | — | `app.state.sim_enabled = False`, `sim_hub = None`, `catalog_refresh = False`; **router-level** 404 on every `/v1/sim/*` route including `POST /sim/runs` `target=everyday`; no `_sim/` on disk; scheduler does not write `marketplace_catalog` |

## Uninstall request

Input to `pch uninstall`.

| Flag | Effect |
|------|--------|
| (none) | Print data location; POSIX: `uv tool uninstall`; Windows-in-tool-env: deferred helper (F6g); exit 0 |
| `--purge-data` | After tool removal, prompt `Type DELETE to remove <data_dir> and the keychain entry:`; on exact match remove both; anything else → exit 1 with data untouched |
| `--yes` | Only meaningful **with** `--purge-data`: skips the prompt. Alone: no additional effect |

## Relationships

```text
Release ──published as──▶ uv tool env ──runs──▶ Hub ──owns──▶ Data directory
                               │                  │
                               │                  └──issues──▶ Recipe (command = env's interpreter)
                               └──reported by──▶ Doctor report
```
