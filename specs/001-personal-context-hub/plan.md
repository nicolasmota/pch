# Implementation Plan: Personal Context Hub (MVP)

**Branch**: `001-personal-context-hub` | **Date**: 2026-08-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-personal-context-hub/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Build the local-first Personal Context Hub MVP: an installable desktop app containing an embedded Personal Context Layer service written in **Python 3.14 with FastAPI**. The service owns an encrypted SQLite vault of typed personal context (profile, preferences, projects, goals, commitments, decisions, memories), a deterministic ABAC policy engine, a memory-proposal pipeline, an approval-gated action-intent flow, a hash-chained audit ledger, and PCA v0 export/import. Agents connect through an authenticated MCP server (official `mcp` Python SDK, Streamable HTTP on loopback, stdio launcher for compatibility); the Hub UI (React, served as static assets in a pywebview shell) and adapters both consume the same Pydantic-schema-driven REST/OpenAPI control plane. Full technical rationale in [research.md](./research.md).

## Technical Context

**Language/Version**: Python 3.14 (uv workspace monorepo); TypeScript/React used only at build time for the UI bundle — no Node.js at runtime

**Primary Dependencies**: FastAPI + uvicorn (REST/OpenAPI control plane), Pydantic v2 (single schema source for domain, REST, and MCP), `mcp` Python SDK / FastMCP (MCP server), SQLAlchemy 2 + Alembic (data access/migrations), `sqlcipher3` (SQLCipher wheels, cp314), `cryptography` (artifact encryption), `keyring` (OS keychain), `pyrage` (age encryption for PCA), pywebview (desktop shell), PyInstaller ≥ 6.15 (packaging), React 19 + Vite (UI)

**Storage**: One SQLCipher-encrypted SQLite database per context space (canonical objects, versions, grants, hash-chained append-only events, FTS5 index) + content-addressed encrypted blob store for artifacts; vault key via OS keychain with optional user passphrase (Argon2id)

**Testing**: pytest (unit + integration against real temp-dir SQLCipher databases), Schemathesis contract tests against the generated OpenAPI 3.1 document, MCP conformance tests via the `mcp` SDK client, Playwright (Python) E2E on the packaged app, seeded forbidden-context suite for SC-003

**Target Platform**: Windows and macOS desktop installers (NSIS/dmg via PyInstaller); Linux AppImage/deb best-effort; fully offline-capable, loopback-only network surface

**Project Type**: Desktop application with embedded local service (uv monorepo: 1 app + 4 packages + UI source)

**Performance Goals**: Common context searches < 1 s over 100k memories/artifact refs (SC-009); context-manifest creation and retrieval p95 < 500 ms locally, excluding model generation; agent-access revocation effective in seconds (SC-004)

**Constraints**: Encrypted at rest; no cloud account or network dependency for core operation (FR-002, FR-003); policy evaluated outside any model (FR-027); audit event persisted in the same transaction as any consequential write (FR-021); no vector index in MVP — retrieval is FTS5 + structured filters with ranking isolated behind an interface

**Scale/Scope**: Single user, single `personal` context space, ≥ 100k durable objects, 2 independently implemented agent runtimes + generic MCP adapter as the compatibility bar; 6 prioritized user stories, 27 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is an unfilled template — the project has not ratified a constitution, so no project-specific gates exist. Generic gates applied in its place:

| Gate | Status | Notes |
|---|---|---|
| Simplicity / no unjustified components | PASS | 1 app + 4 packages, each mapped to a spec concern (see Structure Decision); no speculative services, no vector index, no external policy engine in MVP; single Python runtime end-to-end |
| Testability | PASS | Absolute success criteria (SC-003, SC-005, SC-007) backed by deterministic automated suites; policy engine is a pure function over inputs |
| No premature abstraction | PASS | Deferred: vector retrieval, policy language, sync, A2A — interfaces noted only where the source doc mandates later replaceability (ranking, policy decision) |

**Post-Phase-1 re-check (after data-model.md and contracts/)**: PASS — design artifacts introduce no additional projects, runtimes, or dependencies beyond those justified in research.md.

*Recommendation: run `/speckit-constitution` before implementation if the project wants enforceable principles.*

## Project Structure

### Documentation (this feature)

```text
specs/001-personal-context-hub/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   ├── rest-api.md      # REST/OpenAPI control-plane contract
│   ├── mcp-server.md    # MCP resources/tools contract for agent adapters
│   └── pca-format.md    # Portable Context Archive v0 format
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
apps/
└── hub-desktop/                 # installable app: pywebview shell + PyInstaller packaging
    ├── src/hub_desktop/
    │   ├── main.py              # window lifecycle, service startup, keychain unlock
    │   └── packaging/           # PyInstaller spec, NSIS/dmg config, icons
    └── tests/

frontend/                        # React 19 + Vite UI source (TypeScript, build-time only)
    ├── src/
    │   ├── components/
    │   ├── pages/               # setup, projects, memories, review queue, connections/grants,
    │   │                        #   approvals, audit timeline, export/import
    │   └── api/                 # typed client generated from the OpenAPI document
    └── tests/                   # Playwright E2E (six user stories, forbidden-context suite)

packages/
├── pcl-core/                    # src/pcl_core/ — domain + vault (no agent-facing I/O)
│   ├── src/pcl_core/
│   │   ├── schema/              # Pydantic models: entities, universal metadata, capabilities
│   │   ├── vault/               # SQLCipher SQLite access, Alembic migrations, versions, blob store
│   │   ├── policy/              # ABAC evaluator: grants → allow/redact/deny/require_approval
│   │   ├── memory/              # proposal pipeline, dedup/conflict detection, review queue
│   │   ├── retrieval/           # FTS5 search, recency/authority ranking, citation assembly
│   │   └── audit/               # hash-chained append-only event ledger
│   └── tests/
├── pcl-server/                  # src/pcl_server/ — local service composing pcl-core
│   ├── src/pcl_server/
│   │   ├── rest/                # FastAPI routers (OpenAPI 3.1 from Pydantic), idempotency, auth
│   │   ├── mcp/                 # MCP server (FastMCP): resources/tools, per-connection identity
│   │   ├── pairing/             # agent catalog entries + one-time connection links
│   │   └── static/              # built frontend assets (bundled at CI time)
│   └── tests/                   # contract tests (Schemathesis + MCP conformance)
├── pca/                         # src/pca/ — Portable Context Archive v0 export/import + staging
│   ├── src/pca/
│   └── tests/                   # round-trip fidelity suite (SC-007)
└── pcl-sdk/                     # src/pcl_sdk/ — Python client SDK for adapter authors
    ├── src/pcl_sdk/
    └── tests/
```

**Structure Decision**: uv workspace monorepo with one app, four Python packages, and the UI source tree. `pcl-core` isolates the trust kernel (vault, policy, memory, audit) from anything network-facing; `pcl-server` is the only component agents can reach and consumes `pcl-core` exclusively through its typed API; `pca` is standalone so archives stay readable without a running Hub (FR-023); `pcl-sdk` is the published surface for adapter authors (spec assumption: generic adapter + two real runtimes). The Hub UI has no privileged path — it uses the same REST control plane as any local client, and ships as pre-built static assets inside `pcl-server`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations — table intentionally empty.
