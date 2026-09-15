# CLI

Entry points from the workspace packages. Python 3.12 or newer via uv.

## `pch` / `personal-context-hub`

Packaged user CLI (`apps/hub-desktop`). Product install: `uvx personal-context-hub` or `uv tool install personal-context-hub`. From a checkout, after `make install`, use `uv run pch` (the script lives in `.venv/bin`). Checkout launch does not install from a public index until a real index copy exists.

```bash
pch                                 # native window when possible
pch serve                           # force browser
pch serve --headless --sim
pch doctor [--json]
pch capture [--title TITLE] STATEMENT...
pch smoke
pch upgrade                         # exits 2 until a public-index copy exists
pch uninstall [--purge-data] [--yes]
pch version
```

Checkout equivalents use `uv run pch` with the same subcommands.

Global / launch flags:

| Flag | Default | Notes |
|---|---|---|
| `--data-dir` | `$PCH_DATA_DIR` or `~/.pch` | Vault directory |
| `--port` | `$PCH_PORT` or `8765` | |
| `--host` | `127.0.0.1` | Non-loopback exits **2** |
| `--browser` | off | Force system browser |
| `--headless` | off | No window |
| `--sim` | off | (`serve` only) enable simulator |

`pch capture` writes an owner-confirmed live fact against `--data-dir`. It does not bind a port and is not a pinning verb. When nothing is in play, `--title` and a fact are both required. When a situation is already in play, a fact alone attaches there. Incomplete input writes nothing.

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
| `--dev` | Default `--reload` on (Python/plugin file watch). Does **not** enable the simulator. |
| `--reload` / `--no-reload` | Default on with `--dev` |
| `--port` `--data-dir` `--browser` | Same idea as `pch` |

If something healthy is already on the port, it reuses that Hub and only opens the UI.

Simulator routes stay off unless `PCH_SIM_ENABLED=1`. Catalog refresh stays off unless `PCH_CATALOG_REFRESH=1`.

`make desktop` runs this with the frontend watch process.

---

## `pch-server`

Headless API used by `make serve`:

```bash
uv run pch-server --headless --reload --host 127.0.0.1 --port 8765 --data-dir ~/.pch
```

| Flag | Default |
|---|---|
| `--headless` | off (flag exists for scripts; bind is always loopback) |
| `--host` | `127.0.0.1` (non-loopback exits 2; `::1` coerced to `127.0.0.1`) |
| `--port` | `8765` |
| `--data-dir` | `~/.pch` |
| `--reload` / `--no-reload` | default **on** |

Factory `dev_app()` is the reload target for `pch-server`. Simulator and catalog refresh stay off unless `PCH_SIM_ENABLED=1` / `PCH_CATALOG_REFRESH=1`.

---

## `pch-sdk`

```bash
uv run pch-sdk demo-agent --pair <code> --base http://127.0.0.1:8765 [--token]
uv run pch-sdk mcp-bridge --token "$PCH_TOKEN" --base "$PCH_BASE"
uv run pch-sdk plugin new <id> [--dest]
uv run pch-sdk plugin validate <dir>
uv run pch-sdk plugin pack <dir> [--out]
uv run pch-sdk plugin dev <dir> [--hub http://127.0.0.1:8765]
```

`pch-sdk` does not run loop, sim, or eval. Use `pch-lab` for those.

---

## `pch-lab`

Repository tooling. Not the user SDK.

### Development loop

```bash
uv run pch-lab loop start [--mode full|design-only] [--desc] [--epic] [--dir] [--roadmap] [--resume] [--redo STAGE]
uv run pch-lab loop next
uv run pch-lab loop record --stage specify --outcome pass|fail|blocked_on_person
uv run pch-lab loop record-verdict --critic A|B --verdict WIN|LOSE --round N [--failing …]
uv run pch-lab loop status
uv run pch-lab loop stop
uv run pch-lab loop evidence --command "pytest" --exit-code 0 --summary "…"
```

Default for new feature work: `/speckit-loop` plus this sequencer. It must not commit unless you asked, and must not treat VISION/ROADMAP as implementable features.

### Simulator harness

```bash
uv run pch-lab sim dump [--persona lived-stretch]
uv run pch-lab sim run [--persona] [--delay-ms] [--data-dir] [--target isolated|everyday] \
  [--confirm] [--paired-assistant] [--print-mcp-recipe] [--leave-proposals]
uv run pch-lab sim status [--data-dir]
```

`pause` / `resume` / `stop` print that those apply to the **server-hosted** simulator (`/v1/sim/runs`), not this CLI runner.

### Eval

```bash
uv run pch-lab eval run          # exit 1 if any case fails
```

---

## `pch-archive`

```bash
uv run pch-archive verify-roundtrip <src_hub_dir> <dst_hub_dir>
```

Compares listed object types between two data dirs. No export subcommand — export is HTTP/UI.

---

## Make targets

Run `make help`.

| Target | Meaning |
|---|---|
| `install` | `uv sync --all-packages` + frontend build |
| `serve` | UI watch + `pch-server --headless --reload` |
| `desktop` | UI watch + `hub-desktop --dev --reload` |
| `test` / `test-forbidden` / `test-perf` / `test-all` / `test-dist` | pytest (`test-dist` is packaged wheel install) |
| `lint` / `format` | ruff + eslint / prettier |
| `check-secrets` | tracked-path deny-list |
| `openapi` | write `docs/openapi.json` |
| `demo-agent` | `CODE=` required |
| `bridge` | `TOKEN=` required |
| `smoke` | `pch smoke` |
| `dist` | wheels + `check_release.py` (no publish) |
| `release` | `dist` + publish |
| `clean` | caches, `node_modules`, static assets, `.venv` |

Variables: `UV`, `NPM`, `PORT`, `HOST`, `DATA_DIR`, `FRONTEND`.
