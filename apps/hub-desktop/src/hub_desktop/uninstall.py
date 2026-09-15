from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import keyring
except Exception:
    keyring = None

from pch_core.vault.keys import ACCOUNT, SERVICE

from hub_desktop.pin import PYPI_RELEASE, TOOL_NAME, running_from_uv_tool, uv_executable

UNTOUCHED = (
    "Removed the Hub program. Your data is untouched at {data_dir} (vault.db, blobs/, "
    "vault.salt or vault.key,\nplugins/). To also delete your data: pch uninstall --purge-data"
)
WINDOWS_DEFER = "The program will be removed after this window closes."
NO_PYPI_UPGRADE = "There is no PyPI release yet. From a checkout: git pull && make install"
CHECKOUT_UNINSTALL = (
    "This checkout was not installed with uv tool; skipped uv tool uninstall."
)


def data_dir_message(data_dir: Path) -> str:
    return UNTOUCHED.format(data_dir=data_dir)


def _vault_locked(data_dir: Path) -> bool:
    db = data_dir / "vault.db"
    if not db.exists():
        return False
    try:
        with db.open("a+b"):
            return False
    except OSError:
        return True


def _purge(data_dir: Path) -> int:
    if _vault_locked(data_dir):
        print(f"Refusing to delete {data_dir / 'vault.db'}: the Hub is still running.")
        return 1
    if data_dir.exists():
        shutil.rmtree(data_dir)
    if keyring is not None:
        try:
            keyring.delete_password(SERVICE, ACCOUNT)
        except Exception:
            pass
    return 0


def spawn_windows_deferred(uv: str, tool_args: list[str], pid: int) -> Path:
    temp = Path(os.environ.get("TEMP") or os.environ.get("TMP") or "/tmp")
    script = temp / f"pch-uninst-{pid}.cmd"
    quoted_uv = str(uv)
    args = " ".join(tool_args)
    script.write_text(
        "@echo off\r\n"
        ":wait\r\n"
        f'tasklist /FI "PID eq {pid}" | find "{pid}" >nul'
        " && ping -n 2 127.0.0.1 >nul && goto wait\r\n"
        f'"{quoted_uv}" {args}\r\n'
        'del "%~f0"\r\n',
        encoding="utf-8",
    )
    detached = getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
    new_group = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
    subprocess.Popen(
        ["cmd", "/c", str(script)],
        creationflags=detached | new_group,
        close_fds=True,
    )
    print(WINDOWS_DEFER)
    return script


def run_uv_tool(args: list[str], *, defer_on_windows: bool) -> int:
    uv = uv_executable()
    if uv is None:
        print(" ".join(["uv", *args]))
        return 1
    if defer_on_windows and sys.platform == "win32" and running_from_uv_tool():
        spawn_windows_deferred(uv, args, os.getpid())
        return 0
    completed = subprocess.run([uv, *args], check=False)
    return completed.returncode


def uninstall(
    data_dir: Path,
    *,
    purge_data: bool,
    yes: bool,
    confirm_delete: str | None = None,
) -> int:
    print(data_dir_message(data_dir))
    if purge_data:
        typed = confirm_delete
        if not yes:
            if typed is None:
                typed = input("Type DELETE to remove your data: ").strip()
            if typed != "DELETE":
                print("Aborted.")
                return 1
        purged = _purge(data_dir)
        if purged != 0:
            return purged
    rc = 0
    if running_from_uv_tool():
        rc = run_uv_tool(
            ["tool", "uninstall", TOOL_NAME],
            defer_on_windows=True,
        )
    else:
        print(CHECKOUT_UNINSTALL)
    return rc


def upgrade() -> int:
    if not PYPI_RELEASE:
        print(NO_PYPI_UPGRADE)
        return 2
    return run_uv_tool(
        ["tool", "upgrade", TOOL_NAME],
        defer_on_windows=True,
    )
