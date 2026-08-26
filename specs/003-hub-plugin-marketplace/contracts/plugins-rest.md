# Contract: Plugins REST API

Owner-authenticated (same bearer scheme as 001/002), loopback only. Serves the Plugins page and the developer kit's `plugin dev`.

## Endpoints

| Method & Path | Purpose | Notes |
|---|---|---|
| `GET /v1/plugins` | List installations | Full `PluginInstallation` projection incl. `state`, `isolation`, `last_run` |
| `POST /v1/plugins` | Install from package | Body: `{source: sideload, package_b64}` or `{source: bundled, plugin_id}`; validates manifest, verifies sha256 when given; creates installation in `installed` state — **nothing runs yet** |
| `GET /v1/plugins/{id}/consent` | Consent preview | Plain-language permission rendering from the manifest snapshot (FR-003); includes `unverified` warning for sideloads (FR-011) and `reduced isolation` notice when applicable |
| `POST /v1/plugins/{id}/consent` | Approve & enable | Creates the plugin grant, transitions `installed → enabled`, audits `plugin.consent`; body may scope down (e.g. `schedule: manual`) |
| `POST /v1/plugins/{id}/enable` / `pause` / `disable` | Lifecycle | Pause/disable kill any running process immediately (FR-004) |
| `POST /v1/plugins/{id}/sync` | Manual run | 409 if a run is in flight; 422 if state ≠ `enabled` |
| `DELETE /v1/plugins/{id}` | Remove | Query `purge_data=true|false` (FR-005); purge tombstones all objects with this installation's provenance; both paths audited |
| `GET /v1/plugins/{id}/runs` | Recent runs | From audit ledger (`plugin.sync`, `plugin.denied` events) |

## Errors

Existing error envelope. Notable: `ValidationFailed` (bad manifest/package), `IntegrityMismatch` (sha256, FR-014 — install rejected, nothing written), `ApiVersionUnsupported` (FR-012 — installs as `needs_update`, never runs), `ConsentRequired` (sync attempted pre-consent).

# Contract: Marketplace REST API

| Method & Path | Purpose | Notes |
|---|---|---|
| `GET /v1/marketplace/catalog` | Browse | Verified cached catalog + `fetched_at` + `stale: bool`; triggers background refresh; offline → cached copy or `offline: true` with empty listings (FR-017) |
| `POST /v1/marketplace/refresh` | Force catalog fetch | Verifies Ed25519 signature before replacing cache; on new `withdrawn` flags, pauses affected plugins and audits `plugin.killswitch` (FR-016) |
| `POST /v1/marketplace/install` | Install listing | Body: `{plugin_id, version?}`; downloads package, verifies sha256 against listing, then same path as `POST /v1/plugins` — consent still required before anything runs |
| `GET /v1/plugins/{id}/update` | Update preview | Available version + **permission diff** vs. installed snapshot (FR-015) |
| `POST /v1/plugins/{id}/update` | Apply update | If permissions were added: 422 `ReconsentRequired` until `POST .../consent` approves the diff; permission-neutral updates apply directly |

## Frontend contract (pages)

- **Plugins.tsx**: installation list with state chips (enabled/paused/needs update/flagged), consent modal (renders `GET .../consent` verbatim), lifecycle buttons, removal dialog with keep/purge choice, per-plugin run history.
- **Marketplace.tsx**: catalog browse/search with publisher + verification badge + permission preview *before* install (FR-013), install button → consent modal, update banners with permission diffs, offline/stale notices.
