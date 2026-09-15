"""Portable plugin sandbox backends (018). Fails while isolation is bubblewrap-or-reduced only."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from pch_server.plugins import sandbox
from pch_server.plugins.sandbox import (
    isolation_mode,
    sandbox_available,
    sandbox_backend,
    wrap_plugin_command,
)

ROOT = Path(__file__).resolve().parents[4]
HOST = ROOT / "packages" / "pch-server" / "src" / "pch_server" / "plugins" / "host.py"
PLUGINS_DOC = ROOT / "docs" / "guides" / "plugins.md"
GOOGLE_DOC = ROOT / "docs" / "guides" / "google-connectors.md"


def _force_tools(monkeypatch: pytest.MonkeyPatch, present: dict[str, str], *, probe_ok: bool = True) -> None:
    monkeypatch.delenv("PCH_PLUGIN_SANDBOX", raising=False)

    def which(name: str) -> str | None:
        return present.get(name)

    monkeypatch.setattr(sandbox.shutil, "which", which)
    monkeypatch.setattr(
        sandbox.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0 if probe_ok else 1),
    )


def test_bwrap_probe_selects_linux_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    _force_tools(monkeypatch, {"bwrap": "/usr/bin/bwrap", "sandbox-exec": "/usr/bin/sandbox-exec"})
    assert sandbox_backend() == "bwrap"
    assert sandbox_available() is True
    assert isolation_mode() == "sandboxed"


def test_macos_only_is_sandboxed_not_reduced(monkeypatch: pytest.MonkeyPatch) -> None:
    _force_tools(monkeypatch, {"sandbox-exec": "/usr/bin/sandbox-exec"})
    assert sandbox_backend() == "sandbox-exec"
    assert isolation_mode() == "sandboxed"


def test_no_tools_is_reduced(monkeypatch: pytest.MonkeyPatch) -> None:
    _force_tools(monkeypatch, {})
    assert sandbox_backend() == "none"
    assert sandbox_available() is False
    assert isolation_mode() == "reduced"


def test_failed_probe_is_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    _force_tools(monkeypatch, {"bwrap": "/usr/bin/bwrap"}, probe_ok=False)
    assert sandbox_backend() == "none"
    assert isolation_mode() == "reduced"


def test_force_off_even_when_binary_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    _force_tools(monkeypatch, {"bwrap": "/usr/bin/bwrap"})
    monkeypatch.setenv("PCH_PLUGIN_SANDBOX", "0")
    assert sandbox_backend() == "none"
    assert isolation_mode() == "reduced"


def test_wrap_bwrap_unshares_net(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _force_tools(monkeypatch, {"bwrap": "/usr/bin/bwrap"})
    cmd = ["python", "-c", "serve()"]
    env = {"PCH_PLUGIN_SRC": str(tmp_path / "src")}
    wrapped, env_out = wrap_plugin_command(cmd, root=tmp_path, isolation="sandboxed", env=env)
    assert wrapped[0] == "bwrap"
    assert "--unshare-net" in wrapped
    assert "--die-with-parent" in wrapped
    assert env_out["PCH_PLUGIN_SRC"] == "/plugin/src"


def test_wrap_bwrap_binds_host_and_interpreter(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _force_tools(monkeypatch, {"bwrap": "/usr/bin/bwrap"})
    cmd = [sys.executable, "-c", "serve()"]
    wrapped, _env = wrap_plugin_command(cmd, root=tmp_path, isolation="sandboxed", env={})
    assert "--ro-bind-try" in wrapped
    assert "/usr" in wrapped
    assert sys.executable in wrapped
    assert "--dev" in wrapped
    assert "--proc" in wrapped


def _bwrap_namespace_available() -> bool:
    bwrap = shutil.which("bwrap")
    if not bwrap:
        return False
    try:
        result = subprocess.run(
            [
                bwrap,
                "--unshare-net",
                "--die-with-parent",
                "--ro-bind-try",
                "/usr",
                "/usr",
                "/bin/true",
            ],
            capture_output=True,
            timeout=2,
            text=True,
        )
    except OSError:
        return False
    text = f"{result.stderr}{result.stdout}".lower()
    return "not permitted" not in text


@pytest.mark.skipif(not _bwrap_namespace_available(), reason="bwrap cannot create a user namespace here")
def test_live_bwrap_child_runs_and_network_is_unshared(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PCH_PLUGIN_SANDBOX", raising=False)
    (tmp_path / "src").mkdir()
    cmd = [sys.executable, "-c", "import pch_sdk; print('ok')"]
    wrapped, env = wrap_plugin_command(cmd, root=tmp_path, isolation="sandboxed", env=os.environ.copy())
    assert wrapped[0] == "bwrap"
    ran = subprocess.run(wrapped, capture_output=True, text=True, timeout=10, env=env)
    assert ran.returncode == 0, ran.stderr
    assert "ok" in ran.stdout
    net_cmd = [
        sys.executable,
        "-c",
        "import socket; socket.create_connection(('127.0.0.1', 9), 0.4)",
    ]
    net_wrapped, net_env = wrap_plugin_command(
        net_cmd, root=tmp_path, isolation="sandboxed", env=os.environ.copy()
    )
    blocked = subprocess.run(net_wrapped, capture_output=True, text=True, timeout=10, env=net_env)
    assert blocked.returncode != 0


def test_wrap_sandbox_exec_denies_network(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _force_tools(monkeypatch, {"sandbox-exec": "/usr/bin/sandbox-exec"})
    cmd = ["python", "-c", "serve()"]
    env = {"PCH_PLUGIN_SRC": str(tmp_path / "src")}
    wrapped, env_out = wrap_plugin_command(cmd, root=tmp_path, isolation="sandboxed", env=env)
    assert wrapped[0] == "sandbox-exec"
    assert wrapped[1] == "-p"
    assert "(deny network*)" in wrapped[2]
    assert wrapped[-3:] == cmd
    assert env_out["PCH_PLUGIN_SRC"] == str(tmp_path / "src")


def test_wrap_reduced_and_none_are_bare_interpreter(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _force_tools(monkeypatch, {"bwrap": "/usr/bin/bwrap"})
    cmd = ["python", "-c", "serve()"]
    env = {"PCH_PLUGIN_SRC": "src"}
    reduced, env_r = wrap_plugin_command(cmd, root=tmp_path, isolation="reduced", env=env)
    assert reduced == cmd
    assert env_r == env
    monkeypatch.setenv("PCH_PLUGIN_SANDBOX", "0")
    none, env_n = wrap_plugin_command(cmd, root=tmp_path, isolation="sandboxed", env=env)
    assert none == cmd
    assert env_n == env


def test_host_spawn_uses_wrap() -> None:
    text = HOST.read_text(encoding="utf-8")
    assert "wrap_plugin_command" in text


def test_plugin_docs_name_linux_and_macos_not_windows_sandbox() -> None:
    text = PLUGINS_DOC.read_text(encoding="utf-8").lower()
    assert "bubblewrap" in text or "bwrap" in text
    assert "seatbelt" in text or "sandbox-exec" in text
    assert "windows" in text
    assert "appcontainer" not in text
    google = GOOGLE_DOC.read_text(encoding="utf-8").lower()
    assert "the sandboxed import kit" not in google
