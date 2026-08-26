from __future__ import annotations

import socket
import time
import urllib.error
import urllib.request


def port_free(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def health_ok(host: str, port: int, timeout: float = 0.4) -> bool:
    try:
        with urllib.request.urlopen(f"http://{host}:{port}/health", timeout=timeout) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def choose_port(host: str, preferred: int, *, span: int = 20) -> tuple[int, bool]:
    """Return (port, already_running). Reuse preferred if it is our Hub."""
    if health_ok(host, preferred):
        return preferred, True
    if port_free(host, preferred):
        return preferred, False
    for port in range(preferred + 1, preferred + span + 1):
        if health_ok(host, port):
            return port, True
        if port_free(host, port):
            return port, False
    raise RuntimeError(f"no free port in {preferred}–{preferred + span}")


def wait_for_health(host: str, port: int, timeout: float = 8.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if health_ok(host, port):
            return
        time.sleep(0.05)
    raise TimeoutError(f"Hub did not start on {host}:{port}")


def native_gui_available() -> bool:
    try:
        import gi  # noqa: F401

        return True
    except ImportError:
        pass
    try:
        import qtpy  # noqa: F401

        return True
    except ImportError:
        return False
