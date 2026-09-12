# Getting started

Install the Hub, create a vault, and pair an agent. Nothing in this guide leaves your machine except the Google APIs you optionally connect later.

## What you need

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- A desktop that can open a window or a browser (the API always binds `127.0.0.1`)

Python 3.14 is pulled in by uv. Node.js is only required if you build the UI from source.

## Install and launch

```bash
uvx personal-context-hub
```

The first run pins the tool so later you can type `pch`. The Hub listens on `http://127.0.0.1:8765` by default and opens a native window when pywebview is available, otherwise your browser.

Useful variants:

```bash
pch                  # launch again
pch serve            # force the system browser
pch serve --headless # API + UI, no window
pch doctor           # encryption, UI, loopback, port
pch version
```

Override the data directory or port with `--data-dir` / `--port`, or `PCH_DATA_DIR` / `PCH_PORT`. Full flags: [CLI](reference/cli.md).

## First-run setup

1. Open the Hub. The **Home** page (`/`) initializes the vault and shows encryption status.
2. Give yourself a name if prompted. Setup returns an **owner token** the local UI stores via `GET /v1/bootstrap`.
3. Create a **project** (for example “Europe trip”) under **Projects**. This is the usual anchor for a grant.

The vault file is `~/.pch/vault.db`, encrypted with SQLCipher. The key lives in the OS keyring when available. See [Configuration](reference/configuration.md).

## Pair an assistant (five minutes)

The Hub does not scrape your chats. An assistant sees only what a **grant** allows.

1. Go to **Agents** (`/connections`).
2. Create a pairing link and copy the code (or use the generated recipe).
3. Choose a runtime — Cursor is the primary validated target.
4. Paste the MCP snippet into that runtime’s **user / machine** MCP settings so every window can reach the Hub.
5. Back in the Hub, grant a preset such as **Can read a specific project** and pick the project.

Then, in the assistant, ask something that depends on who you are — “help me continue planning the trip.” A well-behaved client calls `get_context_contract` with a purpose string before inventing facts.

Full walkthrough: [Pair an agent](guides/pair-an-agent.md). What comes back: [Situation package](guides/situation-package.md). Tool catalog: [MCP reference](reference/mcp.md).

### Cursor recipe shape

The Connections page generates this for you. Do not commit `.cursor/mcp.json` — it contains a live token.

```json
{
  "mcpServers": {
    "personal-context-hub": {
      "command": "<python>",
      "args": ["-m", "pcl_sdk", "mcp-bridge"],
      "env": {
        "PCH_TOKEN": "<connection-token>",
        "PCH_BASE": "http://127.0.0.1:8765"
      }
    }
  }
}
```

From a source checkout you can also run `make bridge TOKEN=...`.

## Optional: Calendar and Gmail

You must create a Google Cloud **Desktop app** OAuth client. The Hub never ships a shared client ID.

Write `~/.pch/google_oauth.json` (mode `0600`):

```json
{
  "client_id": "xxxxx.apps.googleusercontent.com",
  "client_secret": "xxxxx"
}
```

Authorized redirect URI: `http://127.0.0.1:8765/v1/connectors/oauth/callback`.

Then **Connectors** in the UI. Calendar → `private` events. Gmail → only the labels, senders, or dates you select, as `sensitive` artifacts.

Details: [Google connectors](guides/google-connectors.md).

## Optional: from source

If you are developing the Hub itself:

```bash
git clone <this-repo>
cd pcl
make install
make serve
```

See [CONTRIBUTING.md](../CONTRIBUTING.md) and [Architecture](architecture.md).

## Check that it works

```bash
curl -s http://127.0.0.1:8765/health
# {"ok": true}

pch doctor
pch smoke    # in-process: setup, project, search, pair, grant, manifest
```

Interactive HTTP docs while the server is up: [http://127.0.0.1:8765/docs](http://127.0.0.1:8765/docs).

## Uninstall

```bash
pch uninstall              # remove the uv tool; keep ~/.pch
pch uninstall --purge-data # also delete the vault
```

## Troubleshooting

| Symptom | What to check |
|---|---|
| `invalid_client` from Google | You used a missing or web client ID. Create a **Desktop app** client and write `~/.pch/google_oauth.json`. |
| Hub refuses to start / SQLCipher | Packaged `pch` needs sqlcipher3. It will not open a plaintext vault unless you set `PCH_PLAIN_SQLITE=1`. |
| Non-loopback host rejected (exit 2) | The Hub binds `127.0.0.1` only. Do not pass `0.0.0.0`. |
| Assistant has no tools | Recipe `PCH_BASE` must match the running port; reload MCP; grant is separate from pairing. |
| Empty situation package | Grant selector vs project id; classification ceiling vs `sensitive` mail; revoked connection. |
| Port already in use | `hub-desktop` reuses a healthy Hub on that port. Or `PCH_PORT=8766 pch`. |

`pch doctor` prints version, encryption, UI, loopback, and pin status.

## Next

- [Concepts](concepts.md) — memory, context, situation, grants
- [The Hub UI](guides/the-hub-ui.md) — every page
- [Security](security.md) — encryption, least privilege, reporting
