# Implementation Plan: Hub Plugin Framework & Marketplace

**Branch**: `003-hub-plugin-marketplace` | **Date**: 2026-08-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-hub-plugin-marketplace/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Turn the Hub from a fixed app into a platform by moving every optional import capability behind a **plugin boundary** with technical enforcement. Plugins are import-only in v1 (write only to the vault, no outward actions, no UI extensions — per clarification). Each plugin runs as a **kernel-launched, sandboxed subprocess** that speaks a versioned JSON-RPC protocol over stdio (the Plugin Host Protocol); it never sees the vault key, owner token, or the open network. Everything a plugin can do — upsert typed objects, keep sync cursors, store its own secrets, make HTTP requests — goes through kernel-mediated capabilities, and the kernel enforces the plugin's **manifest** (declared object types, external hosts, schedule) on every call, so undeclared access is technically impossible, not just reviewed away (FR-002a). The existing Google Calendar and Gmail connectors are repackaged as the first two bundled plugins with a data-preserving migration (FR-009). A **developer kit** in `pcl-sdk` (`plugin new/dev/validate/pack`) lets third parties build import plugins without touching Hub source (FR-010). The **marketplace** is a signed static catalog (curated; third-party listings after manual review, per clarification) fetched periodically by the Hub: integrity-pinned packages, permission-diff re-consent on update, and a withdrawn-flag kill-switch that pauses affected plugins with a user warning (FR-013..FR-017, FR-019). Full rationale in [research.md](./research.md).

## Technical Context

**Language/Version**: Python 3.14 (existing uv workspace monorepo) for kernel, host runtime, and plugins; TypeScript/React 19 build-time only for the Plugins and Marketplace UI pages

**Primary Dependencies**: Existing: FastAPI + uvicorn, Pydantic v2, sqlcipher3, cryptography, httpx. New: none mandatory — the host protocol is stdlib `json` over pipes; sandboxing uses `bubblewrap`/`unshare` when present (no Python dependency); catalog signing verification uses the already-present `cryptography` (Ed25519). Plugins in v1 target a pinned `pcl-plugin-runtime` API shipped inside `pcl-sdk` (stdlib-only), avoiding per-plugin dependency installation entirely.

**Storage**: Existing SQLCipher vault. New `plugin` object type in the `objects` table (installation record: manifest snapshot, version, lifecycle state, grant reference). Plugin grants reuse the existing grants mechanism with a `plugin` principal type. Plugin-scoped secrets (e.g., OAuth refresh tokens) and sync cursors live in the vault `kv` table under `plugin_secret:{id}:*` / `plugin_state:{id}:*` (never in exports, same rule as connector tokens). Cached marketplace catalog in `kv`. Imported objects unchanged — same `objects` table, provenance now carries the plugin identity.

**Testing**: pytest against real temp-dir SQLCipher vaults; host protocol tested by driving real plugin subprocesses over stdio; adversarial suite ships a hostile test plugin that attempts undeclared object types, undeclared hosts, oversized payloads, and protocol abuse (SC-005 requires 100% blocked); marketplace tests use a local static catalog fixture with a test signing key (tampered package, permission-diff update, withdrawn flag); migration test upgrades a populated 002-era vault and asserts zero data loss (SC-001); frontend flows validated via REST contract tests as in 001/002.

**Target Platform**: Same as 001/002 — user's own device, loopback-only service; validated on Linux/WSL2. Sandbox uses Linux user+network namespaces when available; if unavailable, the plugin is marked "reduced isolation" and side-load requires an extra confirmation (documented degradation, mediation still fully enforced).

**Project Type**: Extension of the existing monorepo: new modules in `pcl-core`, `pcl-server`, `pcl-sdk`; new top-level `plugins/` directory for bundled first-party plugins and the third-party example; two new UI pages in `frontend`

**Performance Goals**: Install-to-first-consent under 3 minutes and full disable under 30 seconds from the UI (SC-002); plugin host adds <250 ms startup overhead per sync run on loopback; a crashed/hung plugin never blocks the request path (per-plugin supervisor with timeout kill, FR-008); catalog check piggybacks on the existing scheduler (12 h cadence + on Marketplace page open)

**Constraints**: Import-only plugins (vault writes only — FR-001); technical enforcement, never review-based (FR-002a); nothing runs before explicit consent (FR-003); plugin provenance on 100% of writes (FR-006, SC-003); versioned extension surface with pause-on-incompatibility (FR-012); offline-first — installed plugins work with no internet, marketplace degrades gracefully (FR-017, SC-008); imported content is data, never instructions (FR-018)

