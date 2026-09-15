import json
from pathlib import Path

import pytest
from hub_desktop.cli import main
from hub_desktop.doctor import doctor_ok, doctor_report


def test_doctor_json_fields(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setattr("hub_desktop.doctor.ui_bundled", lambda: True)
    monkeypatch.setattr("hub_desktop.cli.ensure_pinned", lambda v: "none")
    monkeypatch.setattr("hub_desktop.cli.doctor_ok", lambda report: True)
    with pytest.raises(SystemExit) as exited:
        main(["doctor", "--json", "--data-dir", str(tmp_path)])
    assert exited.value.code == 0
    report = json.loads(capsys.readouterr().out)
    for key in (
        "version",
        "data_dir",
        "encrypted",
        "key_storage",
        "ui_bundled",
        "loopback_only",
        "pinned",
        "pinned_interpreter",
        "sim_enabled",
        "uv",
        "native_window",
        "port",
        "plugin_isolation",
        "plugin_sandbox_backend",
    ):
        assert key in report


def test_doctor_exits_when_ui_missing(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("hub_desktop.doctor.ui_bundled", lambda: False)
    report = doctor_report(tmp_path)
    assert doctor_ok(report) is False
    monkeypatch.setattr("hub_desktop.cli.ensure_pinned", lambda v: "none")
    with pytest.raises(SystemExit) as exited:
        main(["doctor", "--json", "--data-dir", str(tmp_path)])
    assert exited.value.code == 1
