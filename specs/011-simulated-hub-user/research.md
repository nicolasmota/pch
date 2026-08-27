# Research: Simulated Hub User

**Feature**: `specs/011-simulated-hub-user/` · **Date**: 2026-08-27

No NEEDS CLARIFICATION markers remained in Technical Context. Decisions below resolve the spec against constitution 1.0.0, Hub 001–010 code (`Hub.create` / `search` / `get_context_contract` / `propose_memory` / `decide_proposal` / pairing), the E6 eval harness (do not replace it), and the frozen PLAN-BAR.

## D1 — Engine in `pcl-sdk`; live surface on the existing loopback Hub; `pcl-core` untouched

**Decision**: A Python module `pcl_sdk.sim` owns persona compile, tick execution, run/tick records, and isolated-space Hub construction. `pcl-sdk sim …` is the headless/CLI path (tests use it in-process, like `eval`). `pcl-server` adds `/v1/sim/*` on the **existing** loopback app plus a second `Hub` instance (`app.state.sim_hub`) whose data dir is the isolated space. The frontend adds `/sim` (timeline + tick inspector). No new listener, no MCP tool required for P1, no vault types added in `pcl-core`.

**Rationale**: Bar 1 requires a live timeline in the Hub the owner already opens. Bar 5/7 require isolated default and no core I/O. Putting the executor in the SDK keeps pytest free of HTTP; the server is a thin host so the UI can poll.

**Alternatives considered**: (a) CLI-only like E6 — rejected: bar 1 fails a post-hoc log dump as the only UI. (b) Engine inside `pcl-core` — rejected: core must stay free of I/O. (c) New port for a “sim server” — rejected: constitution II, no new bind. (d) LLM-driven robot as Hub agent runtime — rejected: constitution product boundary; bar 3.

## D2 — Isolated space is `~/.pch-sim` (tests: temp dir); everyday vault is opt-in with a confirm token

**Decision**: Default data dir for a person’s CLI is `Path.home() / ".pch-sim"` (override `PCH_SIM_DIR`). Tests pass `--data-dir` / a temp path into `run_sim`. `--target everyday` (or REST `target=everyday`) is refused unless `confirm` equals the exact string `WRITE_EVERYDAY_VAULT`. Everyday means the running Hub’s `data_dir` (typically `~/.pch`). SC-004 tests that a default run leaves the everyday object count unchanged.

**Rationale**: FR-007, SC-004, coding agent is not a Hub client, bar 5.

**Alternatives considered**: (a) Default `~/.pch` — rejected: would mix demo data with the owner’s life. (b) Namespace inside the everyday vault — rejected: isolation would be a label, not a space; a mistaken browse would show sim as live life. (c) Always ephemeral (delete on stop) — rejected: the owner wants to inspect the corpus after the run.

## D3 — Scripted persona compiler; bundled `lived-stretch`; inspectable ticks

**Decision**: Ship one bundled persona id `lived-stretch`: a 14-day travel-planning life (Europe trip compatible with the existing demo) plus a work project, mixed memories, a preference supersede, and later search + situation asks. A **declarative** persona file compiles to an ordered tick list at load. `pcl-sdk sim dump --persona lived-stretch` prints the compiled ticks. Compile **fails** if durable owner-creates < 40, kinds do not include project + preference + memory plus at least one more, or query ticks (search or situation ask) < 10. v1 does not call a model to invent ticks.

**Rationale**: Bar 3 (scripted, not “the model will act”), bar 11 (volume floor), FR-002, FR-013.

**Alternatives considered**: (a) Hand-write 50 ticks in a giant JSON — accepted as output of compile, not as the source; source stays compact. (b) Reuse `seed_trip` as a single blob then 10 queries — rejected: volume and mixed kinds would fail the floor; the owner would not *watch* writes. (c) LLM improvisation — rejected: Personal Agency-adjacent, non-deterministic, not inspectable.

## D4 — Roles: owner writes canonical; assistant proposes; auto-accept default

**Decision**: Each tick has `role`: `owner` | `assistant`. Owner ticks call `Hub.create` / `supersede` / `decide_proposal` as `OWNER`. Assistant ticks use a connection minted on the sim Hub (`mint_link` + `pair` + `create_grant`) and call `search`, `get_context_contract`, `brief`, `propose_memory` with `actor=connection_id`. Durable assistant writes never call `create("memory")` directly. Default run auto-accepts the persona’s own proposals via an owner `decide_proposal` tick so the corpus grows (FR-005). `--leave-proposals` skips auto-accept. Timeline always labels the role.

