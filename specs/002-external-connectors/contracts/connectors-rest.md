# REST Contract: Connectors & Assistant Catalog

**Feature**: 002-external-connectors | Base path: `/v1` | Auth: owner bearer token (all routes below are owner-only)

Extends the 001 REST control plane. Error envelope, idempotency middleware, and audit semantics are unchanged.

## Assistant catalog & recipes

### `GET /catalog/assistants`

Returns the static catalog.

```json
[
  {"id": "cursor", "name": "Cursor", "supported": true, "notes": "Primary validated target"},
  {"id": "claude-code", "name": "Claude Code", "supported": true, "notes": ""},
  {"id": "claude-desktop", "name": "Claude Desktop", "supported": true, "notes": "On WSL, run the bridge inside WSL"},
  {"id": "chatgpt", "name": "ChatGPT", "supported": true, "notes": "Requires MCP connector availability on the user's plan"}
]
```

### `POST /connections/{connection_id}/recipe`

Body: `{"assistant": "cursor"}`. Renders the assistant's recipe for an existing paired connection (or a pending one — token is minted at pairing, not here). Emits `connection.recipe_issued` audit event.

Response:

```json
{
  "assistant": "cursor",
  "instructions": "Add this to .cursor/mcp.json, then reload MCP servers.",
  "snippet": {
    "mcpServers": {
      "personal-context-hub": {
        "command": "uv",
        "args": ["run", "pcl-sdk", "mcp-bridge"],
        "env": {"PCH_TOKEN": "<connection token>", "PCH_BASE": "http://127.0.0.1:8765"}
      }
    }
  }
}
```

Errors: `404` unknown connection · `400` unknown/unsupported assistant (unsupported entries cannot render recipes).

## Connector accounts

### `POST /connectors`

Start consent. Body: `{"provider": "google", "kind": "calendar" | "email"}`.

Response `202`: `{"connector_id": "cxa_…", "consent_url": "https://accounts.google.com/…", "status": "pending_consent"}`.

The Hub completes the loopback OAuth redirect in the background; the UI polls `GET /connectors/{id}` until `status` is `active` (consent granted) or the record disappears (consent denied/timeout — nothing is stored, per FR-006).

### `GET /connectors` / `GET /connectors/{id}`

List/detail of `connector_account` objects (never includes tokens). Detail includes `last_sync`, `selection`, `cadence_minutes`, `status`.

### `PATCH /connectors/{id}`

Update `selection` (email selection must remain non-empty — `422` otherwise, FR-015) or `cadence_minutes`. `If-Match` version header semantics as in 001.

### `POST /connectors/{id}/sync`

Manual "sync now". `409` if a run is already in progress. Response: the completed `last_sync` summary. Every run (manual or scheduled) appends a `connector.sync` audit event (FR-009).

### `POST /connectors/{id}/pause` / `POST /connectors/{id}/resume`

Toggle background cadence. Paused connectors still serve already-imported data.

### `DELETE /connectors/{id}?purge=(true|false)`

Disconnect (FR-010). Stops syncs immediately, deletes the stored token, sets status `disconnected`. `purge=true` additionally tombstones all objects whose `source_key` belongs to this connector; `purge=false` (default) keeps them, marked no-longer-syncing via the connector status.

## Imported data access

No new read endpoints: events and email artifacts flow through the existing `/v1/search`, `/v1/mcp/tools/search_personal_context`, and brief endpoints, subject to grants/classification (FR-014, FR-016). Convenience filter added: `GET /v1/search?type=event&from=<iso>&to=<iso>` for schedule ranges.

## Contract tests

1. Consent flow: `POST /connectors` → mock provider → `active` status; denied consent stores nothing.
2. Dedup: same fixture synced twice → identical object count, versions bumped only on change (FR-012).
3. Email ceiling: preset grant (`private` ceiling) search over email topics → redaction notice, zero email content (SC-006).
4. Injection: fixture event/message containing tool-invocation text → retrieval returns it as data; zero grant/policy/action changes (SC-008).
5. Disconnect: `DELETE` with and without `purge`; token gone from `kv` in both cases (SC-007).
