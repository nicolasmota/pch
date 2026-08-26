# Phase 0 Research: Personal Context Hub (MVP)

**Feature**: `specs/001-personal-context-hub/spec.md`
**Date**: 2026-08-21 (revised same day: stack pinned to Python 3.14 + FastAPI per user direction)

This document resolves every technical unknown in the plan's Technical Context. The source product draft (`personal-context-layer-spec.md` v0.1, section 18 "MVP implementation shape" and section 23 "Recommended first decisions") already constrains several choices; the decisions below adopt or refine those constraints.

## D1. Language and runtime

- **Decision**: **Python 3.14** throughout the backend, managed as a **uv workspace** monorepo. Pydantic v2 models are the single schema source of truth for the domain, the REST/OpenAPI contract, and MCP tool schemas. Frontend UI in TypeScript/React (build-time only; no Node at runtime).
- **Rationale**: User direction (Python + FastAPI). Python 3.14 verified viable for this stack: `sqlcipher3` 0.6.2 ships cp314 wheels, PyInstaller supports 3.14 since 6.15 (Aug 2025), and the official MCP Python SDK is pure Python. FastAPI generates OpenAPI 3.1 natively from Pydantic, matching the source doc's OpenAPI + JSON Schema mandate.
- **Alternatives considered**:
  - *TypeScript/Node*: was the initial draft choice (MCP SDK maturity); superseded by explicit user preference — the Python MCP SDK is also first-party and mature.
  - *Python 3.12/3.13 for safety*: unnecessary — all native dependencies verified with 3.14 wheels; fall back per-dependency only if a blocker appears during setup.

## D2. Desktop shell

- **Decision**: **pywebview** window hosting the UI, with the FastAPI service running in-process; packaged as a single installable via **PyInstaller** (≥ 6.15) — NSIS installer on Windows, dmg on macOS. The React UI is built to static assets at build time and served by FastAPI on loopback.
- **Rationale**: Keeps the entire runtime Python (one process to package, supervise, and sign), satisfying plug-and-play install for non-technical users (FR-001). The UI consuming the public REST API keeps the control plane honest — the Hub UI is just the first client, with no privileged back door.
- **Alternatives considered**:
  - *Electron + Python sidecar*: two runtimes to package and keep alive; rejected.
  - *Tauri 2 + Python sidecar*: lighter shell but adds Rust toolchain plus sidecar supervision; rejected for MVP.
  - *Browser tab + system tray daemon*: weaker "installed app" experience and window lifecycle; rejected.

## D3. Canonical storage and encryption at rest

- **Decision**: SQLite via **`sqlcipher3`** (self-contained SQLCipher wheel, full-database encryption), one database file per context space, accessed through **SQLAlchemy 2** (Core-centric) with **Alembic** migrations. Artifacts stored as individually encrypted files (ChaCha20-Poly1305 via the `cryptography` library) in an on-disk blob store keyed by content hash. Vault key held in the OS keychain via **`keyring`**, with an optional user passphrase (Argon2id KDF) for portability.
- **Rationale**: Satisfies FR-002 (encrypted local vault, no cloud account), keeps canonical objects transactional (NFR: transactional writes), and SQLite comfortably handles the 100k-object scale target. SQLCipher encrypts the whole database including indexes, avoiding field-by-field crypto complexity in MVP.
- **Alternatives considered**:
  - *Embedded Postgres*: heavier install, overkill for single-user local vault; schema stays Postgres-compatible for a later hosted mode.
  - *Per-field application-layer encryption over plain SQLite*: breaks FTS indexing and query filtering; rejected.
  - *SQLModel / full ORM style*: thin Core + explicit mappers preferred — versioning and hash-chained audit writes need precise transaction control.

## D4. Search and retrieval

