# Interface Contract: Capture guidance + person-level recipes

**Feature**: `specs/012-assistant-capture-guidance/` · **Date**: 2026-08-27  
**Surfaces**: existing stdio `tools/list`; existing `POST /v1/connections/{id}/recipe`; Connections copy. **No new MCP tool. No new REST router.**

## tools/list (stdio bridge)

`description` MUST NOT be `name.replace("_", " ")` for capture tools.

| Tool | Description MUST include (intent, not exact copy) |
|------|---------------------------------------------------|
| `get_context_contract` | Call at **task start** when the work depends on the person or current situation; pass `purpose`; if the package is empty or withheld, **do not invent** life facts. |
| `propose_memory` | Call when the **person states** a durable fact they want remembered; this is a **proposal**, not live truth; do not propose guesses, demo fiction, or implementation chatter. |

Other tools: MAY keep short names **or** a one-line non-capture disclaimer. SC-002 only fails if the two rows above are bare names.

`inputSchema` for those tools is **unchanged**.

## Recipe POST

`POST /v1/connections/{connection_id}/recipe` body unchanged: `{ "assistant": "<id>" }`.

200 body MUST include:

| Field | Constraint |
|-------|------------|
| `instructions` | Cursor: MUST tell the person to attach at **user/runtime MCP** so every window on this machine can use the Hub. MUST NOT say project `.cursor/mcp.json` is the **only** supported location. Hermes/OpenClaw: keep existing home-config instructions. |
| `runtime_rule` | Non-empty string. MUST mention: situation at task start; propose durable facts; not canonical; do not invent when empty. |
| `snippet` | Unchanged shapes from 009 (`cursor-mcp-json` / `hermes-yaml` / `openclaw-json`). `env.PCH_BASE` loopback. |

The handler MUST NOT create or modify files under `~/.cursor`, `~/.hermes`, or `~/.openclaw`.

Unknown assistant → 422 (existing).

## Three-turn eval (test contract)

Paired token against a temp Hub (plain). Empty vault. Drive:

1. Person task-start line → `POST /v1/mcp/tools/get_context_contract` `{ "purpose": "continue planning the trip" }` → 200; situation may be empty.
2. Two `propose_memory` calls with the fixture facts → 200; `GET` memories canonical list still 0 (or proposals pending only).
3. Owner accept one proposal → that memory becomes listable as live.

`follow_capture_guidance` given `tools/list` + the three person lines MUST select the same tool names in that order. If it does not, descriptions drifted.

## Behavioral contract

| # | Guarantee | Spec ref |
|---|-----------|----------|
| B1 | Situation + propose tool descriptions include when-to-use / when-not | SC-002, FR-001, FR-002 |
| B2 | Cursor recipe is person-level attach, not project-only | SC-001, SC-004, FR-004 |
| B3 | All supported recipe ids include `runtime_rule` | SC-005, FR-005, FR-006 |
| B4 | Three-turn: 1 contract + 2 proposes; 0 canonical before accept | SC-003, FR-003, FR-010 |
| B5 | Recipe POST writes 0 assistant config files | SC-006, FR-007 |
| B6 | AGENTS.md still forbids Hub-client default | SC-007, FR-008 |
| B7 | No new MCP tool, no new listener | FR-009 |

## Fixture tests (fail first)

| SC | File::test |
|----|------------|
| SC-002 | `packages/pcl-sdk/tests/test_mcp_bridge.py::test_situation_and_propose_descriptions_include_when_to_use` |
| SC-003 | `packages/pcl-server/tests/contract/test_capture_guidance.py::test_three_turn_eval_proposes_not_canonical` |
| SC-004 / SC-001 | `packages/pcl-server/tests/contract/test_assistant_catalog.py::test_cursor_recipe_is_person_level_not_project_only` |
| SC-005 | `test_assistant_catalog.py::test_recipes_include_copyable_runtime_rule` |
| SC-006 | `test_capture_guidance.py::test_recipe_does_not_write_assistant_config` |
| SC-007 | `test_capture_guidance.py::test_agents_md_still_forbids_hub_client` |
