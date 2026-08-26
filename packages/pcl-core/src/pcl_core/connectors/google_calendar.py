from __future__ import annotations

from typing import Any

from pcl_core.ids import new_id
from pcl_core.timeutil import now_iso


class GoogleCalendarConnector:
    kind = "calendar"

    def source_key(self, raw: dict[str, Any], account: dict[str, Any]) -> str:
        source_id = raw.get("id") or ""
        return f"google:{account.get('id')}:{source_id}"

    def map_item(self, raw: dict[str, Any], account: dict[str, Any]) -> dict[str, Any] | None:
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
        attendees = [
            a.get("email") or a.get("displayName") or "" for a in raw.get("attendees") or []
        ]
        attendees = [a for a in attendees if a]
        title = raw.get("summary") or "(untitled)"
        now = now_iso()
        return {
            "id": new_id("event"),
            "space_id": "personal",
            "type": "event",
            "title": title,
            "starts_at": starts_at,
            "ends_at": ends_at,
            "all_day": all_day,
            "location": raw.get("location"),
            "attendees": attendees,
            "calendar_id": raw.get("organizer", {}).get("email") or "primary",
            "status": status,
            "source_key": self.source_key(raw, account),
            "source_refs": [account["id"]],
            "classification": "private",
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
