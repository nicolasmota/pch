def test_mcp_actions(client):
    link = client.post("/v1/connections/links", json={"name": "a"}).json()
    pair = client.post("/v1/connections/pair", json={"code": link["code"]}).json()
    agent = {"Authorization": f"Bearer {pair['token']}"}
    r = client.post(
        "/v1/mcp/tools/propose_action",
        headers=agent,
        json={"kind": "send", "summary_human": "ping", "payload": {}, "basis_refs": [], "idempotency_key": "k"},
    )
    assert r.status_code == 200
    st = client.post("/v1/mcp/tools/check_action_status", headers=agent, json={"intent_id": r.json()["id"]})
    assert st.json()["status"] == "pending"
