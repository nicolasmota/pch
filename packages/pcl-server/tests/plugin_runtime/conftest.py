from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from pcl_core.service import Hub

os.environ.setdefault("PCH_PLUGIN_SANDBOX", "0")

_HELPERS = Path(__file__).resolve().parent
if str(_HELPERS) not in sys.path:
    sys.path.insert(0, str(_HELPERS))


@pytest.fixture
def plugin_hub(tmp_path: Path):
    hub = Hub(tmp_path / "vault", plain=True)
    hub.setup("Tester")
    yield hub
    hub.close()
