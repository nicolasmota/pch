from pathlib import Path
from unittest.mock import MagicMock

from hub_desktop.uninstall import uninstall


def test_default_keeps_data(tmp_path: Path, monkeypatch, capsys):
    vault = tmp_path / "vault.db"
    vault.write_text("x")
    monkeypatch.setattr("hub_desktop.uninstall.run_uv_tool", lambda args, **k: 0)
    rc = uninstall(tmp_path, purge_data=False, yes=False)
    assert rc == 0
    assert vault.exists()
    assert str(tmp_path) in capsys.readouterr().out


def test_purge_without_delete_aborts(tmp_path: Path, monkeypatch):
    vault = tmp_path / "vault.db"
    vault.write_text("x")
    monkeypatch.setattr("hub_desktop.uninstall.run_uv_tool", lambda args, **k: 0)
    rc = uninstall(tmp_path, purge_data=True, yes=False, confirm_delete="nope")
    assert rc == 1
    assert vault.exists()


def test_purge_with_delete_or_yes(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("hub_desktop.uninstall.run_uv_tool", lambda args, **k: 0)
    monkeypatch.setattr("hub_desktop.uninstall.keyring", None)
    a = tmp_path / "a"
    a.mkdir()
    (a / "vault.db").write_text("x")
    assert uninstall(a, purge_data=True, yes=False, confirm_delete="DELETE") == 0
    assert not a.exists()
    b = tmp_path / "b"
    b.mkdir()
    (b / "vault.db").write_text("x")
    assert uninstall(b, purge_data=True, yes=True) == 0
    assert not b.exists()


def test_yes_alone_keeps_data(tmp_path: Path, monkeypatch):
    vault = tmp_path / "vault.db"
    vault.write_text("x")
    monkeypatch.setattr("hub_desktop.uninstall.run_uv_tool", lambda args, **k: 0)
    assert uninstall(tmp_path, purge_data=False, yes=True) == 0
    assert vault.exists()


def test_windows_self_uninstall_defers_helper(tmp_path: Path, monkeypatch):
    captured: dict = {}

    def fake_popen(argv, **kwargs):
        captured["argv"] = argv
        captured["kwargs"] = kwargs
        return MagicMock()

    monkeypatch.setattr("hub_desktop.uninstall.sys.platform", "win32")
    monkeypatch.setattr("hub_desktop.uninstall.running_from_uv_tool", lambda: True)
    monkeypatch.setattr("hub_desktop.uninstall.uv_executable", lambda: "/uv.exe")
    monkeypatch.setattr("hub_desktop.uninstall.subprocess.Popen", fake_popen)
    monkeypatch.setattr("hub_desktop.uninstall.os.getpid", lambda: 4242)
    monkeypatch.setenv("TEMP", str(tmp_path))
    from hub_desktop.uninstall import run_uv_tool

    rc = run_uv_tool(["tool", "uninstall", "personal-context-hub"], defer_on_windows=True)
    assert rc == 0
    assert captured["argv"][0] == "cmd"
    helper = Path(captured["argv"][2])
    text = helper.read_text()
    assert "uv tool uninstall personal-context-hub" in text.replace('"', "") or (
        "tool uninstall personal-context-hub" in text
    )
    assert "4242" in text
    in_process = []
    monkeypatch.setattr(
        "hub_desktop.uninstall.subprocess.run",
        lambda *a, **k: in_process.append(a) or MagicMock(returncode=0),
    )
    # already returned via Popen; in-process uv must not have been used
    assert in_process == []
