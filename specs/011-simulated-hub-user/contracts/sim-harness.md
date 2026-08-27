# Contract: Simulated Hub User

**Feature**: `specs/011-simulated-hub-user/`  
**Surfaces**: CLI `pcl-sdk sim`; loopback REST `/v1/sim/*`; Hub UI `/sim`. No new MCP tool for P1. No second bind.

Implementer tests MUST be written first (fail before code satisfies SC-001…SC-008).

## CLI

```text
uv run pcl-sdk sim dump --persona lived-stretch
uv run pcl-sdk sim run --persona lived-stretch [--delay-ms 0] [--data-dir DIR]
uv run pcl-sdk sim run --paired-assistant [--print-mcp-recipe]
uv run pcl-sdk sim run --target everyday --confirm WRITE_EVERYDAY_VAULT
uv run pcl-sdk sim status
uv run pcl-sdk sim pause | resume | stop
```

| Command | Purpose | Exit |
|---------|---------|------|
| `dump` | Print compiled ticks (no Hub writes) | 0; 1 if compile invariants fail |
| `run` | Execute (blocking CLI) or start if server hosts | 0 complete; 1 fail; 2 refuse |
| `status` | Current run: status, current_seq, last tick summary | 0; 1 if none |
| `pause` / `resume` / `stop` | Control | 0; 1 if no run |

Default `--data-dir` for CLI tests is temp. Default for a person’s CLI without `--data-dir` is `~/.pch-sim`. Everyday without exact confirm → exit 2, `refuse_reason=everyday_unconfirmed`. In-flight second `run` → exit 2, `in_flight`. Unknown persona → exit 2, `unknown_persona`.

`--print-mcp-recipe` (only with `--paired-assistant`) prints a stdio recipe targeting `http://127.0.0.1:8765` and the minted token. It does not write `.cursor/mcp.json` (secrets not committed).

## REST (existing loopback app, prefix `/v1`)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/sim/runs` | Start. Body: `persona_id`, optional `paired_assistant`, `auto_accept`, `target`, `confirm`, `delay_ms` |
| GET | `/sim/runs/{id}` | Run + last 20 tick summaries (role, action, result ok/error) |
| GET | `/sim/runs` | Active or latest run (one active) |
| POST | `/sim/runs/{id}/pause` | Pause |
| POST | `/sim/runs/{id}/resume` | Resume |
| POST | `/sim/runs/{id}/stop` | Stop |
| GET | `/sim/runs/{id}/ticks` | Full tick list |
| GET | `/sim/runs/{id}/ticks/{seq}` | Full input + result |
| GET | `/sim/objects/{id}` | `sim_hub.get(id)` for inspector |

Start on isolated space uses `app.state.sim_hub`, never `app.state.hub`, unless `target=everyday` and confirm matches.

**Live contract**: while `status=running`, repeated GET of the run shows `current_seq` increasing without waiting for complete (bar 1). Tests: `delay_ms=0`, start, GET until `current_seq >= 1` then again until `>= 5` before complete.

## UI

Route `/sim` in the existing SPA. Nav item “Simulator” under Start. Controls: start bundled persona, pause, resume, stop. Timeline of ticks (seq, simulated time, role, action, result). Click tick → input + result panel. If `object_id` present, load `/v1/sim/objects/{id}` in that panel (do not navigate to `/memories` on isolated runs). Poll while running.

## Behavioral contract

| # | Guarantee | Spec |
|---|-----------|------|
| B1 | First applied tick visible via GET run in < 120 s from start | SC-001 |
| B2 | Complete `lived-stretch` → object_count ≥ 40, ≥ 4 kinds including project/preference/memory, query_count ≥ 10 | SC-002 |
| B3 | Every applied create has a tick; no canonical write without a tick | SC-003 |
| B4 | Default run: everyday Hub `list()` count unchanged | SC-004 |
| B5 | ≥ 90% of persona situation asks name the active trip project and cite ≥ 1 persona-written id | SC-005 |
| B6 | GET tick seq for each of last 20 returns input and result | SC-006 |
| B7 | `paired_assistant=false`: run completes; assistant ticks `via=in_process_pair`. `true`: those query ticks `via=paired_assistant` | SC-007 |
| B8 | Compile/runtime reject outbound mail/calendar/public bind; no tick calls `propose_action` | SC-008 |
| B9 | Assistant propose is not live in the next contract until accept (unless auto_accept already applied) | FR-005 |
| B10 | Narrow grant: withheld named, content absent | US2.4 |

## Fixture tests (fail first)

| SC | Test |
|----|------|
| SC-001 | `packages/pcl-sdk/tests/sim/test_run.py::test_first_tick_under_two_minutes` |
| SC-002 | `test_run.py::test_lived_stretch_volume` |
| SC-003 | `test_timeline.py::test_every_create_has_tick` |
| SC-004 | `test_isolation.py::test_everyday_vault_unchanged` |
| SC-005 | `test_queries.py::test_situation_asks_hit_trip` |
| SC-006 | `test_timeline.py::test_tick_input_output` |
| SC-007 | `test_pair.py::test_via_label_optional_path` |
| SC-008 | `test_refuse.py::test_no_outbound_actions` |
| FR-007 | `test_isolation.py::test_everyday_refused_without_confirm` |
| FR-005 | `test_roles.py::test_proposal_not_canonical_before_accept` |
| US2.4 | `test_pair.py::test_narrow_grant_withholds` |
| live | `packages/pcl-server/tests/test_sim_rest.py::test_seq_increases_before_complete` |

Frontend page and nav are required for bar 1; REST live test is the automated stand-in for “watch.” Playwright e2e stays skipped like other US tests unless later enabled.
