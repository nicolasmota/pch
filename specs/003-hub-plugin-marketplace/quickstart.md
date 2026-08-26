# Quickstart Validation: Hub Plugin Framework & Marketplace

Runnable scenarios proving the feature end to end. Contracts: [plugin-host-protocol](./contracts/plugin-host-protocol.md), [plugin-manifest](./contracts/plugin-manifest.md), [plugins-rest](./contracts/plugins-rest.md), [marketplace-catalog](./contracts/marketplace-catalog.md). Entities: [data-model.md](./data-model.md).

## Prerequisites

```bash
cd ~/projects/pcl
uv sync
make run          # Hub on http://127.0.0.1:8765
cd frontend && npm run dev   # UI on http://localhost:5173
```

Sandbox check (informational): `bwrap --version || unshare --version` — absence means plugins run in "reduced isolation" and scenario 4's namespace assertion is skipped.

## Scenario 1 — Migration: 002 connectors become plugins (US1, SC-001)

Start from a vault that already has Google Calendar + Gmail connected (the current dev vault qualifies).

1. Upgrade/restart the Hub → migration runs once.
2. `GET /v1/plugins` → two installations (`pcl.google-calendar`, `pcl.gmail`), `origin=bundled`, `state=enabled`, grants carrying the 002-consented scopes.
3. UI Plugins page shows both with last-run info; Connections page no longer lists them as built-in connectors.
4. Trigger `POST /v1/plugins/{id}/sync` for each → outcome `ok`, **0 duplicates** (source_keys unchanged); previously imported events/emails still searchable with intact provenance.
5. Audit timeline shows `plugin.sync` events attributed to each plugin.

**Expected**: zero data loss, zero reconfiguration, both syncs green.

## Scenario 2 — Consent gate & lifecycle (US1, FR-003/004/005)

1. `POST /v1/plugins {source: bundled, plugin_id: "pcl.example-rss"}` → state `installed`.
2. Assert no plugin process has ever spawned (no `plugin.sync` audit events, no run).
3. `GET /v1/plugins/{id}/consent` → plain-language permissions; approve via `POST .../consent` → `enabled`.
4. Sync once; then `POST .../pause` mid-run → process killed, run marked aborted.
5. `DELETE /v1/plugins/{id}?purge_data=true` → imported items tombstoned, `plugin.lifecycle` audited.

**Expected**: nothing runs before consent; pause is immediate; purge removes exactly this plugin's objects.

## Scenario 3 — Developer kit builds the RSS example (US2, SC-004)

```bash
uv run pcl-sdk plugin new my-rss
uv run pcl-sdk plugin dev my-rss --hub http://127.0.0.1:8765     # live capability log
uv run pcl-sdk plugin validate my-rss                             # passes
uv run pcl-sdk plugin pack my-rss                                 # my-rss-0.1.0.pclplugin + sha256
```

Sideload the package via the Plugins page → consent screen shows the **unverified developer** warning (FR-011) → after consent, items appear as `artifact` objects with plugin provenance.

**Expected**: full loop without reading Hub source; validate catches an intentionally added undeclared host before pack.

## Scenario 4 — Adversarial plugin is contained (SC-005, FR-002a/008)

Run the hostile test plugin from the adversarial suite (`pytest packages/pcl-server/tests/plugins/test_adversarial.py` covers the same assertions headlessly):

1. Upserts an undeclared object type → `-32001 PermissionDenied`, `plugin.denied` audited.
2. `hub.http.fetch` to an undeclared host → denied; with sandbox present, a raw `socket.connect` from plugin code fails (no network namespace).
3. Infinite loop → supervisor timeout kill; Hub stays responsive; plugin flagged on Plugins page.
4. 3 denials in one run → run aborted, plugin auto-flagged.

**Expected**: 100% of undeclared attempts blocked; Hub and other plugins unaffected.

## Scenario 5 — Marketplace: install, tamper, update, kill-switch (US3, SC-006/007)

Uses the local catalog fixture (test signing key) served via a static file URL.

1. Marketplace page → listings show publisher, verification badge, permissions **before** install (FR-013).
2. Install a listing → sha256 verified → consent → runs.
3. Tamper test: corrupt the package fixture → `POST /v1/marketplace/install` → `IntegrityMismatch`, nothing written (SC-006).
4. Publish v1.1.0 adding a new host → update preview shows the permission diff; applying without re-consent → 422 `ReconsentRequired`; after approving the diff, update activates (FR-015).
5. Flip `withdrawn` on the listing, `POST /v1/marketplace/refresh` → plugin paused, warning banner, data intact (SC-007).
6. Offline test: stop the catalog server → Marketplace shows cached catalog with stale notice; installed plugins keep syncing (SC-008).

**Expected**: every integrity and consent gate holds; kill-switch pauses without data loss.

## Test suite entry points

```bash
uv run pytest packages/pcl-core/tests/plugin_tests/          # manifest schema, grant derivation
uv run pytest packages/pcl-server/tests/plugin_runtime/      # host protocol, enforcement, supervisor, adversarial, migration
uv run pytest packages/pcl-server/tests/marketplace/         # catalog verify, tamper, kill-switch, offline
uv run pytest packages/pcl-sdk/tests/plugin_kit/             # scaffold, validate, pack round-trip
cd frontend && npm run build                                 # UI type-check
```

## Recorded validation (2026-08-21)

- Plugin + marketplace + kit + PCA secret-exclusion suites: **22 passed**
- Existing connector suites: **18 passed** (002 path unchanged)
- `frontend` `npm run build`: **ok**
- Live Hub Scenarios 1–5 against a populated vault: run after restart so migration converts the current Google connectors; Plugins/Marketplace pages ship in this build.