- **Decision**: SQLite **FTS5** for keyword search with BM25 ranking, combined with structured filters (space, classification, type, labels) applied *before* policy filtering. Ranking blends BM25 with recency and authority weights. **No vector index in MVP**; retrieval isolates ranking behind a `Ranker` interface so a derived, rebuildable local vector index can be added later (per the source doc: vector search is derived-only, never source of truth).
- **Rationale**: Meets SC-009 (common searches < 1 s over 100k objects) without shipping an embedding model or third-party inference in a privacy-first MVP. Citations come from stored provenance, not retrieval scores.
- **Alternatives considered**: *sqlite-vec / local embeddings from day one* (adds model distribution and index-rebuild complexity; deferred to P1); *external search service* (violates local-first; rejected).

## D5. Control plane API

- **Decision**: **FastAPI** on uvicorn, bound to `127.0.0.1` only, versioned under `/v1`. Pydantic v2 request/response models generate the OpenAPI 3.1 document (the normative contract artifact). Write endpoints require idempotency keys and `If-Match` version preconditions; errors are RFC 9457 problem+json.
- **Rationale**: User direction; also the cleanest Python path to the source doc's OpenAPI + JSON Schema mandate. Loopback-only binding plus per-client bearer tokens keeps the attack surface local.
- **Alternatives considered**: Django REST (heavier, ORM coupling), Litestar (fine, smaller ecosystem), Flask (weaker typed-schema story); rejected.

## D6. Agent interface (MCP)

- **Decision**: MCP server built on the official **`mcp` Python SDK** (FastMCP server API), exposed over **Streamable HTTP on loopback** as the primary transport, with a stdio launcher for agents that only support stdio. Each connected agent gets a distinct credential minted during Hub-side pairing (catalog entry or one-time connection link, FR-008); the MCP session identity maps 1:1 to an `AgentConnection` and inherits only that connection's grants (FR-009).
- **Rationale**: MCP is the source doc's designated first integration interface; one server process serving authenticated HTTP sessions matches "many agents, one vault" better than per-agent stdio spawns. Pairing via one-time link keeps setup non-technical. Runs in the same process as FastAPI (mounted ASGI app), sharing the policy engine and audit ledger.
- **Alternatives considered**: stdio-only (no per-agent identity without one process per agent; kept only as compatibility launcher); A2A (explicitly deferred to P2 by the source doc).

## D7. Policy engine

