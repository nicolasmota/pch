# Implementation Plan: Context Engine

**Branch**: `004-context-engine` | **Date**: 2026-08-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/004-context-engine/spec.md`

## Summary

Given an authorized agent's request carrying a stated purpose (and optional subject hint), the Hub assembles a **Context Contract**: the live goal(s), relevant preferences, memories, decisions, constraints, and shared state — each item cited to its vault source with provenance, authority, and freshness — bounded by the agent's existing grant, with an explicit omission section for withheld categories. Technically this is a new assembly module in `pcl-core` (`retrieval/contract.py`) that reuses the existing FTS5 search, `DefaultRanker`, brief/manifest builders, and `policy.evaluate()`; orchestrated by a new `Hub.get_context_contract()`; exposed as a new MCP tool `get_context_contract` on the existing ToolHub and stdio bridge; every issuance/refusal appended to the audit ledger under a new `context.contract` event kind. Contracts are ephemeral responses (not vault objects); the audit record carries item references and omission categories so the person can review issuances in the existing Audit UI.

## Technical Context

**Language/Version**: Python 3.14 (uv workspace); TypeScript/React 19 for the review UI touch-up

**Primary Dependencies**: FastAPI + Pydantic (pcl-server), SQLCipher/SQLite with FTS5 (pcl-core vault), existing in-process MCP ToolHub (`pcl_server/mcp/`), stdio bridge (`pcl_sdk/mcp_bridge.py`)

**Storage**: Existing encrypted vault (`~/.pch`); no new tables — contracts are ephemeral; issuance records go to the existing append-only `events` ledger

**Testing**: pytest (markers: `forbidden_context` for isolation, `e2e`); server contract tests under `packages/pcl-server/tests/contract/`; core unit tests under `packages/pcl-core/tests/`

**Target Platform**: Local loopback server (127.0.0.1:8765), Linux/WSL2; fully offline

**Project Type**: Multi-package Python workspace (core library + server + SDK) with static React frontend

**Performance Goals**: Contract assembly < 2 s on a vault with thousands of objects (SC-006); assembly is a bounded number of FTS queries + in-memory ranking, no N+1 per item

**Constraints**: Loopback only; offline-only assembly (no egress, no plugin syncs); no vector DB / embeddings; no renaming of `SharedState` / `ActionIntent`; imported content is data, never instructions; owner-correction wins (versioned objects — live version only)

**Scale/Scope**: Single-person vault, thousands of objects, handful of paired agents; one new MCP tool, one new schema module, one new retrieval module, one new audit kind, minor Audit UI rendering

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is an unratified template; the operative principles are the Roadmap principles (`docs/ROADMAP.md`) and repo constraints (`AGENTS.md`). Gates derived from them:

| Gate | Status | Evidence |
|------|--------|----------|
| Loopback only; not a public server | PASS | New tool rides existing loopback REST/MCP surface; no new listeners |
| Local-first / offline | PASS | Assembly reads only the vault; FR-010 forbids imports/egress during assembly |
| Minimum privilege; grant-bounded | PASS | Every candidate item passes `policy.evaluate()` under the requesting connection's grant; owner-only surfaces unchanged |
| Imported is data, never instruction | PASS | Contract items are typed data with provenance; `Artifact.untrusted` flag propagates into items |
| No vector DB / no new agent runtime / no A2A | PASS | Ranking reuses FTS5 + `DefaultRanker` + token overlap; MCP only |
| Don't rename `SharedState` / `ActionIntent` | PASS | Contract embeds existing `SharedState` values verbatim under "available state" |
| Explicit control: person's correction wins | PASS | Assembly reads live object versions only; superseded versions never selected |
| Provenance required | PASS | Items without resolvable `source_refs`/citation still carry authority + object id as citation; FR-004/FR-003 enforced in schema |

**Post-design re-check (Phase 1)**: PASS — no new violations introduced; contract remains ephemeral (no new persistence), one new audit kind, no schema renames.

## Project Structure

### Documentation (this feature)

```text
specs/004-context-engine/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── context-contract.md   # Contract shape + MCP tool contract
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
packages/pcl-core/src/pcl_core/
├── schema/
│   ├── contract.py          # NEW: ContextQuery, ContextContract, ContractItem, OmissionNote
│   ├── audit.py             # EDIT: add EventKind.CONTEXT_CONTRACT
│   └── __init__.py          # EDIT: export contract models (not in TYPE_MODELS — not vault objects)
├── retrieval/
│   ├── contract.py          # NEW: situation selection + assembly + sufficiency caps
│   ├── search.py            # REUSE: FTS5, DefaultRanker, citations_for
│   ├── ask.py               # REUSE: significant_tokens (token-overlap relevance)
│   ├── briefs.py            # REUSE: related-object bundling pattern
│   └── manifests.py         # REUSE: redaction-notice pattern for omissions
└── service.py               # EDIT: Hub.get_context_contract() orchestration + audit

packages/pcl-server/src/pcl_server/mcp/
└── tools_context.py         # EDIT: register get_context_contract tool

packages/pcl-sdk/src/pcl_sdk/
└── mcp_bridge.py            # EDIT: TOOL_NAMES + TOOL_SCHEMAS for get_context_contract

frontend/src/pages/
└── Audit.tsx                # EDIT: render context.contract events (agent, purpose, items, omissions)

packages/pcl-core/tests/
├── test_contract_assembly.py     # NEW: selection, ranking, sufficiency, conflicts, empty contract
└── test_contract_grants.py       # NEW: scope bounding + omission notes (unit)

packages/pcl-server/tests/
├── contract/test_mcp_contract.py         # NEW: MCP tool contract tests vs contracts/context-contract.md
└── forbidden_context/test_contract_isolation.py  # NEW: cross-scope leakage = 0 (marker: forbidden_context)
```

**Structure Decision**: Follow the established layering exactly — pure assembly logic in `pcl-core` (no I/O beyond vault), orchestration on `Hub`, exposure in `pcl-server` MCP ToolHub, bridge schema in `pcl-sdk`, review surface in the existing Audit page. No new packages, routers, or tables.

## Complexity Tracking

No constitution-gate violations to justify. The feature adds one schema module, one retrieval module, one Hub method, one MCP tool, one audit kind.
