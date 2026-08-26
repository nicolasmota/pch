# Contract: MCP stdio Bridge (`pcl-sdk mcp-bridge`)

**Feature**: 002-external-connectors | Transport: MCP over stdio | Upstream: Hub REST facade on loopback

## Invocation

```bash
uv run pcl-sdk mcp-bridge            # reads PCH_TOKEN, PCH_BASE from env
uv run pcl-sdk mcp-bridge --token <t> --base http://127.0.0.1:8765   # flags override env
```

- `PCH_TOKEN`: the connection token minted at pairing (001 flow). The bridge never mints, stores, or refreshes tokens.
- `PCH_BASE`: Hub base URL; defaults to `http://127.0.0.1:8765`.
- The bridge exits non-zero with a clear stderr message if the token is missing or `GET /health` fails at startup.

## Exposed MCP tools (1:1 with the Hub tool facade)

Each MCP tool call becomes `POST {PCH_BASE}/v1/mcp/tools/{name}` with `Authorization: Bearer {PCH_TOKEN}` and the arguments as JSON body. Tool list and schemas are declared statically by the bridge, mirroring 001's facade:

| MCP tool | Purpose |
|---|---|
| `search_personal_context(query, purpose, scope?)` | grant-filtered search with citations |
| `get_context_manifest(purpose, requested_capabilities, selectors?, ttl_seconds?)` | purpose-bound context snapshot |
| `propose_memory(memory, evidence_refs, retention?)` | submit claim to proposal queue (email-derived claims per FR-017) |
| `set_shared_state(key, value, ttl_seconds, visibility)` / `get_shared_state(key)` | handoff state |
| `request_approval(intent_summary, rationale, impact)` | approval-gated ask |
| `propose_action(kind, summary_human, payload, basis_refs, idempotency_key)` | external-effect intent |
| `check_action_status(intent_id)` | poll decision |

The bridge adds **no** tools of its own and performs **no** local caching — every call is policy-evaluated and audited by the Hub per request (FR-002, FR-003).

## Error mapping

| Hub response | MCP behavior |
|---|---|
| `403` policy denial / redaction envelope | Tool result with the Hub's denial/redaction message as content (assistant sees the plain-language refusal; nothing leaks) |
| `401`/revoked (FR-004) | Tool error: `"Connection revoked by the user in the Hub."` — bridge stays up so re-pairing instructions can be surfaced |
| Hub unreachable | Tool error naming `PCH_BASE`; bridge does not retry silently |
| `422` validation | Tool error with field detail passthrough |

## Conformance tests

1. Drive the bridge with the `mcp` SDK client over stdio: `tools/list` matches the table above; `search_personal_context` round-trips against a temp Hub and returns cited results.
2. Revoke the connection mid-session → next call yields the revocation tool error (SC-003).
3. Out-of-grant query → refusal content, and the denial appears in the Hub audit under the connection identity (US1 acceptance 2).
4. Kill/restart Hub → unreachable error, then recovery without bridge restart.
