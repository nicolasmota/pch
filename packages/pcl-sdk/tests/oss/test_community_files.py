"""SC-003 / SC-005: community health files, README, templates, licenses, CI."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

PYPROJECTS = [
    ROOT / "packages" / "pcl-core" / "pyproject.toml",
    ROOT / "packages" / "pcl-server" / "pyproject.toml",
    ROOT / "packages" / "pcl-sdk" / "pyproject.toml",
    ROOT / "packages" / "pca" / "pyproject.toml",
    ROOT / "apps" / "hub-desktop" / "pyproject.toml",
]


def test_license_file_is_mit() -> None:
    text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "MIT License" in text or "Permission is hereby granted" in text
    assert "WITHOUT WARRANTY" in text.upper() or "AS IS" in text


def test_package_licenses_are_mit() -> None:
    for path in PYPROJECTS:
        text = path.read_text(encoding="utf-8")
        assert 'license = "MIT"' in text or "license = { text = \"MIT\" }" in text, path


def test_required_community_docs_exist() -> None:
    for name in ("SECURITY.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "LICENSE"):
        assert (ROOT / name).is_file(), name


def test_readme_front_door() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    lower = text.lower()
    assert "local" in lower and ("~/.pch" in text or "your device" in lower)
    assert "uvx personal-context-hub" in text
    assert "MIT" in text or "LICENSE" in text
    assert "CONTRIBUTING" in text
    assert "SECURITY" in text
    assert "CODE_OF_CONDUCT" in text or "Code of Conduct" in text


def test_templates_warn_against_secrets() -> None:
    bug = ROOT / ".github" / "ISSUE_TEMPLATE" / "bug.yml"
    pr = ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md"
    assert bug.is_file()
    assert pr.is_file()
    for path in (bug, pr):
        text = path.read_text(encoding="utf-8").lower()
        hits = sum(
            1
            for token in ("vault", ".env", "oauth", "pairing", "mcp.json")
            if token in text
        )
        umbrella = "vault data, tokens, or oauth" in text or "oauth client" in text
        assert hits >= 3 or umbrella, path


def test_ci_workflow_runs_gates() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "check-secrets" in ci or "check_secrets" in ci
    assert re.search(r"\blint\b", ci)
    assert re.search(r"\btest\b", ci)


def test_gitignore_covers_hub_data_dirs() -> None:
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".pch/" in text or ".pch" in text
    assert ".pch-sim/" in text or ".pch-sim" in text
    assert "pairing_token" in text
