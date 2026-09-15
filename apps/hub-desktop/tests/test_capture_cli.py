from __future__ import annotations

from pathlib import Path

import pytest
from hub_desktop.cli import main
from pch_core.service import Hub


def _open(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("PCH_PLAIN_SQLITE", "1")
    monkeypatch.setattr("hub_desktop.cli.require_cipher_or_exit", lambda data_dir: None)
    hub = Hub(tmp_path, plain=True)
    hub.setup("Tester")
    hub.close()
    return tmp_path


def test_capture_cli_starts_then_attaches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys):
    data_dir = _open(tmp_path, monkeypatch)
    main(
        [
            "--no-pin",
            "capture",
            "--data-dir",
            str(data_dir),
            "--title",
            "Europe trip",
            "ten-day trip for two",
        ]
    )
    out = capsys.readouterr().out
    assert "Europe trip" in out
    main(
        [
            "--no-pin",
            "capture",
            "--data-dir",
            str(data_dir),
            "Amsterdam is the live city",
        ]
    )
    hub = Hub(data_dir, plain=True)
    try:
        sit = hub.current_situation()
        statements = [
            item["body"]["statement"] for item in sit["contract"]["memories"]
        ]
        assert sit["project"]["title"] == "Europe trip"
        assert "ten-day trip for two" in statements
        assert "Amsterdam is the live city" in statements
        assert hub.list("proposal") == []
    finally:
        hub.close()


def test_capture_cli_incomplete_writes_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    data_dir = _open(tmp_path, monkeypatch)
    with pytest.raises(SystemExit) as err:
        main(["--no-pin", "capture", "--data-dir", str(data_dir), "--title", "Europe trip"])
    assert err.value.code not in (0, None)
    hub = Hub(data_dir, plain=True)
    try:
        assert hub.list("project") == []
        assert hub.list("memory") == []
    finally:
        hub.close()
