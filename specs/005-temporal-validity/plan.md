# Implementation Plan: Temporal Validity

**Branch**: `005-temporal-validity` | **Date**: 2026-08-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/005-temporal-validity/spec.md`

## Summary

Preferences and factual memories gain a **validity interval** (start, optional end) distinct from retention, object `version`, and SharedState TTL. A **change of mind** ends the current statement and creates a new current one with the same key/subject — both remain; a **mistake** retracts a statement so it is neither current nor historical truth. The E1 assembler (`retrieval/contract.py`) includes only statements current at an evaluation time (default: now; optional `as_of` on the existing `get_context_contract` request). Overlapping *current* statements still appear as conflicts. The person sees current vs historical on the Memories page (memories + preferences) and can set intervals, supersede, or retract there. No new packages, listeners, tables, vector indexes, or MCP tools.

## Technical Context

**Language/Version**: Python 3.14 (uv workspace); TypeScript/React 19 for the Memories/preferences review surface

**Primary Dependencies**: Pydantic (schema), existing vault `ObjectStore` / `object_versions`, existing `assemble_contract` + `policy.evaluate()`, existing MCP ToolHub + stdio bridge, FastAPI owner REST

**Storage**: Existing encrypted vault (`~/.pch`); no new tables. `valid_from` / `valid_until` live on Preference and Memory documents already stored in `objects`. Issuance records stay on the existing `context.contract` ledger kind. Change-of-mind and retract are `object.write` (two puts or a tombstone) in one transaction.

**Testing**: pytest (markers: `forbidden_context` for isolation, `perf` for SC-007 non-regression); core unit tests under `packages/pcl-core/tests/`; server contract tests under `packages/pcl-server/tests/contract/`; existing trip-handoff style integration for the reversal demo

**Target Platform**: Local loopback server (127.0.0.1:8765), Linux/WSL2; fully offline

**Project Type**: Multi-package Python workspace (core library + server + SDK) with static React frontend

**Performance Goals**: Temporal filter is in-memory on the same bounded lists E1 already loads; assembly remains < 2 s on a vault of a few thousand objects (SC-007), no extra FTS pass, no network egress

**Constraints**: Loopback only; offline-only assembly; no vector DB; no rename of `SharedState` / `ActionIntent`; imported content cannot open or close validity; history must not disappear on change of mind; `pcl-core` remains free of I/O; closed chapters 001–003 are not reopened as epics; Personal Intelligence / Personal Agency out of scope

**Scale/Scope**: Single-person vault; covered types = Preference + Memory only; one optional query field (`as_of`); two Hub operations (`supersede`, `retract`); Memories UI shows interval + current/historical; at most one *current* preference per `key`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` **Version 1.0.0** (ratified 2026-08-26). Gates:

| Gate | Status | Evidence |
|------|--------|----------|
| I. Person owns the context | PASS | Validity and successive truths live in the person's vault objects, not in any runtime memory. Agents still propose; `supersede` / `retract` are owner Hub operations (proposal accept may call `supersede` when replacing a current memory). |
| II. Local-first, loopback-only | PASS | No new listeners. Assembly and resolution read only the vault. FR-012 forbids imports/egress during assembly. |
| III. Least privilege, least context | PASS | Temporal filter runs *after* `policy.evaluate()` on the same candidates E1 already grants. Historical out-of-scope items never appear. Smallest-sufficient: historical intervals are not inlined into the live package (FR-015). |
| IV. Provenance, authority, explicit control | PASS | Change of mind keeps the earlier statement as historical truth (not silent overwrite). Mistake retract is explicit and is not historical truth. Overlapping currents surface as conflicts (research D5 of E1 preserved). Corrections of intervals take effect on the next assembly. Writes stay on the append-only ledger (`object.write`). |
| V. Imported content is data, never instruction | PASS | Email/calendar/plugin payloads cannot call `supersede` or patch `valid_until`. Only owner confirmation (including accept of a proposal) mutates validity. |
| Product: context is temporal; history must not disappear | PASS | Two objects (or two memories) for successive truths; `valid_until` closes the earlier one. Tombstone is reserved for never-true / delete, not for change of mind. |
| Product: do not rename SharedState / ActionIntent | PASS | SharedState TTL unchanged; ActionIntent unchanged. Validity is not either of them. |
| Product: no Personal Intelligence / Personal Agency | PASS | No inference that a preference expired from email; no autonomous action. |
| Workflow: 001–003 closed; child spec only | PASS | Schema fields + Hub ops + assembly filter + UI on existing Memories page. No epic reopening of vault/pairing/plugins. |
| Packages: pcl-core free of I/O | PASS | Interval helpers and assembly stay in `pcl-core`; REST/MCP/UI stay in server/sdk/frontend. |
| Tests: fail first; new assembly → forbidden_context | PASS | SC-001…SC-007 mapped to named tests below; isolation test marked `forbidden_context`. |

