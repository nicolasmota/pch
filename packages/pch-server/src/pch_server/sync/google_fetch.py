from __future__ import annotations

from typing import Any

from pch_core.errors import ValidationFailed

from pch_server.sync import http as sync_http

CALENDAR_URL = "https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
GMAIL_LIST_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
GMAIL_GET_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/{id}"
GMAIL_LABELS_URL = "https://gmail.googleapis.com/gmail/v1/users/me/labels"
GMAIL_PAGE_SIZE = 100
GMAIL_MAX_MESSAGES = 2000


def fetch_calendar_events(
    access_token: str,
    calendar_ids: list[str],
    sync_token: str | None,
) -> tuple[list[dict[str, Any]], list[str], str | None, bool]:
    """Return items, deleted ids, new sync token, and whether a full resync was needed."""
    headers = {"Authorization": f"Bearer {access_token}"}
    items: list[dict[str, Any]] = []
    deleted: list[str] = []
    new_token = sync_token
    full = False
    calendars = calendar_ids or ["primary"]
    for cal_id in calendars:
        params: dict[str, Any] = {"singleEvents": "true", "maxResults": 2500}
        if sync_token:
            params["syncToken"] = sync_token
        else:
            params["timeMin"] = "2020-01-01T00:00:00Z"
        url = CALENDAR_URL.format(calendar_id=cal_id)
        response = sync_http.client().get(url, headers=headers, params=params, timeout=60.0)
        if response.status_code == 410:
            full = True
            params.pop("syncToken", None)
            params["timeMin"] = "2020-01-01T00:00:00Z"
            response = sync_http.client().get(url, headers=headers, params=params, timeout=60.0)
        response.raise_for_status()
        payload = response.json()
        new_token = payload.get("nextSyncToken") or new_token
        for event in payload.get("items") or []:
            if event.get("status") == "cancelled":
                deleted.append(event.get("id") or "")
            else:
                items.append(event)
    return items, [d for d in deleted if d], new_token, full


def _quote_term(term: str) -> str:
    if any(ch.isspace() or ch in '/()"{}' for ch in term):
        escaped = term.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return term


def _gmail_date(value: str) -> str:
    if len(value) >= 10 and value[4] == "-" and value[7] == "-":
        return f"{value[0:4]}/{value[5:7]}/{value[8:10]}"
    return value


def _gmail_query(selection: dict[str, Any]) -> str:
    parts: list[str] = []
    for sender in selection.get("senders") or []:
        parts.append(f"from:{_quote_term(sender)}")
    if selection.get("after"):
        parts.append(f"after:{_gmail_date(str(selection['after']))}")
    if selection.get("before"):
        parts.append(f"before:{_gmail_date(str(selection['before']))}")
    return " ".join(parts)


def resolve_gmail_label_ids(access_token: str, names: list[str]) -> list[str]:
    if not names:
        return []
    headers = {"Authorization": f"Bearer {access_token}"}
    response = sync_http.client().get(GMAIL_LABELS_URL, headers=headers, timeout=60.0)
    response.raise_for_status()
    labels = response.json().get("labels") or []
    by_id: dict[str, str] = {}
    by_name: dict[str, str] = {}
    by_leaf: dict[str, list[str]] = {}
    for lab in labels:
        lid = str(lab.get("id") or "")
        name = str(lab.get("name") or "")
        if not lid:
            continue
        by_id[lid.lower()] = lid
        if name:
            by_name[name.lower()] = lid
            leaf = name.rsplit("/", 1)[-1].lower()
            by_leaf.setdefault(leaf, []).append(lid)
    resolved: list[str] = []
    missing: list[str] = []
    for raw in names:
        key = raw.lower()
        if key in by_id:
            resolved.append(by_id[key])
        elif key in by_name:
            resolved.append(by_name[key])
        elif len(by_leaf.get(key) or []) == 1:
            resolved.append(by_leaf[key][0])
        else:
            missing.append(raw)
    if missing:
        raise ValidationFailed(
            "Gmail has no label named "
            + ", ".join(missing)
            + ". Use the exact name shown in Gmail."
        )
    return resolved


def fetch_gmail_messages(
    access_token: str, selection: dict[str, Any], history_id: str | None
) -> tuple[list[dict], str | None]:
    headers = {"Authorization": f"Bearer {access_token}"}
    label_ids = resolve_gmail_label_ids(access_token, list(selection.get("labels") or []))
    query = _gmail_query(selection)
    messages: list[dict] = []
    page_token: str | None = None
    cursor = history_id
    while len(messages) < GMAIL_MAX_MESSAGES:
        params: list[tuple[str, str]] = [("maxResults", str(GMAIL_PAGE_SIZE))]
        if query:
            params.append(("q", query))
        params.extend(("labelIds", lid) for lid in label_ids)
        if page_token:
            params.append(("pageToken", page_token))
        response = sync_http.client().get(
            GMAIL_LIST_URL, headers=headers, params=params, timeout=60.0
        )
        response.raise_for_status()
        listing = response.json()
        cursor = listing.get("historyId") or cursor
        for stub in listing.get("messages") or []:
            detail = sync_http.client().get(
                GMAIL_GET_URL.format(id=stub["id"]),
                headers=headers,
                params={"format": "full"},
                timeout=60.0,
            )
            detail.raise_for_status()
            messages.append(detail.json())
            if len(messages) >= GMAIL_MAX_MESSAGES:
                break
        page_token = listing.get("nextPageToken")
        if not page_token:
            break
    return messages, cursor
