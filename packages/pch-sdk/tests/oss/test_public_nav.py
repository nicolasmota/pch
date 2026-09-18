from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
NAV = ROOT / "frontend" / "src" / "nav.ts"
SIDEBAR = ROOT / "frontend" / "src" / "components" / "Sidebar.tsx"
CONNECTIONS = ROOT / "frontend" / "src" / "pages" / "Connections.tsx"
PAIR = ROOT / "docs" / "guides" / "pair-an-agent.md"
HUB_UI = ROOT / "docs" / "guides" / "the-hub-ui.md"
GOOGLE = ROOT / "docs" / "guides" / "google-connectors.md"
GETTING_STARTED = ROOT / "docs" / "getting-started.md"

FORBIDDEN_DEFAULT_LABELS = (
    'label: "Access"',
    'label: "Handoff"',
    'label: "Conflicts"',
    'label: "Approvals"',
    'label: "Marketplace"',
    'label: "Connectors"',
)


def test_default_nav_is_home_agents_review() -> None:
    text = NAV.read_text(encoding="utf-8")
    assert 'label: "Home"' in text
    assert 'label: "Agents"' in text
    assert 'label: "Review"' in text
    for label in FORBIDDEN_DEFAULT_LABELS:
        assert label not in text, label
    assert "collapsible" in text
    assert 'heading: "Advanced"' in text
    assert 'to: "/projects"' in text
    assert 'to: "/audit"' in text
    assert 'to: "/plugins"' in text
    assert 'to: "/handoff"' not in text
    assert 'to: "/access"' not in text
    assert 'to: "/connectors"' not in text


def test_sidebar_collapses_advanced() -> None:
    text = SIDEBAR.read_text(encoding="utf-8")
    assert "aria-expanded" in text
    assert "Advanced" in text


def test_agents_page_lists_grants() -> None:
    text = CONNECTIONS.read_text(encoding="utf-8")
    assert 'title="Agents"' in text
    assert 'title="Connections"' not in text
    assert "/v1/grants" in text
    assert "No grants yet." in text


def test_pairing_docs_do_not_require_access_page() -> None:
    pair = PAIR.read_text(encoding="utf-8")
    hub = HUB_UI.read_text(encoding="utf-8")
    assert "Open **Access**" not in pair
    assert "Agents** + **Access**" not in hub
    assert "Advanced" in hub


def test_connectors_is_deep_link_not_nav() -> None:
    hub = HUB_UI.read_text(encoding="utf-8")
    google = GOOGLE.read_text(encoding="utf-8")
    started = GETTING_STARTED.read_text(encoding="utf-8")
    assert "| `/connectors` |" in hub
    assert "Deep links" in hub
    assert "Use the Connectors page for Calendar/Gmail day to day" not in google
    assert "Then **Connectors** in the UI" not in started
    assert "Plugins" in started