**Rationale**: Spec US2, bar 4. In-process pairing is a real grant path (same as E6 isolation), not a stub.

**Alternatives considered**: (a) All writes as OWNER — rejected: would hide the proposal/review path. (b) All writes as assistant auto-canonical — rejected: FR-005. (c) Fake ALLOW-all actor — rejected: withheld categories would be a lie.

## D5 — Live timeline is REST + `/sim` polling, not SSE and not Cursor

**Decision**: Run record + tick list live as JSON files under the sim data dir (`run.json`, `ticks.jsonl`). Server endpoints: start/pause/resume/stop/get run/list ticks/get tick/get object. Frontend `/sim` polls `GET /v1/sim/runs/{id}` about once a second while status is `running`. Tick inspector shows `input` and `result` (FR-008). Object inspector `GET /v1/sim/objects/{id}` is the FR-009 “open in the Hub” surface for the isolated space (everyday `/memories` would show the wrong vault). CLI `sim status` prints the same run. Cursor is not required to see ticks.

**Rationale**: Bar 1 and 10; FR-010; bar 6 (optional paired path must not be the only UI).

**Alternatives considered**: (a) SSE/WebSocket — rejected for v1: extra complexity; 1 s poll meets “watch live.” (b) Only `ticks.jsonl` on disk — rejected: bar 1. (c) Swap the whole UI onto the sim vault — rejected: would hide the everyday Hub the owner already uses.

## D6 — Optional paired-assistant / Cursor path is a flag, not P1

**Decision**: Assistant-role ticks **always** run through the in-process pair (D4). That is how search / situation ask / propose happen without Cursor. `--paired-assistant` (REST `paired_assistant: true`) does not change the executor; it sets tick `via` to `paired_assistant` (else `in_process_pair`) and enables `--print-mcp-recipe`, which prints a stdio recipe for `http://127.0.0.1:8765` plus the minted token. The runner does not drive the Cursor GUI and does not write `.cursor/mcp.json`. Tests do not start Cursor. P1 start works with the flag off.

**Rationale**: Bar 6; user asked Cursor only if necessary.

**Alternatives considered**: (a) Require Cursor to see any query — rejected: bar 6. (b) New A2A protocol — rejected: constitution. (c) Coding agent in this repo as the Hub client — rejected: constitution I.

## D7 — This is not E6 and not Personal Agency

**Decision**: The engine calls existing Hub methods only. It does not score the seven E6 metrics, does not add eval cases, and does not assemble a second Context Contract. Forbidden tick types: outbound `propose_action` that would send mail or create external events, connector apply, plugin outbound, non-loopback bind. Compile rejects those action ids. No foundation model. No improvisation.

**Rationale**: Bar 2/3/7/8, SC-008, constitution horizon items.

**Alternatives considered**: (a) Fold into `pcl-sdk eval` — rejected: E6 is four fixed cases; this is a growing watched corpus. (b) Let ticks call `propose_action` “for realism” — rejected: Personal Agency.

## D8 — Provenance without new schema types

**Decision**: Every sim-created object sets `labels` to include `sim` and `persona:<id>`. Run id is stored on the tick result (`object_id`). Ledger actor is `OWNER` for owner ticks and `connection_id` for assistant ticks. No new `type` in the vault. Sim run metadata stays in `run.json` (not a Hub object).

**Rationale**: Bar 7; keep 001 schema closed.

**Alternatives considered**: (a) New `SimulationRun` vault type — rejected: reopens 001. (b) `source_refs` pointing at a fake id — rejected: citations would 404.

## D9 — Runner pacing

**Decision**: Default delay between ticks is 200 ms when hosted by the server (watchable). CLI `--delay-ms 0` for tests. Pause sets status `paused` and stops scheduling the next tick; in-flight tick either finishes and is appended or is not applied (executor is synchronous per tick inside a lock). Duplicate start on an in-flight run is refused (`in_flight`).

**Rationale**: FR-001, FR-014, FR-015, edge cases.

**Alternatives considered**: (a) Unbounded parallel ticks — rejected: timeline order would race. (b) No delay — rejected: UI would jump to done before the owner looks.
