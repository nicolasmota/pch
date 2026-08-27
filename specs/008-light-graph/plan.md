# Implementation Plan: Light Graph

**Branch**: `008-light-graph` | **Date**: 2026-08-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/008-light-graph/spec.md`

## Summary

E4 adds **typed relations** as explicit vault objects (`from_id`, `to_id`, `relation_type`). `get_context_contract` copies grant-visible links from the situation anchor plus **one hop** onto a new `relations` array on the existing contract. Owner REST is canonical; agents `propose_relation` into the review queue.

Three names that stay three names:

| Name | What it is today | What E4 is not |
|------|------------------|----------------|
| Goal/Memory `project_id` | Membership FK | Not `owned_by`. Do not auto-promote. |
| Project `stakeholders` | String list on the project | Not `related_to`. |
| E3 `operational_phase` | Where the work stands | Not how objects hang together. |

Empty relation set → empty array; assembly never infers links from email, memories, or phase. Isolation: a work-scoped package must not receive personal relation types, endpoints, titles, or ids.

## Technical Context

**Language/Version**: Python 3.14 (uv workspace); TypeScript/React 19 for Projects relations UI + Review Queue

**Primary Dependencies**: FastAPI + Pydantic (pcl-server), existing vault, in-process MCP ToolHub, stdio bridge

**Storage**: Existing encrypted vault (`~/.pch`); no graph database; no new SQLite tables. Live links are `relation` documents. Pending agent writes are `relation_proposal` vault objects.

**Testing**: pytest (markers: `forbidden_context` for SC-004, `perf` for SC-007); core unit tests under `packages/pcl-core/tests/`; server contract tests under `packages/pcl-server/tests/contract/`

**Target Platform**: Local loopback server (127.0.0.1:8765), Linux/WSL2; fully offline

**Project Type**: Multi-package Python workspace (core + server + SDK) with static React frontend

**Performance Goals**: Relation collection is in-memory on `store.list("relation")` already bounded; no extra FTS pass, no network egress. Assembly remains < 2 s on a vault of a few thousand objects (SC-007), same budget as E1–E3.

**Constraints**: Loopback only; no new listener; no pcl-core I/O; no graph DB; no A2A; no social graph; no auto-FK promotion; imported content cannot create relations; no Personal Agency; 001–003 not reopened

**Scale/Scope**: Four relation types, one vault type, one MCP propose tool, REST CRUD + accept/reject, Projects UI + Review Queue; additive `relations` on ContextContract

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Evidence |
|------|--------|----------|
| Loopback only; not a public server | PASS | Existing REST/MCP; no new bind |
| pcl-core free of I/O | PASS | Schema + in-memory collect in `retrieval/contract.py` |
| Least privilege | PASS | Grant filter on both ends; `forbidden_context` test |
| Import is data | PASS | Sync/plugins never create relations |
| Spec-not-vision; 001–003 closed | PASS | Child of E1 |
| No Personal Agency | PASS | Propose + owner confirm; no auto-walk planner |
| Tests fail first | PASS | SC table below |
| Coding agent not Hub client | PASS | Product fields only |

**Post-design re-check (Phase 1)**: PASS — no graph DB, no second MCP read tool, FKs untouched. Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/008-light-graph/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── relations.md
└── tasks.md             # Phase 2 — NOT created by /speckit-plan
```

### Source Code (repository root)

```text
packages/pcl-core/src/pcl_core/
├── schema/
│   ├── relation.py          # NEW: RelationType, Relation, RelationProposal
│   ├── contract.py          # EDIT: RelationRef; ContextContract.relations
│   ├── metadata.py          # EDIT: EntityType.RELATION
│   └── __init__.py          # EDIT: export + TYPE_MODELS
├── retrieval/
│   └── contract.py          # EDIT: collect anchor + one hop into relations[]
└── service.py               # EDIT: create/list/delete relation; propose/accept/reject

packages/pcl-server/src/pcl_server/
├── mcp/tools_context.py     # EDIT: register propose_relation
└── rest/routers/
    └── relations.py         # NEW: owner REST + proposal accept/reject

packages/pcl-sdk/src/pcl_sdk/
└── mcp_bridge.py            # EDIT: TOOL_NAMES + TOOL_SCHEMAS for propose_relation

frontend/src/
├── api/types.ts             # EDIT: Relation, RelationProposal
├── pages/Projects.tsx       # EDIT: list/add/remove relations on a project
└── pages/ReviewQueue.tsx    # EDIT: relation proposals alongside memory + operational

packages/pcl-core/tests/
├── test_relation_schema.py        # NEW: enum, pair uniqueness, no self-link
├── test_relation_contract.py      # NEW: SC-001, SC-002, SC-003, SC-005
└── test_contract_perf.py          # EDIT: SC-007 with relations seeded

packages/pcl-server/tests/
├── contract/test_relation_mcp.py                     # NEW: SC-006 two tokens; propose does not write
└── forbidden_context/test_relation_isolation.py      # NEW: SC-004
```

**Structure Decision**: Follow existing layering — schema + pure collect in `pcl-core`, Hub methods in `service.py`, MCP in `pcl-server`, bridge in `pcl-sdk`, person-visible surfaces on existing Projects and Review Queue. No new packages, no graph engine, no second `get_*` MCP tool.

## Success criteria → tests

Tests written first and MUST fail before satisfying code.

| SC | Test (fail first) | Marker |
|----|-------------------|--------|
| SC-001 | `packages/pcl-core/tests/test_relation_contract.py::test_depends_on_in_package` | (default) |
| SC-002 | `packages/pcl-core/tests/test_relation_contract.py::test_one_hop_blocked_by` | (default) |
| SC-003 | `packages/pcl-core/tests/test_relation_contract.py::test_remove_then_next_contract` | (default) |
| SC-004 | `packages/pcl-server/tests/forbidden_context/test_relation_isolation.py::test_work_scope_omits_personal_relations` | `forbidden_context` |
| SC-005 | `packages/pcl-core/tests/test_relation_contract.py::test_unset_assembles_without_inventing` | (default) |
| SC-006 | `packages/pcl-server/tests/contract/test_relation_mcp.py::test_two_agents_agree` | (default) |
| SC-007 | `packages/pcl-core/tests/test_contract_perf.py::test_contract_assembly_under_two_seconds` — trip has depends_on + one hop; still < 2 s; still `hub.get_context_contract` | `perf` |

## Complexity Tracking

No constitution-gate violations to justify. Empty.
