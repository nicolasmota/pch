# Data Model: Context Quality Evaluation

**Feature**: `specs/010-context-eval/` · **Date**: 2026-08-26

No vault types. Ephemeral report objects only.

## Eval case

| Field | Meaning |
|-------|---------|
| `id` | `killer_demo` \| `temporal_conflict` \| `isolation` \| `runtime_switch` |
| `pass` | bool |
| `detail` | short machine-readable reason if fail |

## Metrics (on the report)

| Key | Type | Pass rule |
|-----|------|-----------|
| `retrieval_accuracy` | bool | situation.project is Europe Trip for killer-demo purpose |
| `precision` | bool | work-scoped package has 0 personal trip titles/ids |
| `freshness` | bool | as-of past shows old spicy value; now shows live |
| `conflict_resolution` | bool | package.conflicts includes preference_key_collision |
| `portability` | bool | two same-grant packages agree on situation.project_id |
| `user_correction` | bool | after drop_london, live chosen destination is not London |
| `assembly_cost_seconds` | float | killer-demo timed `get_context_contract`; fail if ≥ 2.0 |

## Eval report

| Field | Meaning |
|-------|---------|
| `cases` | list of eval cases |
| `metrics` | the seven keys |
| `all_pass` | AND of case passes and metric bools (cost under budget) |

**Validation**: exactly four case ids; all seven metric keys present; no uploaded_at / public_url field.

## Relationships

Report **reads** Context Contract items. It does not persist contracts. Hub objects used are the existing Project, Preference, Memory, Grant, Connection.
