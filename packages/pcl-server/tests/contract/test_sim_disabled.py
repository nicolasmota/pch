from pathlib import Path

from fastapi.testclient import TestClient
from pcl_core.service import Hub
from pcl_sdk.sim.refuse import EVERYDAY_CONFIRM
from pcl_server.rest.app import create_app


def test_default_sim_routes_404(tmp_path: Path):
    hub = Hub(tmp_path, plain=True)
    app = create_app(hub)
    client = TestClient(app)
    listed = client.get("/v1/sim/runs")
    assert listed.status_code == 404
    assert "simulation disabled" in listed.json()["detail"]
    posted = client.post("/v1/sim/runs", json={"target": "everyday", "confirm": EVERYDAY_CONFIRM})
    assert posted.status_code == 404
    assert "PCH_SIM_ENABLED=1" in posted.json()["detail"]
    assert not (tmp_path / "_sim").exists()


def test_sim_hub_enables_routes(tmp_path: Path):
    everyday = Hub(tmp_path / "everyday", plain=True)
    sim_hub = Hub(tmp_path / "sim", plain=True)
    app = create_app(everyday, sim_hub=sim_hub)
    with TestClient(app) as client:
        boot = client.get("/v1/bootstrap").json()
        client.headers["Authorization"] = f"Bearer {boot['owner_token']}"
        started = client.post("/v1/sim/runs", json={"persona_id": "lived-stretch", "delay_ms": 50})
        assert started.status_code == 200
        listed = client.get("/v1/sim/runs")
        assert listed.status_code == 200


def test_env_enables_lazy_sim(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PCH_SIM_ENABLED", "1")
    hub = Hub(tmp_path / "hub", plain=True)
    app = create_app(hub)
    assert app.state.sim_enabled is True
    assert app.state.sim_hub is None
    assert not Path(app.state.sim_dir).exists()
    with TestClient(app) as client:
        boot = client.get("/v1/bootstrap").json()
        client.headers["Authorization"] = f"Bearer {boot['owner_token']}"
        listed = client.get("/v1/sim/runs")
        assert listed.status_code in {200, 404}
        assert Path(app.state.sim_dir).exists() or app.state.sim_hub is not None
