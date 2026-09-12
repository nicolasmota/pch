# Personal Context Hub

Local-first home for your personal context. Agents connect; the context stays yours.

Your data lives on this device (default `~/.pch`), encrypted. The Hub binds **loopback only** (`127.0.0.1`) and is not a public server.

> **Your agent can change. Your context shouldn’t.**

You tell one agent you are planning a ten-day trip for two, Amsterdam or London. You open a different agent and say only: continue planning the trip. It already knows the goal, the people, the candidates — because the Hub assembled a **situation package** under a grant you approved. You drop London. Every agent you have authorized sees Amsterdam as the live one.

That is the product: a portable record of who you are and what you are doing, plus the smallest sufficient slice for the task at hand. Not a chatbot. Not a model. Not a vector database.

**Documentation:** [docs/](docs/README.md) · **Thesis:** [docs/VISION.md](docs/VISION.md) · **License:** [MIT](LICENSE)

[Getting started](docs/getting-started.md) · [Concepts](docs/concepts.md) · [Pair an agent](docs/guides/pair-an-agent.md) · [MCP reference](docs/reference/mcp.md) · [HTTP API](docs/reference/http-api.md) · [Security](docs/security.md)

---

## Install

Needs [uv](https://docs.astral.sh/uv/getting-started/installation/) (one line to install). Then:

```bash
uvx personal-context-hub
```

The Hub opens on your machine. No account, no API key, nothing leaves your device.

| Next time | Upgrade | Remove |
|---|---|---|
| `pch` | `uv tool upgrade personal-context-hub` or `pch upgrade` | `pch uninstall` |

Uninstall keeps `~/.pch` unless you pass `--purge-data`.

Health check: `pch doctor`. Headless (browser only): `pch serve`.

## Connect an assistant

1. Open **Agents** in the Hub and create a pairing link.
2. Pick your runtime (Cursor, Claude Code, Claude Desktop, ChatGPT, Hermes, or OpenClaw) and copy the recipe.
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
make serve            # API with auto-reload (Python + UI watch)
make desktop          # Hub with auto-reload (Python + UI watch)
make test             # pytest
make lint             # ruff + eslint
make help             # all targets
```

Requires Python 3.14, [uv](https://docs.astral.sh/uv/), and Node.js 22+ (UI build only).

While running: interactive API docs at `http://127.0.0.1:8765/docs`, schema at `http://127.0.0.1:8765/openapi.json`.

## Repository

| Path | Role |
|---|---|
| `packages/pcl-core` | Vault, schema, policy, retrieval (no network) |
| `packages/pcl-server` | Loopback HTTP, plugin host, connectors, MCP |
| `packages/pcl-sdk` | CLI, MCP stdio bridge, plugin kit |
| `packages/pca` | Portable Context Archive export/import |
| `apps/hub-desktop` | `pch` / pywebview shell |
| `frontend/` | React 19 UI, built into `pcl-server` static |
| `plugins/` | Bundled import plugins (Calendar, Gmail, example RSS) |

Architecture: [docs/architecture.md](docs/architecture.md).

## Community

- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Roadmap](docs/ROADMAP.md) — operational epics; spawn Speckit features from here, do not implement the roadmap document itself
