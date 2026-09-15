from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

BACKEND_BWRAP = "bwrap"
BACKEND_SANDBOX_EXEC = "sandbox-exec"
BACKEND_NONE = "none"

SANDBOX_EXEC_PROFILE = "(version 1)\n(allow default)\n(deny network*)\n"
_SANDBOX_EXEC_PROBE_PROFILE = "(version 1)(allow default)"
_HOST_RO_BINDS = ("/usr", "/bin", "/sbin", "/lib", "/lib64", "/lib32", "/etc")


def sandbox_backend() -> str:
    if os.environ.get("PCH_PLUGIN_SANDBOX") == "0":
        return BACKEND_NONE
    if _probe_bwrap():
        return BACKEND_BWRAP
    if _probe_sandbox_exec():
        return BACKEND_SANDBOX_EXEC
    return BACKEND_NONE


def sandbox_available() -> bool:
    return sandbox_backend() != BACKEND_NONE


def isolation_mode() -> str:
    return "sandboxed" if sandbox_available() else "reduced"


def wrap_plugin_command(
    cmd: list[str],
    *,
    root: Path,
    isolation: str,
    env: dict[str, str],
) -> tuple[list[str], dict[str, str]]:
    out_env = dict(env)
    if isolation != "sandboxed":
        return list(cmd), out_env
    backend = sandbox_backend()
    if backend == BACKEND_BWRAP:
        interpreter = cmd[0] if cmd else None
        wrapped = [
            *_bwrap_prefix(interpreter=interpreter, plugin_root=root),
            *cmd,
        ]
        out_env["PCH_PLUGIN_SRC"] = "/plugin/src"
        return wrapped, out_env
    if backend == BACKEND_SANDBOX_EXEC:
        return ["sandbox-exec", "-p", SANDBOX_EXEC_PROFILE, *cmd], out_env
    return list(cmd), out_env


def _path_exists(path: str | Path) -> bool:
    try:
        return Path(path).exists()
    except OSError:
        return False


def _python_runtime_paths(interpreter: str) -> list[str]:
    paths: list[str] = []
    raw = Path(interpreter)
    try:
        resolved = raw.resolve()
    except OSError:
        resolved = raw
    for candidate in (raw, resolved):
        paths.append(str(candidate))
    if raw.parent.name == "bin":
        paths.append(str(raw.parent.parent))
    venv = raw.parent.parent if raw.parent.name == "bin" else None
    if venv is not None:
        paths.extend(_pth_targets(venv))
    return paths


def _pth_targets(venv: Path) -> list[str]:
    targets: list[str] = []
    for pth in venv.glob("lib/python*/site-packages/*.pth"):
        try:
            lines = pth.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            text = line.strip()
            if not text or text.startswith("#") or text.startswith("import "):
                continue
            if _path_exists(text):
                targets.append(text)
    return targets


def _bwrap_prefix(*, interpreter: str | None = None, plugin_root: Path | None = None) -> list[str]:
    argv = ["bwrap", "--unshare-net", "--die-with-parent"]
    if _path_exists("/dev"):
        argv.extend(["--dev", "/dev"])
    if _path_exists("/proc"):
        argv.extend(["--proc", "/proc"])
    seen: set[str] = set()

    def bind(src: str, dest: str | None = None) -> None:
        target = dest or src
        key = f"{src}->{target}"
        if key in seen or not _path_exists(src):
            return
        seen.add(key)
        argv.extend(["--ro-bind-try", src, target])

    for host in _HOST_RO_BINDS:
        bind(host)
    if interpreter:
        for path in _python_runtime_paths(interpreter):
            bind(path)
    if plugin_root is not None:
        argv.extend(["--ro-bind", str(plugin_root), "/plugin", "--chdir", "/plugin"])
    argv.extend(["--tmpfs", "/tmp"])
    return argv


def _probe_bwrap() -> bool:
    bwrap = shutil.which("bwrap")
    if not bwrap:
        return False
    true_bin = shutil.which("true") or "/bin/true"
    try:
        result = subprocess.run(
            [*_bwrap_prefix(), true_bin],
            capture_output=True,
            timeout=2,
        )
        return result.returncode == 0
    except Exception:
        return False


def _probe_sandbox_exec() -> bool:
    exe = shutil.which("sandbox-exec")
    if not exe:
        return False
    true_bin = shutil.which("true") or "/usr/bin/true"
    try:
        result = subprocess.run(
            [exe, "-p", _SANDBOX_EXEC_PROBE_PROFILE, true_bin],
            capture_output=True,
            timeout=2,
        )
        return result.returncode == 0
    except Exception:
        return False
