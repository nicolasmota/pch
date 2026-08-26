# Implementation Plan: External Connectors (Real Agents, Calendar, Email)

**Branch**: `002-external-connectors` | **Date**: 2026-08-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-external-connectors/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Make the Hub usable by real assistants and fed by real sources, without changing the MVP's trust kernel. Three additions: (1) an **MCP stdio bridge** shipped in `pcl-sdk` that any MCP-capable assistant (Cursor first, Claude/ChatGPT second) launches locally; it translates MCP tool calls into the Hub's existing authenticated REST tool facade, so every request rides the per-connection identity, grants, purposes, and audit already proven in 001. The Connections page grows an **assistant catalog** that renders a copy-paste recipe (e.g., a ready `mcp.json` block) per assistant. (2) A **Google Calendar connector**: OAuth 2.0 installed-app flow with loopback redirect + PKCE, incremental sync via syncToken every 15 minutes into a new `event` object type (private classification, imported authority, source-keyed dedup). (3) A **Gmail connector**: same OAuth app, selective import only (labels/senders/date range) into sensitive `artifact` objects at 60-minute cadence; the Hub performs no extraction — durable claims arrive only as assistant-submitted memory proposals. A background scheduler in the FastAPI lifespan drives syncs; every run is audited. Full rationale in [research.md](./research.md).

## Technical Context

**Language/Version**: Python 3.14 (existing uv workspace monorepo); TypeScript/React 19 build-time only for UI pages

**Primary Dependencies**: Existing: FastAPI + uvicorn, Pydantic v2, sqlcipher3, cryptography, keyring. New: `mcp` Python SDK (client/stdio server plumbing for the bridge), `httpx` (Google API calls; already present transitively via test stack), `google-auth` + `google-auth-oauthlib` (installed-app OAuth with PKCE). No SQLAlchemy change — connectors reuse the existing `Engine`/`ObjectStore`.

**Storage**: Existing SQLCipher vault. New object types stored in the same `objects` table: `connector_account`, `event`; email messages as `artifact` with `kind="email"`. New `source_key` column + unique index for connector dedup. Provider OAuth tokens encrypted in the vault `kv` table (never in exports); sync runs recorded as audit events plus a `last_sync` summary on the connector object.

**Testing**: pytest against real temp-dir SQLCipher vaults; Google APIs faked with a local httpx.MockTransport fixture (recorded response shapes); MCP bridge tested end-to-end by driving it over stdio with the `mcp` SDK client; forbidden-context suite extended with connector-origin fixtures (prompt-injection payloads in event/message bodies, SC-008).

**Target Platform**: Same as 001 — user's own device, loopback-only service; validated on Linux/WSL2 (Cursor reaches the bridge via stdio, no Windows↔WSL networking required)

**Project Type**: Extension of the existing monorepo (no new packages; new modules in `pcl-core`, `pcl-server`, `pcl-sdk`, new UI pages in `frontend`)

**Performance Goals**: First calendar sync (bounded selection) visible in UI within 5 minutes of consent (SC-004); background sync cadence 15 min calendar / 60 min email; bridge adds <100 ms overhead per tool call on loopback; revocation still effective in seconds (SC-003)

**Constraints**: Read-only connectors (no write-back); connector content is untrusted data — imported authority, never user-confirmed, never policy-bearing (FR-008); no Hub-side claim extraction (FR-017); tokens excluded from PCA exports (FR-011); sync must not block the request path (background task, per-connector lock)

**Scale/Scope**: Single user; one Google account per connector kind initially; first sync bounded by user selection (≤ ~5k items); 3 user stories, 17 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` remains an unfilled template — no ratified project constitution, so the same generic gates used for 001 apply:

| Gate | Status | Notes |
|---|---|---|
| Simplicity / no unjustified components | PASS | No new packages, services, or runtimes; the bridge is a module in the existing `pcl-sdk`; scheduler is an asyncio task in the existing FastAPI lifespan; no queue/broker, no webhook server |
| Testability | PASS | Bridge testable over stdio with the MCP SDK client; connectors testable against mocked Google transports; absolute criteria (SC-002, SC-005, SC-007, SC-008) map to deterministic suites |
| No premature abstraction | PASS | One provider (Google) implemented behind a minimal `Connector` protocol only because two connectors (calendar, email) already exist to share it; no generic "provider framework" |

**Post-Phase-1 re-check (after data-model.md and contracts/)**: PASS — design introduces two object types, one column, five REST resources, and one CLI entry point; no additional projects or runtimes.

## Project Structure

### Documentation (this feature)

```text
specs/002-external-connectors/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   ├── connectors-rest.md   # REST contract: catalog, recipes, connectors, sync
│   └── mcp-bridge.md        # MCP stdio bridge: tools, auth, error mapping
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
packages/
├── pcl-core/
│   └── src/pcl_core/
│       ├── schema/
│       │   ├── connector.py      # ConnectorAccount, SyncRun summary, selection rules
│       │   └── event.py          # Event (calendar) object type
│       ├── connectors/           # NEW: provider sync logic (no network in pcl-core tests)
│       │   ├── base.py           # Connector protocol: plan_sync/apply_items/dedup
│       │   ├── google_calendar.py
│       │   └── gmail.py
│       └── vault/
│           └── engine.py         # + source_key column & unique index (migration)
├── pcl-server/
│   └── src/pcl_server/
│       ├── rest/routers/
│       │   └── connectors.py     # catalog, recipes, connector CRUD, sync-now, runs
│       ├── pairing/
│       │   └── catalog.py        # assistant catalog entries + recipe templates
│       └── sync/
│           ├── scheduler.py      # lifespan task: per-connector cadence, locks
│           └── oauth.py          # installed-app OAuth (loopback redirect, PKCE), token store
└── pcl-sdk/
    └── src/pcl_sdk/
        └── mcp_bridge.py         # `pcl-sdk mcp-bridge`: MCP stdio server ↔ Hub REST facade

frontend/
└── src/pages/
    ├── Connections.tsx           # + assistant catalog with copy-paste recipe per assistant
    └── Connectors.tsx            # NEW: consent flow, selection, sync status, pause/disconnect
```

**Structure Decision**: Keep the 001 boundary intact: `pcl-core` gains pure sync logic (item mapping, dedup, classification defaults) with zero network I/O so it stays testable against the vault alone; `pcl-server` owns everything that touches the network (OAuth, Google API calls via httpx, the scheduler) and exposes connectors over the same authenticated REST plane the UI already uses; `pcl-sdk` ships the bridge because it runs inside the assistant's machine context as a client of the Hub — exactly the role the SDK exists for. No new package: connectors are a feature of the existing service, not a product of their own.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations — table intentionally empty.