**Scale/Scope**: Single user; ~2 bundled + handful of catalog plugins initially; catalog is a static index (tens of listings, not thousands); 3 user stories, 20 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` remains an unfilled template — no ratified project constitution, so the same generic gates used for 001/002 apply:

| Gate | Status | Notes |
|---|---|---|
| Simplicity / no unjustified components | PASS | No new packages, brokers, or services: the host is a supervisor module inside `pcl-server`; plugins are subprocesses of the existing service; the marketplace is a fetched static file, not a server we run; sandboxing reuses OS facilities |
| Testability | PASS | Host protocol is drivable over stdio in pytest; enforcement criteria are absolute (SC-003/005/006/007 = 100%) and map to deterministic adversarial suites; migration has a concrete populated-vault fixture |
| No premature abstraction | PASS | Exactly one plugin kind (import) and one runtime (subprocess/stdio) in v1; no multi-language plugin support, no dependency resolution, no self-service publishing — each deferred until a second concrete consumer exists |

**Post-Phase-1 re-check (after data-model.md and contracts/)**: PASS — design adds one object type, one principal type, two kv prefixes, one REST router pair (plugins, marketplace), one stdio protocol, and one CLI command group; no additional projects or runtimes.

## Project Structure

### Documentation (this feature)

```text
specs/003-hub-plugin-marketplace/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   ├── plugin-host-protocol.md   # stdio JSON-RPC: capabilities, enforcement, errors
│   ├── plugin-manifest.md        # manifest schema + validation rules
│   ├── plugins-rest.md           # REST: install, consent, lifecycle, removal
│   └── marketplace-catalog.md    # signed catalog format, integrity, kill-switch
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
packages/
├── pcl-core/
│   └── src/pcl_core/
│       ├── schema/
│       │   └── plugin.py          # PluginInstallation, Manifest, permission models
│       └── policy.py              # + plugin principal: manifest-derived write caps
├── pcl-server/
│   └── src/pcl_server/
│       ├── plugins/               # NEW: the trusted host
│       │   ├── host.py            # supervisor: launch, sandbox, timeout kill, lifecycle
│       │   ├── protocol.py        # JSON-RPC over stdio: dispatch, capability methods
│       │   ├── enforcement.py     # manifest checks: object types, hosts, payload caps
│       │   ├── egress.py          # mediated HTTP fetch (host allowlist, size/time caps)
│       │   └── migrate.py         # 002 connectors → bundled plugins, data-preserving
│       ├── marketplace/
│       │   └── catalog.py         # fetch, Ed25519 verify, cache, withdrawn handling
│       ├── rest/routers/
│       │   ├── plugins.py         # list/install/consent/enable/pause/remove(+data)
│       │   └── marketplace.py     # browse, install-from-catalog, update w/ perm diff
│       └── sync/
│           └── scheduler.py       # generalized: manifest schedules + catalog checks
└── pcl-sdk/
    └── src/pcl_sdk/
        ├── plugin_runtime/        # NEW: what plugin code imports (stdlib-only shim)
        │   └── __init__.py        # capability client: items, state, secrets, fetch, log
        └── plugin_kit.py          # `pcl-sdk plugin new|dev|validate|pack`

plugins/                           # NEW: first-party plugins + example (each: plugin.toml + src/)
├── google-calendar/
├── gmail/
└── example-rss/                   # third-party DX proof (SC-004)

frontend/
└── src/pages/
    ├── Plugins.tsx                # NEW: installed plugins, consent, lifecycle, removal
    └── Marketplace.tsx            # NEW: browse, permission preview, install, updates
```

**Structure Decision**: The trust boundary drives the layout. `pcl-core` stays pure (schema + policy — it learns what a plugin principal *may* do, never how plugins run). `pcl-server` owns the entire host because the host *is* the enforcement point: process supervision, sandbox setup, capability dispatch, egress proxy, and catalog verification all live where the vault key lives. `pcl-sdk` ships both halves of the developer story — the runtime shim plugins import (so plugin code has zero Hub imports) and the kit CLI (so scaffold/validate/pack need no Hub checkout). Bundled plugins move to a top-level `plugins/` directory to prove the point structurally: after migration, even first-party sync code sits outside the trusted kernel and goes through the same protocol.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations — table intentionally empty.
