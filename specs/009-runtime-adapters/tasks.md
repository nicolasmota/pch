---

description: "Task list for Runtime Adapters"
---

# Tasks: Runtime Adapters

**Input**: Design documents from `/specs/009-runtime-adapters/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/runtime-recipes.md, quickstart.md

**Tests**: Included — SC-001…SC-007. Write tests first; they MUST fail before implementation.

**Organization**: Tasks are grouped by user story so each story is an independently testable increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete sibling tasks)
- **[Story]**: US1 (two real-use packages), US2 (switch without rewrite), US3 (catalog + native recipes)

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 Confirm 002 catalog/recipe surface in `packages/pcl-server/src/pcl_server/pairing/catalog.py` and `packages/pcl-server/src/pcl_server/rest/routers/connections.py` — no new MCP tool, no new vault type

**Checkpoint**: Child of 002 + E1; demo-agent is not a catalog id

---

## Phase 2: Foundational (Blocking Prerequisites)

- [x] T002 Add `format` on recipe responses (`cursor-mcp-json` \| `hermes-yaml` \| `openclaw-json`) in `packages/pcl-server/src/pcl_server/pairing/catalog.py` without breaking Cursor `mcpServers`

**Checkpoint**: Cursor recipe still 200; format field present

---

## Phase 3: User Story 1 - A Second Real Assistant Gets the Same Trip Package (Priority: P1) 🎯 MVP

**Goal**: Hermes and OpenClaw are supported catalog targets. Two real-use tokens, same grant, same trip purpose, identical package.

### Tests for User Story 1 ⚠️ write first, watch them fail

- [x] T003 [P] [US1] `test_catalog_lists_hermes_and_openclaw` in `packages/pcl-server/tests/contract/test_assistant_catalog.py`
- [x] T004 [P] [US1] `test_two_real_use_runtimes_agree` in `packages/pcl-server/tests/contract/test_runtime_adapters.py`

### Implementation for User Story 1

- [x] T005 [US1] Add `hermes` and `openclaw` supported entries in `packages/pcl-server/src/pcl_server/pairing/catalog.py`
- [x] T006 [US1] Keep `get_context_contract` as the only package tool (no code path named for a second read tool)

**Checkpoint**: Catalog lists both; two tokens agree

---

## Phase 4: User Story 2 - Switching Runtime Does Not Mean Re-editing the Trip (Priority: P2)

### Tests for User Story 2 ⚠️ write first

- [x] T007 [P] [US2] `test_switch_runtime_keeps_trip` and `test_revoke_does_not_delete_hub_objects` in `packages/pcl-server/tests/contract/test_runtime_adapters.py`

### Implementation for User Story 2

- [x] T008 [US2] Use existing revoke; confirm Hub methods do not cascade-delete projects on connection revoke (fix only if tests prove a cascade)

**Checkpoint**: Switch/revoke green

---

## Phase 5: User Story 3 - The Person Can See Which Runtimes Are Supported (Priority: P3)

### Tests for User Story 3 ⚠️ write first

- [x] T009 [P] [US3] `test_hermes_and_openclaw_recipes` and `test_unknown_assistant_recipe_rejected` in `packages/pcl-server/tests/contract/test_assistant_catalog.py` (native snippet keys + loopback `PCH_BASE`)
- [x] T010 [P] [US3] Isolation `packages/pcl-server/tests/forbidden_context/test_runtime_isolation.py::test_work_scope_new_runtime_omits_personal_trip`

### Implementation for User Story 3

- [x] T011 [US3] Native `render_recipe` shapes (Hermes `mcp_servers`, OpenClaw `mcp.servers`, Cursor unchanged) in `packages/pcl-server/src/pcl_server/pairing/catalog.py`
- [x] T012 [US3] Types in `frontend/src/api/types.ts`; Connections copy native snippet (YAML text when `format === "hermes-yaml"`) in `frontend/src/pages/Connections.tsx`

**Checkpoint**: Recipes native; picker lists Hermes/OpenClaw; isolation green

---

## Phase 6: Polish

- [x] T013 [P] Run `make test`; record loop evidence
- [x] T014 Confirm quickstart.md against the SC map in `specs/009-runtime-adapters/contracts/runtime-recipes.md`

---

## Dependencies & Execution Order

- Setup → Foundational → US1 (MVP) → US2 → US3 → Polish
- T011 may land with T005 (same file); do not silent-write a second MCP tool

## Notes

- Do not count demo-agent as real-use
- Do not add a new protocol or per-model adapter
- Commit only if the person asked
