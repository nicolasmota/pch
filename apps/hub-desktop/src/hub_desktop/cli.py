from __future__ import annotations

import argparse
import os
import sys
import threading
import time
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI
from pcl_core.service import Hub
from pcl_core.vault.engine import cipher_available
from pcl_server.rest.app import create_app

from hub_desktop import __version__
from hub_desktop.doctor import doctor_ok, doctor_report, print_report
from hub_desktop.launch import is_loopback, launch_hub
from hub_desktop.pin import ensure_pinned, reexec_into_pinned
from hub_desktop.uninstall import uninstall as run_uninstall
from hub_desktop.uninstall import upgrade as run_upgrade

LOOPBACK_MSG = "The Hub is not a public server; it binds loopback only."
REFUSE_LINE1 = (
    "Refusing to start: the encrypted database driver (sqlcipher3) did not load on this platform."
)
REFUSE_LINE2 = (
    "Your vault was not opened in plaintext. "
    "Set PCH_PLAIN_SQLITE=1 only if you accept an unencrypted vault."
)
PINNING_VERBS = {None, "serve", "smoke"}
SPA_TITLE = "Personal Context Hub"


def require_cipher_or_exit(data_dir: Path) -> None:
    if os.environ.get("PCH_PLAIN_SQLITE") == "1":
        return
    if cipher_available():
        return
    print(REFUSE_LINE1)
    print(REFUSE_LINE2)
    raise SystemExit(1)


def packaged_app(data_dir: Path, *, sim_enabled: bool = False) -> FastAPI:
    require_cipher_or_exit(data_dir)
    plain = os.environ.get("PCH_PLAIN_SQLITE") == "1"
    hub = Hub(data_dir, plain=plain)
    if not plain and not hub.engine.encrypted:
        print(REFUSE_LINE1)
        print(REFUSE_LINE2)
        raise SystemExit(1)
    return create_app(hub, sim_enabled=sim_enabled, catalog_refresh=False)


def _data_dir(raw: str | None) -> Path:
    return Path(raw or os.environ.get("PCH_DATA_DIR") or (Path.home() / ".pch"))


def _refuse_host(host: str) -> str:
    if not is_loopback(host):
        print(LOOPBACK_MSG)
        raise SystemExit(2)
    if host.strip().strip("[]") in {"::1"}:
        return "127.0.0.1"
    return host


def cmd_launch(args: argparse.Namespace) -> None:
    data_dir = _data_dir(args.data_dir)
    host = _refuse_host(args.host)
    app = packaged_app(data_dir, sim_enabled=bool(getattr(args, "sim", False)))
    launch_hub(
        app,
        host,
        args.port,
        force_browser=bool(getattr(args, "browser", False)),
        open_window=not bool(getattr(args, "headless", False)),
    )


def cmd_serve(args: argparse.Namespace) -> None:
    data_dir = _data_dir(args.data_dir)
    host = _refuse_host(args.host)
    app = packaged_app(data_dir, sim_enabled=bool(args.sim))
    launch_hub(
        app,
        host,
        args.port,
        force_browser=True,
        open_window=not bool(args.headless),
    )


def cmd_doctor(args: argparse.Namespace) -> None:
    data_dir = _data_dir(args.data_dir)
    report = doctor_report(data_dir, args.port)
    print_report(report, as_json=bool(args.json))
    raise SystemExit(0 if doctor_ok(report) else 1)


def cmd_version(_args: argparse.Namespace) -> None:
    print(__version__)


def cmd_upgrade(_args: argparse.Namespace) -> None:
    raise SystemExit(run_upgrade())


def cmd_uninstall(args: argparse.Namespace) -> None:
    data_dir = _data_dir(args.data_dir)
    raise SystemExit(
        run_uninstall(
            data_dir,
            purge_data=bool(args.purge_data),
            yes=bool(args.yes),
        )
    )


