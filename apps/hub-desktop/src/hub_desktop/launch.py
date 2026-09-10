from __future__ import annotations

import ipaddress
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser

import uvicorn

try:
    import webview
except Exception:
    webview = None


def is_loopback(host: str) -> bool:
    candidate = host.strip().strip("[]")
    if candidate.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(candidate).is_loopback
    except ValueError:
        return False


def bind_host(host: str) -> str:
    """Packaged serve always binds IPv4 loopback; ::1 is accepted as policy only."""
    if host.strip().strip("[]") in {"::1"}:
        return "127.0.0.1"
    return host


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
        pass
    if sys.platform == "darwin":
        try:
            import WebKit  # noqa: F401

            return True
        except ImportError:
            try:
                import objc  # noqa: F401

                return True
            except ImportError:
                return False
    if sys.platform == "win32":
        try:
            import webview.platforms.winforms  # noqa: F401

            return True
        except Exception:
            return False
    return False


def open_ui(url: str, *, force_browser: bool) -> None:
    if not force_browser and native_gui_available() and webview is not None:
        webview.create_window("Personal Context Hub", url)
        webview.start()
        return
    print(f"Opening the Hub in your browser: {url}")
    webbrowser.open(url)


def launch_hub(
    app,
    host: str,
    port: int,
    *,
    force_browser: bool = False,
    open_window: bool = True,
) -> None:
    bound = bind_host(host)
    chosen, already = choose_port(bound, port)
    url = f"http://{bound}:{chosen}/"
    if already:
        print(f"Hub already running at {url}")
        if open_window:
            open_ui(url, force_browser=force_browser)
        return
    config = uvicorn.Config(app, host=bound, port=chosen, log_level="info")
    server = uvicorn.Server(config)

    def run() -> None:
        server.run()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    wait_for_health(bound, chosen)
    if open_window:
        open_ui(url, force_browser=force_browser)
    thread.join()
