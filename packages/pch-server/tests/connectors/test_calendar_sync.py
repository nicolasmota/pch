from urllib.parse import parse_qs, urlparse

import pytest


def _activate(client):
    created = client.post("/v1/connectors", json={"provider": "google", "kind": "calendar"}).json()
    qs = parse_qs(urlparse(created["consent_url"]).query)
    client.get("/v1/connectors/oauth/callback", params={"code": "x", "state": qs["state"][0]})
    return created["connector_id"]


@pytest.mark.connectors
def test_calendar_sync_dedup_and_audit(client):
    cid = _activate(client)
    first = client.post(f"/v1/connectors/{cid}/sync")
    assert first.status_code == 200
    second = client.post(f"/v1/connectors/{cid}/sync")
    assert second.status_code == 200
    events = client.get("/v1/search", params={"q": "Atlas", "type": "event"})
    titles = [r.get("title") for r in events.json().get("results", [])]
    assert titles.count("Atlas planning") == 1
    audit = client.get("/v1/events")
    kinds = [e.get("kind") for e in audit.json()]
    assert "connector.sync" in kinds
    assert "connector.connected" in kinds


@pytest.mark.connectors
def test_calendar_sync_token_expiry_resyncs(client):
    cid = _activate(client)
    client.post(f"/v1/connectors/{cid}/sync")
    client.patch(f"/v1/connectors/{cid}", json={"sync_cursor": "expired"})
    res = client.post(f"/v1/connectors/{cid}/sync")
    assert res.status_code == 200
    events = client.get("/v1/search", params={"q": "Atlas", "type": "event"})
    assert events.json().get("results")
