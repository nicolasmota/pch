# Interface Contract: Temporal Validity

**Feature**: `specs/005-temporal-validity/` · **Date**: 2026-08-26  
**Surfaces**: existing MCP tool `get_context_contract` (additive `as_of`); owner REST for interval, supersede, retract. No new REST router family. No new MCP tool.

Authentication unchanged (002). Owner REST remains `require_owner`. Agents do not call supersede/retract.

## MCP: `get_context_contract` (delta)

Locations unchanged: `tools_context.py`, `pcl_sdk/mcp_bridge.py` `TOOL_SCHEMAS`, `POST /v1/mcp/tools/get_context_contract`.

Request schema — 004 fields plus:

```json
{
  "type": "object",
  "required": ["purpose"],
  "additionalProperties": false,
  "properties": {
    "purpose": { "type": "string", "minLength": 1 },
    "subject_ref": { "type": ["string", "null"] },
    "max_items": { "type": ["integer", "null"], "minimum": 1 },
    "as_of": {
      "type": ["string", "null"],
      "description": "UTC instant at which current vs historical is resolved. Null means now."
    }
  }
}
```

**Behavior**:

| Condition | Result |
|-----------|--------|
| `as_of` omitted or null | Evaluation time = now (UTC). |
| `as_of` valid ISO-8601 | Evaluation time = that instant. Live Preference/Memory must contain it. |
| `as_of` unparseable | 422, no ledger issuance (same as empty purpose). |
| Preference/Memory not current at evaluation time | Omitted from live sections; not listed in `references`. |
| Two current prefs same `key` | Both inlined (caps permitting) + `conflicts.reason = preference_key_collision`. |
| Historical personal pref, work grant | Not in package; omission category as today, no titles/ids. |

Response required fields unchanged from 004. Preference/memory `body` MUST include `valid_from` and `valid_until` (null allowed).

## Owner REST

Base: existing `/v1/memories` and `/v1/preferences`. PATCH/GET already exist; bodies may include the new fields.

### Create (existing POST)

`POST /v1/preferences` with a `key` that already has a **current** preference → **422** with a message that `supersede` is required. Historical same key is allowed.

`POST /v1/memories` does not unique-key; overlapping current `subject_ref` is allowed until accept/supersede (conflicts may list them). Prefer `supersede` from UI.

### Patch interval (existing PATCH)

`PATCH /v1/{memories|preferences}/{id}` with `{ "valid_from": "...", "valid_until": "..." }`.  
`valid_until` before `valid_from` → 422.  
Patching `statement`/`value` only → version bump, not a new historical object.

### Supersede

```http
POST /v1/preferences/{id}/supersede
POST /v1/memories/{id}/supersede
```

```json
{ "value": "likes spicy food", "rationale": "changed my mind" }
```

Memory body uses `statement` instead of `value`.

**200**: `{ "predecessor": { ... }, "successor": { ... } }`  
**404**: id missing.  
**422**: target already historical, `never_true`, or wrong type; or successor would violate current-key uniqueness after close (should not happen if predecessor is the current row).

### Retract (never true)

```http
POST /v1/preferences/{id}/retract
POST /v1/memories/{id}/retract
```

Empty body. **200**: retracted object (`never_true: true`). Subsequent GET list for the Hub UI omits it from current and historical. `GET /v1/memories/{id}` may still return it for owner forensic view (optional); the Memories page list must not show it as historical truth.

## List (existing GET)

`GET /v1/memories` and `GET /v1/preferences` return current **and** historical rows (`never_true` false). Each row includes `valid_from`, `valid_until`. The UI, not the API, badges current vs historical using now.

## Errors (shared)

| Code | When |
|------|------|
| 422 | Empty purpose; bad `as_of`; end before start; second current preference key on create |
| 401/403 | Unchanged; revoked grant still refused + `context.contract` `status: refused` |
| 404 | Unknown id on supersede/retract |

## PCA

Export/import round-trip MUST preserve `valid_from`, `valid_until`, `never_true` on preference and memory objects. No new PCA section type.
