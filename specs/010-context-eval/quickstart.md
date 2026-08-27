# Quickstart: Context Quality Evaluation

**Feature**: `specs/010-context-eval/`
Score the trip package locally. Do not publish the numbers.

## 1. Run the harness

```bash
uv run pcl-sdk eval run
```

Expect JSON with four cases and seven metrics. Exit 0 if `all_pass` is true.

The run uses a temporary vault. It does not open `~/.pch`.

## 2. Read the scorecard

- **killer_demo**: Europe Trip is the situation; `assembly_cost_seconds` is a number under 2.
- **temporal_conflict**: old spicy dislike vs live like (as-of); trip still lists a preference-key conflict.
- **isolation**: work-scoped package has no “Europe” / trip id.
- **runtime_switch**: two assistants agree; revoke does not delete the trip.

## 3. What not to do

Do not upload the JSON. Do not treat token counts as the score. Do not add a second context assembler.
