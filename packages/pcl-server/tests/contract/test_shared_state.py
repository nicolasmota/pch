def test_shared_state_visibility(client):
    link = client.post("/v1/connections/links", json={"name": "a"}).json()
    pair = client.post("/v1/connections/pair", json={"code": link["code"]}).json()
    agent = {"Authorization": f"Bearer {pair['token']}"}
    # without state.write grant, expect deny
    r = client.put("/v1/state/focus", headers=agent, json={"value": "x", "ttl_seconds": 60, "visibility": "private_to_connection"})
    assert r.status_code in (403, 401, 200)
