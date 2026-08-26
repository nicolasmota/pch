# Phase 0 Research: Hub Plugin Framework & Marketplace

**Feature**: 003-hub-plugin-marketplace | **Date**: 2026-08-21

All technical unknowns behind the clarified spec are resolved here. Format per decision: Decision / Rationale / Alternatives considered.

## R1. Plugin isolation mechanism (how "technical enforcement" is real)

**Decision**: Every plugin runs as a **subprocess launched by the Hub**, speaking JSON-RPC over stdio (Plugin Host Protocol v1). Three layers make enforcement technical rather than review-based:

1. **Credential starvation**: the plugin process never receives the vault key, owner token, or any Hub bearer token. Its only channel is the inherited stdio pipe; every message is dispatched against the plugin's grant and manifest by `enforcement.py` before touching anything.
2. **Network removal**: when Linux user+network namespaces are available (`bwrap` preferred, `unshare -rn` fallback — both work on the WSL2 validation target), the subprocess is launched with **no network interfaces at all**. HTTP happens only through the `hub.http.fetch` capability, where the kernel checks the manifest host allowlist, enforces size/time caps, and performs the request itself (`egress.py`).
3. **Filesystem minimization**: under `bwrap`, the plugin sees a read-only view of its own package directory plus a private tmpdir — not the vault file, not the Hub config.

If neither `bwrap` nor `unshare` is usable, layers 1 and full capability mediation still hold; the plugin is marked **"reduced isolation"** in the UI and side-loading requires an extra confirmation. SC-005 (100% of undeclared access blocked) is satisfied by mediation alone; the namespace layer removes the residual "malicious code opens its own socket" channel.

**Rationale**: This is the cheapest arrangement where a malicious plugin *cannot* reach undeclared data even in principle: there is no ambient authority to steal. It also gives FR-008 (crash isolation) for free — a hung plugin is one `SIGKILL` away, and the supervisor already owns the process handle.

**Alternatives considered**:
- *In-process plugins with runtime policy checks*: a Python import can monkey-patch anything in the same interpreter; enforcement would be review-based, which clarification 2 explicitly rejected.
- *WASM runtime (wasmtime/extism)*: genuinely stronger sandbox, but adds a new runtime, a new toolchain for plugin authors, and kills the "reuse existing connector code" migration; revisit if plugins ever ship untrusted native code.
- *Docker/containers*: heavyweight dependency the local-first install story can't assume (WSL2 users may not have Docker running for the Hub).

## R2. Plugin packaging and dependencies

**Decision**: A plugin is a directory (or zip with extension `.pclplugin`) containing `plugin.toml` (manifest) + `src/` **stdlib-only Python** targeting the pinned `pcl_sdk.plugin_runtime` API. No third-party dependencies in v1; the runtime shim provides the capability client (items, state, secrets, fetch, log). Package integrity is the SHA-256 of the canonical zip, pinned in the signed catalog (FR-014).

**Rationale**: Import plugins are thin: fetch (mediated), map fields, upsert. The Google connectors from 002 already use plain httpx calls that translate directly to `hub.http.fetch`. Skipping dependency resolution removes the whole class of install-time supply-chain attacks (setup.py execution, typosquatting) and makes `validate`/`pack` trivial and deterministic.

**Alternatives considered**:
- *Per-plugin uv venvs with locked wheels*: real dependency support, but install-time code execution and per-plugin environments to audit; deferred until a concrete plugin actually needs it.
- *Python wheels as the package format*: entry-point metadata is convenient but wheels invite `pip install` habits and site-packages leakage into the host; a dumb zip keeps the boundary obvious.

## R3. Migrating the 002 connectors without data loss

**Decision**: `plugins/google-calendar/` and `plugins/gmail/` reimplement the 002 sync logic against the runtime shim (the fetch/mapping code moves nearly verbatim; httpx calls become `hub.http.fetch`). A one-time migration (`plugins/migrate.py`, run on first post-upgrade start) converts each existing `connector_account` into a `plugin` installation record with an auto-granted consent equal to what the user already approved in 002 (scopes were consented then; the grant records that provenance). OAuth refresh tokens move from `connector_token:{id}` to `plugin_secret:{plugin_id}:oauth`. **`source_key` values are unchanged**, so re-syncs update in place — zero duplicates, zero reimport (SC-001). The 002 scheduler entries are replaced by manifest schedules with the same cadences (15 min / 60 min).

