from pathlib import Path

from pca.export import export_archive
from pca.import_ import open_archive


def test_filter_and_no_secrets(hub, tmp_path: Path):
    p = hub.create("project", {"title": "A", "status": "active"})
    hub.create("project", {"title": "B", "status": "active"})
    dest = tmp_path / "f.pca"
    export_archive(hub, dest, "pw", {"projects": [p["id"]]})
    opened = open_archive(dest, "pw")
    titles = [r.get("title") for r in opened["records"] if r.get("type") == "project"]
    assert "B" not in titles
    types = {r.get("type") for r in opened["records"]}
    assert "grant" not in types
    assert "connection" not in types
    assert "shared_state" not in types