**Post-design re-check (Phase 1)**: PASS — no new persistence table, no new EventKind required, no new MCP tool, no constitution exceptions. Optional `as_of` is a field on the existing context request, not a new product surface.

## Project Structure

### Documentation (this feature)

```text
specs/005-temporal-validity/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── temporal-validity.md   # MCP as_of delta + owner REST supersede/retract/interval
└── tasks.md                   # Phase 2 (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
packages/pcl-core/src/pcl_core/
├── schema/
│   ├── preference.py        # EDIT: valid_from, valid_until
│   ├── memory.py            # EDIT: valid_from, valid_until, never_true
│   ├── contract.py          # EDIT: ContextQuery.as_of; ContractItem.body may include interval
│   └── __init__.py          # EDIT: re-export helpers if added
├── retrieval/
│   └── contract.py          # EDIT: evaluation time; drop non-current Preference/Memory
├── timeutil.py              # REUSE: now_iso; ADD: parse/compare interval contains
└── service.py               # EDIT: Hub.supersede(), Hub.retract_never_true(); create() rejects second current preference key; decide_proposal may supersede

packages/pcl-server/src/pcl_server/
├── mcp/tools_context.py     # EDIT: pass as_of through get_context_contract
└── rest/routers/memories.py # EDIT: POST supersede/retract; PATCH already carries new fields

packages/pcl-sdk/src/pcl_sdk/
└── mcp_bridge.py            # EDIT: TOOL_SCHEMAS.get_context_contract properties.as_of

frontend/src/
├── api/types.ts             # EDIT: Memory (+ Preference) validity fields
└── pages/Memories.tsx       # EDIT: list preferences too; current/historical badge; interval; supersede; retract

packages/pcl-core/tests/
├── test_validity_schema.py          # NEW: interval validation; never_true; defaults
├── test_validity_resolution.py      # NEW: is_current at now and as_of; open-ended; future start
├── test_change_mind.py              # NEW: supersede keeps historical; retract not historical; unique current key
├── test_contract_assembly.py        # EDIT: current-only prefs/memories; overlapping current → conflict
└── test_contract_perf.py            # EDIT: SC-007 — closed intervals still < 2 s, no egress

packages/pcl-server/tests/
├── contract/test_preference_reversal.py           # NEW: SC-001/SC-002 killer temporal demo
├── contract/test_mcp_contract.py                  # EDIT: as_of accepted; empty as_of = now
└── forbidden_context/test_contract_isolation.py   # EDIT: historical personal pref must not leak (SC-004)
```

**Structure Decision**: Same layering as 004 — interval math and assembly filter in `pcl-core`, owner operations on `Hub`, exposure via existing MCP tool + owner REST, review on the existing Memories page (extended with preferences). No new packages, routers-as-epics, or tables.

## Success criteria → tests

Tests are written first and MUST fail before the implementation that is supposed to satisfy them (constitution Development Workflow).

| SC | Named test | Marker |
|----|------------|--------|
| SC-001 | `packages/pcl-server/tests/contract/test_preference_reversal.py` — after supersede, both agents' contracts present `like` as live and 0 live `dislike` | (default) |
| SC-002 | same file — GET lists still return the dislike row as historical (`valid_until` set, not tombstoned) | (default) |
| SC-003 | `packages/pcl-core/tests/test_validity_resolution.py` — explicit end: current before end, not current after; `test_contract_assembly.py` for package presentation | (default) |
| SC-004 | `packages/pcl-server/tests/forbidden_context/test_contract_isolation.py` — historical personal preference absent from work contract | `forbidden_context` |
| SC-005 | `packages/pcl-core/tests/test_contract_assembly.py` — two current same-key prefs → `preference_key_collision`, neither dropped | (default) |
| SC-006 | `packages/pcl-core/tests/test_change_mind.py` — supersede keeps predecessor historical; retract excluded from historical truth and live package | (default) |
| SC-007 | `packages/pcl-core/tests/test_contract_perf.py` — assembly < 2 s, no network egress, vault includes closed intervals | `perf` |

## Complexity Tracking

No constitution-gate violations to justify. The feature adds two optional datetime fields on two existing types, two Hub operations, one optional query field, and UI badges/actions on one page.
