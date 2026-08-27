# Data Model: Simulated Hub User

**Feature**: `specs/011-simulated-hub-user/` · **Date**: 2026-08-27

No new vault types. Hub objects created by ticks are existing 001 types (`project`, `goal`, `preference`, `memory`, `commitment`, `decision`, …). Run/tick records are files in the sim data dir.

## Persona

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | str | yes | Bundled: `lived-stretch` |
| `title` | str | yes | Person-visible name |
| `simulated_days` | int | yes | `14` for bundled |
| `projects` | list | yes | Seed templates compiled into create ticks |
| `preferences` | list | yes | Includes at least one supersede pair |
| `memory_templates` | list | yes | Expanded across days to hit volume |
| `queries` | list | yes | Search and situation-ask templates |

**Compile invariants** (fail load if broken):

- Durable owner-create ticks ≥ 40
- Kinds include `project`, `preference`, `memory`, and ≥ 1 other (`goal`, `commitment`, or `decision`)
- Query ticks (`search` or `get_context_contract`) ≥ 10
- Zero forbidden action ids (see Tick)

## Scenario (compiled)

Ordered list of Tick. Produced by `compile_persona(persona) -> list[Tick]`. `pcl-sdk sim dump` prints this list. The runner never invents ticks at execution time.

## Tick

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `seq` | int | yes | 1-based order |
| `simulated_at` | str | yes | ISO-8601 inside the persona’s 14-day window |
| `role` | str | yes | `owner` \| `assistant` |
| `action` | str | yes | See action table |
| `input` | object | yes | Body the Hub method will receive (inspectable) |
| `via` | str | yes | `in_process_pair` \| `paired_assistant` |
| `status` | str | yes | `pending` \| `applied` \| `failed` \| `skipped` |
| `result` | object \| null | no | Set when applied/failed |
| `error` | str \| null | no | Failed reason |

### Actions (closed set)

| `action` | Role | Hub call | Canonical? |
|----------|------|----------|------------|
| `create` | owner | `Hub.create(type, body, OWNER)` | yes |
| `supersede` | owner | `Hub.supersede` | yes (history kept) |
| `decide_proposal` | owner | `Hub.decide_proposal` | accept → canonical |
| `search` | owner or assistant | `Hub.search` | no |
| `get_context_contract` | owner or assistant | `Hub.get_context_contract` | no |
| `brief` | owner or assistant | `Hub.brief` | no |
| `propose_memory` | assistant | `Hub.propose_memory` | **no** until decide |

**Forbidden** (compile/runtime refuse): `propose_action`, `apply_connector_items`, `create_connector`, plugin outbound, any bind/listen action.

### Result (applied)

| Field | When |
|-------|------|
| `object_id` | create / supersede / accepted proposal |
| `proposal_id` | propose_memory |
| `hit_count` | search |
| `situation` | get_context_contract (project_id, omitted categories) |
| `withheld` | grant omissions from contract |
| `ok` | bool |

**Invariants**:

- Assistant `propose_memory` never sets canonical memory before a later `decide_proposal` accept (or `--leave-proposals` leaves it pending).
- Every `applied` create has a timeline entry with the same `seq`.
- `via` is `paired_assistant` only when the run was started with that flag; otherwise `in_process_pair` for assistant ticks.

## Run

File: `<sim_data_dir>/run.json`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `schema_version` | int | yes | `1` |
| `id` | str | yes | Unique per start |
| `persona_id` | str | yes | `lived-stretch` |
| `status` | str | yes | `running` \| `paused` \| `complete` \| `failed` \| `stopped` |
| `target` | str | yes | `isolated` \| `everyday` |
| `data_dir` | str | yes | Absolute path of the Hub space used |
| `paired_assistant` | bool | yes | SC-007 label |
| `auto_accept` | bool | yes | Default true |
| `delay_ms` | int | yes | Server default 200; tests 0 |
| `current_seq` | int | yes | Last finished seq (0 before first) |
| `started_at` | str | yes | Real UTC |
| `ended_at` | str \| null | no | |
| `connection_id` | str \| null | no | Minted assistant |
| `object_count` | int | yes | Durable objects after last applied create |
| `query_count` | int | yes | Applied search + contract ticks |

**Invariants**:

- `target=everyday` only if confirm token was `WRITE_EVERYDAY_VAULT`.
- Default start: `target=isolated`, `data_dir` is not the everyday Hub dir.
- Second start while `status=running` → refuse `in_flight`.
- `status=stopped` or `failed`: no pending tick becomes canonical after the last `applied` seq.

## Tick log

File: `<sim_data_dir>/ticks.jsonl` — one JSON Tick per line, rewritten or appended as status changes. `GET /v1/sim/runs/{id}/ticks` returns the array. `GET …/ticks/{seq}` returns one Tick including full `input` and `result`.

## Isolated space

A `Hub(data_dir, plain=True)` distinct from the everyday Hub except when target is everyday. Setup name `Sim`. Same loopback process; two Hub instances.

## Relationships

```text
Persona --compile--> Scenario (ticks)
Run --executes--> Tick --calls--> Hub (existing types)
Tick.result.object_id --> Hub.get
Assistant ticks --> Connection/Grant on the sim Hub
E6 eval harness --> not this model (separate CLI)
```
