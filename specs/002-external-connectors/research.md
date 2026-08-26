# Phase 0 Research: External Connectors

**Feature**: 002-external-connectors | **Date**: 2026-08-21

Every unknown deferred by `/speckit-clarify` is resolved here. Format per decision: Decision / Rationale / Alternatives considered.

## R1. How real assistants connect (pairing transport)

**Decision**: Ship an **MCP stdio bridge** as `uv run pcl-sdk mcp-bridge --token <paired-token> --base http://127.0.0.1:8765`. The bridge is a standard MCP server over stdio that forwards each tool call to the Hub's existing REST tool facade (`POST /v1/mcp/tools/{name}`) with the connection's bearer token. The Connections page generates, per assistant, a ready-to-paste config block — for Cursor, a complete `.cursor/mcp.json` entry with the command and env; for Claude Desktop/Code and ChatGPT-with-MCP, their equivalent config shapes.

**Rationale**:
- Every MCP-capable client supports stdio servers; none require the Hub to expose a new network protocol. The Hub's loopback-only, bearer-authenticated surface stays exactly as audited in 001 (FR-005).
- Auth is solved for free: the pairing token from 001 rides in the bridge's env; the Hub sees the same per-connection identity it already policy-checks and audits (FR-002, FR-003). Revocation (FR-004) works unchanged — the facade returns the revocation error and the bridge surfaces it as an MCP tool error.
- On WSL2, Cursor runs commands inside the workspace's environment, so stdio needs no Windows↔WSL networking at all — decisive for the primary validation target chosen in clarification.

**Alternatives considered**:
- *Mount Streamable HTTP MCP directly in FastAPI*: cleanest long-term, but the installed `mcp` 2.0 SDK's server surface changed (no `mcp.server.fastmcp`), auth header injection varies per client, and it adds a second protocol server to the audited surface. Deferred to a follow-on; the REST facade is already the single choke point.
- *Per-assistant native plugins/GPT actions*: one integration per vendor, each with its own review process; violates "agents are replaceable clients".

## R2. Google OAuth on a local-first device

**Decision**: OAuth 2.0 **installed-app flow with loopback redirect and PKCE** (RFC 8252) via `google-auth-oauthlib`. `POST /v1/connectors` returns the Google consent URL; the Hub listens on an ephemeral loopback port for the redirect, exchanges the code, and stores the refresh token **encrypted in the vault `kv` table** (same key hierarchy as the vault; never in `objects`, never in PCA exports — FR-011). Scopes: `calendar.readonly` and `gmail.readonly` only. The consent screen in the Hub UI restates scope, cadence, and read-only status before the browser opens (FR-006).

**Rationale**: RFC 8252 is Google's supported pattern for apps without a server; PKCE removes the client-secret problem for installed apps; `keyring` was considered for token storage but the vault `kv` store already exists, is encrypted, and keeps the export-exclusion rule enforceable in one place.

**Alternatives considered**:
- *Device code flow*: worse UX (type a code), designed for input-constrained devices.
- *User-supplied API key/service account*: violates "no developer configuration" (FR-006's consent flow must be clickable by a non-technical user).
- *OS keyring for tokens*: viable, but splits secret storage across two systems and complicates the "zero credentials in exports" test (SC-007).

## R3. Sync engine (cadence, dedup, incremental)

**Decision**: A single **asyncio scheduler task** started in the FastAPI lifespan. Per connector: next-run timestamp (15 min calendar / 60 min email per clarification), an asyncio lock so manual "sync now" and background runs never overlap, and provider-side incremental tokens — Calendar `syncToken` (falls back to bounded full window on 410), Gmail `historyId` (falls back to bounded `q=` query). Items map to vault objects with a **`source_key`** (`provider:account:source_id`) enforced by a unique index; re-imports update in place, provider-side deletions tombstone on next sync. Each run appends `connector.sync` audit events with counts and outcome (FR-009, FR-012).

**Rationale**: One user, two connectors — a cron daemon, task queue, or webhook push endpoint would each add an always-on component the threat model must then cover. Incremental tokens are the providers' own dedup guarantee; `source_key` covers reconnects and overlapping windows.

**Alternatives considered**:
- *Provider push (watch channels / Pub/Sub)*: requires a public HTTPS endpoint — incompatible with loopback-only.
- *APScheduler dependency*: brings persistence and threading semantics we don't need; a 30-line asyncio loop is auditable.

## R4. Modeling imported items

**Decision**: Calendar events become a new first-class **`event` object type** (start/end, attendees as opaque strings, recurrence flattened to instances within the sync window), default classification `private` (per clarification), authority `imported`. Email messages become **`artifact` objects with `kind="email"`** (subject, sender, date, body text, headers subset), default classification `sensitive` (FR-016), authority `imported`. Both carry provenance (`source_refs` → connector account id, `source_key`, synced-at) and are indexed by the existing FTS pipeline so granted assistants retrieve them with citations (FR-014). No new retrieval path: policy capability mapping extends `_cap_for` — `event` → `memory.retrieve` under project/grant scoping rules unchanged.

**Rationale**: Events need typed fields for schedule questions ("this week") — stuffing them into artifacts would push date logic into search strings. Email is evidence, which is exactly what `artifact` already models; reuse keeps the proposal-evidence chain (FR-017) working with zero new plumbing.

**Alternatives considered**:
- *Everything as artifacts*: loses typed start/end filtering for briefs.
- *Everything as memories*: memories are claims; connector items are untrusted source material — conflating them would break the authority model (FR-007/FR-008).

## R5. Assistant catalog & recipes

**Decision**: Static catalog in `pcl_server/pairing/catalog.py`: Cursor (supported, primary), Claude Code (supported), Claude Desktop (supported, notes for WSL users), ChatGPT (supported where MCP connectors are available; marked "check plan availability"), others listed unsupported (FR-001, edge case "runtime doesn't support connection method"). Each entry has a recipe template rendered with the freshly minted pairing token and Hub URL. Recipes are copy-paste config; no file is written by the Hub itself.

**Rationale**: A static list is honest about what was validated (SC-001 targets Cursor) and cheap to extend; writing config files into assistant installs would require per-OS paths and permissions — brittle and scary.

**Alternatives considered**: auto-detection/auto-install of assistant configs — rejected for MVP-plus scope (silent writes into other apps' config undermines the trust story).
