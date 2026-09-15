def _pair(client, name: str, project_id: str) -> dict:
    link = client.post("/v1/connections/links", json={"name": name}).json()
    pair = client.post("/v1/connections/pair", json={"code": link["code"]}).json()
    client.post(
        "/v1/grants",
        json={
            "connection_id": pair["connection_id"],
            "capabilities": ["project.read", "commitment.read", "memory.retrieve", "profile.read"],
            "selectors": {"project": project_id},
            "classification_ceiling": "private",
        },
    )
    return pair


def _seed_trip(client):
    prj = client.post(
        "/v1/projects",
        json={
            "title": "Europe Trip",
            "charter": "Plan a 10-day travel trip for two. Candidates: Amsterdam and London.",
            "status": "active",
            "operational_phase": "comparing_itineraries",
            "current_step": "rank two remaining itineraries",
            "situation_intent": "choose next itinerary",
        },
    ).json()
    client.post("/v1/goals", json={"title": "Plan 10-day trip for two", "status": "open", "project_id": prj["id"]})
    client.put(
        "/v1/state/trip.phase",
        json={"value": "comparing itineraries", "ttl_seconds": 86400, "visibility": "shared"},
    )
    return prj


def test_two_agents_agree(client):
    prj = _seed_trip(client)
    one = _pair(client, "cursor", prj["id"])
    two = _pair(client, "hermes", prj["id"])
    purpose = {"purpose": "continue planning the trip"}
    a = client.post(
        "/v1/mcp/tools/get_context_contract",
        headers={"Authorization": f"Bearer {one['token']}"},
        json=purpose,
    ).json()
    b = client.post(
        "/v1/mcp/tools/get_context_contract",
        headers={"Authorization": f"Bearer {two['token']}"},
        json=purpose,
    ).json()
    assert a["situation"]["operational_phase"] == "comparing_itineraries"
    assert b["situation"]["operational_phase"] == "comparing_itineraries"
    assert a["situation"]["situation_intent"] == b["situation"]["situation_intent"] == "choose next itinerary"
    assert a["situation"]["status"] == "active"
    handoff_keys = {item["body"].get("key") for item in a["state"]}
    assert "trip.phase" in handoff_keys
    assert a["situation"]["operational_phase"] != "comparing itineraries"


def test_propose_does_not_patch_until_accept(client):
    prj = _seed_trip(client)
    agent = _pair(client, "cursor", prj["id"])
    proposed = client.post(
        "/v1/mcp/tools/propose_operational_state",
        headers={"Authorization": f"Bearer {agent['token']}"},
        json={
            "target_id": prj["id"],
            "operational_phase": "choosing_hotel",
            "situation_intent": "pick a hotel tonight",
        },
    )
    assert proposed.status_code == 200
    body = proposed.json()
    assert body["status"] == "pending"
    assert body["type"] == "operational_proposal"
    live = client.get(f"/v1/projects/{prj['id']}").json()
    assert live["operational_phase"] == "comparing_itineraries"
    assert live["situation_intent"] == "choose next itinerary"

    pending = client.get("/v1/operational-proposals?status=pending").json()
    assert any(row["id"] == body["id"] for row in pending)

    accepted = client.post(f"/v1/operational-proposals/{body['id']}/accept")
    assert accepted.status_code == 200
    live = client.get(f"/v1/projects/{prj['id']}").json()
    assert live["operational_phase"] == "choosing_hotel"
    assert live["situation_intent"] == "pick a hotel tonight"

    again = client.post(
        "/v1/mcp/tools/propose_operational_state",
        headers={"Authorization": f"Bearer {agent['token']}"},
        json={"target_id": prj["id"], "operational_phase": "planning"},
    ).json()
    rejected = client.post(f"/v1/operational-proposals/{again['id']}/reject")
    assert rejected.status_code == 200
    live = client.get(f"/v1/projects/{prj['id']}").json()
    assert live["operational_phase"] == "choosing_hotel"
    conflict = client.post(f"/v1/operational-proposals/{again['id']}/accept")
    assert conflict.status_code == 409
