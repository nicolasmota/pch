"""Hub facade modules (019). Fails while Hub is still one service.py god file."""

from __future__ import annotations

from pathlib import Path

from pch_core.service import Hub

ROOT = Path(__file__).resolve().parents[3]
SERVICE = ROOT / "packages" / "pch-core" / "src" / "pch_core" / "service.py"
HUB = ROOT / "packages" / "pch-core" / "src" / "pch_core" / "hub"


def test_service_facade_has_no_plugin_pairing_or_capture_bodies() -> None:
    text = SERVICE.read_text(encoding="utf-8")
    assert "def mint_link" not in text
    assert "def create_plugin_installation" not in text
    assert "def owner_capture" not in text
    assert len(text.splitlines()) < 220


def test_hub_keeps_public_methods() -> None:
    assert callable(Hub.mint_link)
    assert callable(Hub.create_plugin_installation)
    assert callable(Hub.owner_capture)


def test_named_domain_modules() -> None:
    pairing = (HUB / "pairing.py").read_text(encoding="utf-8")
    plugins = (HUB / "plugins.py").read_text(encoding="utf-8")
    context = (HUB / "context.py").read_text(encoding="utf-8")
    assert "def mint_link" in pairing
    assert "def create_plugin_installation" in plugins
    assert "def owner_capture" in context
