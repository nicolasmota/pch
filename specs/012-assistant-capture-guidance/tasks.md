---
description: "Task list for Assistant Capture Guidance"
---

# Tasks: Assistant Capture Guidance

**Input**: Design documents from `/specs/012-assistant-capture-guidance/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/capture-guidance.md, quickstart.md

**Tests**: Included — SC-001…SC-007. Write tests first; they MUST fail before implementation. Constitution 1.0.0: no `pcl-core` I/O, no new listener, no Hub writes to assistant config, coding agent is not a Hub client by default.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 / US2 / US3 from spec.md
- Include exact file paths

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Module skeleton so tests can import constants

- [x] T001 Create `packages/pcl-sdk/src/pcl_sdk/capture_guidance.py` with placeholder exports `SITUATION_READ_DESCRIPTION`, `MEMORY_PROPOSE_DESCRIPTION`, `RUNTIME_RULE`, `NON_CAPTURE_DESCRIPTION`, `THREE_TURN_LINES`, `follow_capture_guidance`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared constants and eval helper used by bridge, recipes, and tests. Blocks all stories.

**⚠️ CRITICAL**: No user story implementation until this phase is complete. Tests for later stories may import these names.

- [x] T002 Implement capture strings and `follow_capture_guidance(lines, tools) -> list[str]` in `packages/pcl-sdk/src/pcl_sdk/capture_guidance.py` (data-model.md + contracts/capture-guidance.md). Descriptions MUST include when-to-use / when-not. `RUNTIME_RULE` MUST mention task-start read, durable-fact propose, propose-not-canonical, empty honesty. Helper MUST return `get_context_contract` then two `propose_memory` for `THREE_TURN_LINES` only if tool descriptions contain the trigger phrases; otherwise raise.

**Checkpoint**: Constants importable; helper encodes SC-003 sequence

---

## Phase 3: User Story 1 - Connected assistant knows when to read and propose (Priority: P1) 🎯 MVP

**Goal**: `tools/list` carries when-to-read / when-to-propose. Three-turn eval: situation request + two proposals, none canonical before accept.

**Independent Test**: `test_situation_and_propose_descriptions_include_when_to_use` and `test_three_turn_eval_proposes_not_canonical` pass.

### Tests for User Story 1 (MUST fail first)

- [x] T003 [P] [US1] `test_situation_and_propose_descriptions_include_when_to_use` in `packages/pcl-sdk/tests/test_mcp_bridge.py` (SC-002)
- [x] T004 [P] [US1] `test_three_turn_eval_proposes_not_canonical` in `packages/pcl-server/tests/contract/test_capture_guidance.py` (SC-003)

### Implementation for User Story 1

- [x] T005 [US1] Wire `_mcp_tools` in `packages/pcl-sdk/src/pcl_sdk/mcp_bridge.py` to use `SITUATION_READ_DESCRIPTION` / `MEMORY_PROPOSE_DESCRIPTION` (stop `name.replace("_", " ")` for those tools). Optional `NON_CAPTURE_DESCRIPTION` for other listed tools.
- [x] T006 [US1] Drive three-turn REST MCP calls in `packages/pcl-server/tests/contract/test_capture_guidance.py` using `follow_capture_guidance` + paired token; assert 0 canonical memories until owner accept.

**Checkpoint**: US1 independently demoable via `tools/list` + contract eval. No new MCP tool.

---

## Phase 4: User Story 2 - Pairing reaches every window (Priority: P2)

**Goal**: Cursor recipe instructs user/runtime MCP. Project `.cursor/mcp.json` is not the only supported path. Hub does not write assistant config.

**Independent Test**: `test_cursor_recipe_is_person_level_not_project_only` and `test_recipe_does_not_write_assistant_config` pass.

### Tests for User Story 2 (MUST fail first)

- [x] T007 [P] [US2] `test_cursor_recipe_is_person_level_not_project_only` in `packages/pcl-server/tests/contract/test_assistant_catalog.py` (SC-001, SC-004)
- [x] T008 [P] [US2] `test_recipe_does_not_write_assistant_config` in `packages/pcl-server/tests/contract/test_capture_guidance.py` (SC-006)

### Implementation for User Story 2

- [x] T009 [US2] Update Cursor (and other `mcpServers`) `instructions` in `packages/pcl-server/src/pcl_server/pairing/catalog.py` to person/runtime attach; keep snippet shapes from 009; `PCH_BASE` loopback.

**Checkpoint**: Recipe text matches quickstart “other window.” No file writes under `~/.cursor`.

---

## Phase 5: User Story 3 - Copyable runtime rule; this repo is not a Hub client (Priority: P3)

**Goal**: Every supported recipe includes `runtime_rule`. Connections shows/copies it. `AGENTS.md` still forbids Hub-client default.

**Independent Test**: `test_recipes_include_copyable_runtime_rule` and `test_agents_md_still_forbids_hub_client` pass.

### Tests for User Story 3 (MUST fail first)

- [x] T010 [P] [US3] `test_recipes_include_copyable_runtime_rule` in `packages/pcl-server/tests/contract/test_assistant_catalog.py` (SC-005) — cursor, hermes, openclaw at minimum
- [x] T011 [P] [US3] `test_agents_md_still_forbids_hub_client` in `packages/pcl-server/tests/contract/test_capture_guidance.py` (SC-007)

### Implementation for User Story 3

- [x] T012 [US3] Add `runtime_rule` from `RUNTIME_RULE` to `render_recipe` in `packages/pcl-server/src/pcl_server/pairing/catalog.py` for every supported assistant
- [x] T013 [US3] Add `runtime_rule?: string` to `AssistantRecipe` in `frontend/src/api/types.ts`; show the rule and include it in copy in `frontend/src/pages/Connections.tsx`

**Checkpoint**: All three stories independently testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T014 Confirm `AGENTS.md` still contains the not-a-Hub-client sentence (no weakening)
- [x] T015 Run `make test` and `make lint`; `uv run pcl-sdk loop evidence` then record test stage

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: start immediately
- **Foundational (Phase 2)**: depends on Setup — BLOCKS stories
- **US1 (Phase 3)**: after Foundational — MVP
- **US2 (Phase 4)**: after catalog exists (same `catalog.py` as US3; sequential with US3 on that file)
- **US3 (Phase 5)**: after US2 instructions exist (same `catalog.py`)
- **Polish**: after stories

### User Story Dependencies

- **US1**: no other stories (bridge + eval)
- **US2**: catalog instructions; independent of US1 runtime
- **US3**: extends US2 recipe payload; frontend depends on `runtime_rule` field

### Parallel Opportunities

- T003/T004 after T002
- T007/T008 after T002 (tests fail until T009)
- T010/T011 after T002
- Do not parallelize T009 and T012 on `catalog.py`

---

## Parallel Example: User Story 1 tests

```bash
# After T002, write failing tests together:
# packages/pcl-sdk/tests/test_mcp_bridge.py
# packages/pcl-server/tests/contract/test_capture_guidance.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1–2 constants + helper
2. Failing US1 tests
3. Bridge descriptions + three-turn eval green
4. Validate SC-002, SC-003

### Incremental Delivery

1. US1 → tools know when to call
2. US2 → other windows can see the Hub
3. US3 → pasteable rule + Connections
4. Polish + `make test`

### Notes

- Do not commit unless the person asked
- Do not write `.cursor/mcp.json` or `~/.cursor/mcp.json`
- Do not modify `pcl-core` except by calling existing Hub methods
- Do not add MCP tools or listeners
- Tests fail before satisfying code
