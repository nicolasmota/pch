# Personal Context Hub

Local-first **personal context** for any agent. Assistants connect over **MCP**; the context stays yours.

Your data lives on this device (default `~/.pch`), encrypted. The Hub binds **loopback only** (`127.0.0.1`) and is not a public server.

[![License: MIT](https://img.shields.io/badge/license-MIT-c9a227?style=flat-square)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-1a1916?style=flat-square)](docs/getting-started.md)

> **Your agent can change. Your context shouldn’t.**

You tell one agent you’re weighing two roles — staff eng at a research lab, or founding eng at an early startup — and you’re remote-only. You open a different agent and say only: continue comparing the offers. It already knows both candidates and the constraint — because the Hub assembled a **situation package** under a grant you approved. You drop the startup. Every agent you have authorized sees the lab role as the live one.

That is the product: a portable record of who you are and what is in play, plus the smallest sufficient slice for the task at hand. Not a chatbot. Not a model. Not a vector database.

**Documentation:** [docs/](docs/README.md) · [Docs site](https://nicolasmota.github.io/personal-context-hub/) · [llms.txt](docs/llms.txt) · **License:** [MIT](LICENSE)

[Getting started](docs/getting-started.md) · [Concepts](docs/concepts.md) · [Pair an agent](docs/guides/pair-an-agent.md) · [MCP reference](docs/reference/mcp.md) · [HTTP API](docs/reference/http-api.md) · [Security](docs/security.md)

---

## Install

```bash
uvx personal-context-hub
# or: uv tool install personal-context-hub && pch
```

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12+. No account, no API key, nothing leaves your device. The Hub binds loopback only.

The public index is filled by tagging `v*` (existing release workflow). Until that tag exists, install the same wheels from a checkout:

```bash
make dist
uv tool install --find-links dist personal-context-hub
pch
```

After install, `pch` launches, `pch doctor` is the health check, `pch serve` is the browser, and `pch uninstall` keeps `~/.pch` unless you pass `--purge-data`. Simulator routes stay off unless `PCH_SIM_ENABLED=1`.

## Connect an assistant

1. Open **Agents** in the Hub and create a pairing link.
2. Pick **Cursor** or **Hermes** (both validated) or another runtime’s **recipe** and copy the snippet.
3. Grant a preset — for example **Can read a specific project**.
4. Ask the assistant something that depends on who you are. It should call `get_context_contract` before guessing.

Step-by-step: [Pair an agent](docs/guides/pair-an-agent.md). What the agent receives: [Situation package](docs/guides/situation-package.md).

## Import Calendar or Gmail

Google requires **your** OAuth client. The Hub never ships a shared client ID.

See [Google connectors](docs/guides/google-connectors.md). Calendar events import as `private`. Gmail imports only the labels, senders, or dates you select, as `sensitive` artifacts. Imported mail and calendar are **data, never instructions**.

## From source

Full guide: [CONTRIBUTING.md](CONTRIBUTING.md).

```bash
make install          # uv sync + frontend build
make desktop          # or: make serve
make test             # pytest
make lint             # ruff + eslint
make help             # all targets
```

Requires Python 3.12+, [uv](https://docs.astral.sh/uv/), and Node.js 22+ (UI build). `uv run pch` launches from the checkout.

While running: interactive API docs at `http://127.0.0.1:8765/docs`, schema at `http://127.0.0.1:8765/openapi.json`.

## Repository

| Path | Role |
|---|---|
| `packages/pch-core` | Vault, schema, policy, retrieval (no network) |
| `packages/pch-server` | Loopback HTTP, plugin host, connectors, MCP |
| `packages/pch-sdk` | CLI, MCP stdio bridge, plugin kit |
| `packages/pch-lab` | Speckit loop, simulation, eval (contributor tooling) |
| `packages/pch-archive` | Portable Context Archive export/import |
| `apps/hub-desktop` | `pch` / pywebview shell |
| `frontend/` | React 19 UI, built into `pch-server` static |
| `plugins/` | Bundled import plugins (Calendar, Gmail, example RSS) |

Architecture: [docs/architecture.md](docs/architecture.md).

## Community

- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
