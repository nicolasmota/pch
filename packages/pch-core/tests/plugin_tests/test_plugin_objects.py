import pytest


@pytest.mark.plugins
def test_plugin_install_consent_and_items(hub):
    inst = hub.create_plugin_installation(
        {
            "id": "pcl.example-rss",
            "name": "RSS",
            "description": "d",
            "version": "0.1.0",
            "publisher": "ex",
            "api_version": 1,
            "entry": "sync:main",
            "permissions": {
                "secrets": False,
                "schedule": "manual",
                "hosts": ["example.com"],
                "produces": [{"type": "artifact", "classification": "personal"}],
            },
        }
    )
    assert inst["state"] == "installed"
    hub.consent_plugin(inst["id"])
    assert hub.get_plugin(inst["id"])["state"] == "enabled"
    hub.set_plugin_secret(inst["id"], "oauth", "secret-token")
    summary = hub.apply_plugin_items(
        inst["id"],
        [
            {
                "type": "artifact",
                "title": "Hello",
                "source_key": "rss:1",
                "classification": "personal",
            }
        ],
    )
    assert summary["created"] == 1
    found = hub.store.get_by_source_key("rss:1")
    assert f"plugin:{inst['id']}" in found["source_refs"]
    events = [e for e in hub.events() if e.get("kind") == "plugin.sync"]
    assert events
    hub.remove_plugin(inst["id"], purge_data=True)
    assert hub.store.get_by_source_key("rss:1") is None
    assert hub.store.get_by_source_key("rss:1", include_deleted=True) is not None
