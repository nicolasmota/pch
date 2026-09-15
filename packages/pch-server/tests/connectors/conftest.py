from __future__ import annotations

import httpx
import pytest
from pch_server.sync.http import set_client

CALENDAR_ITEM = {
    "id": "evt-1",
    "status": "confirmed",
    "summary": "Atlas planning",
    "start": {"dateTime": "2026-08-24T10:00:00Z"},
    "end": {"dateTime": "2026-08-24T11:00:00Z"},
    "organizer": {"email": "primary"},
}

GMAIL_MESSAGE = {
    "id": "msg-1",
    "payload": {
        "mimeType": "text/plain",
        "headers": [
            {"name": "Subject", "value": "Flight confirmed"},
            {"name": "From", "value": "airline@example.com"},
            {"name": "To", "value": "me@example.com"},
            {"name": "Date", "value": "2026-08-12"},
        ],
        "body": {"data": "RmxpZ2h0IG9uIHRoZSAxMnRo"},
    },
}

GMAIL_MESSAGE_2 = {
    "id": "msg-2",
    "payload": {
        "mimeType": "text/plain",
        "headers": [
            {"name": "Subject", "value": "Hotel booked"},
            {"name": "From", "value": "hotel@example.com"},
            {"name": "To", "value": "me@example.com"},
            {"name": "Date", "value": "2026-08-13"},
        ],
        "body": {"data": "SG90ZWw="},
    },
}


def _handler(request: httpx.Request) -> httpx.Response:
    url = str(request.url)
    if "oauth2.googleapis.com/token" in url:
        return httpx.Response(
            200, json={"access_token": "access", "refresh_token": "refresh", "expires_in": 3600}
        )
    if "calendar/v3" in url:
        if request.url.params.get("syncToken") == "expired":
            return httpx.Response(410, json={"error": {"code": 410}})
        items = [CALENDAR_ITEM]
        if request.url.params.get("syncToken") == "gone":
            items = [{**CALENDAR_ITEM, "status": "cancelled"}]
        return httpx.Response(200, json={"items": items, "nextSyncToken": "tok-2"})
    if url.rstrip("/").endswith("/gmail/v1/users/me/labels"):
        return httpx.Response(
            200,
            json={
                "labels": [
                    {"id": "INBOX", "name": "INBOX", "type": "system"},
                    {"id": "Label_travel", "name": "travel", "type": "user"},
                    {"id": "Label_llm", "name": "LLM", "type": "user"},
                ]
            },
        )
    if url.endswith("/gmail/v1/users/me/messages") or "/users/me/messages?" in url:
        if request.url.params.get("pageToken") == "p2":
            return httpx.Response(200, json={"messages": [{"id": "msg-2"}], "historyId": "h2"})
        return httpx.Response(
            200, json={"messages": [{"id": "msg-1"}], "nextPageToken": "p2", "historyId": "h1"}
        )
    if "/users/me/messages/msg-1" in url:
        return httpx.Response(200, json=GMAIL_MESSAGE)
    if "/users/me/messages/msg-2" in url:
        return httpx.Response(200, json=GMAIL_MESSAGE_2)
    return httpx.Response(404, json={"error": url})


@pytest.fixture(autouse=True)
def google_http(monkeypatch):
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_ID", "test.apps.googleusercontent.com")
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return _handler(request)

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    set_client(client)
    yield seen
    set_client(None)
    client.close()
