import pytest
from pch_server.plugins.migrate import migrate_connectors
from pch_server.rest.app import create_app


@pytest.mark.plugins
def test_migration_preserves_source_keys(plugin_hub):
    connector = plugin_hub.create_connector("google", "calendar")
    plugin_hub.patch_connector(connector["id"], {"status": "active"})
    plugin_hub.set_connector_token(connector["id"], '{"access_token":"migrated-token"}')
    key = f"google:{connector['id']}:evt1"
    plugin_hub.apply_connector_items(
        connector["id"],
        [
            {
                "id": "evt_atlas_1",
                "type": "event",
                "title": "Atlas planning",
                "starts_at": "2026-01-01T00:00:00Z",
                "ends_at": "2026-01-01T01:00:00Z",
                "source_key": key,
                "classification": "private",
                "authority": "source_imported",
            }
        ],
    )
    migrated = migrate_connectors(plugin_hub)
    assert migrated
    inst = plugin_hub.get_plugin(migrated[0])
    assert inst["source_account_id"] == connector["id"]
    assert inst["state"] == "enabled"
    assert plugin_hub.get_plugin_secret(inst["id"], "oauth") == '{"access_token":"migrated-token"}'
    found = plugin_hub.store.get_by_source_key(key)
    assert found["title"] == "Atlas planning"
    connector = plugin_hub.store.get(connector["id"])
    assert connector["status"] == "disconnected"


@pytest.mark.plugins
def test_create_app_migrates(plugin_hub):
    connector = plugin_hub.create_connector("google", "calendar")
    plugin_hub.patch_connector(connector["id"], {"status": "active"})
    plugin_hub.set_connector_token(connector["id"], '{"access_token":"x"}')
    create_app(plugin_hub)
    plugins = [p for p in plugin_hub.list_plugins() if p.get("plugin_id") == "pcl.google-calendar"]
    assert plugins
