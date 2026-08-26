from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from pcl_core.ids import new_id
from pcl_core.schema.audit import EventKind
from pcl_core.service import Hub
from pcl_core.timeutil import now_iso
from pcl_server.rest.auth import get_hub, require_owner

router = APIRouter(tags=["portability"])


class ExportBody(BaseModel):
    passphrase: str
    filters: dict = {}


class StageBody(BaseModel):
    path: str
    passphrase: str


class ApplyBody(BaseModel):
    resolutions: list[dict] = []


@router.post("/export")
def export(body: ExportBody, hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)) -> dict:
    from pca.export import export_archive

    dest = hub.data_dir / "exports" / f"space-{now_iso().replace(':', '')}.pca"
    result = export_archive(hub, dest, body.passphrase, body.filters)
    hub.ledger.append(EventKind.EXPORT_CREATED, "owner", "export created", extra=result)
    hub.engine.conn.commit()
    return result


@router.post("/import/stage")
def stage(body: StageBody, hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)) -> dict:
    from pca.import_ import open_archive
    from pca.resolve import plan_resolutions
    from pca.untrusted import mark_untrusted

    opened = open_archive(Path(body.path), body.passphrase)
    records = [mark_untrusted(r) for r in opened["records"]]
    existing = {r["id"]: r for t in ("memory", "project", "goal") for r in hub.list(t)}
    for t in ("commitment", "decision", "preference", "artifact", "profile", "person"):
        for r in hub.list(t):
            existing[r["id"]] = r
    plan = plan_resolutions(records, set(existing), existing)
    staging_id = new_id("import_staging")
    payload = {
        "id": staging_id,
        "type": "import_staging",
        "archive_manifest": opened["manifest"],
        "records": records,
        "conflicts": [p for p in plan if p["action"] == "conflict"],
        "item_resolutions": plan,
        "status": "staged",
        "space_id": "personal",
        "owner": hub.person_id(),
        "labels": [],
        "classification": "private",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "source_refs": [],
        "confidence": 1.0,
        "authority": "source_imported",
        "retention": {"mode": "until_revoked"},
        "policy_tags": [],
        "version": 1,
    }
    with hub.engine.tx():
        hub.store.put(payload)
        hub.ledger.append(EventKind.IMPORT_STAGED, "owner", "import staged", [staging_id])
    return payload


@router.get("/import/staging/{staging_id}")
def get_staging(staging_id: str, hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)) -> dict:
    return hub.get(staging_id)


@router.post("/import/staging/{staging_id}/apply")
def apply(
    staging_id: str, body: ApplyBody, hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)
) -> dict:
    from pca.resolve import apply_resolution

    staging = hub.get(staging_id)
    choices = {r.get("id"): r.get("action", "merge") for r in body.resolutions}
    applied = 0
    with hub.engine.tx():
        for item in staging.get("item_resolutions") or []:
            action = choices.get(item["id"], item["action"])
            if action in ("skip", "conflict"):
                if action == "conflict":
                    continue
                continue
            rec = apply_resolution(action if action != "create" else "merge", item["record"])
            rec["authority"] = rec.get("authority") or "source_imported"
            hub.store.put(rec)
            applied += 1
        staging["status"] = "applied"
        hub.store.put(staging)
        hub.ledger.append(EventKind.IMPORT_APPLIED, "owner", f"imported {applied}", [staging_id])
    return {"applied": applied, "staging_id": staging_id}
