from __future__ import annotations

import base64

from fastapi import APIRouter, Depends, Query
from pcl_core.errors import ConsentRequired, NotFound, ValidationFailed
from pcl_core.schema.audit import EventKind
from pcl_core.service import Hub
from pydantic import BaseModel

from pcl_server.plugins.host import isolation_mode, run_plugin_sync
from pcl_server.plugins.package import load_manifest, manifest_to_snapshot, unpack_package
from pcl_server.plugins.paths import bundled_dir, plugins_root
from pcl_server.rest.auth import get_hub, require_owner

router = APIRouter(prefix="/plugins", tags=["plugins"])


class InstallBody(BaseModel):
    source: str = "bundled"
    plugin_id: str | None = None
    package_b64: str | None = None
    sha256: str | None = None


class ConsentBody(BaseModel):
    schedule: str | None = None


def _consent_preview(inst: dict) -> dict:
    manifest = inst.get("manifest") or {}
    perms = manifest.get("permissions") or {}
    produces = perms.get("produces") or []
    produce_bits = [
        f"{p.get('type')} ({p.get('classification')})" + (f" kind={p.get('kind')}" if p.get("kind") else "")
        for p in produces
        if isinstance(p, dict)
    ]
    warnings: list[str] = []
    if inst.get("origin") == "sideload":
        warnings.append("Unverified developer — this package was side-loaded, not reviewed.")
    if inst.get("isolation") == "reduced":
        warnings.append("Reduced isolation — OS sandbox unavailable; capability mediation still applies.")
    text = (
        f"{manifest.get('name')} wants to: add {', '.join(produce_bits) or 'no objects'} "
        f"· contact {', '.join(perms.get('hosts') or []) or 'no hosts'} "
        f"· run every {perms.get('schedule', 'manual')} "
        + ("· keep its own sign-in tokens" if perms.get("secrets") else "")
    )
    return {
        "installation_id": inst["id"],
        "plugin_id": inst.get("plugin_id"),
        "text": text,
        "permissions": perms,
        "warnings": warnings,
        "unverified": inst.get("origin") == "sideload",
    }


@router.get("")
def list_plugins(hub: Hub = Depends(get_hub), _: str = Depends(require_owner)) -> list[dict]:
    installed = {p.get("plugin_id"): p for p in hub.list_plugins()}
    out = list(hub.list_plugins())
    root = plugins_root()
    if root.is_dir():
        for child in sorted(root.iterdir()):
            manifest_path = child / "plugin.toml"
            if not manifest_path.is_file():
                continue
            try:
                snap = manifest_to_snapshot(load_manifest(manifest_path))
            except Exception:
                continue
            if snap["id"] in installed:
                continue
            out.append({
                "id": None,
                "plugin_id": snap["id"],
                "plugin_version": snap["version"],
                "manifest": snap,
                "origin": "bundled",
                "state": "available",
                "package_dir": str(child),
            })
    return out


@router.post("")
def install_plugin(body: InstallBody, hub: Hub = Depends(get_hub), _: str = Depends(require_owner)) -> dict:
    if body.source == "bundled":
        if not body.plugin_id:
            raise ValidationFailed("plugin_id required")
        existing = next((p for p in hub.list_plugins() if p.get("plugin_id") == body.plugin_id), None)
        if existing:
            raise ValidationFailed(f"{body.plugin_id} is already installed")
        root = bundled_dir(body.plugin_id)
        if root is None:
            raise NotFound(body.plugin_id)
        manifest = manifest_to_snapshot(load_manifest(root / "plugin.toml"))
        inst = hub.create_plugin_installation(manifest, origin="bundled", isolation=isolation_mode())
        inst["package_dir"] = str(root)
        hub.store.put(inst)
        hub.engine.conn.commit()
        return inst
    if body.source == "sideload":
        if not body.package_b64:
            raise ValidationFailed("package_b64 required")
        dest = hub.data_dir / "plugins" / "sideload"
        dest.mkdir(parents=True, exist_ok=True)
        data = base64.b64decode(body.package_b64)
        target = dest / f"tmp-{hub.person_id()}"
        if target.exists():
            import shutil

            shutil.rmtree(target)
        manifest_obj = unpack_package(data, target, body.sha256)
        snap = manifest_to_snapshot(manifest_obj)
        inst = hub.create_plugin_installation(
            snap, origin="sideload", package_sha256=body.sha256 or "", isolation=isolation_mode()
        )
        final = dest / inst["id"]
        target.rename(final)
        inst["package_dir"] = str(final)
        hub.store.put(inst)
        hub.engine.conn.commit()
        return inst
    raise ValidationFailed("unsupported source")


@router.get("/{installation_id}/consent")
def consent_preview(installation_id: str, hub: Hub = Depends(get_hub), _: str = Depends(require_owner)) -> dict:
    return _consent_preview(hub.get_plugin(installation_id))


@router.post("/{installation_id}/consent")
def consent(installation_id: str, body: ConsentBody | None = None, hub: Hub = Depends(get_hub), _: str = Depends(require_owner)) -> dict:
    return hub.consent_plugin(installation_id, schedule=(body.schedule if body else None))


@router.post("/{installation_id}/enable")
def enable(installation_id: str, hub: Hub = Depends(get_hub), _: str = Depends(require_owner)) -> dict:
    inst = hub.get_plugin(installation_id)
    if inst.get("state") == "installed":
        raise ConsentRequired("consent required")
    return hub.set_plugin_state(installation_id, "enabled")


@router.post("/{installation_id}/pause")
def pause(installation_id: str, hub: Hub = Depends(get_hub), _: str = Depends(require_owner)) -> dict:
    return hub.set_plugin_state(installation_id, "paused")


@router.post("/{installation_id}/disable")
def disable(installation_id: str, hub: Hub = Depends(get_hub), _: str = Depends(require_owner)) -> dict:
    return hub.set_plugin_state(installation_id, "disabled")


@router.post("/{installation_id}/sync")
def sync_now(installation_id: str, hub: Hub = Depends(get_hub), _: str = Depends(require_owner)) -> dict:
    return run_plugin_sync(hub, installation_id, reason="manual")


@router.delete("/{installation_id}")
def remove(
    installation_id: str,
    purge_data: bool = Query(False),
    hub: Hub = Depends(get_hub),
    _: str = Depends(require_owner),
) -> dict:
    return hub.remove_plugin(installation_id, purge_data=purge_data)


@router.get("/{installation_id}/runs")
def runs(installation_id: str, hub: Hub = Depends(get_hub), _: str = Depends(require_owner)) -> list[dict]:
    events = hub.ledger.list_events(kind=str(EventKind.PLUGIN_SYNC), limit=50)
    return [e.model_dump(mode="json") for e in events if installation_id in e.refs]


@router.get("/{installation_id}")
def get_plugin(installation_id: str, hub: Hub = Depends(get_hub), _: str = Depends(require_owner)) -> dict:
    return hub.get_plugin(installation_id)


@router.get("/{installation_id}/update")
def update_preview(installation_id: str, hub: Hub = Depends(get_hub), _: str = Depends(require_owner)) -> dict:
    from pcl_server.rest.routers.marketplace import update_preview as mp_preview

    return mp_preview(installation_id, hub, _)


@router.post("/{installation_id}/update")
def apply_update(installation_id: str, hub: Hub = Depends(get_hub), _: str = Depends(require_owner)) -> dict:
    from pcl_server.rest.routers.marketplace import apply_update as mp_update

    return mp_update(installation_id, None, hub, _)
