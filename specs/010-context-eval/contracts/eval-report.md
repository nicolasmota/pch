# Interface Contract: Local eval report

**Feature**: `specs/010-context-eval/` · **Date**: 2026-08-26  
**Surface**: CLI `pcl-sdk eval run` (stdout JSON). No new MCP tool. No public HTTP.

## Command

```text
uv run pcl-sdk eval run
```

Exit 0 if `all_pass` is true; else 1. No network.

## Report JSON

```json
{
  "cases": [
    {"id": "killer_demo", "pass": true, "detail": ""},
    {"id": "temporal_conflict", "pass": true, "detail": ""},
    {"id": "isolation", "pass": true, "detail": ""},
    {"id": "runtime_switch", "pass": true, "detail": ""}
  ],
  "metrics": {
    "retrieval_accuracy": true,
    "precision": true,
    "freshness": true,
    "conflict_resolution": true,
    "portability": true,
    "user_correction": true,
    "assembly_cost_seconds": 0.12
  },
  "all_pass": true
}
```

Required keys: `cases`, `metrics`, `all_pass`. Forbidden: `leaderboard`, `public_url`, `token_count` as a scored field.

## Behavioral contract

| # | Guarantee | Spec ref |
|---|-----------|----------|
| B1 | Killer demo: accuracy true iff situation is Europe Trip | SC-001 |
| B2 | Isolation: precision true iff 0 personal trip titles/ids | SC-002 |
| B3 | Freshness uses as-of vs now on spicy preference | SC-003 |
| B4 | Conflict listed for dual current same key | SC-004 |
| B5 | drop_london → correction true | SC-005 |
| B6 | Two connections agree; revoke keeps trip | SC-006 |
| B7 | assembly_cost_seconds < 2.0 on killer demo | SC-007 |
| B8 | Default vault is temp; not ~/.pch | FR-004 |

## Fixture tests (fail first)

All in `packages/pcl-sdk/tests/eval/test_harness.py` as named in plan.md.
