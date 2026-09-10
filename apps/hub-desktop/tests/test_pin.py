import os
from pathlib import Path

import pytest
from hub_desktop import __version__
from hub_desktop.pin import INSTALLED_LINE, ensure_pinned, pinned_interpreter, reexec_into_pinned


def _install_fake_uv(tmp_path: Path, monkeypatch, tool_dir: Path) -> Path:
    log = tmp_path / "uv.log"
    script = tmp_path / "bin"
    script.mkdir()
    uv = script / "uv"
    uv.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        f"open({str(log)!r}, 'a').write(' '.join(sys.argv[1:]) + '\\n')\n"
        "if sys.argv[1:3] == ['tool', 'dir']:\n"
        f"    print({str(tool_dir)!r})\n"
        "raise SystemExit(0)\n"
    )
    uv.chmod(0o755)
    monkeypatch.setenv("PATH", str(script) + os.pathsep + os.environ["PATH"])
    return log


def test_first_launch_installs_once(tmp_path: Path, monkeypatch, capsys):
    tool_dir = tmp_path / "tools"
    tool_dir.mkdir()
    log = _install_fake_uv(tmp_path, monkeypatch, tool_dir)
    monkeypatch.setattr("hub_desktop.pin.running_from_uv_tool", lambda: False)
    action = ensure_pinned(__version__)
    assert action == "installed"
    assert f"tool install personal-context-hub=={__version__}" in log.read_text()
    assert INSTALLED_LINE in capsys.readouterr().out


def test_reexec_into_pinned_interpreter(tmp_path: Path, monkeypatch):
    interp = tmp_path / "python"
    interp.write_text("")
    captured: list[str] = []

    def fake_execv(path, argv):
        captured.extend(argv)
        raise SystemExit(0)

    monkeypatch.setattr("hub_desktop.pin.pinned_interpreter", lambda: interp)
    monkeypatch.setattr("hub_desktop.pin.os.execv", fake_execv)
    monkeypatch.setattr("hub_desktop.pin.sys.platform", "linux")
    with pytest.raises(SystemExit):
        reexec_into_pinned(["serve", "--headless"])
    assert captured[:4] == [str(interp), "-m", "hub_desktop.cli", "--no-pin"]
    assert captured[4:] == ["serve", "--headless"]


def test_no_pin_flag_skips(monkeypatch, tmp_path: Path):
    calls: list[str] = []
    monkeypatch.setattr("hub_desktop.cli.ensure_pinned", lambda v: calls.append(v) or "none")
    monkeypatch.setattr("hub_desktop.cli.cmd_launch", lambda args: None)
    from hub_desktop.cli import main

    main(["--no-pin", "--data-dir", str(tmp_path)])
    assert calls == []


def test_pin_targets_user_tool_dir(tmp_path: Path, monkeypatch):
    tool_dir = tmp_path / "user-tools"
    posix = tool_dir / "personal-context-hub" / "bin"
    posix.mkdir(parents=True)
    python = posix / "python"
    python.write_text("")
    python.chmod(0o755)
    _install_fake_uv(tmp_path, monkeypatch, tool_dir)
    assert str(pinned_interpreter()).startswith(str(tool_dir))
    assert "sudo" not in str(pinned_interpreter())


def test_missing_uv_skips_and_launches(monkeypatch, tmp_path: Path, capsys):
    monkeypatch.setattr("hub_desktop.pin.shutil.which", lambda name: None)
    monkeypatch.setattr("hub_desktop.pin.running_from_uv_tool", lambda: False)
    action = ensure_pinned(__version__)
    assert action == "skipped_no_uv"
    assert "uv was not found" in capsys.readouterr().out
    called = {}
    monkeypatch.setattr("hub_desktop.cli.ensure_pinned", lambda v: "skipped_no_uv")
    monkeypatch.setattr("hub_desktop.cli.packaged_app", lambda *a, **k: object())
    monkeypatch.setattr(
        "hub_desktop.cli.launch_hub",
        lambda *a, **k: called.setdefault("ok", True),
    )
    from hub_desktop.cli import main

    main(["--data-dir", str(tmp_path), "--headless"])
    assert called.get("ok") is True
