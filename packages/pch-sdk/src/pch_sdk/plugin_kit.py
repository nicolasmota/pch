from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import tomllib
import zipfile
from pathlib import Path

STDLIB_ALLOW = {
    "__future__",
    "json",
    "re",
    "base64",
    "datetime",
    "email",
    "html",
    "http",
    "urllib",
    "xml",
    "hashlib",
    "math",
    "collections",
    "itertools",
    "functools",
    "typing",
    "dataclasses",
    "enum",
    "pathlib",
    "io",
    "os",
    "sys",
    "time",
    "string",
    "textwrap",
    "decimal",
    "copy",
}

SKELETON_TOML = """[plugin]
id = "{plugin_id}"
name = "{name}"
description = "Import items into the Hub."
version = "0.1.0"
publisher = "local-dev"
api_version = 1
entry = "sync:main"

[permissions]
secrets = false
schedule = "manual"
hosts = ["example.com"]

[[permissions.produces]]
type = "artifact"
classification = "personal"
"""

SKELETON_SYNC = '''from pch_sdk.plugin_runtime import hub


def main() -> dict:
    hub.log("hello from {plugin_id}")
    items = [
        {{
            "type": "artifact",
            "title": "Example item",
            "body": "Created by the plugin scaffold.",
            "source_key": "example:{plugin_id}:1",
            "classification": "personal",
            "authority": "source_imported",
        }}
    ]
    hub.items_upsert(items)
    return {{"created": 1, "updated": 0}}
'''


def cmd_new(plugin_id: str, dest: Path | None = None) -> Path:
    target = dest or Path.cwd() / plugin_id
    target.mkdir(parents=True, exist_ok=True)
    (target / "src").mkdir(exist_ok=True)
    (target / "plugin.toml").write_text(
        SKELETON_TOML.format(plugin_id=plugin_id, name=plugin_id),
        encoding="utf-8",
    )
    (target / "src" / "sync.py").write_text(SKELETON_SYNC.format(plugin_id=plugin_id), encoding="utf-8")
    return target


def _validate_imports(src: Path) -> None:
    if not src.is_dir():
        raise SystemExit("src/ missing")
    for file in src.rglob("*.py"):
        tree = ast.parse(file.read_text(), filename=str(file))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module.split(".")[0]]
            for name in names:
                if name == "pch_sdk":
                    continue
                if name.startswith("pcl_"):
                    raise SystemExit(f"forbidden import {name} in {file.name}")
                if name not in STDLIB_ALLOW and not (src / f"{name}.py").exists() and not (src / name).is_dir():
                    raise SystemExit(f"non-stdlib import {name} in {file.name}")


def cmd_validate(plugin_dir: Path) -> dict:
    raw = tomllib.loads((plugin_dir / "plugin.toml").read_text())
    plugin = raw.get("plugin") or {}
    hosts = (raw.get("permissions") or {}).get("hosts") or []
    for host in hosts:
        if "/" in host or "*" in host or host.startswith("http"):
            raise SystemExit(f"undeclared-style host invalid: {host}")
    _validate_imports(plugin_dir / "src")
    return {"ok": True, "id": plugin.get("id"), "version": plugin.get("version")}


def cmd_pack(plugin_dir: Path, dest: Path | None = None) -> dict:
    info = cmd_validate(plugin_dir)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(plugin_dir.rglob("*")):
            if file.is_file() and "__pycache__" not in file.parts:
                zf.write(file, file.relative_to(plugin_dir).as_posix())
    data = buffer.getvalue()
    digest = hashlib.sha256(data).hexdigest()
    out = dest or (plugin_dir / f"{info['id']}-{info['version']}.pclplugin")
    out.write_bytes(data)
    return {"path": str(out), "sha256": digest, "bytes": len(data)}


def cmd_dev(plugin_dir: Path, hub_base: str) -> None:
    report = cmd_validate(plugin_dir)
    print(json.dumps({"dev": True, "hub": hub_base, **report}, indent=2))
    print("Pack with `pch-sdk plugin pack` then POST /v1/plugins with source=sideload.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="pch-sdk plugin")
    sub = parser.add_subparsers(dest="action", required=True)
    new_p = sub.add_parser("new")
    new_p.add_argument("plugin_id")
    new_p.add_argument("--dest")
    val_p = sub.add_parser("validate")
    val_p.add_argument("plugin_dir")
    pack_p = sub.add_parser("pack")
    pack_p.add_argument("plugin_dir")
    pack_p.add_argument("--out")
    dev_p = sub.add_parser("dev")
    dev_p.add_argument("plugin_dir")
    dev_p.add_argument("--hub", default="http://127.0.0.1:8765")
    args = parser.parse_args(argv)
    if args.action == "new":
        print(cmd_new(args.plugin_id, Path(args.dest) if args.dest else None))
        return
    if args.action == "validate":
        print(json.dumps(cmd_validate(Path(args.plugin_dir)), indent=2))
        return
    if args.action == "pack":
        print(json.dumps(cmd_pack(Path(args.plugin_dir), Path(args.out) if args.out else None), indent=2))
        return
    if args.action == "dev":
        cmd_dev(Path(args.plugin_dir), args.hub)
        return
