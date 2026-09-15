# Hub plugins

Import-only extensions. Plugin code talks to the Hub through `pch_sdk.plugin_runtime` (stdio JSON-RPC). It never sees the vault key or the open network.

**Full guide:** [docs/guides/plugins.md](../docs/guides/plugins.md)

## Developer loop

```bash
uv run pch-sdk plugin new my.importer
uv run pch-sdk plugin validate my.importer
uv run pch-sdk plugin pack my.importer
# Side-load the .pclplugin via Plugins → or POST /v1/plugins source=sideload
uv run pch-sdk plugin dev my.importer --hub http://127.0.0.1:8765
```

`plugin.toml` declares produced object types, HTTPS hosts, schedule, and whether the plugin may store secrets. Undeclared access is denied by the host.

## Bundled plugins

- `google-calendar` — `pcl.google-calendar`
- `gmail` — `pcl.gmail`
- `example-rss` — third-party DX proof

Marketplace listings are a signed static `catalog.json`. Third-party publish is a curator-reviewed PR, not self-service.
