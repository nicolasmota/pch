from __future__ import annotations

import argparse
import os
import threading
import webbrowser
from pathlib import Path

import uvicorn
from pcl_core.service import Hub
from pcl_server.__main__ import run_server
from pcl_server.rest.app import create_app

from hub_desktop.launch import choose_port, native_gui_available, wait_for_health


def _open_ui(url: str, *, force_browser: bool) -> None:
    if not force_browser and native_gui_available():
        import webview

        webview.create_window("Personal Context Hub", url)
        webview.start()
        return
    print(f"Opening the Hub in your browser: {url}")
    webbrowser.open(url)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="hub-desktop")
    parser.add_argument("--dev", action="store_true")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PCH_PORT", "8765")))
    parser.add_argument(
        "--data-dir",
        default=os.environ.get("PCH_DATA_DIR", str(Path.home() / ".pch")),
    )
    parser.add_argument(
        "--browser",
        action="store_true",
        help="open the system browser instead of a native window",
    )
    parser.add_argument(
        "--reload",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="restart the API when Python/plugin files change (default: on with --dev)",
    )
    args = parser.parse_args(argv)
    os.environ["PCH_DATA_DIR"] = args.data_dir
    reload = args.dev if args.reload is None else args.reload

    host = "127.0.0.1"
    port, already = choose_port(host, args.port)
    url = f"http://{host}:{port}/"

    if already:
        print(f"Hub already running at {url}")
        _open_ui(url, force_browser=args.browser)
        return

    if reload:

        def open_when_ready() -> None:
            wait_for_health(host, port, timeout=30.0)
            _open_ui(url, force_browser=True)

        opener = threading.Thread(target=open_when_ready, daemon=True)
        opener.start()
        run_server(host, port, reload=True)
        return

    hub = Hub(Path(args.data_dir), plain=os.environ.get("PCH_PLAIN_SQLITE") == "1")
    app = create_app(hub)
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)

    def run() -> None:
        server.run()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    wait_for_health(host, port)
    _open_ui(url, force_browser=args.browser)
    thread.join()


if __name__ == "__main__":
    main()
