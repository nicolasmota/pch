from pathlib import Path

from pca.export import export_archive
from pca.import_ import open_archive


def test_plugin_secret_excluded_from_export(hub, tmp_path: Path):
    inst = hub.create_plugin_installation(
        {
            "id": "pcl.example-rss",
            "name": "RSS",
            "description": "d",
            "version": "0.1.0",
            "publisher": "ex",
            "api_version": 1,
            "entry": "sync:main",
            "permissions": {"hosts": ["example.com"], "produces": [{"type": "artifact", "classification": "personal"}]},
        }
    )
    secret = "plugin-super-secret"
    hub.set_plugin_secret(inst["id"], "oauth", secret)
    dest = tmp_path / "space.pca"
    export_archive(hub, dest, "pw")
    opened = open_archive(dest, "pw")
    blob = str(opened["records"]) + str(opened["manifest"]) + str(opened["versions"])
    assert secret not in blob
    assert "plugin_secret:" not in blob
    assert any(k.startswith("plugin_secret:") for k in hub.kv_keys())
