# Research: Context Engine

**Feature**: `specs/004-context-engine/` · **Date**: 2026-08-26

No NEEDS CLARIFICATION markers remained in the Technical Context; the decisions below resolve the open design choices against the existing codebase (mapped 2026-08-26: schema in `pcl_core/schema/`, retrieval in `pcl_core/retrieval/`, policy in `pcl_core/policy/`, MCP in `pcl_server/mcp/`, bridge in `pcl_sdk/mcp_bridge.py`).

## D1 — Contract is an ephemeral response, not a vault object

**Decision**: `ContextContract` is a Pydantic response model returned by the MCP tool; it is never persisted as a vault object. Issuance is recorded in the append-only ledger (new `EventKind.CONTEXT_CONTRACT`) with agent, purpose, included item references, and omission categories.

**Rationale**: The spec (FR-008, US3) requires reviewability, not replayability. The ledger already gives tamper-evident history and the Audit UI already lists events. Persisting full contracts would duplicate vault content, grow the vault with derived data, and create a second source of truth that could go stale after corrections — violating "correction wins".

**Alternatives considered**: (a) Store contracts as vault objects like `ContextManifest` does (type `"manifest"`) — rejected: manifests are grants-adjacent artifacts with TTLs; contracts are per-request reads and would accumulate fast. (b) Store only in memory — rejected: fails FR-008 auditability.

## D2 — Situation selection: anchor-first, lexical matching, no embeddings

**Decision**: Selection resolves the purpose to at most one anchor Project (plus its Goals): use the optional `subject_ref` hint when provided; otherwise run FTS5 over projects/goals with `significant_tokens(purpose)` (reused from `retrieval/ask.py`) and pick the top-ranked in-scope match. If several projects tie, the contract carries candidate situations (project refs only) instead of merging them. No match → minimal contract (D6).

**Rationale**: FR-006 and the edge cases demand "never merge unrelated projects". The vault already links Goals/Decisions/Commitments/Memories via `project_id`, so an anchor gives a high-precision bundle exactly like `project_brief` does today. Lexical matching keeps E1 inside the roadmap's "no vector DB" boundary.

**Alternatives considered**: (a) Pure query-wide search without an anchor — rejected: returns hits, not a situation; that is what `search_personal_context` already does. (b) Embedding similarity — rejected by roadmap ("Não cabe: vector DB"). (c) LLM-side selection — rejected: the engine must not depend on any model (model-agnostic principle).

## D3 — Assembly and ranking reuse existing primitives

**Decision**: With an anchor, assemble by category: live Goals; Decisions; open Commitments (as constraints); Preferences (global + project-scoped); Memories ranked by `DefaultRanker` (authority `user_confirmed` first, then `updated_at`) combined with token-overlap relevance to the purpose; non-expired `SharedState` visible to the connection. Sufficiency caps per category (inline top-N, e.g. 10 memories, matching `project_brief`'s existing cap); items beyond the cap appear as reference-only entries (id + type + title, no body).

**Rationale**: FR-006 requires the smallest sufficient set; caps plus reference-entries satisfy SC-007 without inventing a new ranking system. Every reused piece (`DefaultRanker`, `citations_for`, `significant_tokens`, brief bundling) is already tested from 001.

**Alternatives considered**: (a) Token-budget-based truncation — rejected: token counting is runtime-specific; roadmap defers "otimização de tokens como produto". (b) No caps — rejected: fails SC-007 on large situations.

## D4 — Grant bounding and omission notes derive from policy decisions

**Decision**: Every candidate item passes the existing `policy.evaluate()` under the requesting connection's grant before inclusion. DENY/REDACT outcomes are aggregated (not per-item) into `OmissionNote`s keyed by category: `scope_not_granted` (selector mismatch), `classification_ceiling` (above grant ceiling), `capability_missing` (e.g. no `memory.retrieve`). Notes carry counts and category labels only — never titles, ids, or content of withheld items. Owner requests bypass grants as today.

**Rationale**: FR-004/FR-005 and US2. Reusing the evaluator means assembly can never be more permissive than search already is; aggregation prevents the omission section itself from leaking (an itemized list of withheld titles would be a side channel). The pattern mirrors `redaction_notices` in `build_manifest`.

**Alternatives considered**: (a) Per-item omission entries — rejected: leaks existence/shape of withheld data. (b) Silent omission — rejected: fails FR-004; agents would hallucinate around gaps.

## D5 — Conflicts surface, freshness is metadata, no temporal resolution

**Decision**: Preferences sharing a `key` with different values, and contradictory memories, are all included as live items, each carrying `authority`, `confidence`, `updated_at`, and citations. The contract adds a lightweight `conflicts` list pairing the item ids. No winner is chosen.

**Rationale**: FR-012 defers resolution to E2. Exposing the pair explicitly (rather than leaving the agent to notice) makes the E2 seam clean: E2 will replace the pair with the vigente item plus history. "Dropped London" works without temporal logic because it is a Decision (status `rejected`) — a state change on an object, not a validity conflict.

**Alternatives considered**: (a) Latest-wins — rejected: silently discards, violates FR-012. (b) Omit both — rejected: hides real context.

## D6 — Empty/minimal contract instead of errors

**Decision**: When nothing in scope matches the purpose, return a valid contract with: echoed purpose, empty sections, granted scope, omission notes (if in-scope-relevant material was withheld), and `situation: null`. Grant-revoked or unauthenticated requests are refused at the auth/policy layer as today, and the refusal is appended to the ledger under the same `context.contract` kind with `status: "refused"`.

**Rationale**: FR-011 and acceptance scenario US1-4. A structured empty contract lets agents distinguish "nothing known" from "request failed", and keeps the audit trail uniform for issuances and refusals (FR-008).

**Alternatives considered**: 404/error on no match — rejected: agents would retry with broader queries, pushing toward unscoped dumps.

## D7 — Exposure: one new MCP tool on the existing surfaces

**Decision**: Register `get_context_contract` in `attach_tools` (`pcl_server/mcp/tools_context.py`), add name + JSON schema to `TOOL_NAMES`/`TOOL_SCHEMAS` in `pcl_sdk/mcp_bridge.py`. HTTP access comes free via the existing generic `POST /v1/mcp/tools/get_context_contract`. No new REST router; the review UI (US3) reads existing `GET /v1/events` filtered by kind `context.contract`.

**Rationale**: FR-009 ("existing MCP connection surface, no runtime-specific adapter"). This is exactly how the other seven tools are wired; pairing/auth (`actor_from_token`) is untouched. Complements, does not replace, `search_personal_context` and `get_context_manifest` (spec assumption).

**Alternatives considered**: (a) Extend `get_context_manifest` — rejected: manifests answer "what may be disclosed under this grant" (capability negotiation, TTL); contracts answer "what does this agent need now" (situation assembly). Overloading would break 002 clients. (b) New REST router — rejected: unnecessary; generic tool endpoint plus events API cover both consumers.

## D8 — Performance: bounded queries, no N+1

**Decision**: Assembly issues a bounded number of vault queries: one FTS pass for anchor selection, one `list`/filter pass per category scoped by `project_id`, one shared-state read. Ranking and caps run in memory. Target < 2 s (SC-006) verified by a perf-marked test on a seeded vault of a few thousand objects.

**Rationale**: `project_brief` already demonstrates this bundle shape is cheap; FTS5 handles the only text-scan step.

**Alternatives considered**: Precomputed situation index — rejected as premature; revisit only if the perf test fails.
