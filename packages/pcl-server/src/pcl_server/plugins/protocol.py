from __future__ import annotations

import json
from typing import Any

from pcl_core.errors import PolicyDenied, ValidationFailed
from pcl_core.service import Hub

from pcl_server.plugins.egress import mediated_fetch
from pcl_server.plugins.enforcement import RunGuard

API_VERSION = 1


class ProtocolError(Exception):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def encode(message: dict) -> bytes:
    return (json.dumps(message, separators=(",", ":")) + "\n").encode()


def decode_line(line: str) -> dict:
    return json.loads(line)


def dispatch(hub: Hub, guard: RunGuard, method: str, params: dict[str, Any]) -> Any:
    installation_id = guard.installation["id"]
    try:
        if method == "hub.items.upsert":
            items = guard.check_upsert(list(params.get("items") or []))
            summary = hub.apply_plugin_items(installation_id, items, [])
            guard.created += int(summary.get("created") or 0)
            guard.updated += int(summary.get("updated") or 0)
            return {"ok": True, "summary": summary}
        if method == "hub.items.tombstone":
            keys = [str(k) for k in (params.get("source_keys") or [])]
            summary = hub.apply_plugin_items(installation_id, [], keys)
            guard.tombstoned += int(summary.get("tombstoned") or 0)
            return {"ok": True, "summary": summary}
        if method == "hub.state.get":
            return {"value": hub.get_plugin_state_value(installation_id, str(params.get("key") or ""))}
        if method == "hub.state.set":
            value = str(params.get("value") or "")
            guard.check_state_size(value)
            hub.set_plugin_state_value(installation_id, str(params.get("key") or ""), value)
            return {"ok": True}
        if method == "hub.secrets.get":
            guard.check_secrets()
            return {"value": hub.get_plugin_secret(installation_id, str(params.get("name") or ""))}
        if method == "hub.secrets.set":
            guard.check_secrets()
            hub.set_plugin_secret(installation_id, str(params.get("name") or ""), str(params.get("value") or ""))
            return {"ok": True}
        if method == "hub.http.fetch":
            return mediated_fetch(
                guard,
                str(params.get("method") or "GET"),
                str(params.get("url") or ""),
                params.get("headers"),
                params.get("body"),
            )
        if method == "hub.oauth.begin":
            guard.check_secrets()
            from pcl_server.sync.oauth import start_consent

            kind = "calendar" if "calendar" in " ".join(params.get("scopes") or []) else "email"
            url = start_consent(hub, installation_id, kind)
            return {"consent_url": url, "status": "pending"}
        if method == "hub.log":
            return {"ok": True}
        if method == "hub.progress":
            return {"ok": True}
        raise ProtocolError(-32601, f"unknown method {method}")
    except PolicyDenied as exc:
        raise ProtocolError(-32001, exc.detail) from exc
    except ValidationFailed as exc:
        code = -32002 if "exceeds" in exc.detail or "at most" in exc.detail else -32602
        raise ProtocolError(code, exc.detail) from exc
