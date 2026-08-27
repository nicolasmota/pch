# Research: Context Quality Evaluation

**Feature**: `specs/010-context-eval/` · **Date**: 2026-08-26

Mapped 2026-08-26: E1 `get_context_contract`; E2 `as_of` + preference collision; E3 phase; E4 relations; E5 two real-use tokens + revoke. No product-level scorecard exists — only pytest.

## D1 — Local harness, not a public benchmark

**Decision**: `pcl-sdk eval run` builds a temp Hub (`plain=True`), runs four cases, prints JSON to stdout. No HTTP upload. No shared leaderboard file in the repo.

**Rationale**: FR-004, roadmap “Não cabe: benchmark público.”

**Alternatives considered**: (a) Publish scores to a gist/CI artifact store — rejected. (b) Only document “run make test” — rejected: unnamed metrics fail the bar. (c) Frontend dashboard — rejected: CLI is enough for E6; UI can wait.

## D2 — Score the existing contract

**Decision**: Every metric is a function of `Hub.get_context_contract` output (plus `time.perf_counter` for cost). No second assembler. No LLM-as-judge.

**Rationale**: FR-003, bar criterion 2 and 10.

**Alternatives considered**: (a) Ask an LLM if the package is “good” — rejected: not observable. (b) Duplicate assembly in the SDK — rejected: would drift from E1.

## D3 — Four cases, seven metrics

**Decision**:

| Case | Fixture | Metrics it feeds |
|------|---------|------------------|
| killer_demo | `seed_trip` + purpose continue planning the trip | retrieval_accuracy, assembly_cost |
| temporal_conflict | `seed_spicy` supersede + `seed_trip` key collision | freshness, conflict_resolution |
| isolation | trip + work projects; work-scoped grant | precision |
| runtime_switch | two paired connections, same grant; revoke first | portability; trip still listed after revoke |

Correction uses `drop_london` on the killer-demo vault (or a dedicated pass after seed_trip): live chosen destination is not London.

**Rationale**: Spec US1–US3, SC-001…SC-007.

**Alternatives considered**: (a) One mega-case — rejected: failures would be opaque. (b) Score token length — rejected: FR-005.

## D4 — Ephemeral vault; not ~/.pch

**Decision**: Default data dir is `tempfile.mkdtemp()`. Tests and CLI share `run_eval(data_dir=...)`.

**Rationale**: Constitution coding agent ≠ Hub client; FR-007 without touching the person’s encrypted vault.

**Alternatives considered**: (a) Default `~/.pch` — rejected: eval would mix with live data. (b) Read-only overlay — unnecessary for v1.

## D5 — Real grants for isolation/portability

**Decision**: Isolation and portability mint real connections and grants (`mint_link` / `pair` / `create_grant`) and call `get_context_contract(actor=connection_id)`. Do not stub `policy.evaluate`.

**Rationale**: FR-006. A fake ALLOW-all would fake precision.

**Alternatives considered**: (a) Owner-only isolation test — rejected: owner bypasses policy. (b) HTTP TestClient — optional; in-process Hub is enough and faster.

## D6 — CLI next to loop

**Decision**: `uv run pcl-sdk eval run` in `__main__.py`. Exit code 0 if all cases pass; 1 otherwise.

**Rationale**: Person-visible without a new binary.

**Alternatives considered**: `make eval` only — rejected: FR-007 wants the existing CLI family.
