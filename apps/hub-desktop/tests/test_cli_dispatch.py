import inspect
from pathlib import Path

import pytest
from hub_desktop import cli
from hub_desktop.cli import LOOPBACK_MSG, main


def test_verbs_route(capsys, monkeypatch, tmp_path: Path):
    monkeypatch.setattr("hub_desktop.cli.ensure_pinned", lambda v: "none")
    monkeypatch.setattr("hub_desktop.doctor.ui_bundled", lambda: True)
    monkeypatch.setattr("hub_desktop.cli.doctor_ok", lambda report: True)
    main(["version"])
    assert "0.2.0" in capsys.readouterr().out
    with pytest.raises(SystemExit) as exited:
        main(["doctor", "--json", "--data-dir", str(tmp_path)])
    assert exited.value.code == 0


def test_no_verb_launches(monkeypatch, tmp_path: Path):
    called: dict = {}
    monkeypatch.setattr("hub_desktop.cli.ensure_pinned", lambda v: "none")
    monkeypatch.setattr("hub_desktop.cli.packaged_app", lambda data_dir, **k: called.setdefault("app", True))
    monkeypatch.setattr(
        "hub_desktop.cli.launch_hub",
        lambda app, host, port, **k: called.setdefault("launch", (host, port, k)),
    )
    main(["--no-pin", "--data-dir", str(tmp_path), "--headless"])
    assert called.get("app") is True
    assert called.get("launch")


def test_refuses_non_loopback(capsys, monkeypatch):
    monkeypatch.setattr("hub_desktop.cli.ensure_pinned", lambda v: "none")
    with pytest.raises(SystemExit) as exited:
        main(["--no-pin", "--host", "0.0.0.0"])
    assert exited.value.code == 2
    assert LOOPBACK_MSG in capsys.readouterr().out


def test_launch_never_prompts():
    source = inspect.getsource(cli)
    assert "input(" not in source
    lower = source.lower()
    assert "api key" not in lower
    assert "create an account" not in lower
    assert "sign up" not in lower


def test_reattach_when_running(monkeypatch, tmp_path: Path):
    opened: list = []
    monkeypatch.setattr("hub_desktop.cli.ensure_pinned", lambda v: "none")
    monkeypatch.setattr("hub_desktop.cli.packaged_app", lambda data_dir, **k: object())
    monkeypatch.setattr("hub_desktop.launch.choose_port", lambda host, port, span=20: (port, True))
    monkeypatch.setattr("hub_desktop.launch.open_ui", lambda url, **k: opened.append(url))
    main(["--no-pin", "--data-dir", str(tmp_path), "--browser"])
    assert opened
