from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Literal

PinAction = Literal["none", "installed", "skipped_no_uv", "skipped_no_pypi", "failed"]

TOOL_NAME = "personal-context-hub"
# Flip when personal-context-hub is actually on PyPI. Until then, checkout
# launches must not call `uv tool install` against an empty index.
PYPI_RELEASE = False
INSTALLED_LINE = "Installed for offline use. Next time run: pch"
MISSING_UV_LINE = (
    "uv was not found; from a checkout use: make install && uv run pch"
)
REEXEC_FAIL_LINE = "Could not switch to the installed copy; continuing."


def uv_executable() -> str | None:
    return shutil.which("uv")


def uv_tool_dir() -> Path | None:
    uv = uv_executable()
    if uv is None:
        return None
    try:
        result = subprocess.run(
            [uv, "tool", "dir"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError, TimeoutError):
        return None
    if result.returncode != 0:
        return None
    line = (result.stdout or "").strip().splitlines()
    if not line:
        return None
    return Path(line[-1].strip())


def running_from_uv_tool() -> bool:
    tool_dir = uv_tool_dir()
    if tool_dir is None:
        return False
    try:
        prefix = Path(sys.prefix).resolve()
        base = tool_dir.resolve()
        return prefix == base or base in prefix.parents or prefix.is_relative_to(base)
    except (OSError, ValueError):
        return False


def pinned_interpreter() -> Path | None:
    tool_dir = uv_tool_dir()
    if tool_dir is None:
        return None
    posix = tool_dir / TOOL_NAME / "bin" / "python"
    win = tool_dir / TOOL_NAME / "Scripts" / "python.exe"
    if posix.exists():
        return posix
    if win.exists():
        return win
    return None


def ensure_pinned(version: str) -> PinAction:
    if running_from_uv_tool():
        return "none"
    if not PYPI_RELEASE:
        return "skipped_no_pypi"
    uv = uv_executable()
    if uv is None:
        print(MISSING_UV_LINE)
        return "skipped_no_uv"
    try:
        result = subprocess.run(
            [uv, "tool", "install", f"{TOOL_NAME}=={version}"],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.SubprocessError, TimeoutError):
        return "failed"
    if result.returncode == 0:
        print(INSTALLED_LINE)
        return "installed"
    return "failed"


def reexec_into_pinned(argv: list[str]) -> None:
    interp = pinned_interpreter()
    if interp is None:
        print(REEXEC_FAIL_LINE)
        return
    cmd = [str(interp), "-m", "hub_desktop.cli", "--no-pin", *argv]
    if sys.platform == "win32":
        completed = subprocess.run(cmd, check=False)
        raise SystemExit(completed.returncode)
    os.execv(str(interp), cmd)
    raise SystemExit(1)