def _wait_health(base: str, timeout: float = 8.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            response = httpx.get(f"{base}/health", timeout=0.4)
            if response.status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(0.05)
    raise TimeoutError(f"Hub did not start at {base}")


def cmd_smoke(args: argparse.Namespace) -> None:
    data_dir = _data_dir(args.data_dir)
    host = "127.0.0.1"
    app = packaged_app(data_dir)
    config = uvicorn.Config(app, host=host, port=args.port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    base = f"http://{host}:{args.port}"
    try:
        _wait_health(base)
        health = httpx.get(f"{base}/health", timeout=5.0)
        page = httpx.get(f"{base}/", timeout=5.0)
        if health.status_code != 200 or SPA_TITLE not in page.text:
            print("smoke: health or SPA title failed")
            raise SystemExit(1)
        setup = httpx.post(f"{base}/v1/setup", json={"name": "Smoke"}, timeout=10.0)
        if setup.status_code != 200:
            print("smoke: setup failed")
            raise SystemExit(1)
        token = setup.json().get("owner_token") or ""
        headers = {"Authorization": f"Bearer {token}"}
        project = httpx.post(
            f"{base}/v1/projects",
            headers=headers,
            json={"title": "Atlas", "status": "active"},
            timeout=10.0,
        )
        search = httpx.get(
            f"{base}/v1/search", params={"q": "Atlas"}, headers=headers, timeout=10.0
        )
        link = httpx.post(
            f"{base}/v1/connections/links",
            headers=headers,
            json={"name": "smoke"},
            timeout=10.0,
        )
        pair = httpx.post(
            f"{base}/v1/connections/pair",
            json={"code": link.json()["code"]},
            timeout=10.0,
        )
        httpx.post(
            f"{base}/v1/grants",
            headers=headers,
            json={
                "connection_id": pair.json()["connection_id"],
                "preset": "read_project",
                "selectors": {"project": project.json()["id"]},
            },
            timeout=10.0,
        )
        manifest = httpx.post(
            f"{base}/v1/mcp/tools/get_context_manifest",
            headers={"Authorization": f"Bearer {pair.json()['token']}"},
            json={
                "purpose": "smoke",
                "requested_capabilities": ["project.read"],
                "selectors": {"project": project.json()["id"]},
            },
            timeout=10.0,
        )
        if project.status_code != 200 or search.status_code != 200 or manifest.status_code != 200:
            print("smoke: 001/004 HTTP calls failed")
            raise SystemExit(1)
        if not search.json().get("results"):
            print("smoke: Atlas not searchable")
            raise SystemExit(1)
    finally:
        server.should_exit = True
        thread.join(timeout=5)
    raise SystemExit(0)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pch")
    parser.add_argument("--no-pin", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        "--data-dir",
        default=os.environ.get("PCH_DATA_DIR", str(Path.home() / ".pch")),
    )
    parser.add_argument("--port", type=int, default=int(os.environ.get("PCH_PORT", "8765")))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--browser", action="store_true")
    parser.add_argument("--headless", action="store_true")
    sub = parser.add_subparsers(dest="verb")

    serve = sub.add_parser("serve")
    serve.add_argument("--headless", action="store_true")
    serve.add_argument("--port", type=int, default=int(os.environ.get("PCH_PORT", "8765")))
    _data_dir_default = os.environ.get("PCH_DATA_DIR", str(Path.home() / ".pch"))
    serve.add_argument("--data-dir", default=_data_dir_default)
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--sim", action="store_true")

    doctor = sub.add_parser("doctor")
    doctor.add_argument("--json", action="store_true")
    doctor.add_argument("--data-dir", default=_data_dir_default)
    doctor.add_argument("--port", type=int, default=int(os.environ.get("PCH_PORT", "8765")))

    smoke = sub.add_parser("smoke")
    smoke.add_argument("--port", type=int, default=int(os.environ.get("PCH_PORT", "8765")))
    smoke.add_argument("--data-dir", default=_data_dir_default)

    sub.add_parser("upgrade")
    uninstall_p = sub.add_parser("uninstall")
    uninstall_p.add_argument("--purge-data", action="store_true")
    uninstall_p.add_argument("--yes", action="store_true")
    uninstall_p.add_argument(
        "--data-dir",
        default=os.environ.get("PCH_DATA_DIR", str(Path.home() / ".pch")),
    )
    sub.add_parser("version")
    return parser


def main(argv: list[str] | None = None) -> None:
    raw = list(sys.argv[1:] if argv is None else argv)
    no_pin = "--no-pin" in raw
    stripped = [item for item in raw if item != "--no-pin"]
    parser = _parser()
    args = parser.parse_args(stripped)
    args.no_pin = no_pin
    if not hasattr(args, "data_dir"):
        args.data_dir = os.environ.get("PCH_DATA_DIR", str(Path.home() / ".pch"))
    if not hasattr(args, "port"):
        args.port = int(os.environ.get("PCH_PORT", "8765"))
    if not hasattr(args, "host"):
        args.host = "127.0.0.1"
    if not hasattr(args, "sim"):
        args.sim = False
    if not hasattr(args, "headless"):
        args.headless = False
    if not no_pin and args.verb in PINNING_VERBS:
        action = ensure_pinned(__version__)
        if action == "installed":
            reexec_into_pinned(stripped)
    dispatch = {
        None: cmd_launch,
        "serve": cmd_serve,
        "doctor": cmd_doctor,
        "smoke": cmd_smoke,
        "upgrade": cmd_upgrade,
        "uninstall": cmd_uninstall,
        "version": cmd_version,
    }
    handler = dispatch.get(args.verb)
    if handler is None:
        parser.print_help()
        raise SystemExit(2)
    handler(args)


if __name__ == "__main__":
    main()
