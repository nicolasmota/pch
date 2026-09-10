from pathlib import Path

from fastapi.testclient import TestClient
from hub_desktop.cli import packaged_app


def test_first_launch_writes_nothing(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PCH_PLAIN_SQLITE", "1")
    app = packaged_app(tmp_path)
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        hub = app.state.hub
        assert hub.list() == []
        assert hub.ledger.list_events() == []
        assert hub.connections() == []
        assert hub.list("proposal") == []
        assert hub._kv_get("marketplace_catalog") is None
    names = set(p.name for p in tmp_path.iterdir())
    assert names <= {"vault.db", "blobs", "vault.key"}
    blobs = tmp_path / "blobs"
    if blobs.exists():
        assert list(blobs.iterdir()) == []
    assert not (tmp_path / "_sim").exists()
