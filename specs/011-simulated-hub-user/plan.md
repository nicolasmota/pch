# Implementation Plan: Simulated Hub User

**Branch**: `011-simulated-hub-user` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/011-simulated-hub-user/spec.md`

## Summary

The Hub owner starts a **scripted synthetic person** (`lived-stretch`) on an **isolated** space, watches a **live timeline** of owner writes and assistant asks, then inspects inputs/results. The engine lives in `pcl-sdk sim`; the existing loopback Hub hosts `/v1/sim` and a `/sim` page. It is not Personal Agency, not a foundation model, not E6, and not a second Context Engine — ticks call `Hub.create` / `search` / `get_context_contract` / `propose_memory` / `decide_proposal`. Cursor is an optional recipe for the same in-process pair.

Three names that stay three names:

| Name | What it is | What 011 is not |
|------|------------|-----------------|
| Synthetic user | Scripted ticks the owner watches | Personal Agency |
| E6 `pcl-sdk eval` | Four scored cases | This growing corpus |
| Silent seeder | `seed_trip` in tests | A timeline-less dump |

## Technical Context

**Language/Version**: Python 3.14 (uv workspace); TypeScript React 19 frontend (existing)

**Primary Dependencies**: `pcl_core.service.Hub` (create, search, get_context_contract, propose_memory, decide_proposal, mint_link, pair, create_grant); FastAPI routers already in `pcl-server`; existing SPA

**Storage**: Isolated Hub dir default `~/.pch-sim` (tests: temp). Run files `run.json` + `ticks.jsonl` in that dir. Everyday `~/.pch` not touched by default. No new SQLite schema.

**Testing**: pytest `packages/pcl-sdk/tests/sim/` and `packages/pcl-server/tests/test_sim_rest.py`. Tests written first and must fail before satisfying SC-001…SC-008.

**Target Platform**: Local loopback Hub (Linux/WSL2). Offline. Same `127.0.0.1:8765`.

**Project Type**: SDK CLI module + loopback REST + one SPA page

**Performance Goals**: First tick visible < 2 minutes (in practice milliseconds with `delay_ms=0`). Server pacing 200 ms/tick so a 50+ tick run is watchable.

**Constraints**: Loopback only; `pcl-core` no I/O added; no foundation model; no outbound actions; 001–003 not reopened; coding agent not Hub client; sim content is data; provenance via labels `sim` / `persona:<id>`

**Scale/Scope**: One bundled persona; one active run per sim space; ≥40 objects; ≥10 queries; two Hub instances in one process

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` **v1.0.0** (ratified 2026-08-26). Gates:

| Gate | Status | Evidence |
|------|--------|----------|
| I. Person owns context; coding agent is not a Hub client | PASS | Isolated `sim_hub`; optional MCP recipe printed, never auto-written to `.cursor/mcp.json`; this coding agent does not pair as the sim |
| II. Local-first, loopback-only; not a public server | PASS | No new listener; `/v1/sim` on existing app (D1, D5) |
| III. Least privilege / least context | PASS | Assistant ticks use real grants; narrow-grant test (B10); no ALLOW-all stub |
| IV. Provenance / explicit control | PASS | Labels `sim`/`persona:*`; pause/stop; everyday requires confirm token |
| V. Imported / sim content is data, never instruction | PASS | Ticks are data writes/queries; compile rejects outbound actions |
| `pcl-core` free of I/O | PASS | Engine in `pcl-sdk`; REST in `pcl-server`; core only reused `Hub` methods |
| Spec-not-vision; closed 001–003 | PASS | Child spec via `--desc` (harness, like 006); no new vault types; does not implement VISION/ROADMAP |
| No Personal Intelligence / Personal Agency | PASS | Scripted ticks; forbidden `propose_action`; D7 |
| Hub must not ship its own agent runtime for real users | PASS | Observation harness + in-process pair; not a product agent that replaces Cursor |
| Tests fail before satisfying implementation | PASS | SC table below |
| No new cloud / vector DB / extra policy engine | PASS | Stdlib + existing Hub policy |
| Secrets not committed | PASS | Recipe printed to stdout; no commit of tokens or vault DBs |

**Post-design re-check (Phase 1)**: PASS — two Hub instances on one loopback app is not a second bind; Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/011-simulated-hub-user/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/sim-harness.md
├── PLAN-BAR.md              # Frozen before this pack
└── tasks.md                 # /speckit-tasks — NOT created by /speckit-plan
```

### Source Code (repository root)

```text
packages/pcl-sdk/src/pcl_sdk/
├── __main__.py                    # EDIT: subparser `sim`
└── sim/
    ├── __init__.py                # NEW: compile, run, status
    ├── persona.py                 # NEW: load + compile lived-stretch
    ├── personas/lived-stretch.json  # NEW: declarative persona
    ├── runner.py                  # NEW: execute ticks against Hub
    ├── records.py                 # NEW: run.json / ticks.jsonl
    └── cli.py                     # NEW: dump/run/status/pause/resume/stop

packages/pcl-sdk/tests/sim/
├── test_run.py                    # NEW: SC-001, SC-002
├── test_timeline.py               # NEW: SC-003, SC-006
├── test_isolation.py              # NEW: SC-004, everyday refuse
├── test_queries.py                # NEW: SC-005
├── test_pair.py                   # NEW: SC-007, withhold
├── test_roles.py                  # NEW: FR-005
└── test_refuse.py                 # NEW: SC-008

packages/pcl-server/src/pcl_server/rest/
├── app.py                         # EDIT: sim_hub, include sim router, runner task
└── routers/sim.py                 # NEW: /v1/sim/*

packages/pcl-server/tests/test_sim_rest.py  # NEW: live seq increases

frontend/src/
├── App.tsx                        # EDIT: /sim route
├── components/Sidebar.tsx         # EDIT: Simulator nav
├── api/types.ts                   # EDIT: sim types
└── pages/Sim.tsx                  # NEW: timeline + inspector
```

**Structure Decision**: SDK owns the testable engine (D1). Server hosts it for the SPA (D5). Frontend is one page (bar 1). No `pcl-core` files. E6 `eval/` package is not modified.

## Success criteria → tests

| SC | Test (must fail first) |
|----|------------------------|
| SC-001 | `packages/pcl-sdk/tests/sim/test_run.py::test_first_tick_under_two_minutes` |
| SC-002 | `test_run.py::test_lived_stretch_volume` |
| SC-003 | `packages/pcl-sdk/tests/sim/test_timeline.py::test_every_create_has_tick` |
| SC-004 | `packages/pcl-sdk/tests/sim/test_isolation.py::test_everyday_vault_unchanged` |
| SC-005 | `packages/pcl-sdk/tests/sim/test_queries.py::test_situation_asks_hit_trip` |
| SC-006 | `test_timeline.py::test_tick_input_output` |
| SC-007 | `packages/pcl-sdk/tests/sim/test_pair.py::test_via_label_optional_path` |
| SC-008 | `packages/pcl-sdk/tests/sim/test_refuse.py::test_no_outbound_actions` |

REST live: `packages/pcl-server/tests/test_sim_rest.py::test_seq_increases_before_complete` (bar 1).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution-gate violations. No new listener, cloud dependency, vector index, policy engine, or kernel I/O. Second `Hub` in-process is reuse of the existing engine, not a new runtime product.
