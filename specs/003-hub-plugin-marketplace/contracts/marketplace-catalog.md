# Contract: Marketplace Catalog Format

A static, signed index the Hub fetches over HTTPS. No server-side API; the signature, not the transport, is the trust anchor.

## Files

| File | Content |
|---|---|
| `catalog.json` | The index (below) |
| `catalog.json.sig` | Ed25519 signature over the exact bytes of `catalog.json` |
| `packages/{plugin_id}-{version}.pclplugin` | Package zips referenced by the index |

The verification public key ships pinned inside the Hub. Key rotation = Hub release. The catalog URL is configurable (default: first-party GitHub repo raw URL) so self-hosted/mirrored catalogs work.

## `catalog.json` schema

```json
{
  "format": 1,
  "generated_at": "2026-08-21T00:00:00Z",
  "publishers": {
    "pcl-first-party": {"name": "PCL", "verification": "first_party"},
    "acme-dev": {"name": "Acme", "verification": "verified"}
  },
  "listings": [
    {
      "plugin_id": "pcl.google-calendar",
      "name": "Google Calendar",
      "description": "Imports your calendar events.",
      "category": "connector",
      "publisher": "pcl-first-party",
      "withdrawn": null,
      "signals": {"installs": null, "rating": null},
      "versions": [
        {
          "version": "1.0.0",
          "api_version": 1,
          "package_url": "https://.../packages/pcl.google-calendar-1.0.0.pclplugin",
          "sha256": "…64 hex chars…",
          "released_at": "2026-08-21T00:00:00Z",
          "permissions_summary": {
            "produces": [{"type": "event", "classification": "private"}],
            "hosts": ["www.googleapis.com", "oauth2.googleapis.com", "accounts.google.com"],
            "schedule": "15m",
            "secrets": true
          }
        }
      ]
    }
  ]
}
```

`withdrawn` when set: `{"reason": "credential harvesting", "at": "…", "advisory_url": "…"}`.

## Client rules (the Hub)

1. Fetch `catalog.json` + `.sig`; verify signature against the pinned key **before** parsing; on failure keep the previous cache and audit `marketplace.catalog_check` with `outcome=signature_invalid`.
2. `permissions_summary` is display-only; the authoritative manifest is inside the package — at install the Hub re-verifies that the packaged manifest is a subset-or-equal of the summary shown pre-install, else `IntegrityMismatch`.
3. Package download: verify sha256 against the listing before unpacking; mismatch → reject, audit, never activate (FR-014, SC-006).
4. On any catalog refresh, diff `withdrawn` flags against installed plugins: newly withdrawn → pause plugin, set `state_reason`, warn user, audit `plugin.killswitch` (FR-016, SC-007).
5. Unknown `format` versions → keep cache, surface "catalog needs newer Hub".

## Publishing workflow (process, v1)

Third-party developer opens a PR against the catalog repo adding their listing + package (FR-019). Curator review checks: `plugin validate` passes, permissions are minimal and match the description, publisher identity is established. Merge = published; the CI of the catalog repo re-signs the index. Self-service publishing is out of scope (clarification 3).
