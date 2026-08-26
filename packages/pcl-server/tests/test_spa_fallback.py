from pathlib import Path

from fastapi.testclient import TestClient

from pcl_core.service import Hub
from pcl_server.rest.app import create_app


def test_ui_routes_survive_refresh(tmp_path: Path):
    hub = Hub(tmp_path, plain=True)
    client = TestClient(create_app(hub))
    static = Path(__file__).resolve().parents[2] / "src" / "pcl_server" / "static" / "index.html"
    if not static.is_file():
        return
    for path in ("/connectors", "/projects", "/export", "/connections"):
        res = client.get(path)
        assert res.status_code == 200, path
        assert "html" in res.headers.get("content-type", "")
    api = client.get("/v1/bootstrap")
    assert api.status_code == 200
    assert "owner_token" in api.json()
