from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
README = ROOT / "README.md"


def _install_section() -> str:
    text = README.read_text()
    assert "## Install" in text
    install = text.split("## Install", 1)[1]
    next_heading = install.find("\n## ")
    assert next_heading != -1
    return install[:next_heading]


def test_readme_install_section():
    section = _install_section()
    assert "uvx personal-context-hub" in section
    assert "uv tool install personal-context-hub" in section
    assert "make install" in section
    assert "uv run pch" in section
    assert "After that, `pch` launches" not in section
    assert "PCH_SIM_ENABLED=1" in section


def test_front_door_names_packaged_install():
    section = _install_section()
    uvx_at = section.find("uvx personal-context-hub")
    clone_at = section.find("make install")
    assert uvx_at != -1
    assert clone_at != -1
    assert uvx_at < clone_at
