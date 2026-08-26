# Interface Contract: `get_context_contract`

**Feature**: `specs/004-context-engine/` · **Date**: 2026-08-26
**Surfaces**: MCP tool (in-process ToolHub + stdio bridge) and generic HTTP tool endpoint. No new REST router.

## Tool registration

| Surface | Location | Contract |
|---------|----------|----------|
| In-process MCP | `attach_tools` in `packages/pcl-server/src/pcl_server/mcp/tools_context.py` | Tool name `get_context_contract` |
| Stdio bridge | `TOOL_NAMES` + `TOOL_SCHEMAS` in `packages/pcl-sdk/src/pcl_sdk/mcp_bridge.py` | Same name and schema |
| HTTP | `POST /v1/mcp/tools/get_context_contract` (existing generic route in `rest/app.py`) | Bearer/`x-pch-token` auth; actor from token |

Authentication and pairing are unchanged (002). The tool is available to any paired connection holding at least one active grant; it is also callable by the owner.

## Request schema (ContextQuery)

```json
{
  "type": "object",
  "required": ["purpose"],
  "additionalProperties": false,
  "properties": {
    "purpose": {
      "type": "string",
      "minLength": 1,
      "description": "What the agent is trying to do for the person right now."
    },
    "subject_ref": {
      "type": ["string", "null"],
      "description": "Optional vault object id (typically a Project) to anchor the situation."
    },
    "max_items": {
      "type": ["integer", "null"],
      "minimum": 1,
      "description": "Optional per-category cap; engine sufficiency caps still apply."
    }
  }
}
```

## Response schema (ContextContract)

Field semantics are normative in [data-model.md](../data-model.md); this is the wire shape.

```json
{
  "type": "object",
  "required": [
    "contract_id", "purpose", "situation", "candidates",
    "goals", "preferences", "memories", "decisions", "constraints",
    "state", "references", "conflicts",
    "granted_scope", "omissions", "assembled_at"
  ],
  "properties": {
    "contract_id": { "type": "string" },
    "purpose": { "type": "string" },
    "situation": {
      "oneOf": [
        { "type": "null" },
        { "$ref": "#/$defs/situation_ref" }
      ]
    },
    "candidates": { "type": "array", "items": { "$ref": "#/$defs/situation_ref" } },
    "goals": { "type": "array", "items": { "$ref": "#/$defs/contract_item" } },
    "preferences": { "type": "array", "items": { "$ref": "#/$defs/contract_item" } },
    "memories": { "type": "array", "items": { "$ref": "#/$defs/contract_item" } },
    "decisions": { "type": "array", "items": { "$ref": "#/$defs/contract_item" } },
    "constraints": { "type": "array", "items": { "$ref": "#/$defs/contract_item" } },
    "state": { "type": "array", "items": { "$ref": "#/$defs/contract_item" } },
    "references": { "type": "array", "items": { "$ref": "#/$defs/item_ref" } },
    "conflicts": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["item_ids", "reason"],
        "properties": {
          "item_ids": { "type": "array", "items": { "type": "string" }, "minItems": 2 },
          "reason": { "type": "string" }
        }
      }
    },
    "granted_scope": {
      "type": "object",
      "required": ["grant_id", "selectors", "classification_ceiling", "capabilities"],
      "properties": {
        "grant_id": { "type": "string" },
        "selectors": { "type": "object" },
        "classification_ceiling": { "type": "string" },
        "capabilities": { "type": "array", "items": { "type": "string" } },
        "summary_human": { "type": "string" }
      }
    },
    "omissions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["category", "label", "count"],
        "properties": {
          "category": {
            "enum": ["scope_not_granted", "classification_ceiling", "capability_missing", "policy_exclusion"]
          },
          "label": { "type": "string" },
          "count": { "type": "integer", "minimum": 1 }
        }
      }
    },
    "assembled_at": { "type": "string", "format": "date-time" }
  },
  "$defs": {
    "situation_ref": {
      "type": "object",
      "required": ["project_id", "title", "status"],
      "properties": {
        "project_id": { "type": "string" },
        "title": { "type": "string" },
        "status": { "type": "string" }
      }
    },
    "item_ref": {
      "type": "object",
      "required": ["id", "type", "summary"],
      "properties": {
        "id": { "type": "string" },
        "type": { "type": "string" },
        "summary": { "type": "string" }
      }
    },
    "contract_item": {
      "type": "object",
      "required": ["ref", "body", "citation", "authority", "freshness", "untrusted"],
      "properties": {
        "ref": { "$ref": "#/$defs/item_ref" },
        "body": { "type": "object" },
        "citation": { "type": "array", "items": { "type": "object" }, "minItems": 1 },
        "authority": {
          "enum": ["user_confirmed", "source_imported", "agent_inferred", "proposed"]
        },
        "confidence": { "type": ["number", "null"] },
        "freshness": { "type": "string", "format": "date-time" },
        "untrusted": { "type": "boolean" }
      }
    }
  }
}
```

## Behavioral contract

| # | Guarantee | Spec ref |
|---|-----------|----------|
| B1 | Every inlined item passed grant evaluation (ALLOW) under the requesting connection's grant. Zero out-of-scope items, always. | FR-005, SC-003 |
| B2 | Every inlined item carries `citation` with at least the source object id; no uncited items. | FR-003, SC-004 |
| B3 | `omissions` names categories and counts only; never ids, titles, or content of withheld items. | FR-004 |
| B4 | No situation match → HTTP 200 with `situation: null`, empty item arrays, valid `granted_scope` and `omissions`. Never an unscoped dump, never a 404. | FR-011 |
| B5 | Ambiguous purpose (tie) → `situation: null` plus `candidates` refs; unrelated projects are never merged into one item set. | Edge cases |
| B6 | Conflicting live items are all included and listed in `conflicts`; the engine never silently drops one side. | FR-012 |
| B7 | Assembly performs no network egress, no plugin syncs, no imports. Offline behavior identical to online. | FR-010 |
| B8 | Only live object versions appear. A correction to a source object is reflected in every contract assembled after it. | FR-007 |
| B9 | Each call appends exactly one ledger event `context.contract` (`status: issued`) with `contract_id`, actor, purpose, item refs, omission categories. | FR-008 |
| B10 | Invalid/revoked token → 401/403 as today, plus one ledger event `context.contract` (`status: refused`). Empty `purpose` → 422 validation error (no ledger issuance event). | FR-008, US2-3 |
| B11 | `SharedState` values appear under `state` unmodified; nothing is renamed. | Assumptions |
| B12 | Response is deterministic for an unchanged vault and grant (stable ordering: ranking order, ties by id). | Testability |

## Review surface (US3)

No new endpoint. The Audit UI (`frontend/src/pages/Audit.tsx`) renders `context.contract` events from existing `GET /v1/events`: agent, purpose, status, item refs, omission categories, timestamp. Owner-only, as the events API already is.
