# Implementation Plan: Runtime Adapters

**Branch**: `009-runtime-adapters` | **Date**: 2026-08-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/009-runtime-adapters/spec.md`

## Summary

E5 makes **portability real**: the Hub already pairs Cursor (002). This feature adds **Hermes** and **OpenClaw** as first-class catalog pairing targets with **native connection recipes** (Hermes YAML `mcp_servers` in `~/.hermes/config.yaml`; OpenClaw JSON `mcp.servers` in `~/.openclaw/openclaw.json`). Both still talk to the existing stdio bridge and `get_context_contract`. Two real-use runtimes, same grant, same purpose → identical situation package. Switching runtime does not rewrite the trip. Demo-agent is a **named non-example**.

Three names that stay three names:

| Name | What it is today | What E5 is not |
|------|------------------|----------------|
| Cursor recipe (002) | One real client, `mcpServers` JSON | Not “portability done.” Keep it; add Hermes + OpenClaw. |
| Demo-agent / test runtime | In-repo fixture | Not a real-use runtime. Do not count toward SC-001. |
| New A2A protocol | Constitution forbid | Not this epic. Same connection surface. |

No per-model adapter when the runtime already speaks the existing connection. Recipe **text shape** differs; the **package** must not.

## Technical Context

**Language/Version**: Python 3.14 (uv workspace); TypeScript/React 19 for Connections catalog copy UX

**Primary Dependencies**: Existing pairing catalog (`pcl_server/pairing/catalog.py`), REST `/v1/catalog/assistants` + `/v1/connections/{id}/recipe`, stdio bridge, `get_context_contract`

**Storage**: No new vault types. Catalog is code (same as 002). Recipes are ephemeral responses; `connection.recipe_issued` audit already exists.

**Testing**: pytest; extend `packages/pcl-server/tests/contract/test_assistant_catalog.py`; NEW `test_runtime_adapters.py` (two real-use tokens agree; switch/revoke); `forbidden_context` for a newly listed runtime name

**Target Platform**: Local loopback (127.0.0.1:8765), Linux/WSL2; fully offline

**Project Type**: Multi-package Python workspace with static React frontend

**Performance Goals**: Recipe render is in-process; no extra assembly cost. Package time stays on the E1 budget.

**Constraints**: Loopback only; recipes MUST use `127.0.0.1` (not a public bind); no pcl-core I/O; no A2A; no adapter-per-model; imported content cannot widen grants; 001–003 not reopened; no Personal Agency

**Scale/Scope**: Two catalog ids + native snippets + instructions; Connections copy path; contract tests. No new MCP tools.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Evidence |
|------|--------|----------|
| Loopback only; not a public server | PASS | Recipes keep `PCH_BASE=http://127.0.0.1:8765` |
| pcl-core free of I/O | PASS | Catalog/recipes stay in pcl-server pairing |
| Least privilege | PASS | Same grants; isolation test on new runtime name |
| Import is data | PASS | Pairing a second runtime does not ingest mail |
| Spec-not-vision; 001–003 closed | PASS | Child of 002 catalog + E1 contract |
| No Personal Agency | PASS | Runtimes consume context; they do not auto-act |
| Tests fail first | PASS | SC table below |
| Coding agent not Hub client | PASS | Product pairing only |
| No new A2A | PASS | Existing bridge + `get_context_contract` |

**Post-design re-check (Phase 1)**: PASS — native recipe shapes are still the same stdio bridge; no new listener; no protocol object. Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/009-runtime-adapters/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── runtime-recipes.md
└── tasks.md             # Phase 2 — NOT created by /speckit-plan
```

### Source Code (repository root)

```text
packages/pcl-server/src/pcl_server/
├── pairing/catalog.py           # EDIT: hermes + openclaw entries; native snippet + instructions
└── rest/routers/connections.py  # REUSE: GET catalog, POST recipe (422 unknown)

packages/pcl-sdk/src/pcl_sdk/
└── mcp_bridge.py                # REUSE: no new tools

frontend/src/
├── api/types.ts                 # EDIT: recipe snippet is native (not only mcpServers)
└── pages/Connections.tsx        # EDIT: copy native snippet; Hermes/OpenClaw appear from catalog

packages/pcl-server/tests/
├── contract/test_assistant_catalog.py           # EDIT: SC-001, SC-002 (hermes, openclaw, unknown 422)
├── contract/test_runtime_adapters.py            # NEW: SC-003 two real-use tokens; SC-004/005 switch+revoke
└── forbidden_context/test_runtime_isolation.py  # NEW: SC-006 work-scoped hermes/openclaw name
```

**Structure Decision**: Extend 002 catalog/recipes. Do not add MCP tools, vault types, or a second assembly entry point. Connections already loads `/v1/catalog/assistants`; adding catalog rows is the picker. Copy must serialize the **native** snippet (YAML fragment for Hermes, JSON for OpenClaw/Cursor), not force everything through Cursor's `mcpServers` envelope.

## Success criteria → tests

Tests written first and MUST fail before satisfying code.

| SC | Test (fail first) | Marker |
|----|-------------------|--------|
| SC-001 | `packages/pcl-server/tests/contract/test_assistant_catalog.py::test_catalog_lists_hermes_and_openclaw` | (default) |
| SC-002 | `test_assistant_catalog.py::test_hermes_and_openclaw_recipes` + `test_unknown_assistant_recipe_rejected` | (default) |
| SC-003 | `packages/pcl-server/tests/contract/test_runtime_adapters.py::test_two_real_use_runtimes_agree` | (default) |
| SC-004 | `test_runtime_adapters.py::test_switch_runtime_keeps_trip` | (default) |
| SC-005 | `test_runtime_adapters.py::test_revoke_does_not_delete_hub_objects` | (default) |
| SC-006 | `packages/pcl-server/tests/forbidden_context/test_runtime_isolation.py::test_work_scope_new_runtime_omits_personal_trip` | `forbidden_context` |
| SC-007 | Recipe `PCH_BASE` is loopback in catalog tests; no new bind. Assembly still `hub.get_context_contract` / existing MCP tool | (default) |

Live paste into a running Hermes/OpenClaw desktop is **manual** (quickstart). Automated tests prove catalog, native recipes, pairing, identical packages, switch/revoke, isolation.

## Complexity Tracking

No constitution-gate violations to justify. Empty.
