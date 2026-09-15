from urllib.parse import parse_qs, urlparse

import pytest


@pytest.mark.connectors
def test_email_withheld_from_private_ceiling(client):
    created = client.post(
        "/v1/connectors",
        json={"provider": "google", "kind": "email", "selection": {"labels": ["travel"]}},
    ).json()
    qs = parse_qs(urlparse(created["consent_url"]).query)
    client.get("/v1/connectors/oauth/callback", params={"code": "x", "state": qs["state"][0]})
    client.post(f"/v1/connectors/{created['connector_id']}/sync")
    link = client.post("/v1/connections/links", json={"name": "demo"}).json()
    pair = client.post("/v1/connections/pair", json={"code": link["code"]}).json()
    client.post(
        "/v1/grants",
        json={"connection_id": pair["connection_id"], "preset": "read_active_projects"},
    )
    agent = {"Authorization": f"Bearer {pair['token']}"}
    res = client.get("/v1/search", params={"q": "Flight", "purpose": "brief"}, headers=agent)
    statements = [
        r.get("subject") or r.get("title") or r.get("statement")
        for r in res.json().get("results", [])
    ]
    assert "Flight confirmed" not in statements
    assert res.json().get("redactions")
