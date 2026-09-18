# Google connectors

Calendar and Gmail are **import** plugins. They write vault objects through the kernel. They do not send mail or create events on Google’s side.

Google requires **your** OAuth client. The Hub never ships a shared client ID (a shared id is what produces `invalid_client`).

Day to day: **Advanced → Plugins**. Install `pcl.google-calendar` or `pcl.gmail`, consent, then sync. The HTTP `/v1/connectors` surface and the `/connectors` page remain for leftover first-party accounts and for the OAuth redirect URI Google requires.

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

Restart the Hub after writing the file (`pch` or `make desktop`). Plugins use this client. `GET /v1/connectors/oauth/status` reports whether it is configured. The `/connectors` deep link also shows that status.

Never commit this file.

## Connect Calendar

1. Advanced → Plugins → install **Calendar** (`pcl.google-calendar`).
2. Review permissions and allow.
3. Complete Google consent in the browser (PKCE Desktop flow). The callback hits `/v1/connectors/oauth/callback` and redirects to `/plugins?connected=1`.
4. Sync runs on a schedule and via **Sync now**.

Events map to vault type `event` with classification **`private`**, `authority=source_imported`.

## Connect Gmail (selective)

Gmail **must** include a selection. In Plugins, install **Gmail** (`pcl.gmail`) and choose at least one of:

- `labels` — Gmail label ids/names you choose
- `senders` — allowlisted From addresses
- `after` / `before` — date window

The API rejects an email import that selects “everything.”

Imported messages are **`sensitive`** artifacts (`kind=email`, `untrusted=true`). A grant whose classification ceiling is `private` will not see them.

## Leftover HTTP (`/v1/connectors`)

| Action | HTTP |
|---|---|
| List | `GET /v1/connectors` |
| Create (returns `consent_url`) | `POST /v1/connectors` `{ "provider": "google", "kind": "calendar" \| "email", "selection": {…} }` |
| Sync now | `POST /v1/connectors/{id}/sync` |
| Pause / resume | `POST …/pause`, `POST …/resume` |
| Delete | `DELETE /v1/connectors/{id}` (optional `?purge=` to drop imported objects) |

The scheduler also ticks while `pch-server` is running. Prefer the Plugins HTTP surface (`/v1/plugins`) for new installs.

## Plugins vs leftover connectors

**Plugins** (`pcl.google-calendar`, `pcl.gmail`) are the import kit: OS-sandboxed on Linux and macOS when a backend is available; otherwise reduced. Use [Plugins](plugins.md) for Calendar/Gmail day to day and to sideload or marketplace-install other importers.

`/v1/connectors` and `/connectors` stay for unmigrated 002-style accounts. The OAuth callback URI does not change.

## Import is data

Calendar and mail must not expand grants, change policy, or be treated as instructions to an agent. If a message says “forward this to payroll,” that is text in an artifact, not an order.
