from pathlib import Path

import pytest
from hub_desktop.cli import REFUSE_LINE1, REFUSE_LINE2, packaged_app, require_cipher_or_exit


def test_refuses_plaintext_without_writing(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setattr("hub_desktop.cli.cipher_available", lambda: False)
    monkeypatch.delenv("PCH_PLAIN_SQLITE", raising=False)
    with pytest.raises(SystemExit) as exited:
        require_cipher_or_exit(tmp_path)
    assert exited.value.code == 1
    out = capsys.readouterr().out
    assert REFUSE_LINE1 in out
    assert REFUSE_LINE2 in out
    assert not (tmp_path / "vault.db").exists()
    assert not (tmp_path / "blobs").exists()
    assert not (tmp_path / "vault.key").exists()


def test_plain_env_skips_probe(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("hub_desktop.cli.cipher_available", lambda: False)
    monkeypatch.setenv("PCH_PLAIN_SQLITE", "1")
    require_cipher_or_exit(tmp_path)
    app = packaged_app(tmp_path)
    assert app.state.sim_enabled is False
    assert app.state.catalog_refresh is False
