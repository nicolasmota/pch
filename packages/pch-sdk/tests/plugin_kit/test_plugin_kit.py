from pathlib import Path

import pytest
from pch_sdk.plugin_kit import cmd_new, cmd_pack, cmd_validate


@pytest.mark.plugins
def test_scaffold_validate_pack(tmp_path: Path):
    dest = cmd_new("kit.demo", tmp_path / "kit.demo")
    assert (dest / "plugin.toml").is_file()
    assert (dest / "src" / "sync.py").is_file()
    report = cmd_validate(dest)
    assert report["ok"] is True
    packed = cmd_pack(dest)
    assert packed["sha256"]
    assert Path(packed["path"]).is_file()


@pytest.mark.plugins
def test_validate_rejects_non_stdlib(tmp_path: Path):
    dest = cmd_new("kit.bad", tmp_path / "kit.bad")
    (dest / "src" / "sync.py").write_text("import requests\n\ndef main():\n    return {}\n")
    with pytest.raises(SystemExit):
        cmd_validate(dest)
