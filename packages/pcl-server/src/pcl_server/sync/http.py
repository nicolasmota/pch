from __future__ import annotations

import httpx

_client: httpx.Client | None = None


def client() -> httpx.Client:
    global _client
    if _client is None:
        _client = httpx.Client(timeout=30.0)
    return _client


def set_client(value: httpx.Client | None) -> None:
    global _client
    _client = value
