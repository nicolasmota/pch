# Implementation Plan: Assistant Capture Guidance

**Branch**: `012-assistant-capture-guidance` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/012-assistant-capture-guidance/spec.md`

## Summary

Paired assistants **ignore** the Hub unless told when to call. Today the stdio bridge lists tools as the function name with spaces (`propose memory`), and the Cursor recipe says paste into **this project's** `.cursor/mcp.json`. Other windows never see the Hub; even this window does not capture.

This child spec (002/009 recipes + bridge; do not reopen 001–003) ships:

1. **When-to-read / when-to-propose** text on `get_context_contract` and `propose_memory` (existing tools; no new protocol).
2. **Cursor recipe** instructs person/runtime attach (Cursor Settings → MCP / user-level), not “only this repo’s project file.” Same `mcpServers` snippet; Hermes/OpenClaw keep native paths (already user-level).
3. **Copyable runtime rule** on every supported recipe. Hub never writes the person’s assistant config.
4. **Three-turn eval** (deterministic fixture, not a live model): task start → situation request; two durable facts → two proposals; none canonical before accept.
5. **AGENTS.md** stays: coding agent on this repo is not a Hub client by default.

## Technical Context

**Language/Version**: Python 3.14 (uv workspace); TypeScript/React 19 only if Connections must show the runtime-rule block (prefer render in recipe JSON so UI already copies `instructions`)

**Primary Dependencies**: `pcl_sdk.mcp_bridge` (`tools/list` descriptions), `pcl_server.pairing.catalog.render_recipe`, existing `get_context_contract` / `propose_memory`, review queue

**Storage**: No new vault types. Guidance is code constants. Recipes remain ephemeral POST responses.

**Testing**: pytest; NEW contract tests on `tools/list` descriptions; recipe instruction strings; three-turn capture eval; AGENTS.md still contains the not-a-client sentence; 0 filesystem writes to `~/.cursor/mcp.json`

**Target Platform**: Local loopback (127.0.0.1:8765), Linux/WSL2; fully offline

**Project Type**: Multi-package Python workspace; recipe copy on existing Connections page

**Performance Goals**: `tools/list` stays in-process; description text is static. No extra Hub round-trip to fetch guidance.

**Constraints**: Loopback only; no pcl-core I/O; no new listener; Hub MUST NOT write assistant config; propose-not-canonical; imported content is data; 001–003 not reopened; coding agent on this repo is not a Hub client by default; no Personal Agency / Intelligence

**Scale/Scope**: Two tool descriptions (situation + propose) + optional one-liners on other tools; recipe `instructions` + `runtime_rule` field; Connections displays the rule if the recipe payload includes it; one eval fixture. No new MCP tools. No second assembly entry.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Evidence |
|------|--------|----------|
| Loopback only; not a public server | PASS | Recipes keep `PCH_BASE=http://127.0.0.1:8765`; no new bind |
| pcl-core free of I/O | PASS | Descriptions + recipes in pcl-sdk / pcl-server pairing |
| Least privilege | PASS | Same grants; empty/off-grant honesty in guidance |
| Import is data | PASS | Guidance forbids proposing mail/calendar as orders or extracting situation from them |
| Spec-not-vision; 001–003 closed | PASS | Child of 002 bridge + 009 recipes |
| No Personal Agency | PASS | Propose only; no outward act |
| Tests fail first | PASS | SC table below |
| Coding agent not Hub client | PASS | AGENTS.md unchanged as default; Hub does not pair the implementer |
| No new A2A | PASS | Existing tools only |
| No chat scraper | PASS | D5: no transcript importer, no new listener |

**Post-design re-check (Phase 1)**: PASS — guidance is static strings on existing `tools/list` and recipe JSON; no vault types; no listener; Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/012-assistant-capture-guidance/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── capture-guidance.md
└── tasks.md             # Phase 2 — NOT created by /speckit-plan
```

### Source Code (repository root)

```text
packages/pcl-sdk/src/pcl_sdk/
├── mcp_bridge.py                    # EDIT: TOOL_DESCRIPTIONS; stop name.replace("_"," ")
└── capture_guidance.py              # NEW: shared when-to-use constants + runtime_rule text + three-turn expected calls

packages/pcl-server/src/pcl_server/
└── pairing/catalog.py               # EDIT: Cursor instructions = user MCP; runtime_rule on all supported ids

frontend/src/pages/Connections.tsx   # EDIT: show/copy runtime_rule when present (plain text)

packages/pcl-sdk/tests/
└── test_mcp_bridge.py               # EDIT or NEW: tools/list descriptions (SC-002)

packages/pcl-server/tests/contract/
├── test_assistant_catalog.py        # EDIT: recipe instructions person-level; runtime_rule present (SC-004, SC-005)
└── test_capture_guidance.py         # NEW: SC-003 three-turn eval; SC-006 no config write

tests or repo root:
└── AGENTS.md                        # REUSE: assert default not-a-client sentence still present (SC-007)
```

**Structure Decision**: Put capture strings in `pcl_sdk.capture_guidance` so the bridge `tools/list`, the recipe `runtime_rule`, and the eval fixture **cannot drift**. Catalog `render_recipe` imports the same rule text. Do not add MCP tools. Do not write `~/.cursor/mcp.json`. Connections copies the new field; if the page already copies `instructions`, extend the copy payload rather than a new route.

## Success criteria → tests

Tests written first and MUST fail before satisfying code.

| SC | Test (fail first) | Marker |
|----|-------------------|--------|
| SC-002 | `packages/pcl-sdk/tests/test_mcp_bridge.py::test_situation_and_propose_descriptions_include_when_to_use` | (default) |
| SC-003 | `packages/pcl-server/tests/contract/test_capture_guidance.py::test_three_turn_eval_proposes_not_canonical` | (default) |
| SC-004 | `packages/pcl-server/tests/contract/test_assistant_catalog.py::test_cursor_recipe_is_person_level_not_project_only` | (default) |
| SC-005 | `test_assistant_catalog.py::test_recipes_include_copyable_runtime_rule` | (default) |
| SC-001 | Same catalog test: instructions mention every window / user MCP; plus quickstart manual | (default) |
| SC-006 | `test_capture_guidance.py::test_recipe_does_not_write_assistant_config` | (default) |
| SC-007 | `test_capture_guidance.py::test_agents_md_still_forbids_hub_client` | (default) |
