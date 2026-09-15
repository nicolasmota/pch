from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BOARD = ROOT / "frontend" / "src" / "components" / "SituationBoard.tsx"
SETUP = ROOT / "frontend" / "src" / "pages" / "Setup.tsx"

FORBIDDEN_EMPTY = (
    "Create a project or pair an agent",
    "Create a project",
    "Pair an agent",
    "once a project is in play",
)


def test_empty_home_is_capture_not_deferral() -> None:
    board = BOARD.read_text(encoding="utf-8")
    setup = SETUP.read_text(encoding="utf-8")
    text = board + "\n" + setup
    assert "What's in play" in board
    assert "A durable fact" in board
    for phrase in FORBIDDEN_EMPTY:
        assert phrase not in text, phrase
