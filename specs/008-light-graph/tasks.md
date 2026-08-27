---

description: "Task list for Light Graph"
---

# Tasks: Light Graph

**Input**: Design documents from `/specs/008-light-graph/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/relations.md, quickstart.md

**Tests**: Included — SC-001…SC-007. Write tests first; they MUST fail before implementation.

**Organization**: Tasks are grouped by user story so each story is an independently testable increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete sibling tasks)
- **[Story]**: US1 (relations on package), US2 (isolation), US3 (Hub + propose)

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 Add `RelationType` and `Relation` (`from_id`, `to_id`, `relation_type`, live/removed) in `packages/pcl-core/src/pcl_core/schema/relation.py`
- [x] T002 [P] Add `RelationRef` and required `relations: list[RelationRef]` on `ContextContract` in `packages/pcl-core/src/pcl_core/schema/contract.py`
- [x] T003 Add `EntityType.RELATION`, PREFIXES, export + `TYPE_MODELS` in `packages/pcl-core/src/pcl_core/schema/metadata.py`, `packages/pcl-core/src/pcl_core/ids.py`, `packages/pcl-core/src/pcl_core/schema/__init__.py`

**Checkpoint**: Models exist; assembly still omits relations until T010

---

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Schema tests: four types; self-link rejected; pair uniqueness in `packages/pcl-core/tests/test_relation_schema.py`
- [x] T005 Add `RelationProposal` in `packages/pcl-core/src/pcl_core/schema/relation.py` (or `proposal.py`) and export it

**Checkpoint**: Proposal model exists; no MCP yet

---

## Phase 3: User Story 1 - The Package Names How This Work Hangs Together (Priority: P1) 🎯 MVP

**Goal**: Owner creates `depends_on` / `blocked_by`. `get_context_contract` includes anchor links plus one hop. FKs are not auto-promoted. Two agents agree. Unset still assembles. Perf < 2 s.

**Independent Test**: Trip `depends_on` visa; visa `blocked_by` person; two agents see both links (SC-001, SC-002, SC-006). No relations → `[]` (SC-005). Perf still < 2 s (SC-007).

### Tests for User Story 1 ⚠️ write first, watch them fail

- [x] T006 [P] [US1] `test_depends_on_in_package`, `test_one_hop_blocked_by`, `test_unset_assembles_without_inventing` in `packages/pcl-core/tests/test_relation_contract.py`
- [x] T007 [P] [US1] Two MCP tokens agree (SC-006) in `packages/pcl-server/tests/contract/test_relation_mcp.py`
- [x] T008 [P] [US1] Extend `packages/pcl-core/tests/test_contract_perf.py` with relations seeded (SC-007)

### Implementation for User Story 1

- [x] T009 [US1] `Hub.create_relation` / `list_relations` / `delete_relation` (self-link 422, duplicate 409, PATCH type) in `packages/pcl-core/src/pcl_core/service.py`
- [x] T010 [US1] Collect grant-visible relations (anchor + one hop, cap 20) onto `ContextContract.relations` in `packages/pcl-core/src/pcl_core/retrieval/contract.py`; do not emit `project_id` as `owned_by`
- [x] T011 [US1] Owner REST `POST/GET/DELETE /v1/relations` and `PATCH /v1/relations/{id}` in `packages/pcl-server/src/pcl_server/rest/routers/relations.py` included from `packages/pcl-server/src/pcl_server/rest/app.py`

**Checkpoint**: Trip→visa→person on the package; FKs distinct

---

## Phase 4: User Story 2 - Out-of-Scope Ends Stay Hidden (Priority: P2)

**Independent Test**: Personal depends_on; work agent sees 0 personal relations (SC-004).

### Tests for User Story 2 ⚠️ write first, watch them fail

- [x] T012 [P] [US2] Isolation in `packages/pcl-server/tests/forbidden_context/test_relation_isolation.py`

### Implementation for User Story 2

- [x] T013 [US2] Omit relation unless both ends ALLOW; omission counts only, no titles/ids, in `packages/pcl-core/src/pcl_core/retrieval/contract.py`

**Checkpoint**: Isolation green

---

## Phase 5: User Story 3 - The Person Can See and Correct Relations (Priority: P3)

**Independent Test**: Projects page add/remove/change type; propose does not live-write until accept.

### Tests for User Story 3 ⚠️ write first, watch them fail

- [x] T014 [P] [US3] `propose_relation` pending; accept creates; reject does not, plus `test_remove_then_next_contract` in `packages/pcl-server/tests/contract/test_relation_mcp.py` and `packages/pcl-core/tests/test_relation_contract.py`

### Implementation for User Story 3

- [x] T015 [US3] `Hub.propose_relation` / `decide_relation_proposal` in `packages/pcl-core/src/pcl_core/service.py`
- [x] T016 [US3] MCP `propose_relation` in `packages/pcl-server/src/pcl_server/mcp/tools_context.py` and `packages/pcl-sdk/src/pcl_sdk/mcp_bridge.py`
- [x] T017 [US3] REST `GET /v1/relation-proposals`, `POST …/accept|reject` in `packages/pcl-server/src/pcl_server/rest/routers/relations.py`
- [x] T018 [US3] Types in `frontend/src/api/types.ts`; list/add/remove/change-type on `frontend/src/pages/Projects.tsx`; Review Queue rows on `frontend/src/pages/ReviewQueue.tsx`

**Checkpoint**: Person-visible + propose/accept

---

## Phase 6: Polish

- [x] T019 [P] Run `make test`; record loop evidence
- [x] T020 Confirm quickstart.md against the SC map in `specs/008-light-graph/contracts/relations.md`

---

## Dependencies & Execution Order

- Setup → Foundational → US1 (MVP) → US2 (uses collect path) → US3 → Polish
- US1 after T005; US2 after T010; US3 after T005

## Notes

- Do not auto-promote FKs or stakeholders
- Do not add a second MCP read tool
- Do not walk beyond one hop
- Commit only if the person asked