- **Decision**: An embedded Python policy evaluator (in `pcl-core`) implementing ABAC over a small closed vocabulary: subject (connection), space, resource type + selector, capability (e.g. `project.read`, `memory.retrieve`, `action.propose`), purpose, constraints (project scope, classification ceiling, expiry), and decision effects (`allow`, `redact`, `deny`, `require_approval`). Every decision emits an audit event. No external policy language in MVP.
- **Rationale**: FR-027 requires policy evaluated outside the model; the MVP grant model (scoped read grants + approval-required actions, FR-018) fits a deterministic, pure-function evaluator that is easy to test to the SC-003 bar (100% forbidden-context blocking). A general policy language (the source doc's open decision #3) is deliberately deferred.
- **Alternatives considered**: OPA/Rego or Cedar — powerful but adds a runtime, a language, and an authoring UX the MVP does not need; rejected for now with the evaluator's decision interface kept compatible with a future swap.

## D8. Audit ledger (tamper evidence)

- **Decision**: Append-only `events` table with a per-space hash chain: each event stores `sha256(prev_hash || canonical_json(event))`. A periodic checkpoint of the head hash is written to the OS keychain. Consequential writes/actions commit their audit event in the same SQLite transaction as the state change (FR-021).
- **Rationale**: Gives local tamper evidence without external anchoring infrastructure. Same-transaction commit guarantees "no unaudited consequential action".
- **Alternatives considered**: Signed external log anchoring (needs network/third party, violates local-first); plain append-only table without chaining (fails "tamper-evident"); rejected.

## D9. Portable Context Archive (PCA v0)

- **Decision**: PCA v0 = a zip archive encrypted with **age** (passphrase recipient, via `pyrage`), containing: `manifest.json` (format version, space, filters, counts, integrity hashes), `objects/*.jsonl` (one file per entity type, canonical JSON records including provenance, authority, classification, versions), `events.jsonl` (audit lineage), `artifacts/` (encrypted-at-source blobs by content hash), and `schemas/` (the JSON Schemas — exported from the Pydantic models — that the records conform to). Import stages into a quarantine area with merge / replace / keep-separate resolution keyed on stable ULIDs (FR-025).
- **Rationale**: Readable without a running Hub (FR-023: documented + open), `age` is a simple, audited, widely implemented encryption format with passphrase support, and embedding schemas makes the archive self-describing for migration. `pyrage` ships abi3 wheels (PyO3), compatible with 3.14.
- **Alternatives considered**: Plain zip + per-file crypto (harder to reason about), SQLite-file export (not vendor-neutral or human-inspectable), JSON-LD everywhere (deferred; plain canonical JSON + schemas is enough for v0).

## D10. Identifiers, versioning, conflicts

- **Decision**: ULIDs with type prefixes (`mem_`, `prj_`, `grant_`…) via `python-ulid`. Every durable object carries `version` (monotonic int) plus full prior versions in an `object_versions` table. Writes are optimistic-concurrency (`If-Match` on version). Memory conflicts (FR-016) are detected on proposal acceptance by exact-duplicate hash and same-subject contradiction (same entity + attribute path, different value) and surfaced as `conflict` records — never auto-resolved against a user-confirmed value (FR-007).
- **Rationale**: Sortable IDs simplify sync later; full version history is required for "why does the system believe this" (US4) and undo.

## D11. Testing strategy

- **Decision**: **pytest** for unit and integration tests (policy evaluator, memory pipeline, PCA round trip run against real SQLCipher databases in temp dirs); **Schemathesis** contract tests driving the FastAPI app from its generated OpenAPI document, plus MCP conformance tests through the `mcp` SDK client; **Playwright (Python)** driving the packaged app UI for the six spec user stories; a seeded **forbidden-context suite** asserting SC-003's 100% block rate.
- **Rationale**: SC-003/SC-005/SC-007 are absolute (100%) criteria and need deterministic automated suites, not manual QA. Schemathesis makes the OpenAPI document itself the tested contract.

## D12. Target platform and packaging

- **Decision**: Windows and macOS installers first (PyInstaller ≥ 6.15 → NSIS / dmg), Linux AppImage/deb best-effort. Frontend built with Vite at CI time into static assets bundled inside the package. Auto-update deferred; MVP updates are manual installer downloads.
- **Rationale**: Matches where pilot users are; keeps release engineering minimal. PyInstaller 6.15+ officially supports Python 3.14.

## Resolved unknowns summary

| Technical Context field | Resolution |
|---|---|
| Language/Version | Python 3.14 (uv workspace); TypeScript only for UI build (D1) |
| Primary dependencies | FastAPI, Pydantic v2, uvicorn, `mcp` SDK (FastMCP), SQLAlchemy 2 + Alembic, `sqlcipher3`, `cryptography`, `keyring`, `pyrage` (age), pywebview, PyInstaller, React 19 + Vite (D2–D9) |
| Storage | SQLCipher-encrypted SQLite per space + encrypted blob store (D3) |
| Testing | pytest, Schemathesis vs OpenAPI, MCP SDK conformance, Playwright E2E (D11) |
| Target platform | Windows/macOS desktop, Linux best-effort (D12) |
| Project type | Desktop app + embedded local service, uv monorepo (D1, D2) |
| Performance goals | Search < 1 s @ 100k objects; manifest p95 < 500 ms local (D4) |
| Constraints | Offline-capable, loopback-only network surface, encrypted at rest, no cloud account (D3, D5) |
| Scale/scope | Single user, 1 space, ≥ 100k memories/artifact refs, 2 real agent runtimes (spec assumptions) |
