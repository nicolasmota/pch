from __future__ import annotations

import ast
import hashlib
import io
import json
import tomllib
import zipfile
from pathlib import Path

from pcl_core.errors import IntegrityMismatch, ValidationFailed
from pcl_core.schema.plugin import PluginManifest

STDLIB_ALLOW = {
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


def parse_manifest(raw: bytes | str | dict) -> PluginManifest:
    if isinstance(raw, dict):
        data = raw
    else:
        text = raw.decode() if isinstance(raw, bytes) else raw
        data = tomllib.loads(text)
    try:
        return PluginManifest.from_toml_dict(data)
    except Exception as exc:
        raise ValidationFailed(f"invalid manifest: {exc}") from exc


def load_manifest(path: Path) -> PluginManifest:
    return parse_manifest(path.read_bytes())


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pack_dir(plugin_dir: Path) -> tuple[bytes, str]:
    manifest_path = plugin_dir / "plugin.toml"
    if not manifest_path.is_file():
        raise ValidationFailed("plugin.toml missing")
    load_manifest(manifest_path)
    validate_stdlib(plugin_dir / "src")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(plugin_dir.rglob("*")):
            if file.is_file() and "__pycache__" not in file.parts:
                zf.write(file, file.relative_to(plugin_dir).as_posix())
    data = buffer.getvalue()
    return data, sha256_bytes(data)


def unpack_package(data: bytes, dest: Path, expected_sha256: str | None = None) -> PluginManifest:
    digest = sha256_bytes(data)
    if expected_sha256 and digest != expected_sha256:
        raise IntegrityMismatch("package sha256 mismatch")
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        zf.extractall(dest)
    manifest = load_manifest(dest / "plugin.toml")
    validate_stdlib(dest / "src")
    return manifest


def validate_stdlib(src: Path) -> None:
    if not src.is_dir():
        raise ValidationFailed("src/ missing")
    for file in src.rglob("*.py"):
        tree = ast.parse(file.read_text(), filename=str(file))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module.split(".")[0]]
            for name in names:
                if name in {"pcl_sdk"}:
                    continue
                if name.startswith("pcl_"):
                    raise ValidationFailed(f"forbidden import {name} in {file.name}")
                if name not in STDLIB_ALLOW and name not in sys_stdlib_extra():
                    # allow relative and local modules (no dots, file exists)
                    if (src / f"{name}.py").exists() or (src / name).is_dir():
                        continue
                    raise ValidationFailed(f"non-stdlib import {name} in {file.name}")


def sys_stdlib_extra() -> set[str]:
    return STDLIB_ALLOW | {"__future__"}


def manifest_to_snapshot(manifest: PluginManifest) -> dict:
    return json.loads(manifest.model_dump_json())
