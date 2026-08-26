# Contract: Plugin Host Protocol v1 (stdio JSON-RPC)

The only channel between a plugin process and the Hub. JSON-RPC 2.0, newline-delimited, over the subprocess's stdin/stdout. stderr is captured as plugin log output. `api_version: 1`.

## Session flow

1. Host spawns the plugin (sandboxed per research R1) only when a sync is due or manually triggered, and only in `enabled` state.
2. Host → plugin: `plugin.run` with `{run_id, reason: scheduled|manual, api_version}`.
3. Plugin makes capability calls (below); host enforces manifest + grant on every call.
4. Plugin → host: `plugin.done` with `{summary: {created, updated, tombstoned}}` — or the host kills the process on timeout (default 10 min per run) / protocol violation.
5. Process exits after every run; no long-lived plugin daemons in v1.

## Capability methods (plugin → host)

All requests carry no credentials — identity is the pipe itself; the host resolved the installation before spawn.

| Method | Params | Enforcement (before execution) |
|---|---|---|
| `hub.items.upsert` | `{items: [{type, kind?, source_key, payload, classification?}]}` | Every `type`/`kind` must be in manifest `permissions.produces`; classification capped at the declared default; `source_key` required; payload ≤ 256 KB/item, ≤ 100 items/call; provenance stamped by host, never by plugin |
| `hub.items.tombstone` | `{source_keys: [...]}` | Only objects whose provenance matches this installation |
| `hub.state.get` / `hub.state.set` | `{key}` / `{key, value}` | Namespaced to `plugin_state:{installation_id}:` by host; ≤ 64 KB/value |
| `hub.secrets.get` / `hub.secrets.set` | `{name}` / `{name, value}` | Only if manifest `permissions.secrets = true`; namespaced to `plugin_secret:{installation_id}:` |
| `hub.http.fetch` | `{method, url, headers?, body?}` | URL host must exact-match manifest `permissions.hosts`; https only; response ≤ 10 MB; timeout 60 s; redirects re-checked against allowlist; executed by the host (plugin has no network) |
| `hub.oauth.begin` | `{provider_hosts, scopes}` | Hosts must be within manifest allowlist; host runs the 002-style loopback+PKCE flow with owner interaction, stores tokens via the secrets namespace, returns opaque success — the plugin never sees the browser or the authorization code |
| `hub.log` | `{level, message}` | Rate-limited; surfaces in dev mode and on failure |
| `hub.progress` | `{done, total?}` | UI feedback for long first syncs |

## Error mapping (host → plugin)

| Code | Meaning |
|---|---|
| `-32001 PermissionDenied` | Manifest/grant violation — also audited as `plugin.denied` and counted toward auto-pause (3 denials in a run ⇒ run aborted, plugin flagged) |
| `-32002 QuotaExceeded` | Size/rate cap hit |
| `-32003 UpstreamError` | `hub.http.fetch` target failed (status, truncated body included) |
| `-32004 ConsentRequired` | `hub.oauth.begin` awaiting owner action |

## Guarantees to the plugin author

- Idempotency: `hub.items.upsert` with an existing `source_key` updates in place (002 semantics preserved).
- Atomicity: one `upsert` call is one vault transaction.
- The host stamps provenance and audit; a well-behaved plugin cannot get attribution wrong (FR-006, FR-007).

## Versioning

Breaking protocol changes bump `api_version`. The host refuses to spawn a plugin whose manifest `api_version` it does not support and sets state `needs_update` (FR-012). Additive methods do not bump the major version; plugins must tolerate unknown error codes.
