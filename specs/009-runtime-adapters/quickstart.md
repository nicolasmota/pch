# Quickstart: Runtime Adapters

**Feature**: `specs/009-runtime-adapters/`
Prove two real-use assistants consume the same trip package, and that switching one does not rewrite the Hub.

Requires `make serve`, an existing Europe Trip (or create it), and Connections.

## 1. Catalog names the runtimes

Open **Connections**. The assistant picker lists **Hermes** and **OpenClaw** (and still **Cursor**). They are not disabled placeholders.

`GET /v1/catalog/assistants` includes `id=hermes` and `id=openclaw` with `supported: true`.

## 2. Copy a native recipe

Create a pairing link. Pick **Hermes** → Generate recipe. Instructions mention `~/.hermes/config.yaml` and `mcp_servers`. Snippet is that YAML shape, not Cursor’s `mcpServers` envelope.

Repeat for **OpenClaw**: `~/.openclaw/openclaw.json` / `mcp.servers`.

Unknown assistant id → 422. `PCH_BASE` is `http://127.0.0.1:8765`.

Manual (optional): paste into a live Hermes or OpenClaw session and reload MCP. CI does not require those desktops.

## 3. Two real-use connections, same package

Pair two connections (Cursor + Hermes, or Hermes + OpenClaw). Same grant, same trip project if scoped. Each calls `get_context_contract` with purpose `"continue planning the trip"`.

Expect both payloads:

- same `situation.project_id` (Europe Trip)
- same live goals
- E3 phase / E4 relations if you set them
- **no** second tool name

## 4. Switch without re-editing

Revoke the first connection. Pair the second (or keep the second). Next package still names Europe Trip, budget preference, and phase if set. Projects list is unchanged.

## 5. Isolation

Work-scoped grant on a connection using a Hermes or OpenClaw recipe: zero personal trip titles or ids.

## 6. What not to do

Do not count demo-agent as a real-use runtime. Do not add `get_openclaw_context`. Do not bind the Hub off loopback so a “remote MCP URL” looks easier.
