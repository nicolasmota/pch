# Implementation Plan: Development Loop Automation

**Branch**: `006-dev-loop-automation` | **Date**: 2026-08-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/006-dev-loop-automation/spec.md`

## Summary

The person starts **one** instruction (`/speckit-loop` / `pcl-sdk loop start`) with a description, a roadmap epic, an existing spec folder, or “next unfinished epic.” A **testable sequencer** in `pcl-sdk` owns the stage graph (specify → freeze Gauntlet bar → plan → two critics → tasks → analyze → implement → tests → delivery → complete), resume, finite retries, and refusals (vision/roadmap are not features; 001–003 are not reopened as epics). Speckit skills still do the writing; the sequencer is the gate they cannot skip. Design-only stops after Gauntlet WIN. Complete is impossible without fresh test evidence. No Hub pairing, no new listener, no auto-commit.

## Technical Context

**Language/Version**: Python 3.14 (uv workspace); Markdown skill for Cursor/Hermes agents

**Primary Dependencies**: existing `pcl-sdk` Click-less argparse CLI; Pydantic for `RUN.json`; stdlib `hashlib` for bar SHA-256. Speckit skills already in `.cursor/skills/speckit-*`

**Storage**: `specs/<nnn>-<name>/RUN.json` plus existing spec artifacts. No vault tables. No new SQLite.

**Testing**: pytest under `packages/pcl-sdk/tests/devloop/` (see contracts). Tests written first and must fail before the sequencer satisfies SC-001…SC-007. `make test` includes this package via workspace `testpaths`.

**Target Platform**: Local repo checkout (Linux/WSL2). Fully offline. No network listener.

**Project Type**: CLI module inside the existing SDK package + one project skill

**Performance Goals**: `loop next` / `status` on a spec folder is instantaneous (file read). Not a Hub latency target.

**Constraints**: Loopback/Hub unchanged; `pcl-core` untouched; coding agent is not a Hub client; FR-017 no commit/push unless the person asked; Gauntlet cannot be skipped; constitution 1.0.0 gates below

**Scale/Scope**: One active run per spec folder; two critics per Gauntlet round; 3 Gauntlet rounds; 2 test-repair cycles; era epics E1–E6 sequenced one at a time via `--roadmap`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` **v1.0.0** (ratified 2026-08-26). Gates:

| Gate | Status | Evidence |
|------|--------|----------|
| I. Person owns context; coding agent is not a Hub client | PASS | No pairing, no vault writes, no MCP tools added (D8, FR-016) |
| II. Local-first, loopback-only; not a public server | PASS | No new listener; CLI reads/writes repo files only |
| III. Least privilege / least context | PASS | No grant/assembly change; no `forbidden_context` delta required |
| IV. Provenance / explicit control | PASS | Person stop/resume; constitution exceptions `blocked_on_person`; no silent complete |
| V. Imported content is data | PASS | Loop does not ingest email/calendar; Speckit artifacts are repo files, not vault imports |
| `pcl-core` free of I/O | PASS | All new code in `pcl-sdk` + `.cursor/skills/` + `AGENTS.md` |
| Spec-not-vision; closed 001–003 | PASS | `refuse_reason=not_a_feature` / `closed_chapter` (D4, SC-007) |
| No Personal Intelligence / Personal Agency product | PASS | Repo DX only; `--roadmap` spawns child specs, does not implement horizon items |
| Tests fail before satisfying implementation | PASS | Contract lists test files; plan requires them first |
| No new cloud dependency / vector DB / extra policy engine | PASS | Stdlib + existing argparse/Pydantic |
| Secrets not committed | PASS | Loop does not add vault DBs, `.env`, or `.cursor/mcp.json` to git |

**Post-design re-check (Phase 1)**: PASS — RUN.json is a spec-folder file, not a vault object; no Hub UI; Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/006-dev-loop-automation/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1 — the one-trigger demo
├── contracts/
│   └── dev-loop.md      # CLI + RUN.json + fixture tests
├── PLAN-BAR.md          # Frozen before this pack (Gauntlet)
└── tasks.md             # Phase 2 (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
packages/pcl-sdk/src/pcl_sdk/
├── __main__.py                 # EDIT: subparser `loop`
├── devloop/
│   ├── __init__.py             # NEW: exports start/next/record/status
│   ├── stages.py               # NEW: stage graph, next_stage, complete_allowed
│   ├── runfile.py              # NEW: load/save RUN.json, bar hash
│   ├── refuse.py               # NEW: vision/roadmap/empty/closed-chapter/in-flight
│   └── cli.py                  # NEW: argparse handlers
packages/pcl-sdk/tests/devloop/
├── test_refuse.py              # NEW: SC-007 (fail first)
├── test_sequence.py            # NEW: SC-001 (fail first)
├── test_resume.py              # NEW: SC-006 (fail first)
├── test_gauntlet.py            # NEW: SC-002 (fail first)
├── test_delivery.py            # NEW: SC-003, SC-004, SC-005 (fail first)
└── test_status.py              # NEW: US3 status (fail first)
.cursor/skills/speckit-loop/
└── SKILL.md                    # NEW: one trigger; call CLI; run named Speckit/Gauntlet stage
AGENTS.md                       # EDIT: document `/speckit-loop` as the start instruction (SC-008)
```

**Structure Decision**: Sequencer in `pcl-sdk` (existing CLI package). Agent adapter is one Speckit-style skill. No `pcl-core`, `pcl-server`, or `frontend` files. Speckit’s `workflow.yml` is not the runtime (D1); do not replace speckit-specify/plan/tasks/implement skills.

## Success criteria → tests

| SC | Test (must fail first) |
|----|------------------------|
| SC-001 | `test_sequence.py::test_full_order_without_skip` |
| SC-002 | `test_gauntlet.py::test_plan_rejected_before_bar`; `test_lose_keeps_bar_hash` |
| SC-003 | `test_delivery.py::test_budget_exhausted_stops_before_implement` |
| SC-004 | `test_delivery.py::test_complete_requires_test_evidence` |
| SC-005 | `test_delivery.py::test_unmet_items_block_complete` |
| SC-006 | `test_resume.py::test_resume_after_specify_skips_specify` |
| SC-007 | `test_refuse.py::test_vision_and_roadmap_refused` |
| SC-008 | Skill + `AGENTS.md` start line; `test_status.py::test_help_lists_start` (CLI help names `loop start`) |

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution-gate violations. No new listener, cloud dependency, vector index, policy engine, or kernel I/O.
