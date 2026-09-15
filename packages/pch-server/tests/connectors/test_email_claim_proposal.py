from urllib.parse import parse_qs, urlparse

import pytest


@pytest.mark.connectors
def test_email_claim_lands_in_review_queue(client):
    created = client.post(
        "/v1/connectors",
        json={"provider": "google", "kind": "email", "selection": {"labels": ["travel"]}},
    ).json()
    qs = parse_qs(urlparse(created["consent_url"]).query)
    client.get("/v1/connectors/oauth/callback", params={"code": "x", "state": qs["state"][0]})
    client.post(f"/v1/connectors/{created['connector_id']}/sync")
    arts = client.get("/v1/search", params={"q": "Flight"}).json()["results"]
    email = next(r for r in arts if r.get("kind") == "email")
    link = client.post("/v1/connections/links", json={"name": "demo"}).json()
    pair = client.post("/v1/connections/pair", json={"code": link["code"]}).json()
    client.post(
        "/v1/grants",
        json={
            "connection_id": pair["connection_id"],
            "preset": "read_active_projects",
            "classification_ceiling": "sensitive",
        },
    )
    agent = {"Authorization": f"Bearer {pair['token']}"}
    proposed = client.post(
        "/v1/mcp/tools/propose_memory",
        headers=agent,
        json={
            "memory": {
                "statement": "Flight confirmed for the 12th",
                "kind": "semantic",
                "sensitivity_flags": ["financial"],
            },
            "evidence_refs": [email["id"]],
        },
    )
    assert proposed.status_code == 200
    queue = client.get("/v1/memories/proposals?status=pending")
    assert queue.status_code == 200
    statements = [
        (p.get("proposed_memory") or {}).get("statement") or p.get("statement")
        for p in queue.json()
    ]
    assert any("Flight confirmed" in (s or "") for s in statements)
    memories = client.get("/v1/memories").json()
    assert all("Flight confirmed for the 12th" != m.get("statement") for m in memories)
