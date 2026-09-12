# CLI

Entry points from the workspace packages. Python 3.14 via uv.

## `pch` / `personal-context-hub`

Packaged user CLI (`apps/hub-desktop`). First launch of `serve` / `smoke` / default may pin the uv tool.

```bash
pch                          # native window when possible
pch serve                    # force browser
pch serve --headless --sim
pch doctor [--json]
pch smoke
pch upgrade                  # uv tool upgrade personal-context-hub
pch uninstall [--purge-data] [--yes]
pch version
```

Global / launch flags:

| Flag | Default | Notes |
|---|---|---|
| `--data-dir` | `$PCH_DATA_DIR` or `~/.pch` | Vault directory |
| `--port` | `$PCH_PORT` or `8765` | |
| `--host` | `127.0.0.1` | Non-loopback exits **2** |
| `--browser` | off | Force system browser |
| `--headless` | off | No window |
| `--sim` | off | (`serve` only) enable simulator |

`PCH_PLAIN_SQLITE=1` is the unencrypted escape hatch; packaged `pch` otherwise refuses to start without SQLCipher.

---

## `hub-desktop`

Development shell:

```bash
uv run hub-desktop --dev --reload
uv run hub-desktop --port 8765 --data-dir ~/.pch --browser
```

| Flag | Notes |
|---|---|
| `--dev` | Simulator + catalog refresh |
| `--reload` / `--no-reload` | Default on with `--dev` |
| `--port` `--data-dir` `--browser` | Same idea as `pch` |

If something healthy is already on the port, it reuses that Hub and only opens the UI.

`make desktop` runs this with the frontend watch process.

---

## `pcl-server`

Headless API used by `make serve`:

```bash
uv run pcl-server --headless --reload --host 127.0.0.1 --port 8765 --data-dir ~/.pch
```

| Flag | Default |
|---|---|
| `--headless` | off (flag exists for scripts; bind is always loopback) |
| `--host` | `127.0.0.1` (non-loopback exits 2; `::1` coerced to `127.0.0.1`) |
| `--port` | `8765` |
| `--data-dir` | `~/.pch` |
| `--reload` / `--no-reload` | default **on** |

Factory `dev_app()` enables simulator and catalog refresh.

---

## `pcl-sdk`

```bash
uv run pcl-sdk demo-agent --pair <code> --base http://127.0.0.1:8765 [--token]
uv run pcl-sdk mcp-bridge --token "$PCH_TOKEN" --base "$PCH_BASE"
uv run pcl-sdk plugin new <id> [--dest]
uv run pcl-sdk plugin validate <dir>
uv run pcl-sdk plugin pack <dir> [--out]
uv run pcl-sdk plugin dev <dir> [--hub http://127.0.0.1:8765]
uv run pcl-sdk eval run          # exit 1 if any case fails
```

### Development loop

```bash
uv run pcl-sdk loop start [--mode full|design-only] [--desc] [--epic] [--dir] [--roadmap] [--resume] [--redo STAGE]
uv run pcl-sdk loop next
uv run pcl-sdk loop record --stage specify --outcome pass|fail|blocked_on_person
uv run pcl-sdk loop record-verdict --critic A|B --verdict WIN|LOSE --round N [--failing …]
uv run pcl-sdk loop status
uv run pcl-sdk loop stop
uv run pcl-sdk loop evidence --command "pytest" --exit-code 0 --summary "…"
```

Default for new feature work: `/speckit-loop` plus this sequencer. It must not commit unless you asked, and must not treat VISION/ROADMAP as implementable features.

### Simulator harness

```bash
uv run pcl-sdk sim dump [--persona lived-stretch]
uv run pcl-sdk sim run [--persona] [--delay-ms] [--data-dir] [--target isolated|everyday] \
  [--confirm] [--paired-assistant] [--print-mcp-recipe] [--leave-proposals]
uv run pcl-sdk sim status [--data-dir]
```

`pause` / `resume` / `stop` print that those apply to the **server-hosted** simulator (`/v1/sim/runs`), not this CLI runner.

---

## `pca`

```bash
uv run pca verify-roundtrip <src_hub_dir> <dst_hub_dir>
```

Compares listed object types between two data dirs. No export subcommand — export is HTTP/UI.

---

## Make targets

Run `make help`.

| Target | Meaning |
|---|---|
| `install` | `uv sync --all-packages` + frontend build |
| `serve` | UI watch + `pcl-server --headless --reload` |
| `desktop` | UI watch + `hub-desktop --dev --reload` |
| `test` / `test-forbidden` / `test-perf` / `test-all` | pytest |
| `lint` / `format` | ruff + eslint / prettier |
| `check-secrets` | tracked-path deny-list |
| `openapi` | write `docs/openapi.json` |
| `demo-agent` | `CODE=` required |
| `bridge` | `TOKEN=` required |
| `smoke` | `pch smoke` |
| `release` | wheels + `check_release.py` + publish |
| `clean` | caches, `node_modules`, static assets, `.venv` |

Variables: `UV`, `NPM`, `PORT`, `HOST`, `DATA_DIR`, `FRONTEND`.
