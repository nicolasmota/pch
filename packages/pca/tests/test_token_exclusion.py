from pathlib import Path

from pca.export import export_archive
from pca.import_ import open_archive


def test_connector_token_excluded_from_export(hub, tmp_path: Path):
    connector = hub.create_connector("google", "calendar")
    secret = "super-secret-refresh-token"
    hub.set_connector_token(connector["id"], secret)
    dest = tmp_path / "space.pca"
    export_archive(hub, dest, "pw")
    opened = open_archive(dest, "pw")
    blob = str(opened["records"]) + str(opened["manifest"]) + str(opened["versions"])
    assert secret not in blob
    assert "connector_token:" not in blob
    assert any(k.startswith("connector_token:") for k in hub.kv_keys())
