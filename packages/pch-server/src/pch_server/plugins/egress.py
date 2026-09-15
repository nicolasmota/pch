from __future__ import annotations

from urllib.parse import urlparse

import httpx
from pch_core.errors import ValidationFailed

from pch_server.plugins.enforcement import MAX_RESPONSE_BYTES, RunGuard
from pch_server.sync import http as sync_http

FETCH_TIMEOUT = 60.0


def mediated_fetch(guard: RunGuard, method: str, url: str, headers: dict | None = None, body: str | None = None) -> dict:
    guard.check_fetch_url(url)
    verb = method.upper()
    if verb not in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"}:
        raise ValidationFailed(f"unsupported method {method}")
    request_headers = dict(headers or {})
    client = sync_http.client()
    current = url
    for _ in range(5):
        guard.check_fetch_url(current)
        response = client.request(
            verb,
            current,
            headers=request_headers,
            content=body.encode() if body is not None and verb != "GET" else None,
            timeout=FETCH_TIMEOUT,
            follow_redirects=False,
        )
        if response.status_code in {301, 302, 303, 307, 308} and response.headers.get("location"):
            current = str(httpx.URL(current).join(response.headers["location"]))
            if urlparse(current).scheme != "https":
                guard.deny("redirect left https")
            continue
        content = response.content[: MAX_RESPONSE_BYTES + 1]
        truncated = len(content) > MAX_RESPONSE_BYTES
        body_text = content[:MAX_RESPONSE_BYTES].decode("utf-8", errors="replace")
        return {
            "status": response.status_code,
            "headers": {k: v for k, v in response.headers.items() if k.lower() in {"content-type", "etag"}},
            "body": body_text,
            "truncated": truncated,
        }
    raise ValidationFailed("too many redirects")
