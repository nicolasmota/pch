from pathlib import Path

from hub_desktop.cli import packaged_app
from pch_core.vault.engine import Engine


def test_packaged_entry_never_plain(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("PCH_PLAIN_SQLITE", raising=False)
    seen: list[Engine] = []
    original = Engine.__init__

    def wrapped(self, path, key, *, plain=None):
        original(self, path, key, plain=plain)
        seen.append(self)

    monkeypatch.setattr(Engine, "__init__", wrapped)
    packaged_app(tmp_path)
    assert len(seen) == 1
    assert seen[0].encrypted is True
    assert not (tmp_path / "_sim").exists()
