# Personal Context Hub

Local-first home for your personal context. Agents connect; the context stays yours.

## Prerequisites

- Python 3.14
- [uv](https://docs.astral.sh/uv/)
- Node.js 22+ (UI build only; not required at runtime)

## Setup

```bash
make install          # uv sync + frontend build
make serve            # API with auto-reload (Python + UI watch)
make desktop          # Hub with auto-reload (Python + UI watch)
make test             # pytest
make help             # all targets
```

Without Make:

```bash
uv sync
(cd frontend && npm ci && npm run build)
uv run pcl-server --headless --reload
# or, with the native/browser shell:
uv run hub-desktop --dev --reload
# UI rebuilds: (cd frontend && npm run build:watch)
```

Headless API (no window):

```bash
uv run pcl-server --headless
```

OpenAPI: `http://127.0.0.1:8765/v1/openapi.json`

Reference agent:

```bash
uv run pcl-sdk demo-agent --pair <link>
```

## Tests

```bash
uv run pytest
uv run pytest -m forbidden_context
uv run pytest -m perf
```

See `specs/001-personal-context-hub/quickstart.md` for the six validation scenarios.

## Connect a real assistant (Cursor)

1. Start the hub: `make serve`
2. Open Connections, create a pairing link, pick **Cursor**, generate the recipe, copy the JSON.
3. Paste into `.cursor/mcp.json` (or Cursor MCP settings).
4. Grant the connection a preset. Ask Cursor a question about your vault.

The bridge is `uv run pcl-sdk mcp-bridge` with `PCH_TOKEN` and `PCH_BASE`. Convenience: `make bridge TOKEN=...`

## Google Calendar / Gmail

Google requires **your** OAuth client. The Hub never ships a shared client ID (that is what caused `invalid_client`).

1. In [Google Cloud Console](https://console.cloud.google.com/apis/credentials) create a project.
2. Enable **Google Calendar API** and **Gmail API**.
3. Create OAuth credentials of type **Desktop app**. Copy the client ID (and secret if shown).
4. Add authorized redirect URI: `http://127.0.0.1:8765/v1/connectors/oauth/callback`
5. Write `~/.pch/google_oauth.json`:

```json
{
  "client_id": "xxxxx.apps.googleusercontent.com",
  "client_secret": "xxxxx"
}
```

6. Restart the Hub (`make desktop`), then Connect from the Connectors page.

Calendar events import as `private`. Gmail imports only the labels/senders/dates you select, as `sensitive` artifacts.

## Plugins

Optional import capabilities run as sandboxed plugins. See `plugins/README.md` for the developer kit (`pcl-sdk plugin new|validate|pack`) and bundled Calendar/Gmail/RSS plugins. The Hub UI has **Plugins** and **Marketplace** pages.
