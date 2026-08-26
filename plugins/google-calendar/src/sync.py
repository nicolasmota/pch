from __future__ import annotations

import json
from urllib.parse import urlencode

from pcl_sdk.plugin_runtime import hub

CALENDAR_URL = "https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"


def main() -> dict:
    raw = hub.secrets_get("oauth")
    if not raw:
        hub.oauth_begin(
            ["www.googleapis.com", "oauth2.googleapis.com", "accounts.google.com"],
            ["https://www.googleapis.com/auth/calendar.readonly"],
        )
        return {"created": 0, "updated": 0, "tombstoned": 0}
    token = json.loads(raw).get("access_token") or ""
    account_id = hub.account_id
    cursor = hub.state_get("sync_cursor")
    selection = hub.run_params.get("selection") or {}
    calendar_ids = selection.get("calendar_ids") or ["primary"]
    headers = {"Authorization": f"Bearer {token}"}
    items: list[dict] = []
    deleted: list[str] = []
    new_cursor = cursor
    for cal_id in calendar_ids:
        params: dict[str, str] = {"singleEvents": "true", "maxResults": "250"}
        if cursor:
            params["syncToken"] = cursor
        else:
            params["timeMin"] = "2020-01-01T00:00:00Z"
        page_token = ""
        retried_410 = False
        while True:
            page_params = dict(params)
            if page_token:
                page_params["pageToken"] = page_token
            url = CALENDAR_URL.format(calendar_id=cal_id) + "?" + urlencode(page_params)
            response = hub.http_fetch(url, headers=headers)
            if int(response.get("status") or 0) == 410:
                if retried_410:
                    break
                retried_410 = True
                params.pop("syncToken", None)
                params["timeMin"] = "2020-01-01T00:00:00Z"
                page_token = ""
                continue
            payload = json.loads(response.get("body") or "{}")
            new_cursor = payload.get("nextSyncToken") or new_cursor
            for event in payload.get("items") or []:
                if event.get("status") == "cancelled":
                    deleted.append(event.get("id") or "")
                else:
                    mapped = _map(event, account_id)
                    if mapped:
                        items.append(mapped)
            page_token = str(payload.get("nextPageToken") or "")
            if not page_token:
                break
    if items:
        hub.items_upsert(items)
    if deleted:
        hub.items_tombstone([f"google:{account_id}:{eid}" for eid in deleted if eid])
    if new_cursor:
        hub.state_set("sync_cursor", new_cursor)
    return {"created": len(items), "updated": 0, "tombstoned": len(deleted)}


def _map(raw: dict, account_id: str) -> dict | None:
    status = (raw.get("status") or "confirmed").lower()
    if status not in ("confirmed", "tentative", "cancelled"):
        status = "confirmed"
    start = raw.get("start") or {}
    end = raw.get("end") or {}
    all_day = "date" in start and "dateTime" not in start
    starts_at = start.get("dateTime") or start.get("date") or ""
    ends_at = end.get("dateTime") or end.get("date") or starts_at
    if not starts_at:
        return None
    attendees = [a.get("email") or a.get("displayName") or "" for a in raw.get("attendees") or []]
    source_id = raw.get("id") or ""
    return {
        "type": "event",
        "title": raw.get("summary") or "(untitled)",
        "starts_at": starts_at,
        "ends_at": ends_at,
        "all_day": all_day,
        "location": raw.get("location"),
        "attendees": [a for a in attendees if a],
        "calendar_id": (raw.get("organizer") or {}).get("email") or "primary",
        "status": status,
        "source_key": f"google:{account_id}:{source_id}",
        "classification": "private",
        "authority": "source_imported",
    }
