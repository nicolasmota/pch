from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]

pytestmark = pytest.mark.release


def test_tool_install_from_dist(tmp_path: Path) -> None:
    uv = shutil.which("uv")
    if uv is None:
        pytest.skip("uv is required to install from dist")
    static = (
        ROOT
        / "packages"
        / "pch-server"
        / "src"
        / "pch_server"
        / "static"
        / "index.html"
    )
    if not static.is_file():
        pytest.skip("UI static missing; run make frontend first")

    dist = tmp_path / "dist"
    tools = tmp_path / "tools"
    bindir = tmp_path / "bin"
    cache = tmp_path / "cache"
    data = tmp_path / "pch-data"
    dist.mkdir()
    bindir.mkdir()
    env = {
        **os.environ,
        "UV_TOOL_DIR": str(tools),
        "UV_TOOL_BIN_DIR": str(bindir),
        "UV_CACHE_DIR": str(cache),
        "PCH_DATA_DIR": str(data),
    }
    build = subprocess.run(
        [uv, "run", "python", "scripts/build_release.py", str(dist)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert build.returncode == 0, build.stderr
    gate = subprocess.run(
        [uv, "run", "python", "scripts/check_release.py", str(dist)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert gate.returncode == 0, gate.stdout + gate.stderr
    install = subprocess.run(
        [
            uv,
            "tool",
            "install",
            "--python",
            ">=3.12",
            "--find-links",
            str(dist),
            "personal-context-hub",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert install.returncode == 0, install.stdout + install.stderr
    pch = bindir / "pch"
    assert pch.is_file()
    doctor = subprocess.run(
        [str(pch), "doctor", "--json", "--data-dir", str(data)],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert doctor.returncode == 0, doctor.stdout + doctor.stderr
    report = json.loads(doctor.stdout)
    assert report["encrypted"] is True
    assert report["ui_bundled"] is True
    assert data.resolve() != (Path.home() / ".pch").resolve()
