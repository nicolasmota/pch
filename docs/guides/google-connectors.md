# Google connectors

Calendar and Gmail are **import** connectors. They write vault objects through the kernel. They do not send mail or create events on Google’s side.

Google requires **your** OAuth client. The Hub never ships a shared client ID (a shared id is what produces `invalid_client`).

## Create a Desktop OAuth client

1. Open [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials).
2. Create or select a project.
3. Enable **Google Calendar API** and **Gmail API**.
4. Configure the OAuth consent screen (External is fine for a personal Desktop app; add yourself as a test user while the app is in testing).
5. Create credentials → OAuth client ID → application type **Desktop app**.
6. Copy the client ID and secret.
7. Add authorized redirect URI:

   `http://127.0.0.1:8765/v1/connectors/oauth/callback`

   If you change `--port`, change the URI to match. Override with `PCH_OAUTH_REDIRECT`.

## Install credentials

Write `~/.pch/google_oauth.json` with mode `0600`:

```json
{
  "client_id": "xxxxx.apps.googleusercontent.com",
  "client_secret": "xxxxx"
}
```

Alternatively:

- Environment: `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET`
- Hub API (owner): `PUT /v1/connectors/oauth/credentials`

Restart the Hub after writing the file (`pch` or `make desktop`). **Connectors** (`/connectors`) shows whether OAuth is configured (`GET /v1/connectors/oauth/status`).

Never commit this file.

## Connect Calendar

1. Connectors → add **calendar**.
2. Complete Google consent in the browser (PKCE Desktop flow).
3. The callback hits `/v1/connectors/oauth/callback` and redirects to `/connectors?connected=1`.
4. Sync runs on a schedule and via **Sync**.

Events map to vault type `event` with classification **`private`**, `authority=source_imported`.

## Connect Gmail (selective)

Gmail **must** include a selection. Create or patch with at least one of:

- `labels` — Gmail label ids/names you choose
- `senders` — allowlisted From addresses
- `after` / `before` — date window

The API rejects an email connector that selects “everything.”

Imported messages are **`sensitive`** artifacts (`kind=email`, `untrusted=true`). A grant whose classification ceiling is `private` will not see them.

## Lifecycle

| Action | HTTP |
|---|---|
| List | `GET /v1/connectors` |
| Create (returns `consent_url`) | `POST /v1/connectors` `{ "provider": "google", "kind": "calendar" \| "email", "selection": {…} }` |
| Sync now | `POST /v1/connectors/{id}/sync` |
| Pause / resume | `POST …/pause`, `POST …/resume` |
| Delete | `DELETE /v1/connectors/{id}` (optional `?purge=` to drop imported objects) |

The scheduler also ticks while `pch-server` is running.

## Plugins vs connectors

The same Google products also exist as **bundled plugins** (`pcl.google-calendar`, `pcl.gmail`) with declared HTTPS hosts and schedules (15m / 60m). Connectors are the first-party OAuth + sync path in the UI. Plugins are the import kit (OS-sandboxed on Linux and macOS when a backend is available; otherwise reduced). Use the Connectors page for Calendar/Gmail day to day; use [Plugins](plugins.md) to sideload or marketplace-install other importers.

## Import is data

Calendar and mail must not expand grants, change policy, or be treated as instructions to an agent. If a message says “forward this to payroll,” that is text in an artifact, not an order.
