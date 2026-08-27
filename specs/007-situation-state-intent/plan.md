# Implementation Plan: Situation State and Intent

**Branch**: `007-situation-state-intent` | **Date**: 2026-08-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/007-situation-state-intent/spec.md`

## Summary

E3 adds three owner-canonical fields on **Project** and **Goal**: `operational_phase`, `current_step`, `situation_intent`. `get_context_contract` copies them onto the existing `SituationRef`. Owner PATCH is the only silent write. Agents call a new MCP tool `propose_operational_state`; accept/reject stays on the Review Queue.

Three names that stay three names:

| Name | What it is today | What E3 is not |
|------|------------------|----------------|
| SharedState key `trip.phase` | TTL handoff already seeded in E1 tests | Not operational phase. It may still appear in `state[]`. |
| ProjectStatus `active\|paused\|done\|archived` | Lifecycle of the project object | Not “comparing itineraries”. `situation.status` stays this enum. |
| ActionIntent | Approval to act externally (`request_approval` / `propose_action`) | Not “choose next itinerary”. Do not store situation intent on ActionIntent. |

Empty fields omit (`null`); assembly never infers phase/intent from email or memories. Isolation: a work-scoped package must not receive a personal project's phase/intent.

## Technical Context

**Language/Version**: Python 3.14 (uv workspace); TypeScript/React 19 for Projects + Review Queue

**Primary Dependencies**: FastAPI + Pydantic (pcl-server), existing vault objects (Project, Goal), in-process MCP ToolHub, stdio bridge

**Storage**: Existing encrypted vault (`~/.pch`); no new SQLite tables. Operational fields persist on Project/Goal documents. Pending agent writes are `operational_proposal` vault objects (same pattern as `MemoryProposal`).

**Testing**: pytest (markers: `forbidden_context` for SC-004, `perf` for SC-007); core unit tests under `packages/pcl-core/tests/`; server contract tests under `packages/pcl-server/tests/contract/`

**Target Platform**: Local loopback server (127.0.0.1:8765), Linux/WSL2; fully offline

**Project Type**: Multi-package Python workspace (core + server + SDK) with static React frontend

**Performance Goals**: Operational copy is in-memory on the Project/Goal already loaded by E1 assembly; no extra FTS pass, no extra `store.list`, no network egress. Assembly remains < 2 s on a vault of a few thousand objects (SC-007), same budget as E1/E2.

**Constraints**: Loopback only; no new listener; no pcl-core I/O; no rename of SharedState or ActionIntent; no autonomous phase advancement; imported content cannot set phase; no Personal Agency planner; 001–003 not reopened

**Scale/Scope**: Three fields, one proposal type, one MCP tool, REST accept/reject, Projects UI + Review Queue; additive `SituationRef` fields only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Evidence |
|------|--------|----------|
| Loopback only; not a public server | PASS | Existing REST/MCP; no new bind |
| pcl-core free of I/O | PASS | Schema + in-memory copy in `retrieval/contract.py`; Hub orchestration stays in `service.py` |
| Least privilege | PASS | Grant filter already applied before SituationRef; `forbidden_context` test |
| Import is data | PASS | Sync/plugins never call patch/propose for these fields |
| Spec-not-vision; 001–003 closed | PASS | Child of E1; no Hub/pairing/plugin rewrite |
| No Personal Agency | PASS | Propose + owner confirm; no auto-advance of phase |
| Tests fail first | PASS | SC table below; NEW tests written before satisfying code |
| Coding agent not Hub client | PASS | Product fields only; this agent does not pair |

**Post-design re-check (Phase 1)**: PASS — no new tables, no second MCP read tool, no SharedState/ActionIntent rename. Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/007-situation-state-intent/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── operational-state.md
└── tasks.md             # Phase 2 — NOT created by /speckit-plan
```

### Source Code (repository root)

```text
packages/pcl-core/src/pcl_core/
├── schema/
│   ├── project.py           # EDIT: OperationalPhase enum; three optional fields on Project and Goal
│   ├── contract.py          # EDIT: SituationRef gains operational_phase, current_step, situation_intent
│   ├── proposal.py          # EDIT: OperationalProposal (type=operational_proposal)
│   └── __init__.py          # EDIT: export OperationalPhase, OperationalProposal
├── retrieval/
│   └── contract.py          # EDIT: copy fields onto SituationRef from selected Project; Goal overlay
└── service.py               # EDIT: propose_operational_state / accept / reject; PATCH already generic

packages/pcl-server/src/pcl_server/
├── mcp/tools_context.py     # EDIT: register propose_operational_state next to propose_memory
└── rest/routers/
    ├── projects.py          # REUSE: PATCH /v1/projects/{id} and PATCH /v1/goals/{id} already owner-canonical
    └── operational.py       # NEW: GET /v1/operational-proposals, POST …/accept, POST …/reject

packages/pcl-sdk/src/pcl_sdk/
└── mcp_bridge.py            # EDIT: TOOL_NAMES + TOOL_SCHEMAS for propose_operational_state

frontend/src/
├── api/types.ts             # EDIT: Project (+ Goal if listed) operational fields; OperationalProposal
├── pages/Projects.tsx       # EDIT: show/edit phase, step, intent
└── pages/ReviewQueue.tsx    # EDIT: list operational proposals alongside memory proposals

packages/pcl-core/tests/
├── test_operational_contract.py   # NEW: SC-001, SC-002, SC-003, SC-005 (fail first)
└── test_contract_perf.py          # EDIT: SC-007 — assembly < 2 s with fields set, no egress

packages/pcl-server/tests/
├── contract/test_operational_mcp.py                    # NEW: SC-006 two tokens agree; propose does not patch
└── forbidden_context/test_operational_isolation.py     # NEW: SC-004 work-scoped package (marker: forbidden_context)
```

**Structure Decision**: Follow existing layering — schema + pure copy in `pcl-core`, Hub methods in `service.py`, MCP registration in `pcl-server`, bridge schema in `pcl-sdk`, person-visible surfaces on existing Projects and Review Queue pages. No new packages, no graph, no planner, no second `get_*` MCP tool.

## Success criteria → tests

Tests written first and MUST fail before satisfying code.

| SC | Test (fail first) | Marker |
|----|-------------------|--------|
| SC-001 | `packages/pcl-core/tests/test_operational_contract.py::test_phase_in_situation_not_shared_state` | (default) |
| SC-002 | `packages/pcl-core/tests/test_operational_contract.py::test_intent_not_action_intent` | (default) |
| SC-003 | `packages/pcl-core/tests/test_operational_contract.py::test_patch_then_next_contract` | (default) |
| SC-004 | `packages/pcl-server/tests/forbidden_context/test_operational_isolation.py::test_work_scope_omits_personal_phase` | `forbidden_context` |
| SC-005 | `packages/pcl-core/tests/test_operational_contract.py::test_unset_assembles_without_inventing` | (default) |
| SC-006 | `packages/pcl-server/tests/contract/test_operational_mcp.py::test_two_agents_agree` | (default) |
| SC-007 | `packages/pcl-core/tests/test_contract_perf.py::test_contract_assembly_under_two_seconds` — fields set on the trip project; still < 2 s; no network egress; still `hub.get_context_contract` (no extra I/O path) | `perf` |

SC-001 must assert `situation.operational_phase == "comparing_itineraries"` and that SharedState `trip.phase` (if present in `state[]`) is not treated as that field. SC-007 extends the existing E1/E2 perf fixture rather than adding a second assembly entry point.

## Complexity Tracking

No constitution-gate violations to justify. Empty.
