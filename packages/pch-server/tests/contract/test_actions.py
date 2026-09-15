def test_action_idempotency(client):
    link = client.post("/v1/connections/links", json={"name": "a"}).json()
    pair = client.post("/v1/connections/pair", json={"code": link["code"]}).json()
    agent = {"Authorization": f"Bearer {pair['token']}"}
    body = {"kind": "send_message", "summary_human": "email Jane", "payload": {}, "basis_refs": [], "idempotency_key": "abc"}
    a = client.post("/v1/actions/intents", headers=agent, json=body).json()
    b = client.post("/v1/actions/intents", headers=agent, json=body).json()
    assert a["id"] == b["id"]
    pending = client.get("/v1/approvals?status=pending").json()
    assert pending
    client.post(f"/v1/approvals/{a['id']}/decide", json={"decision": "approved"})
