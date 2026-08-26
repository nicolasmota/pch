from __future__ import annotations

import importlib
import json
import os
import sys
from typing import Any

MAX_ITEMS_PER_CALL = 100


def _chunks[T](items: list[T], size: int = MAX_ITEMS_PER_CALL) -> list[list[T]]:
    if not items:
        return []
    return [items[i : i + size] for i in range(0, len(items), size)]


def _read() -> dict:
    line = sys.stdin.readline()
    if not line:
        raise EOFError("host closed")
    return json.loads(line)


def _write(message: dict) -> None:
    sys.stdout.write(json.dumps(message, separators=(",", ":")) + "\n")
    sys.stdout.flush()


class PermissionDenied(RuntimeError):
    pass


class HubClient:
    def __init__(self) -> None:
        self._next_id = 1
        self.run_params: dict[str, Any] = {}

    @property
    def account_id(self) -> str:
        return str(self.run_params.get("account_id") or "")

    def _call(self, method: str, params: dict[str, Any] | None = None) -> Any:
        req_id = self._next_id
        self._next_id += 1
        _write({"jsonrpc": "2.0", "id": req_id, "method": method, "params": params or {}})
        while True:
            message = _read()
            if message.get("method") == "plugin.run":
                continue
            if message.get("id") != req_id and "result" not in message and "error" not in message:
                continue
            if message.get("error"):
                err = message["error"]
                if err.get("code") == -32001:
                    raise PermissionDenied(err.get("message") or "denied")
                raise RuntimeError(err.get("message") or "rpc error")
            return message.get("result")

    def items_upsert(self, items: list[dict]) -> Any:
        result: Any = {"ok": True}
        for chunk in _chunks(items, MAX_ITEMS_PER_CALL):
            result = self._call("hub.items.upsert", {"items": chunk})
        return result

    def items_tombstone(self, source_keys: list[str]) -> Any:
        result: Any = {"ok": True}
        for chunk in _chunks(source_keys, MAX_ITEMS_PER_CALL):
            result = self._call("hub.items.tombstone", {"source_keys": chunk})
        return result

    def state_get(self, key: str) -> str | None:
        result = self._call("hub.state.get", {"key": key}) or {}
        return result.get("value")

    def state_set(self, key: str, value: str) -> None:
        self._call("hub.state.set", {"key": key, "value": value})

    def secrets_get(self, name: str) -> str | None:
        result = self._call("hub.secrets.get", {"name": name}) or {}
        return result.get("value")

    def secrets_set(self, name: str, value: str) -> None:
        self._call("hub.secrets.set", {"name": name, "value": value})

    def http_fetch(
        self,
        url: str,
        method: str = "GET",
        headers: dict | None = None,
        body: str | None = None,
    ) -> dict:
        return (
            self._call(
                "hub.http.fetch",
                {"url": url, "method": method, "headers": headers, "body": body},
            )
            or {}
        )

    def oauth_begin(self, provider_hosts: list[str], scopes: list[str]) -> dict:
        return (
            self._call(
                "hub.oauth.begin",
                {"provider_hosts": provider_hosts, "scopes": scopes},
            )
            or {}
        )

    def log(self, message: str, level: str = "info") -> None:
        self._call("hub.log", {"level": level, "message": message})

    def progress(self, done: int, total: int | None = None) -> None:
        self._call("hub.progress", {"done": done, "total": total})


hub = HubClient()


def serve() -> None:
    src = os.environ.get("PCH_PLUGIN_SRC", "")
    entry = os.environ.get("PCH_PLUGIN_ENTRY", "sync:main")
    if src:
        sys.path.insert(0, src)
    message = _read()
    if message.get("method") != "plugin.run":
        raise RuntimeError("expected plugin.run")
    hub.run_params = message.get("params") or {}
    module_name, _, func_name = entry.partition(":")
    module = importlib.import_module(module_name)
    result = getattr(module, func_name or "main")() or {}
    summary = result if isinstance(result, dict) else {}
    _write({"jsonrpc": "2.0", "method": "plugin.done", "params": {"summary": summary}})
