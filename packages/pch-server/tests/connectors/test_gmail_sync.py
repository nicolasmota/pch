from urllib.parse import parse_qs, urlparse

import pytest


@pytest.mark.connectors
def test_gmail_selective_import(client):
    created = client.post(
        "/v1/connectors",
        json={"provider": "google", "kind": "email", "selection": {"labels": ["travel"]}},
    )
    assert created.status_code in (200, 202)
    qs = parse_qs(urlparse(created.json()["consent_url"]).query)
    client.get("/v1/connectors/oauth/callback", params={"code": "x", "state": qs["state"][0]})
    cid = created.json()["connector_id"]
    synced = client.post(f"/v1/connectors/{cid}/sync")
    assert synced.status_code == 200
    found = client.get("/v1/search", params={"q": "Flight"})
    arts = [r for r in found.json().get("results", []) if r.get("kind") == "email"]
    assert arts
    assert arts[0]["classification"] == "sensitive"
    assert "html" not in (arts[0].get("body_text") or "").lower()


@pytest.mark.connectors
def test_gmail_unknown_label_fails_sync(client):
    created = client.post(
        "/v1/connectors",
        json={"provider": "google", "kind": "email", "selection": {"labels": ["no-such-label"]}},
    )
    assert created.status_code in (200, 202)
    qs = parse_qs(urlparse(created.json()["consent_url"]).query)
    client.get("/v1/connectors/oauth/callback", params={"code": "x", "state": qs["state"][0]})
    synced = client.post(f"/v1/connectors/{created.json()['connector_id']}/sync")
    assert synced.status_code == 422
    assert "label" in (synced.json().get("detail") or "").lower()


@pytest.mark.connectors
def test_gmail_label_matches_case_insensitive(client, google_http):
    created = client.post(
        "/v1/connectors",
        json={"provider": "google", "kind": "email", "selection": {"labels": ["llm"]}},
    )
    assert created.status_code in (200, 202)
    qs = parse_qs(urlparse(created.json()["consent_url"]).query)
    client.get("/v1/connectors/oauth/callback", params={"code": "x", "state": qs["state"][0]})
    synced = client.post(f"/v1/connectors/{created.json()['connector_id']}/sync")
    assert synced.status_code == 200
    listed = [
        req
        for req in google_http
        if "/users/me/messages" in str(req.url) and "/messages/" not in str(req.url)
    ]
    assert listed
    assert listed[-1].url.params.get("labelIds") == "Label_llm"


@pytest.mark.connectors
def test_gmail_paginates_all_pages(client):
    created = client.post(
        "/v1/connectors",
        json={"provider": "google", "kind": "email", "selection": {"after": "2026-01-01"}},
    )
    assert created.status_code in (200, 202)
    qs = parse_qs(urlparse(created.json()["consent_url"]).query)
    client.get("/v1/connectors/oauth/callback", params={"code": "x", "state": qs["state"][0]})
    synced = client.post(f"/v1/connectors/{created.json()['connector_id']}/sync")
    assert synced.status_code == 200
    found = client.get("/v1/search", params={"q": ""})
    subjects = {
        r.get("subject") or r.get("title")
        for r in found.json().get("results", [])
        if r.get("kind") == "email"
    }
    assert "Flight confirmed" in subjects
    assert "Hotel booked" in subjects


@pytest.mark.connectors
def test_gmail_date_only_query(client, google_http):
    created = client.post(
        "/v1/connectors",
        json={"provider": "google", "kind": "email", "selection": {"after": "2026-01-01"}},
    )
    assert created.status_code in (200, 202)
    qs = parse_qs(urlparse(created.json()["consent_url"]).query)
    client.get("/v1/connectors/oauth/callback", params={"code": "x", "state": qs["state"][0]})
    synced = client.post(f"/v1/connectors/{created.json()['connector_id']}/sync")
    assert synced.status_code == 200
    listed = [
        req
        for req in google_http
        if "/users/me/messages" in str(req.url) and "/messages/" not in str(req.url)
    ]
    assert listed
    assert "after:2026/01/01" in (listed[0].url.params.get("q") or "")
    assert listed[0].url.params.get("labelIds") is None
