# Data Model: External Connectors

**Feature**: 002-external-connectors | **Date**: 2026-08-21

All new objects live in the existing `objects` table and carry the 001 universal metadata envelope (id, space_id, type, classification, owner, provenance, confidence, authority, retention, version). Only deltas are described here.

## Schema delta (vault)

| Change | Detail |
|---|---|
| `objects.source_key` | New nullable TEXT column: `"{provider}:{account}:{source_id}"`; unique partial index where non-null. Dedup + update-in-place key for connector items (FR-012) |
| `kv` entries | `connector_token:{connector_id}` → encrypted OAuth refresh-token blob. Excluded from PCA export by key prefix (FR-011) |

## New object types

### `connector_account` (id prefix `cxa`)

| Field | Type | Notes |
|---|---|---|
| provider | enum: `google` | first provider per spec assumption |
| kind | enum: `calendar`, `email` | one account object per connector kind |
| account_label | str | e.g., masked address shown in UI; never the token |
| status | enum: `active`, `paused`, `reconnect_needed`, `disconnected` | lifecycle below |
| selection | object | calendar: `{calendar_ids: [str]}`; email: `{labels: [str], senders: [str], after: date?, before: date?}` — email selection MUST be non-empty (FR-015) |
| cadence_minutes | int | default 15 (calendar) / 60 (email), per clarification |
| sync_cursor | str? | Calendar `syncToken` / Gmail `historyId` |
| last_sync | object? | `{at, outcome, created, updated, tombstoned, error?}` (FR-009 status surface) |
| classification | fixed `private` | the account object itself |

**Lifecycle**: `active ⇄ paused` (user), `active → reconnect_needed` (provider auth failure; stale data stays readable), `* → disconnected` (user; stops syncs immediately, user chooses keep-or-delete for imported items — FR-010).

### `event` (id prefix `evt`)

| Field | Type | Notes |
|---|---|---|
| title | str | FTS-indexed |
| starts_at / ends_at | ISO datetime | typed for schedule queries and briefs |
| all_day | bool | |
| location | str? | |
| attendees | list[str] | opaque display strings; no contact resolution in this feature |
| calendar_id | str | source calendar |
| status | enum: `confirmed`, `tentative`, `cancelled` | cancelled ⇒ tombstoned object |
| classification | default `private` | per clarification; user-reclassifiable to `sensitive` (FR-013) |
| authority | fixed `imported` | never user-confirmed (FR-007) |
| source_refs | [connector_account id] | provenance chain |

### `artifact` extension (email)

Existing `artifact` type, `kind="email"`:

| Field | Type | Notes |
|---|---|---|
| subject / sender / recipients | str / str / list[str] | subject+body FTS-indexed |
| sent_at | ISO datetime | |
| body_text | str | text/plain part only; HTML stripped; attachments NOT imported |
| classification | default `sensitive` | per FR-016; excluded from grants without sensitive ceiling |
| authority | fixed `imported` | untrusted data (FR-008) — content can never carry policy authority |

## Policy integration (no evaluator changes)

- `_cap_for("event")` → `memory.retrieve`; email artifacts already map via `artifact`.
- Classification ceilings do the email gating: presets cap at `private`, so `sensitive` email artifacts are redacted with notice (US3 scenario 3) — existing evaluator behavior, new fixtures only.
- Derived claims: assistants call the existing `propose_memory` tool citing `artifact`/`event` ids as evidence (FR-017). No new proposal fields.

## Audit events (new kinds)

| Kind | When |
|---|---|
| `connector.connected` / `connector.disconnected` / `connector.paused` | consent completed / user disconnect (+kept-or-deleted choice) / pause-resume |
| `connector.sync` | every run: refs = connector id; extra = counts + outcome (FR-009) |
| `connection.recipe_issued` | assistant recipe rendered with a pairing token (US1 traceability) |

## Assistant catalog (static, not vault data)

`CatalogEntry`: `{id, name, supported: bool, notes, recipe_template}` — rendered with `{token, base_url, connection_id}` at recipe time. Cursor, Claude Code, Claude Desktop, ChatGPT entries per research R5.
