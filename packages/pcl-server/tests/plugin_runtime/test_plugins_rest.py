import pytest


@pytest.mark.plugins
def test_plugins_rest_install_consent_lifecycle(client):
    listed = client.get("/v1/plugins")
    assert listed.status_code == 200
    ids = {row.get("plugin_id") for row in listed.json()}
    assert "pcl.example-rss" in ids
    created = client.post("/v1/plugins", json={"source": "bundled", "plugin_id": "pcl.example-rss"})
    assert created.status_code == 200
    inst_id = created.json()["id"]
    assert created.json()["state"] == "installed"
    preview = client.get(f"/v1/plugins/{inst_id}/consent")
    assert preview.status_code == 200
    assert "RSS" in preview.json()["text"] or "rss" in preview.json()["plugin_id"]
    consented = client.post(f"/v1/plugins/{inst_id}/consent", json={})
    assert consented.status_code == 200
    assert consented.json()["state"] == "enabled"
    paused = client.post(f"/v1/plugins/{inst_id}/pause", json={})
    assert paused.json()["state"] == "paused"
    enabled = client.post(f"/v1/plugins/{inst_id}/enable", json={})
    assert enabled.json()["state"] == "enabled"
    deleted = client.delete(f"/v1/plugins/{inst_id}?purge_data=true")
    assert deleted.status_code == 200


@pytest.mark.plugins
def test_sync_before_consent_fails(client):
    created = client.post("/v1/plugins", json={"source": "bundled", "plugin_id": "pcl.example-rss"})
    inst_id = created.json()["id"]
    res = client.post(f"/v1/plugins/{inst_id}/sync", json={})
    assert res.status_code in {409, 422}
