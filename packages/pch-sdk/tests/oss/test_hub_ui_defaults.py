from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
NAV = ROOT / "frontend" / "src" / "nav.ts"


def test_default_nav_hides_marketplace_and_simulator() -> None:
    text = NAV.read_text(encoding="utf-8")
    assert 'to: "/marketplace"' in text
    assert 'to: "/sim"' in text
    assert 'if (item.to === "/marketplace") return false' in text
    assert 'if (item.to === "/sim") return simEnabled' in text
