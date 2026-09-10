from __future__ import annotations

import json
import os
from pathlib import Path

import pcl_server
from pcl_core.service import Hub
from pcl_core.vault.engine import cipher_available
from pcl_core.vault.keys import key_storage

from hub_desktop import __version__
from hub_desktop.launch import choose_port, native_gui_available
from hub_desktop.pin import pinned_interpreter, running_from_uv_tool, uv_executable


def ui_bundled() -> bool:
    return (Path(pcl_server.__file__).resolve().parent / "static" / "index.html").is_file()


def doctor_report(data_dir: Path, port: int = 8765) -> dict:
    plain_requested = os.environ.get("PCH_PLAIN_SQLITE") == "1"
    encrypted = False
    if (data_dir / "vault.db").exists():
        hub = Hub(data_dir, plain=plain_requested)
        encrypted = hub.engine.encrypted
        hub.close()
    else:
        encrypted = cipher_available() and not plain_requested
    pinned = running_from_uv_tool()
    interp = pinned_interpreter()
    native = "native" if native_gui_available() else "browser"
    bound = "127.0.0.1"
    try:
        chosen, _already = choose_port(bound, port)
    except RuntimeError:
        chosen = port
    return {
        "version": __version__,
        "data_dir": str(data_dir),
        "encrypted": encrypted,
        "key_storage": key_storage(data_dir),
        "ui_bundled": ui_bundled(),
        "loopback_only": True,
        "pinned": pinned,
        "pinned_interpreter": str(interp) if interp else None,
        "sim_enabled": False,
        "uv": uv_executable(),
        "native_window": native,
        "port": chosen,
    }


def doctor_ok(report: dict) -> bool:
    plain_requested = os.environ.get("PCH_PLAIN_SQLITE") == "1"
    encrypted_ok = bool(report.get("encrypted")) or plain_requested
    return encrypted_ok and bool(report.get("ui_bundled"))


def print_report(report: dict, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(report, indent=2))
        return
    for key, value in report.items():
        print(f"{key}: {value}")
