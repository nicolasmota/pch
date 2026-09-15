from __future__ import annotations

import os
from pathlib import Path


def plugins_root() -> Path:
    env = os.environ.get("PCH_PLUGINS_DIR")
    if env:
        return Path(env)
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "plugins"
        if candidate.is_dir() and (candidate / "google-calendar").exists():
            return candidate
    return Path.cwd() / "plugins"


def bundled_dir(plugin_id: str) -> Path | None:
    slug = plugin_id.split(".")[-1] if plugin_id.startswith("pcl.") else plugin_id
    mapping = {
        "pcl.google-calendar": "google-calendar",
        "pcl.gmail": "gmail",
        "pcl.example-rss": "example-rss",
        "google-calendar": "google-calendar",
        "gmail": "gmail",
        "example-rss": "example-rss",
    }
    name = mapping.get(plugin_id) or mapping.get(slug)
    if not name:
        return None
    path = plugins_root() / name
    return path if path.is_dir() else None
