import pytest
from pch_core.errors import PolicyDenied
from pch_core.policy.plugin import (
    check_host,
    check_produce,
    manifest_from_snapshot,
    permission_diff,
)
from pch_core.schema.plugin import PluginManifest


def _manifest(**overrides) -> PluginManifest:
    raw = {
        "plugin": {
            "id": "pcl.example-rss",
            "name": "RSS",
            "description": "d",
            "version": "0.1.0",
            "publisher": "ex",
            "api_version": 1,
            "entry": "sync:main",
        },
        "permissions": {
            "hosts": ["example.com"],
            "schedule": "60m",
            "produces": [{"type": "artifact", "classification": "personal"}],
        },
    }
    raw["permissions"].update(overrides)
    return manifest_from_snapshot(raw)


@pytest.mark.plugins
def test_produce_allows_declared_type():
    check_produce(_manifest(), "artifact", None, "personal")


@pytest.mark.plugins
def test_produce_denies_undeclared_type():
    with pytest.raises(PolicyDenied):
        check_produce(_manifest(), "event", None, "private")


@pytest.mark.plugins
def test_host_denies_undeclared():
    with pytest.raises(PolicyDenied):
        check_host(_manifest(), "evil.example")


@pytest.mark.plugins
def test_permission_diff_hosts():
    old = _manifest()
    new = _manifest(hosts=["example.com", "feeds.bbci.co.uk"])
    diff = permission_diff(old, new)
    assert "host:feeds.bbci.co.uk" in diff["added"]
