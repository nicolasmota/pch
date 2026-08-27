# Interface Contract: Runtime recipes + same situation package

**Feature**: `specs/009-runtime-adapters/` · **Date**: 2026-08-26  
**Surfaces**: existing catalog + recipe REST; existing MCP `get_context_contract`; Connections page. **No new MCP tool.**

## Catalog

`GET /v1/catalog/assistants` (owner) MUST include:

| id | name | supported |
|----|------|-----------|
| `cursor` | Cursor | true |
| `hermes` | Hermes | true |
| `openclaw` | OpenClaw | true |

Other 002 ids may remain. Demo-agent MUST NOT appear as a supported real-use target.

## Recipe POST

`POST /v1/connections/{connection_id}/recipe` body: `{ "assistant": "<id>" }`.

| assistant | HTTP | `format` | `snippet` keys |
|-----------|------|----------|----------------|
| `hermes` | 200 | `hermes-yaml` | `mcp_servers.personal-context-hub.{command,args,env}` |
| `openclaw` | 200 | `openclaw-json` | `mcp.servers.personal-context-hub.{command,args,env}` |
| `cursor` | 200 | `cursor-mcp-json` | `mcpServers.personal-context-hub.{command,args,env}` (unchanged) |
| unknown / unsupported | 422 | — | — |

Shared env:

```json
{
  "PCH_TOKEN": "<issued token>",
  "PCH_BASE": "http://127.0.0.1:8765"
}
```

Shared command family: `uv` + `["run", "pcl-sdk", "mcp-bridge"]` (same as 002). `PCH_BASE` host MUST be loopback.

`instructions` (normative intent, not exact copy):

- Hermes: paste under `mcp_servers` in `~/.hermes/config.yaml`; reload MCP in the session.
- OpenClaw: paste under `mcp.servers` in `~/.openclaw/openclaw.json` (or Settings → MCP).
- Cursor: unchanged (`.cursor/mcp.json`).

Audit: `connection.recipe_issued` still emitted on 200.

## Situation package (unchanged tool)

`POST /v1/mcp/tools/get_context_contract` with Bearer token from pairing. Required keys remain E1 (+ `relations` from E4). Two real-use tokens, same grant, same purpose → identical `situation` and `goals` (and `relations` / operational fields if set). **No** `get_hermes_context` / `get_openclaw_context`.

## Connections UI

- Picker options come from catalog GET (Hermes and OpenClaw appear without a hardcoded third page).
- Generate recipe uses POST above.
- Copy uses native snippet (YAML text for `hermes-yaml`; JSON for the others).
- Unknown assistant never shown as supported.

## Behavioral contract

| # | Guarantee | Spec ref |
|---|-----------|----------|
| B1 | Catalog includes supported `hermes` and `openclaw`; Cursor remains. | SC-001 |
| B2 | Valid recipe 200 with native snippet; unknown 422. | SC-002 |
| B3 | Two real-use paired tokens agree on the trip package. | SC-003 |
| B4 | After pairing B, trip facts are present without re-entry. | SC-004 |
| B5 | Revoke A does not delete Hub objects. | SC-005 |
| B6 | Work-scoped newly listed runtime: 0 personal trip titles/ids. | SC-006 |
| B7 | `PCH_BASE` loopback; no new bind; existing `get_context_contract`. | SC-007 |
| B8 | No new MCP read tool. No A2A. No per-model adapter. | FR-005 |

## Fixture tests (fail first)

| SC | File::test | Marker |
|----|------------|--------|
| SC-001 | `packages/pcl-server/tests/contract/test_assistant_catalog.py::test_catalog_lists_hermes_and_openclaw` | (default) |
| SC-002 | `test_assistant_catalog.py::test_hermes_and_openclaw_recipes` and `test_unknown_assistant_recipe_rejected` | (default) |
| SC-003 | `packages/pcl-server/tests/contract/test_runtime_adapters.py::test_two_real_use_runtimes_agree` | (default) |
| SC-004 | `test_runtime_adapters.py::test_switch_runtime_keeps_trip` | (default) |
| SC-005 | `test_runtime_adapters.py::test_revoke_does_not_delete_hub_objects` | (default) |
| SC-006 | `packages/pcl-server/tests/forbidden_context/test_runtime_isolation.py::test_work_scope_new_runtime_omits_personal_trip` | `forbidden_context` |
| SC-007 | loopback `PCH_BASE` asserted in catalog recipe tests | (default) |
