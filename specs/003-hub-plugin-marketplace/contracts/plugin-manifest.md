# Contract: Plugin Manifest (`plugin.toml`)

The author's complete declaration of intent. The host enforces the *installed snapshot*; editing the file after install has no effect until an update is consented.

## Schema

```toml
[plugin]
id = "pcl.google-calendar"        # unique slug, immutable across versions
name = "Google Calendar"
description = "Imports your calendar events into the Hub."   # shown verbatim on consent screen
version = "1.0.0"                  # semver, must increase on update
publisher = "pcl-first-party"      # must match catalog listing for marketplace installs
api_version = 1                    # Plugin Host Protocol major version
entry = "sync:main"                # module:function inside src/

[permissions]
secrets = true                     # plugin-scoped secret storage (OAuth tokens)
schedule = "15m"                   # "5m".."24h" or "manual"
hosts = [                          # exact hostnames; https only; no wildcards in v1
  "www.googleapis.com",
  "oauth2.googleapis.com",
  "accounts.google.com",
]

[[permissions.produces]]
type = "event"                     # object type the plugin may upsert
classification = "private"         # default + ceiling for its writes

[[permissions.produces]]
type = "artifact"
kind = "email"
classification = "sensitive"
```

## Validation rules (enforced by `pcl-sdk plugin validate` and re-checked at install)

1. All fields above are required except `secrets` (default `false`); unknown keys anywhere → reject (fail closed).
2. `id` matches `^[a-z0-9][a-z0-9.-]{2,63}$`; `version` is valid semver; `schedule` ≥ 5 minutes or `"manual"`.
3. `hosts` entries are bare hostnames (no scheme, port, path, or wildcard).
4. `produces[].type` must be a Hub-known importable type (`event`, `artifact`, `note`); `classification` must be a valid level; plugins cannot declare types they cannot produce (no `memory` — claims arrive only via assistant proposals, 002 rule preserved).
5. `src/` imports resolve to stdlib or `pcl_sdk.plugin_runtime` only (R2); violation → validation error listing offending imports.
6. Package layout: `plugin.toml` at root, code under `src/`, nothing else executable.

## Consent rendering (FR-003)

The consent screen is generated from the manifest alone, in plain language:

> **Google Calendar** wants to: add **events** (private) to your vault · contact **www.googleapis.com, oauth2.googleapis.com, accounts.google.com** · run every **15 minutes** in the background · keep its own **sign-in tokens**.

Permission-adding updates render only the diff and require re-consent for the additions (FR-015).
