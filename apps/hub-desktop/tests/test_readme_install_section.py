from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
README = ROOT / "README.md"


def test_readme_install_section():
    text = README.read_text()
    assert "## Install" in text
    install = text.split("## Install", 1)[1]
    next_heading = install.find("\n## ")
    assert next_heading != -1
    section = install[:next_heading]
    assert len(section.splitlines()) <= 25
    fenced_or_indented = [
        line.strip()
        for line in section.splitlines()
        if "uvx personal-context-hub" in line
    ]
    assert len(fenced_or_indented) == 1
    assert fenced_or_indented[0].strip() == "uvx personal-context-hub"
    above = text.split("## Contributing", 1)[0]
    for banned in ("git clone", "npm", "make install", "uv sync"):
        assert banned not in above
