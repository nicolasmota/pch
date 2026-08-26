from pathlib import Path

from pcl_core.service import Hub


def test_vault_persists(tmp_path: Path):
    d = tmp_path / "v"
    h = Hub(d, plain=True)
    h.setup("A")
    p = h.create("project", {"title": "Atlas", "charter": "ship", "status": "active"})
    h.close()
    h2 = Hub(d, plain=True)
    got = h2.get(p["id"])
    assert got["title"] == "Atlas"
    h2.close()


def test_sqlcipher_row_factory(tmp_path: Path):
    h = Hub(tmp_path / "cipher", plain=False)
    h.setup("Nick")
    assert h.setup_status()["initialized"] is True
    assert h.owner_token
    h.close()
