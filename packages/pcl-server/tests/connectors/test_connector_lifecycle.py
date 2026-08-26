from urllib.parse import parse_qs, urlparse

import pytest


def _activate(client, kind="calendar", selection=None):
    body = {"provider": "google", "kind": kind}
    if selection is not None:
        body["selection"] = selection
    created = client.post("/v1/connectors", json=body)
    assert created.status_code == 200 or created.status_code == 202
    data = created.json()
    qs = parse_qs(urlparse(data["consent_url"]).query)
    cb = client.get("/v1/connectors/oauth/callback", params={"code": "x", "state": qs["state"][0]})
    assert cb.status_code in (200, 303)
    return data["connector_id"]


@pytest.mark.connectors
def test_connector_lifecycle(client):
    cid = _activate(client)
    listed = client.get("/v1/connectors")
    assert listed.status_code == 200
    assert any(c["id"] == cid for c in listed.json())
    patched = client.patch(f"/v1/connectors/{cid}", json={"cadence_minutes": 30})
    assert patched.status_code == 200
    assert patched.json()["cadence_minutes"] == 30
    synced = client.post(f"/v1/connectors/{cid}/sync")
    assert synced.status_code == 200
    paused = client.post(f"/v1/connectors/{cid}/pause")
    assert paused.json()["status"] == "paused"
    resumed = client.post(f"/v1/connectors/{cid}/resume")
    assert resumed.json()["status"] == "active"
    deleted = client.delete(f"/v1/connectors/{cid}")
    assert deleted.status_code == 200
    remaining = client.get("/v1/connectors")
    assert remaining.status_code == 200
    assert all(c["id"] != cid for c in remaining.json())
    assert client.get(f"/v1/connectors/{cid}").status_code == 404


@pytest.mark.connectors
def test_email_empty_selection_rejected(client):
    res = client.post(
        "/v1/connectors", json={"provider": "google", "kind": "email", "selection": {}}
    )
    assert res.status_code == 422


@pytest.mark.connectors
def test_missing_google_client_rejected(client, monkeypatch):
    monkeypatch.delenv("GOOGLE_OAUTH_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_OAUTH_CLIENT_SECRET", raising=False)
    status = client.get("/v1/connectors/oauth/status")
    assert status.json()["configured"] is False
    res = client.post("/v1/connectors", json={"provider": "google", "kind": "calendar"})
    assert res.status_code == 422
    assert "OAuth" in (res.json().get("detail") or "")


@pytest.mark.connectors
def test_save_google_credentials(client, monkeypatch):
    monkeypatch.delenv("GOOGLE_OAUTH_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_OAUTH_CLIENT_SECRET", raising=False)
    saved = client.put(
        "/v1/connectors/oauth/credentials",
        json={
            "client_id": "123-abc.apps.googleusercontent.com",
            "client_secret": "secret",
        },
    )
    assert saved.status_code == 200
    assert saved.json()["configured"] is True
    assert client.get("/v1/connectors/oauth/status").json()["configured"] is True


@pytest.mark.connectors
def test_concurrent_sync_busy(client, monkeypatch):
    cid = _activate(client)
    from pcl_server.sync import scheduler

    scheduler._thread_locks[cid] = True
    try:
        res = client.post(f"/v1/connectors/{cid}/sync")
        assert res.status_code == 409
    finally:
        scheduler._thread_locks.pop(cid, None)
