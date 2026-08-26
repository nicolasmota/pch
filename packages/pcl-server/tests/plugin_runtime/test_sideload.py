import base64
from pathlib import Path

import pytest

from pcl_sdk.plugin_kit import cmd_new, cmd_pack


@pytest.mark.plugins
def test_sideload_unverified_warning(client, tmp_path):
    dest = cmd_new("local.demo", tmp_path / "local.demo")
    packed = cmd_pack(dest)
    data = base64.b64encode(Path(packed["path"]).read_bytes()).decode()
    res = client.post("/v1/plugins", json={"source": "sideload", "package_b64": data, "sha256": packed["sha256"]})
    assert res.status_code == 200
    inst_id = res.json()["id"]
    assert res.json()["origin"] == "sideload"
    preview = client.get(f"/v1/plugins/{inst_id}/consent").json()
    assert preview["unverified"] is True
    assert any("nverified" in w.lower() or "side" in w.lower() for w in preview["warnings"])
