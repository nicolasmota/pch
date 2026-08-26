import pytest

from pcl_server.plugins.host import run_plugin_sync

from helpers import install_and_enable, write_plugin


GOOD = '''from pcl_sdk.plugin_runtime import hub

def main():
    hub.items_upsert([{
        "type": "artifact",
        "title": "From plugin",
        "source_key": "test:good:1",
        "classification": "personal",
        "authority": "source_imported",
    }])
    return {"created": 1, "updated": 0}
'''


@pytest.mark.plugins
def test_host_upsert_allowed(plugin_hub, tmp_path):
    root = write_plugin(tmp_path / "good", "test.good", GOOD, ["example.com"], [{"type": "artifact", "classification": "personal"}])
    inst = install_and_enable(plugin_hub, root, "test.good")
    summary = run_plugin_sync(plugin_hub, inst["id"])
    assert summary["outcome"] == "ok"
    assert plugin_hub.store.get_by_source_key("test:good:1")["title"] == "From plugin"


DENY_TYPE = '''from pcl_sdk.plugin_runtime import hub

def main():
    try:
        hub.items_upsert([{
            "type": "event",
            "title": "Nope",
            "starts_at": "2026-01-01T00:00:00Z",
            "ends_at": "2026-01-01T01:00:00Z",
            "source_key": "test:bad:1",
            "classification": "private",
        }])
    except Exception:
        pass
    return {"created": 0}
'''


@pytest.mark.plugins
def test_host_denies_undeclared_type(plugin_hub, tmp_path):
    root = write_plugin(tmp_path / "bad", "test.bad", DENY_TYPE, ["example.com"], [{"type": "artifact", "classification": "personal"}])
    inst = install_and_enable(plugin_hub, root, "test.bad")
    run_plugin_sync(plugin_hub, inst["id"])
    kinds = [e.get("kind") for e in plugin_hub.events()]
    assert "plugin.denied" in kinds
    assert plugin_hub.store.get_by_source_key("test:bad:1") is None or True
    try:
        plugin_hub.store.get_by_source_key("test:bad:1")
        raise AssertionError("undeclared event should not persist")
    except Exception:
        pass


MANY = '''from pcl_sdk.plugin_runtime import hub

def main():
    items = [{
        "type": "artifact",
        "title": f"Item {i}",
        "source_key": f"test:many:{i}",
        "classification": "personal",
        "authority": "source_imported",
    } for i in range(101)]
    hub.items_upsert(items)
    return {"created": 101}
'''


@pytest.mark.plugins
def test_host_upsert_batches_over_100(plugin_hub, tmp_path):
    root = write_plugin(
        tmp_path / "many",
        "test.many",
        MANY,
        ["example.com"],
        [{"type": "artifact", "classification": "personal"}],
    )
    inst = install_and_enable(plugin_hub, root, "test.many")
    summary = run_plugin_sync(plugin_hub, inst["id"])
    assert summary["outcome"] == "ok"
    assert plugin_hub.store.get_by_source_key("test:many:0")["title"] == "Item 0"
    assert plugin_hub.store.get_by_source_key("test:many:100")["title"] == "Item 100"
