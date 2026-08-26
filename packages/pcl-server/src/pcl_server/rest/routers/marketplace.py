from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from pcl_core.errors import ReconsentRequired, ValidationFailed
from pcl_core.policy.plugin import manifest_from_snapshot, permission_diff
from pcl_core.service import Hub

from pcl_server.marketplace.catalog import find_listing, load_cached_catalog, refresh_catalog
from pcl_server.plugins.host import isolation_mode
from pcl_server.plugins.package import manifest_to_snapshot, sha256_bytes, unpack_package
from pcl_server.rest.auth import get_hub, require_owner
from pcl_server.sync import http as sync_http

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


class InstallBody(BaseModel):
    plugin_id: str
    version: str | None = None


class UpdateConsentBody(BaseModel):
    approve_additions: bool = False


def _with_install_state(hub: Hub, catalog: dict) -> dict:
    installed = {p.get("plugin_id"): p for p in hub.list_plugins()}
    for listing in catalog.get("listings") or []:
        inst = installed.get(listing.get("plugin_id"))
        if inst:
            listing["installed"] = True
            listing["installation_id"] = inst.get("id")
            listing["installed_state"] = inst.get("state")
        else:
            listing["installed"] = False
    return catalog


@router.get("/catalog")
def get_catalog(hub: Hub = Depends(get_hub), _: str = Depends(require_owner)) -> dict:
    from pcl_server.marketplace.catalog import catalog_url, local_bundled_catalog

    if not catalog_url():
        return _with_install_state(hub, local_bundled_catalog())
    cached = load_cached_catalog(hub)
    if cached is None:
        return _with_install_state(hub, refresh_catalog(hub))
    cached.setdefault("stale", False)
    return _with_install_state(hub, cached)


@router.post("/refresh")
def post_refresh(hub: Hub = Depends(get_hub), _: str = Depends(require_owner)) -> dict:
    return _with_install_state(hub, refresh_catalog(hub))


@router.post("/install")
def install(body: InstallBody, hub: Hub = Depends(get_hub), _: str = Depends(require_owner)) -> dict:
    from pcl_server.marketplace.catalog import catalog_url, local_bundled_catalog

    existing = next((p for p in hub.list_plugins() if p.get("plugin_id") == body.plugin_id), None)
    if existing:
        raise ValidationFailed(f"{body.plugin_id} is already installed")

    catalog = local_bundled_catalog() if not catalog_url() else (load_cached_catalog(hub) or refresh_catalog(hub))
    listing = find_listing(catalog, body.plugin_id, body.version)
    chosen = listing["chosen"]
    package_url = chosen.get("package_url")
    expected = chosen.get("sha256")
    if listing.get("origin") == "bundled" or not package_url:
        from pcl_server.plugins.package import load_manifest
        from pcl_server.plugins.paths import bundled_dir

        root = bundled_dir(body.plugin_id)
        if root is None:
            raise ValidationFailed("bundled plugin not found")
        snap = manifest_to_snapshot(load_manifest(root / "plugin.toml"))
        inst = hub.create_plugin_installation(snap, origin="bundled", isolation=isolation_mode())
        inst["package_dir"] = str(root)
        hub.store.put(inst)
        hub.engine.conn.commit()
        return inst
    if not expected:
        raise ValidationFailed("listing missing package")
    response = sync_http.client().get(package_url, timeout=60.0)
    response.raise_for_status()
    if sha256_bytes(response.content) != expected:
        from pcl_core.errors import IntegrityMismatch

        raise IntegrityMismatch("package sha256 mismatch")
    dest = hub.data_dir / "plugins" / "marketplace" / body.plugin_id
    if dest.exists():
        import shutil

        shutil.rmtree(dest)
    manifest = unpack_package(response.content, dest, expected)
    snap = manifest_to_snapshot(manifest)
    summary = chosen.get("permissions_summary") or {}
    if summary:
        declared_hosts = set(snap["permissions"]["hosts"])
        listed_hosts = set(summary.get("hosts") or [])
        if not declared_hosts.issubset(listed_hosts) and listed_hosts:
            from pcl_core.errors import IntegrityMismatch

            raise IntegrityMismatch("packaged manifest exceeds catalog summary")
    inst = hub.create_plugin_installation(
        snap, origin="marketplace", package_sha256=expected, isolation=isolation_mode()
    )
    inst["package_dir"] = str(dest)
    hub.store.put(inst)
    hub.engine.conn.commit()
    return inst


@router.get("/plugins/{installation_id}/update")
def update_preview(installation_id: str, hub: Hub = Depends(get_hub), _: str = Depends(require_owner)) -> dict:
    inst = hub.get_plugin(installation_id)
    catalog = load_cached_catalog(hub) or refresh_catalog(hub)
    listing = find_listing(catalog, inst["plugin_id"])
    chosen = listing["chosen"]
    old = manifest_from_snapshot(inst["manifest"])
    new_summary = chosen.get("permissions_summary") or {}
    new_manifest = {
        "id": inst["plugin_id"],
        "name": listing.get("name") or inst["plugin_id"],
        "description": listing.get("description") or "",
        "version": chosen.get("version"),
        "publisher": listing.get("publisher") or "",
        "api_version": chosen.get("api_version") or 1,
        "entry": old.entry,
        "permissions": {
            "secrets": bool(new_summary.get("secrets", old.permissions.secrets)),
            "schedule": new_summary.get("schedule") or old.permissions.schedule,
            "hosts": new_summary.get("hosts") or old.permissions.hosts,
            "produces": new_summary.get("produces") or [p.model_dump() for p in old.permissions.produces],
        },
    }
    diff = permission_diff(old, manifest_from_snapshot(new_manifest))
    return {
        "current_version": inst.get("plugin_version"),
        "available_version": chosen.get("version"),
        "diff": diff,
        "reconsent_required": bool(diff["added"]),
    }


@router.post("/plugins/{installation_id}/update")
def apply_update(
    installation_id: str,
    body: UpdateConsentBody | None = None,
    hub: Hub = Depends(get_hub),
    _: str = Depends(require_owner),
) -> dict:
    preview = update_preview(installation_id, hub, _)
    if preview["reconsent_required"] and not (body and body.approve_additions):
        raise ReconsentRequired("permission additions require re-consent")
    catalog = load_cached_catalog(hub) or refresh_catalog(hub)
    inst = hub.get_plugin(installation_id)
    listing = find_listing(catalog, inst["plugin_id"])
    chosen = listing["chosen"]
    response = sync_http.client().get(chosen["package_url"], timeout=60.0)
    response.raise_for_status()
    dest = hub.data_dir / "plugins" / "marketplace" / inst["plugin_id"]
    dest.mkdir(parents=True, exist_ok=True)
    manifest = unpack_package(response.content, dest, chosen.get("sha256"))
    inst["manifest"] = manifest_to_snapshot(manifest)
    inst["plugin_version"] = manifest.version
    inst["package_dir"] = str(dest)
    inst["package_sha256"] = chosen.get("sha256") or ""
    hub.store.put(inst)
    if preview["reconsent_required"]:
        hub.consent_plugin(installation_id)
    hub.engine.conn.commit()
    return inst
