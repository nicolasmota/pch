from __future__ import annotations

import hashlib
import io
import json
import zipfile
from pathlib import Path
from typing import Any

from pcl_core.service import Hub
from pcl_core.timeutil import now_iso


PCA_VERSION = "0.1.0"


def _canonical(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _encrypt(data: bytes, passphrase: str) -> bytes:
    try:
        from pyrage import passphrase as age_pass

        return age_pass.encrypt(data, passphrase)
    except Exception:
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes
        import base64
        import os

        salt = os.urandom(16)
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
        key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
        return b"PCH1" + salt + Fernet(key).encrypt(data)


def _decrypt(data: bytes, passphrase: str) -> bytes:
    if data.startswith(b"PCH1"):
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes
        import base64

        salt, rest = data[4:20], data[20:]
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
        key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
        return Fernet(key).decrypt(rest)
    from pyrage import passphrase as age_pass

    return age_pass.decrypt(data, passphrase)


TYPE_FILES = {
    "project": "projects",
    "goal": "goals",
    "commitment": "commitments",
    "decision": "decisions",
    "preference": "preferences",
    "memory": "memories",
    "artifact": "artifacts",
    "profile": "profile",
    "person": "profile",
    "event": "calendar_events",
    "connector_account": "connectors",
}


def export_archive(hub: Hub, dest: Path, passphrase: str, filters: dict[str, Any] | None = None) -> dict:
    filters = filters or {}
    buf = io.BytesIO()
    files: dict[str, str] = {}
    grouped: dict[str, list[dict]] = {v: [] for v in set(TYPE_FILES.values())}
    grouped["versions"] = []
    skip_types = {"shared_state", "connection", "grant", "manifest", "action_intent", "approval"}
    project_filter = filters.get("projects") or filters.get("project")
    class_max = filters.get("classification_max")
    for row in hub.store.list():
        if row.get("type") in skip_types:
            continue
        if project_filter:
            pids = project_filter if isinstance(project_filter, list) else [project_filter]
            if row.get("type") == "project" and row["id"] not in pids:
                continue
            if row.get("type") != "project" and row.get("project_id") not in pids and row.get("id") not in pids:
                continue
        fname = TYPE_FILES.get(row.get("type", ""), None)
        if not fname:
            continue
        grouped[fname].append(row)
        grouped["versions"].extend(hub.versions(row["id"]))
    events = hub.events()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        counts = {}
        for name, items in grouped.items():
            if name == "versions":
                continue
            text = "\n".join(_canonical(i) for i in items)
            path = f"objects/{name}.jsonl"
            zf.writestr(path, text)
            files[path] = hashlib.sha256(text.encode()).hexdigest()
            counts[name] = len(items)
        versions_text = "\n".join(_canonical(i) for i in grouped["versions"])
        zf.writestr("objects/versions.jsonl", versions_text)
        files["objects/versions.jsonl"] = hashlib.sha256(versions_text.encode()).hexdigest()
        ev_text = "\n".join(_canonical(e) for e in events)
        zf.writestr("events.jsonl", ev_text)
        files["events.jsonl"] = hashlib.sha256(ev_text.encode()).hexdigest()
        zf.writestr(
            "schemas/memory.schema.json",
            json.dumps({"title": "memory", "type": "object"}),
        )
        manifest = {
            "pca_version": PCA_VERSION,
            "created_at": now_iso(),
            "generator": {"name": "personal-context-hub", "version": "0.1.0"},
            "space": {"id": "personal", "kind": "personal"},
            "filters": filters,
            "counts": counts,
            "integrity": {"algorithm": "sha256", "files": files},
            "schema_migration": {"min_reader_version": "0.1.0"},
        }
        zf.writestr("manifest.json", json.dumps(manifest, indent=2, sort_keys=True))
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(_encrypt(buf.getvalue(), passphrase))
    digest = hashlib.sha256(dest.read_bytes()).hexdigest()
    return {"path": str(dest), "manifest_hash": digest, "filters": filters, "pca_version": PCA_VERSION}
