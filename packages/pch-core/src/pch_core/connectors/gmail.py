from __future__ import annotations

import base64
from typing import Any

from pch_core.ids import new_id
from pch_core.timeutil import now_iso


def _decode_body(data: str) -> str:
    padded = data + "=" * (-len(data) % 4)
    try:
        return base64.urlsafe_b64decode(padded.encode()).decode("utf-8", errors="replace")
    except Exception:
        return ""


def extract_plain_text(payload: dict[str, Any]) -> str:
    mime = payload.get("mimeType") or ""
    body = payload.get("body") or {}
    data = body.get("data")
    if mime == "text/plain" and data:
        return _decode_body(data)
    for part in payload.get("parts") or []:
        text = extract_plain_text(part)
        if text:
            return text
    return ""


class GmailConnector:
    kind = "email"

    def source_key(self, raw: dict[str, Any], account: dict[str, Any]) -> str:
        source_id = raw.get("id") or ""
        return f"google:{account.get('id')}:{source_id}"

    def map_item(self, raw: dict[str, Any], account: dict[str, Any]) -> dict[str, Any] | None:
        payload = raw.get("payload") or {}
        headers = {
            h.get("name", "").lower(): h.get("value", "") for h in payload.get("headers") or []
        }
        subject = headers.get("subject") or "(no subject)"
        sender = headers.get("from") or ""
        to = headers.get("to") or ""
        recipients = [p.strip() for p in to.split(",") if p.strip()]
        sent_at = headers.get("date") or raw.get("internalDate") or ""
        body_text = extract_plain_text(payload)
        now = now_iso()
        return {
            "id": new_id("artifact"),
            "space_id": "personal",
            "type": "artifact",
            "kind": "email",
            "title": subject,
            "subject": subject,
            "sender": sender,
            "recipients": recipients,
            "sent_at": sent_at,
            "body_text": body_text,
            "body": body_text,
            "untrusted": True,
            "source_key": self.source_key(raw, account),
            "source_refs": [account["id"]],
            "classification": "sensitive",
            "authority": "source_imported",
            "owner": account.get("owner") or "",
            "labels": [],
            "created_at": now,
            "updated_at": now,
            "confidence": 1.0,
            "retention": {"mode": "until_revoked"},
            "policy_tags": [],
            "version": 1,
        }
