# Implementation Plan: Context Quality Evaluation

**Branch**: `010-context-eval` | **Date**: 2026-08-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/010-context-eval/spec.md`

## Summary

E6 adds a **local eval harness** that scores the existing situation package on four fixed cases (killer demo, temporal conflict, isolation, runtime switch) and seven metrics (retrieval accuracy, precision, freshness, conflict resolution, portability, user correction, assembly cost). It lives in `pcl-sdk eval run`, uses an ephemeral vault by default, and prints a local report. It does **not** publish a benchmark and does **not** score token counts.

Three names that stay three names:

| Name | What it is today | What E6 is not |
|------|------------------|----------------|
| `make test` | Engineering suite | Not a named quality scorecard for the person |
| Public benchmark | Out of constitution/roadmap | Not this epic |
| Token optimization | Product anti-goal | Assembly cost is **duration** (+ optional item counts), not tokenizer races |

The harness **calls** `Hub.get_context_contract` (and pairing/grants/as_of/trip seed). It does not assemble a second contract.

## Technical Context

**Language/Version**: Python 3.14 (uv workspace); pcl-sdk CLI

**Primary Dependencies**: `pcl_core.service.Hub`, `trip_seed` / `spicy_seed` / `drop_london`, existing grants/pairing

**Storage**: Ephemeral temp vault (default). Does not write `~/.pch` unless a future flag is added (out of required path). Report is stdout JSON.

**Testing**: pytest under `packages/pcl-sdk/tests/eval/`

**Target Platform**: Local CLI, Linux/WSL2, offline

**Project Type**: SDK CLI + in-process Hub (plain sqlite temp dir)

**Performance Goals**: Killer-demo assembly still < 2 s (SC-007)

**Constraints**: No public upload; no pcl-core I/O added; coding agent not Hub client; 001–003 closed; no Personal Intelligence/Agency; loopback if any HTTP (this harness is in-process, no listener)

**Scale/Scope**: Four cases, one report schema, one CLI command

## Constitution Check

| Gate | Status | Evidence |
|------|--------|----------|
| Loopback / not public | PASS | In-process Hub; no new bind; no upload |
| pcl-core free of I/O | PASS | Harness in pcl-sdk; core unchanged except reuse |
| Least privilege | PASS | Isolation case uses real `policy.evaluate` via grants |
| Import is data | PASS | No import path |
| Spec-not-vision; 001–003 closed | PASS | Scores E1–E5 |
| No Personal Agency/Intelligence | PASS | Metrics only |
| Tests fail first | PASS | SC table |
| Coding agent not Hub client | PASS | Temp dir vault, not `~/.pch` |

**Post-design re-check**: PASS. Complexity Tracking empty.

## Project Structure

```text
specs/010-context-eval/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/eval-report.md
└── tasks.md

packages/pcl-sdk/src/pcl_sdk/
├── eval/
│   ├── __init__.py
│   └── harness.py          # NEW: four cases + metrics
└── __main__.py             # EDIT: eval run

packages/pcl-sdk/tests/eval/
└── test_harness.py         # NEW: SC-001…SC-007
```

**Structure Decision**: SDK-side harness. No new MCP tool. No frontend required (CLI is the person-visible surface).

## Success criteria → tests

| SC | Test (fail first) | Marker |
|----|-------------------|--------|
| SC-001 | `packages/pcl-sdk/tests/eval/test_harness.py::test_killer_demo_accuracy` | (default) |
| SC-002 | `test_harness.py::test_isolation_precision` | (default) |
| SC-003 | `test_harness.py::test_freshness_as_of` | (default) |
| SC-004 | `test_harness.py::test_conflict_listed` | (default) |
| SC-005 | `test_harness.py::test_correction_drop_london` | (default) |
| SC-006 | `test_harness.py::test_portability_and_revoke` | (default) |
| SC-007 | `test_harness.py::test_assembly_cost_reported` | (default) |

## Complexity Tracking

Empty.
