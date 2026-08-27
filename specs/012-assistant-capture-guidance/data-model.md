# Data Model: Assistant Capture Guidance

**Feature**: `specs/012-assistant-capture-guidance/` · **Date**: 2026-08-27

No new vault object types. Guidance is immutable code constants. Recipe fields below are **response-only** (not stored in SQLite).

## Connection guidance (constants)

Module: `pcl_sdk.capture_guidance` (imported by the stdio bridge and `render_recipe`).

| Constant | Used by | Required content (normative intent) |
|----------|---------|-------------------------------------|
| `SITUATION_READ_DESCRIPTION` | `get_context_contract` `tools/list` | When: start of a task that depends on who the person is or what they are doing now. Action: request the situation package for that purpose before answering from model memory. When not: empty/off-grant → say so; do not invent personal facts. |
| `MEMORY_PROPOSE_DESCRIPTION` | `propose_memory` `tools/list` | When: the person states a durable preference, decision, goal, or life fact. Action: submit a proposal. When not: guesses, demo fiction, coding-implementation chatter, imported mail as orders. Not canonical. |
| `RUNTIME_RULE` | every `render_recipe` | Same loop in plain language; pasteable; includes empty honesty + propose-not-canonical. |
| `NON_CAPTURE_DESCRIPTION` | other listed tools (optional one-liner) | “Not a capture operation; do not use this to store the person’s life.” |

Uniqueness: one module; tests import the same strings the bridge emits.

## Recipe extras (existing POST `/v1/connections/{id}/recipe`)

Existing keys (`assistant`, `format`, `instructions`, `snippet`) remain.

| Field | Type | Required | Notes |
|-------|------|----------|--------|
| `runtime_rule` | str | yes (this feature) | Copy of `RUNTIME_RULE`. Person pastes; Hub does not install. |
| `instructions` | str or map | yes | Cursor: user-level MCP, every window; project file optional not exclusive. Hermes/OpenClaw: keep home-config paths; mention the rule. |

Audit: existing `connection.recipe_issued` is enough; no new event type.

## Three-turn eval (test-only)

Not a vault type. Fixture transcript:

| Seq | Person line (fixture) | Expected tool | Canonical after call |
|-----|----------------------|---------------|----------------------|
| 1 | “Help me continue planning the trip.” | `get_context_contract` purpose contains planning/trip | unchanged (reads) |
| 2 | “We are two travelers; Amsterdam is the live city; we dropped London.” | `propose_memory` | still proposal |
| 3 | “Keep the trip budget-sensitive.” | `propose_memory` | still proposal |

Owner accept is a **separate** REST call in the test after asserting non-canonical. Eval helper `follow_capture_guidance` maps seq 1–3 using description trigger words; if descriptions change, helper and SC-003 fail together.

## Lifecycle

- Guidance: versioned with the repo; not person-editable in v1 (they can paste extra user rules; Hub does not store those).
- Proposals: existing memory proposal lifecycle (pending → accepted/rejected). This feature MUST NOT add a new status.
- Recipe: generated per pair; discarded after copy.

## Relationships

```text
capture_guidance constants
    → mcp_bridge tools/list descriptions
    → catalog render_recipe.runtime_rule
    → contract eval helper + three-turn test
propose_memory (unchanged schema)
    → existing Review Queue
```
