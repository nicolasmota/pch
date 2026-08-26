from __future__ import annotations

import argparse
import json
import os

from pcl_sdk.client import Client
from pcl_sdk.mcp_bridge import main as bridge_main
from pcl_sdk.plugin_kit import main as plugin_kit_main


def demo(base: str, code: str | None, token: str | None) -> None:
    client = Client(base, token or "")
    if code:
        result = client.pair(code)
        print(json.dumps(result, indent=2))
        token = result["token"]
        client.token = token
    print(
        json.dumps(client.call("search_personal_context", query="Atlas", purpose="demo"), indent=2)
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="pcl-sdk")
    sub = parser.add_subparsers(dest="cmd")
    demo_p = sub.add_parser("demo-agent")
    demo_p.add_argument("--pair", dest="code")
    demo_p.add_argument("--base", default="http://127.0.0.1:8765")
    demo_p.add_argument("--token", default="")
    bridge_p = sub.add_parser("mcp-bridge")
    bridge_p.add_argument("--token", default=os.environ.get("PCH_TOKEN", ""))
    bridge_p.add_argument("--base", default=os.environ.get("PCH_BASE", "http://127.0.0.1:8765"))
    plugin_p = sub.add_parser("plugin")
    plugin_p.add_argument("plugin_args", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.cmd == "demo-agent":
        demo(args.base, args.code, args.token or None)
        return
    if args.cmd == "mcp-bridge":
        bridge_main(args.token or None, args.base)
        return
    if args.cmd == "plugin":
        plugin_kit_main(args.plugin_args)
        return
    parser.print_help()
    raise SystemExit(1)


if __name__ == "__main__":
    main()
