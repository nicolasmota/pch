from __future__ import annotations

import base64
import json
from urllib.parse import urlencode

from pch_sdk.plugin_runtime import hub

GMAIL_LIST = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
GMAIL_GET = "https://gmail.googleapis.com/gmail/v1/users/me/messages/{id}"
GMAIL_LABELS = "https://gmail.googleapis.com/gmail/v1/users/me/labels"
PAGE_SIZE = 100
MAX_MESSAGES = 2000


def main() -> dict:
    raw = hub.secrets_get("oauth")
    if not raw:
        hub.oauth_begin(
            ["gmail.googleapis.com", "oauth2.googleapis.com", "accounts.google.com"],
            ["https://www.googleapis.com/auth/gmail.readonly"],
        )
        return {"created": 0, "updated": 0}
    token = json.loads(raw).get("access_token") or ""
    headers = {"Authorization": f"Bearer {token}"}
    selection = hub.run_params.get("selection") or {}
    account_id = hub.account_id
    label_ids = _resolve_labels(headers, selection.get("labels") or [])
    query = _query(selection)
    listed: list[str] = []
    page = None
    while len(listed) < MAX_MESSAGES:
        params: dict[str, str] = {"maxResults": str(PAGE_SIZE), "q": query}
        if label_ids:
            params["labelIds"] = ",".join(label_ids)
        if page:
            params["pageToken"] = page
        response = hub.http_fetch(GMAIL_LIST + "?" + urlencode(params), headers=headers)
        payload = json.loads(response.get("body") or "{}")
        for msg in payload.get("messages") or []:
            if msg.get("id"):
                listed.append(msg["id"])
        page = payload.get("nextPageToken")
        if not page:
            break
    items = []
    for mid in listed[:MAX_MESSAGES]:
        response = hub.http_fetch(GMAIL_GET.format(id=mid) + "?format=full", headers=headers)
        mapped = _map(json.loads(response.get("body") or "{}"), account_id)
        if mapped:
            items.append(mapped)
            if len(items) >= 50:
                hub.items_upsert(items)
                items = []
    if items:
        hub.items_upsert(items)
    return {"created": len(listed), "updated": 0}


def _resolve_labels(headers: dict, names: list[str]) -> list[str]:
    if not names:
        return []
    payload = json.loads(hub.http_fetch(GMAIL_LABELS, headers=headers).get("body") or "{}")
    by_name = {str(lbl.get("name") or "").lower(): str(lbl.get("id") or "") for lbl in payload.get("labels") or []}
    resolved = []
    missing = []
    for name in names:
        found = by_name.get(name.lower())
        if found:
            resolved.append(found)
        else:
            missing.append(name)
    if missing:
        raise RuntimeError("unknown gmail labels: " + ", ".join(missing))
    return resolved


def _query(selection: dict) -> str:
    parts: list[str] = []
    for sender in selection.get("senders") or []:
        parts.append(f"from:{sender}")
    after = selection.get("after")
    if after:
        parts.append("after:" + _date(str(after)))
    before = selection.get("before")
    if before:
        parts.append("before:" + _date(str(before)))
    return " ".join(parts)


def _date(value: str) -> str:
    if len(value) >= 10 and value[4] == "-" and value[7] == "-":
        return f"{value[0:4]}/{value[5:7]}/{value[8:10]}"
    return value


def _decode(data: str) -> str:
    padded = data + "=" * (-len(data) % 4)
    try:
        return base64.urlsafe_b64decode(padded.encode()).decode("utf-8", errors="replace")
    except Exception:
        return ""


def _plain(payload: dict) -> str:
    mime = payload.get("mimeType") or ""
    body = payload.get("body") or {}
    data = body.get("data")
    if mime == "text/plain" and data:
        return _decode(data)
    for part in payload.get("parts") or []:
        text = _plain(part)
        if text:
            return text
    return ""


def _map(raw: dict, account_id: str) -> dict | None:
    if not raw.get("id"):
        return None
    payload = raw.get("payload") or {}
    headers = {h.get("name", "").lower(): h.get("value", "") for h in payload.get("headers") or []}
    subject = headers.get("subject") or "(no subject)"
    body = _plain(payload)
    return {
        "type": "artifact",
        "kind": "email",
        "title": subject,
        "subject": subject,
        "sender": headers.get("from") or "",
        "recipients": [p.strip() for p in (headers.get("to") or "").split(",") if p.strip()],
        "sent_at": headers.get("date") or raw.get("internalDate") or "",
        "body_text": body,
        "body": body,
        "untrusted": True,
        "source_key": f"google:{account_id}:{raw['id']}",
        "classification": "sensitive",
        "authority": "source_imported",
    }
