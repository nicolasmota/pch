# Research: Light Graph

**Feature**: `specs/008-light-graph/` · **Date**: 2026-08-26

No NEEDS CLARIFICATION markers remained in the Technical Context; the decisions below resolve the open design choices against the existing codebase (mapped 2026-08-26: FKs on Goal/Memory `project_id`, Project `stakeholders`, assembly in `pcl_core/retrieval/contract.py`, MCP in `pcl_server/mcp/tools_context.py`, E3 operational fields on SituationRef).

## D1 — Explicit Relation objects, not FKs, not a graph DB

**Decision**: Add vault type `relation` with `from_id`, `to_id`, `relation_type` (`owned_by` \| `depends_on` \| `blocked_by` \| `related_to`). Persist via existing `ObjectStore`. Do **not** auto-promote Goal/Memory `project_id` into `owned_by`. Do **not** treat Project `stakeholders` as `related_to`. Those two are **named non-examples**.

**Rationale**: Spec FR-001/FR-003. FKs already mean membership. Typed links are a different claim. A graph database is constitutionally out of scope.

**Alternatives considered**: (a) Infer `owned_by` from `project_id` — rejected: silent rewrite of 001 semantics; tests would confuse membership with typed ownership. (b) Neo4j / SQLite recursive CTE graph — rejected: roadmap “Não cabe: graph database”; unbounded walk. (c) Encode links as SharedState — rejected: TTL would drop “depends on visa.” (d) Memory kind `relationship` — rejected: durable memory ≠ live typed link (MemoryKind.RELATIONSHIP already exists as a memory kind, not a graph edge).

## D2 — Contract `relations[]`; depth = anchor + one hop

**Decision**: Extend `ContextContract` with `relations: list[RelationRef]`. Each ref: `id`, `relation_type`, `from` ItemRef, `to` ItemRef (summary only; no nested body). Collect: (1) live relations where `from_id` or `to_id` is the selected Project; (2) one hop: live relations whose `from_id` or `to_id` is an endpoint already included in (1), excluding the reverse duplicate of (1). Cap: 20 relations. Empty → `[]`. Never infer from memories, artifacts, email, or E3 phase.

**Rationale**: FR-002, SC-002 (visa `blocked_by` person). Unbounded walk fails isolation and perf.

**Alternatives considered**: (a) New MCP tool `get_graph` — rejected: E1 seam is one contract. (b) Full BFS — rejected: SC-007 + isolation side channel. (c) Only outbound `from_id = anchor` — rejected: SC-002 needs one hop from the visa.

## D3 — Owner writes; agents propose

**Decision**: Owner `POST /v1/relations`, `DELETE /v1/relations/{id}`, `PATCH` type only. Duplicate (same from, to, type) → 409. Self-link → 422. Unknown type → 422. MCP `propose_relation` writes `relation_proposal` pending on Review Queue; accept creates the relation; reject does not. Agents cannot silent-create.

**Rationale**: FR-005. Same propose/accept pattern as memory and operational state.

**Alternatives considered**: (a) Agents POST relations via MCP — rejected: silent canonical write. (b) Reuse `propose_memory` — rejected: pollutes memory lineage. (c) Reuse `propose_operational_state` — rejected: different object.

## D4 — Isolation: both ends must allow

**Decision**: Include a relation only if `policy.evaluate` ALLOWs both endpoints (or the owner). If the near end is in-scope and the far end is not, omit the relation and increment an omission count (`scope_not_granted`); do not put the far-end title or id in `omissions` or `relations`. Work-scoped packages must contain 0 personal relation types/endpoints.

**Rationale**: FR-007, SC-004. A redacted far-end id would still leak existence of a personal visa.

**Alternatives considered**: (a) Include type but redact far-end as `"withheld"` — rejected: still signals a personal depends-on. (b) Per-item omission with titles — rejected: E1 already forbids that.

## D5 — Tests fail first; trip + visa seed

**Decision**: Named SC map in plan.md. NEW `test_relation_contract.py`, `forbidden_context/test_relation_isolation.py`, `contract/test_relation_mcp.py`. EDIT `test_contract_perf.py` with depends_on + blocked_by seeded. Trip seed in tests (not production seed) creates visa project + person endpoint as a Profile or Person already in setup.

**Rationale**: Constitution tests-fail-first. SC-007 stays on `hub.get_context_contract`.

**Alternatives considered**: (a) One `test_e4.py` — rejected: tasks would invent files. (b) New assembly entry point — rejected: SC-007.

## D6 — Performance: one list pass

**Decision**: `store.list("relation")` once per assembly; filter in memory by anchor id and one-hop set. No extra FTS. SC-007 extends `test_contract_perf.py`.

**Rationale**: Spec SC-007.

**Alternatives considered**: Adjacency index table — rejected as premature; revisit only if perf fails.
