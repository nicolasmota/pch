import socket
from pathlib import Path

from fastapi.testclient import TestClient
from hub_desktop.cli import packaged_app


class LoopbackSocket(socket.socket):
    def connect(self, addr):
        host = addr[0] if isinstance(addr, tuple) else addr
        if isinstance(host, bytes):
            host = host.decode()
        if host not in {"127.0.0.1", "::1", "localhost"} and not str(host).startswith("127."):
            raise AssertionError(f"non-loopback connect {addr}")
        return super().connect(addr)


def test_001_scenarios_offline(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PCH_PLAIN_SQLITE", "1")
    monkeypatch.setattr(socket, "socket", LoopbackSocket)
    app = packaged_app(tmp_path)
    with TestClient(app) as client:
        boot = client.get("/v1/bootstrap").json()
        client.headers["Authorization"] = f"Bearer {boot['owner_token']}"
        setup = client.post("/v1/setup", json={"name": "Offline"})
        assert setup.status_code == 200
        project = client.post("/v1/projects", json={"title": "Atlas", "status": "active"})
        assert project.status_code == 200
        found = client.get("/v1/search", params={"q": "Atlas"})
        assert found.json()["results"]


def test_004_situation_package_offline(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PCH_PLAIN_SQLITE", "1")
    monkeypatch.setattr(socket, "socket", LoopbackSocket)
    app = packaged_app(tmp_path)
    with TestClient(app) as client:
        boot = client.get("/v1/bootstrap").json()
        client.headers["Authorization"] = f"Bearer {boot['owner_token']}"
        client.post("/v1/setup", json={"name": "Offline"})
        prj = client.post("/v1/projects", json={"title": "Atlas", "status": "active"}).json()
        link = client.post("/v1/connections/links", json={"name": "agent"}).json()
        pair = client.post("/v1/connections/pair", json={"code": link["code"]}).json()
        client.post(
            "/v1/grants",
            json={
                "connection_id": pair["connection_id"],
                "preset": "read_project",
                "selectors": {"project": prj["id"]},
            },
        )
        man = client.post(
            "/v1/mcp/tools/get_context_manifest",
            headers={"Authorization": f"Bearer {pair['token']}"},
            json={
                "purpose": "test",
                "requested_capabilities": ["project.read"],
                "selectors": {"project": prj["id"]},
            },
        )
        assert man.status_code == 200
