from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
NAV = ROOT / "frontend" / "src" / "nav.ts"


def test_default_nav_hides_marketplace_and_simulator() -> None:
    text = NAV.read_text(encoding="utf-8")
    # Marketplace is a deep link only — never listed in PRIMARY_NAV / ADVANCED_NAV.
    assert 'to: "/marketplace"' not in text
    # Simulator is gated: added to Advanced only when simEnabled is true.
    assert 'to: "/sim"' in text
    assert "if (simEnabled)" in text
    assert 'advanced.unshift({ to: "/sim", label: "Simulator" })' in text