**Rationale**: Dogfooding through the same protocol is the only honest proof the boundary works (and structurally enforced by moving the code out of `pcl-server`). Keeping `source_key` stable is what makes the migration invisible to the user.

**Alternatives considered**: keeping built-ins in-process and using the plugin path only for third parties — rejected: two code paths to maintain, and the first-party path would silently accumulate privileges (exactly what FR-002a forbids).

## R4. Marketplace catalog: hosting, signing, kill-switch

**Decision**: The catalog is a **static JSON index** (`catalog.json`) plus a detached **Ed25519 signature**, hosted at a configurable HTTPS URL (default: a first-party GitHub repo via raw URL). The verification public key ships pinned in the Hub. Each listing: plugin id, publisher, verification status, per-version entries (manifest summary, package URL, SHA-256), and a `withdrawn` flag with reason. The Hub fetches on a 12 h scheduler cadence and on Marketplace page open, caches the last verified copy in vault `kv` (offline browsing, FR-017/SC-008). Kill-switch: a listing turning `withdrawn` pauses the installed plugin and surfaces a warning banner on next catalog check; data untouched (FR-016). Third-party submission = pull request to the catalog repo; the curator reviews and merges (FR-019) — process, not Hub code.

**Rationale**: A signed static file needs no marketplace server, no accounts, no uptime promise — it matches local-first and is fully verifiable offline once fetched. GitHub PRs give review, provenance, and history for free at v1 scale (tens of listings).

**Alternatives considered**:
- *Hosted registry API (accounts, uploads, search)*: real infrastructure with real attack surface, unjustified for a curated tens-of-plugins catalog; the client contract (signed index) survives a later move to a hosted backend.
- *Sigstore/TUF*: stronger update-security frameworks, but their complexity dwarfs v1; the pinned-key + per-package SHA-256 design covers the threat model (tampered package, compromised CDN) at this scale.

## R5. Plugin identity, grants, and audit integration

**Decision**: Plugins become a **third principal type** alongside owner and connection in the existing policy engine. Installing creates a `plugin` object (installation record) and a grant whose scope is *derived from the manifest*: writable object types (with per-type classification defaults), host allowlist, schedule. Consent (FR-003) is the grant activation moment — the plugin process is never spawned before it. Every capability call is policy-checked against that grant and audited with `actor=plugin:{id}` (`plugin.sync`, `plugin.denied`, `plugin.lifecycle` events), satisfying FR-007/SC-003 with the same ledger the UI timeline already renders.

**Rationale**: 001 built exactly the right enforcement kernel; giving plugins their own principal type reuses grants, ceilings, audit, and the UI timeline instead of growing a parallel permission system.

**Alternatives considered**: modeling plugins as connections (002-style paired agents) — rejected: connections are *readers* with retrieval grants; plugins are *writers* with produce-type grants, and conflating them would blur exactly the read/write boundary v1 depends on (import-only).

## R6. Developer kit shape

**Decision**: `uv run pcl-sdk plugin new <id>` scaffolds manifest + sync skeleton + a runnable fake-source example; `plugin dev` runs the plugin against a local Hub in dev mode (verbose capability log, denials printed with the manifest line that would allow them); `plugin validate` checks manifest schema, stdlib-only imports, undeclared-capability probes, and payload limits; `plugin pack` emits `.pclplugin` + SHA-256. A single guide (`plugins/README.md`) covers the loop end to end. SC-004's proof: `plugins/example-rss/` is built using only the kit and guide.

**Rationale**: The kit rides the SDK package developers already install to talk to the Hub; no Hub checkout, no extra tool. Validation reusing the *same* `enforcement.py` rules the host applies at runtime means "passes validate" ≈ "won't be denied in production".

**Alternatives considered**: a separate `pcl-plugin-cli` package — one more thing to version and install, with no benefit until the kit outgrows the SDK.
