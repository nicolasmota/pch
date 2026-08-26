def test_catalog_and_recipe(client):
    listed = client.get("/v1/catalog/assistants")
    assert listed.status_code == 200
    ids = [a["id"] for a in listed.json()]
    assert "cursor" in ids
    link = client.post("/v1/connections/links", json={"name": "cursor"}).json()
    recipe = client.post(
        f"/v1/connections/{link['connection_id']}/recipe",
        json={"assistant": "cursor"},
    )
    assert recipe.status_code == 200
    body = recipe.json()
    assert "pcl-sdk" in str(body["snippet"])
    assert body["snippet"]["mcpServers"]["personal-context-hub"]["env"]["PCH_TOKEN"]
    events = client.get("/v1/events").json()
    assert any(e.get("kind") == "connection.recipe_issued" for e in events)
    bad = client.post(
        f"/v1/connections/{link['connection_id']}/recipe",
        json={"assistant": "not-a-real-agent"},
    )
    assert bad.status_code == 422
