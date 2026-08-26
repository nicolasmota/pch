# Data Model: Hub Plugin Framework & Marketplace

**Feature**: 003-hub-plugin-marketplace | **Date**: 2026-08-21

All entities live in the existing SQLCipher vault. No new tables: one new object type (`plugin`), one new grant principal type, and two new `kv` prefixes. Imported data objects are unchanged except for plugin provenance.

## Manifest (embedded document, not a vault object)

Declared by the plugin author in `plugin.toml`; a snapshot is frozen into the installation record at install time (the *snapshot*, not the file on disk, is what the host enforces).

| Field | Type | Rules |
|---|---|---|
| `id` | string | Reverse-DNS-ish slug, e.g. `pcl.google-calendar`; unique per Hub; immutable across versions |
| `name`, `description` | string | Plain language; rendered on consent screen verbatim |
| `version` | semver string | Must increase on update |
| `publisher` | string | Publisher id; must match catalog listing for marketplace installs |
| `api_version` | int | Plugin Host Protocol major version targeted; host pauses plugin if unsupported (FR-012) |
| `entry` | string | Module path inside `src/`, e.g. `sync:main` |
| `permissions.produces` | list | Object types the plugin may upsert, each with `type` (e.g. `event`, `artifact`), optional `kind`, and `classification` default; anything else is denied (FR-002) |
| `permissions.hosts` | list of hostnames | Exact-match allowlist for `hub.http.fetch`; no wildcards in v1 |
| `permissions.schedule` | interval string | e.g. `15m`, `60m`, `manual`; min 5m |
| `permissions.secrets` | bool | Whether the plugin may use plugin-scoped secret storage (e.g. OAuth tokens) |

Validation: schema-checked by `plugin validate` and re-checked by the host at install; unknown keys rejected (fail closed).

## PluginInstallation (vault object, `type="plugin"`)

The local record of one installed plugin on this Hub (spec entity: Installation Record).

| Field | Type | Notes |
|---|---|---|
| `id` | uuid | Object id; referenced by grant, audit events, provenance |
| `plugin_id` | string | Manifest `id` |
| `version` | semver | Currently installed version |
| `manifest` | object | Frozen manifest snapshot (enforcement source of truth) |
| `origin` | enum | `bundled` \| `marketplace` \| `sideload` |
| `package_sha256` | string | Integrity fingerprint verified at install (FR-014); empty for bundled |
| `state` | enum | Lifecycle state, see transitions below |
| `state_reason` | string | e.g. `withdrawn: credential harvesting`, `api_version 2 unsupported` |
| `grant_id` | uuid | The plugin grant created at consent |
| `isolation` | enum | `sandboxed` \| `reduced` (namespace sandbox unavailable, R1) |
| `last_run` | object | `{at, outcome, created, updated, tombstoned, error?}` — mirrors 002 connector `last_sync` |

### Lifecycle state transitions

```text
installed ──consent──▶ enabled ⇄ paused (user, or kill-switch/failure with state_reason)
    │                     │
    │                     ├──api mismatch──▶ needs_update (FR-012; re-enabled by compatible update)
    │                     └──user disable──▶ disabled ──user remove──▶ removed (+ optional data purge, FR-005)
    └──user remove (never consented: nothing ever ran)──▶ removed
```

Rules: no plugin process exists in any state except `enabled` (FR-003); entering `paused`/`disabled` kills the process immediately (FR-004); `removed` with purge tombstones every object whose provenance references this installation (FR-005).

## PluginGrant (existing grants store, new principal type `plugin`)

Created at consent, revoked at disable/removal. Derived from the manifest snapshot — the user approves the manifest, the grant records the approval.

| Field | Notes |
|---|---|
| `principal` | `plugin:{installation_id}` |
| `produces` | Allowed object types/kinds + classification each write receives |
| `hosts` | Egress allowlist copied from manifest |
| `schedule` | Approved cadence |
| `approved_at`, `approved_manifest_version` | Re-consent bumps these; permission-adding updates require it (FR-015) |

Enforcement: every host-protocol call resolves this grant; denials are audited as `plugin.denied` (FR-007). Content written by plugins is data only — grants never confer retrieval, action, or policy rights (FR-001, FR-018).

## CatalogListing + Publisher (fetched document, cached in `kv`)

One entry in the signed `catalog.json` (spec entities: Marketplace Listing, Publisher, Plugin Package).

| Field | Notes |
|---|---|
| `plugin_id`, `name`, `description`, `category` | Display fields (FR-013) |
| `publisher` | `{id, name, verification: first_party \| verified \| community}` (FR-019) |
| `versions[]` | Each: `{version, api_version, manifest_summary, package_url, sha256, released_at}` |
| `withdrawn` | `{flag, reason, at}` — kill-switch; pauses installs on next catalog check (FR-016) |
| `signals` | `{installs?, rating?}` — optional/minimal in v1 (assumption) |

Catalog integrity: the whole index is Ed25519-signed; the Hub verifies against a pinned key before caching. A listing's `sha256` is the only trust anchor for its package (FR-014).

## Vault `kv` additions

| Prefix | Contents | Export rule |
|---|---|---|
| `plugin_secret:{installation_id}:*` | Plugin-scoped secrets (OAuth refresh tokens) | Excluded from PCA exports, same as 002 connector tokens |
| `plugin_state:{installation_id}:*` | Sync cursors (syncToken, historyId), scratch state | Excluded from exports; deleted on removal |
| `marketplace_catalog` | Last verified catalog + fetch metadata | Excluded from exports |

## Provenance on imported objects

Unchanged object shapes from 001/002 (`event`, `artifact`, …). The `source_refs` provenance block now carries `plugin:{installation_id}` as the importing identity plus the existing `source_key`. Migration (R3) rewrites the 002 connector references to the new plugin installations while keeping every `source_key` byte-identical — this is what makes SC-001 (zero loss, zero duplicates) testable.

## Audit events (existing ledger, new event kinds)

`plugin.install`, `plugin.consent`, `plugin.lifecycle` (enable/pause/disable/remove, with reason), `plugin.sync` (counts + outcome), `plugin.denied` (capability, manifest rule violated), `plugin.killswitch`, `marketplace.catalog_check`. All carry `actor=plugin:{installation_id}` or `actor=owner` as appropriate — the UI timeline renders them with no schema change (FR-007, SC-003).
