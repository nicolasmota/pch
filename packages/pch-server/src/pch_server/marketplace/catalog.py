from __future__ import annotations

import json
import os
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from pch_core.errors import IntegrityMismatch, ValidationFailed
from pch_core.schema.audit import EventKind
from pch_core.service import Hub
from pch_core.timeutil import now_iso

from pch_server.sync import http as sync_http

CATALOG_KV = "marketplace_catalog"
DEFAULT_KEY_PATH = "marketplace_public.key"


def pinned_public_key(hub: Hub) -> bytes | None:
    env = os.environ.get("PCH_CATALOG_PUBKEY")
    if env:
        return bytes.fromhex(env)
    path = Path(os.environ.get("PCH_CATALOG_PUBKEY_FILE") or (hub.data_dir / DEFAULT_KEY_PATH))
    if path.is_file():
        raw = path.read_bytes().strip()
        try:
            return bytes.fromhex(raw.decode())
        except ValueError:
            return raw
    return None


def catalog_url() -> str | None:
    return os.environ.get("PCH_CATALOG_URL")


def verify_catalog(body: bytes, signature: bytes, public_key: bytes) -> None:
    key = Ed25519PublicKey.from_public_bytes(public_key)
    try:
        key.verify(signature, body)
    except InvalidSignature as exc:
        raise IntegrityMismatch("catalog signature invalid") from exc


def load_cached_catalog(hub: Hub) -> dict | None:
    raw = hub._kv_get(CATALOG_KV)
    if not raw:
        return None
    return json.loads(raw)


def local_bundled_catalog() -> dict:
    from pch_server.plugins.package import load_manifest
    from pch_server.plugins.paths import plugins_root

    publishers = {
        "pcl-first-party": {"name": "PCL", "verification": "first_party"},
        "example-dev": {"name": "Example", "verification": "community"},
    }
    listings: list[dict] = []
    root = plugins_root()
    if root.is_dir():
        for child in sorted(root.iterdir()):
            manifest_path = child / "plugin.toml"
            if not manifest_path.is_file():
                continue
            try:
                manifest = load_manifest(manifest_path)
            except Exception:
                continue
            snap = manifest.model_dump(mode="json")
            perms = snap.get("permissions") or {}
            listings.append(
                {
                    "plugin_id": manifest.id,
                    "name": manifest.name,
                    "description": manifest.description,
                    "category": "connector",
                    "publisher": manifest.publisher,
                    "origin": "bundled",
                    "withdrawn": None,
                    "versions": [
                        {
                            "version": manifest.version,
                            "api_version": manifest.api_version,
                            "package_url": None,
                            "sha256": None,
                            "permissions_summary": {
                                "produces": perms.get("produces") or [],
                                "hosts": perms.get("hosts") or [],
                                "schedule": perms.get("schedule"),
                                "secrets": perms.get("secrets"),
                            },
                        }
                    ],
                }
            )
    return {
        "format": 1,
        "listings": listings,
        "publishers": publishers,
        "offline": False,
        "stale": False,
        "source": "bundled",
        "fetched_at": now_iso(),
    }


def refresh_catalog(hub: Hub) -> dict:
    url = catalog_url()
    if not url:
        payload = local_bundled_catalog()
        hub._kv_set(CATALOG_KV, json.dumps(payload))
        hub.ledger.append(
            EventKind.MARKETPLACE_CATALOG_CHECK,
            "owner",
            "local bundled catalog",
            extra={"outcome": "bundled", "count": len(payload["listings"])},
        )
        return payload
    client = sync_http.client()
    try:
        catalog_resp = client.get(url, timeout=30.0)
        catalog_resp.raise_for_status()
        sig_resp = client.get(url + ".sig", timeout=30.0)
        sig_resp.raise_for_status()
    except Exception:
        cached = load_cached_catalog(hub) or {
            "format": 1,
            "listings": [],
            "publishers": {},
        }
        cached["offline"] = True
        cached["stale"] = True
        hub.ledger.append(EventKind.MARKETPLACE_CATALOG_CHECK, "owner", "catalog fetch failed", extra={"outcome": "offline"})
        return cached
    public = pinned_public_key(hub)
    if public:
        try:
            verify_catalog(catalog_resp.content, sig_resp.content, public)
        except IntegrityMismatch:
            cached = load_cached_catalog(hub)
            hub.ledger.append(
                EventKind.MARKETPLACE_CATALOG_CHECK,
                "owner",
                "catalog signature invalid",
                extra={"outcome": "signature_invalid"},
            )
            if cached:
                cached["stale"] = True
                return cached
            raise
    payload = json.loads(catalog_resp.content)
    payload["fetched_at"] = now_iso()
    payload["offline"] = False
    payload["stale"] = False
    previous = load_cached_catalog(hub)
    _apply_withdrawn(hub, previous, payload)
    hub._kv_set(CATALOG_KV, json.dumps(payload))
    hub.ledger.append(EventKind.MARKETPLACE_CATALOG_CHECK, "owner", "catalog refreshed", extra={"outcome": "ok"})
    return payload


def _apply_withdrawn(hub: Hub, previous: dict | None, current: dict) -> None:
    prev_flags = {
        item.get("plugin_id"): item.get("withdrawn")
        for item in (previous or {}).get("listings") or []
        if item.get("withdrawn")
    }
    for listing in current.get("listings") or []:
        withdrawn = listing.get("withdrawn")
        if not withdrawn:
            continue
        plugin_id = listing.get("plugin_id")
        if prev_flags.get(plugin_id) == withdrawn:
            continue
        for inst in hub.list_plugins():
            if inst.get("plugin_id") == plugin_id and inst.get("state") == "enabled":
                reason = withdrawn.get("reason") if isinstance(withdrawn, dict) else str(withdrawn)
                hub.set_plugin_state(inst["id"], "paused", f"withdrawn: {reason}")
                hub.ledger.append(
                    EventKind.PLUGIN_KILLSWITCH,
                    "owner",
                    f"paused {plugin_id}: {reason}",
                    [inst["id"]],
                )


def find_listing(catalog: dict, plugin_id: str, version: str | None = None) -> dict:
    for listing in catalog.get("listings") or []:
        if listing.get("plugin_id") != plugin_id:
            continue
        versions = listing.get("versions") or []
        chosen = None
        if version:
            chosen = next((v for v in versions if v.get("version") == version), None)
        else:
            chosen = versions[-1] if versions else None
        if not chosen:
            raise ValidationFailed("version not found")
        return {**listing, "chosen": chosen}
    raise ValidationFailed(f"listing not found: {plugin_id}")
