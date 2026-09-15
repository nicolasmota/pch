# Plugins

Plugins are **import-only** extensions. They write vault objects through kernel capabilities. They do not act outward (send, create external events, export, or extend the UI).

Plugin code talks to the Hub through `pch_sdk.plugin_runtime` (stdio JSON-RPC). It never sees the vault key or the open network — `hub.http.fetch` is host-mediated against declared hostnames.

## Bundled plugins

| Id | What it imports | Classification | Schedule |
|---|---|---|---|
| `pcl.google-calendar` | Calendar events (`event`) | `private` | 15m |
| `pcl.gmail` | Selected mail (`artifact` kind `email`) | `sensitive` | 60m |
| `pcl.example-rss` | RSS/Atom items as artifacts | `personal` | 60m |

The Hub UI **Plugins** page is the default path. Marketplace listings (`/marketplace`) are a signed static `catalog.json` and stay off the main menu. Third-party publish is a curator-reviewed PR, not self-service.

## Developer loop

```bash
uv run pch-sdk plugin new my.importer
uv run pch-sdk plugin validate my.importer
uv run pch-sdk plugin pack my.importer
# Side-load the .pclplugin via Plugins, or POST /v1/plugins with source=sideload
uv run pch-sdk plugin dev my.importer --hub http://127.0.0.1:8765
```

`plugin new` writes `plugin.toml` and `src/sync.py`. `pack` produces `{id}-{version}.pclplugin` (zip) and prints sha256. `dev` validates and reminds you to pack + sideload; it does not hot-attach a running child by itself.

## plugin.toml

```toml
[plugin]
id = "my.importer"
name = "My importer"
description = "Import items into the Hub."
version = "0.1.0"
publisher = "local-dev"
api_version = 1
entry = "sync:main"

[permissions]
secrets = false
schedule = "manual"          # or 15m, 60m, 2h — minimum 5m if timed
hosts = ["example.com"]      # bare hostnames only — no URLs, paths, or wildcards

[[permissions.produces]]
type = "artifact"            # event | artifact | note
classification = "personal"
```

- `id`: 3–64 char slug `[a-z0-9][a-z0-9.-]*`
- `version`: semver
- `hosts`: undeclared hosts are denied at fetch time
- `secrets`: must be true to use `hub.secrets_*`
- Produced types other than `event` / `artifact` / `note` are rejected

## Runtime API

```python
from pch_sdk.plugin_runtime import hub


def main() -> dict:
    hub.log("hello from my.importer")
    hub.items_upsert(
        [
            {
                "type": "artifact",
                "title": "Example item",
                "body": "Created by the plugin scaffold.",
                "source_key": "example:my.importer:1",
                "classification": "personal",
                "authority": "source_imported",
            }
        ]
    )
    return {"created": 1, "updated": 0}
```

Host methods:

| Method | Purpose |
|---|---|
| `hub.items_upsert(items)` | Create/update imported objects (chunks of 100) |
| `hub.items_tombstone(source_keys)` | Soft-delete by source key |
| `hub.state_get` / `hub.state_set` | Plugin-local cursor/state strings |
| `hub.secrets_get` / `hub.secrets_set` | Named secrets, only if `permissions.secrets` |
| `hub.http_fetch(url, method=..., headers=..., body=...)` | Egress allowlisted to declared hosts |
| `hub.oauth_begin(provider_hosts, scopes)` | Start host-mediated OAuth |
| `hub.log(message, level="info")` | Host log |
| `hub.progress(done, total=None)` | Run progress |

Imports from the plugin tree are limited: stdlib allowlist plus `pch_sdk`. Importing `pch_core` / `pch_server` fails `plugin validate`.

## Isolation and consent

Installations have origin `bundled` | `marketplace` | `sideload` and isolation `sandboxed` or `reduced`. The person consents per install (`GET|POST /v1/plugins/{id}/consent`) and can enable, pause, disable, sync, or delete.

OS sandbox backends:

- Linux: bubblewrap (`bwrap`) — plugin child network unshared. The probe bind-mounts host `/usr` (and the interpreter) so the child can actually start; a nested container that cannot create a user namespace reports `reduced` / `none`.
- macOS: seatbelt (`sandbox-exec`) — plugin child network denied
- Other systems, including Windows: `reduced`. No Windows OS sandbox ships. Capability mediation still applies.

`pch doctor --json` reports `plugin_isolation` and `plugin_sandbox_backend` (`bwrap`, `sandbox-exec`, or `none`). Set `PCH_PLUGIN_SANDBOX=0` to force reduced even when a backend binary exists.

Enforcement is technical isolation, not marketplace curation. Curation reduces risk; it is never the enforcement mechanism.

## HTTP (owner)

| Method | Path |
|---|---|
| `GET` `POST` | `/v1/plugins` |
| `GET` `POST` | `/v1/plugins/{id}/consent` |
| `POST` | `/v1/plugins/{id}/enable` `pause` `disable` `sync` |
| `GET` | `/v1/plugins/{id}` `/v1/plugins/{id}/runs` |
| `DELETE` | `/v1/plugins/{id}` |
| `GET` `POST` | `/v1/marketplace/catalog` `refresh` `install` |

Catalog URL/key: `PCH_CATALOG_URL`, `PCH_CATALOG_PUBKEY`. Dev servers may set `PCH_CATALOG_REFRESH=1`. Extra plugin search path: `PCH_PLUGINS_DIR`.
