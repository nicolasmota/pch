from __future__ import annotations

import hashlib
import io
import json
import zipfile
from pathlib import Path
from typing import Any

from pch_archive.export import _decrypt


class IntegrityError(ValueError):
    pass


def open_archive(path: Path, passphrase: str) -> dict[str, Any]:
    raw = _decrypt(path.read_bytes(), passphrase)
    zf = zipfile.ZipFile(io.BytesIO(raw))
    manifest = json.loads(zf.read("manifest.json"))
    files = manifest.get("integrity", {}).get("files", {})
    for rel, expected in files.items():
        data = zf.read(rel)
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected:
            raise IntegrityError(f"hash mismatch for {rel}")
    records: list[dict] = []
    for name in zf.namelist():
        if name.startswith("objects/") and name.endswith(".jsonl") and not name.endswith("versions.jsonl"):
            text = zf.read(name).decode()
            for line in text.splitlines():
                if line.strip():
                    records.append(json.loads(line))
    versions = []
    if "objects/versions.jsonl" in zf.namelist():
        for line in zf.read("objects/versions.jsonl").decode().splitlines():
            if line.strip():
                versions.append(json.loads(line))
    return {"manifest": manifest, "records": records, "versions": versions, "zip": zf}
