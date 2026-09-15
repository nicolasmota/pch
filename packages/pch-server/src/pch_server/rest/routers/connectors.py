from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from pch_core.errors import ValidationFailed
from pch_core.service import Hub
from pydantic import BaseModel

from pch_server.rest.auth import get_hub, require_owner
from pch_server.sync.oauth import (
    complete_consent,
    google_oauth_configured,
    require_google_oauth,
    save_google_oauth,
    start_consent,
)
from pch_server.sync.scheduler import run_connector_sync

router = APIRouter(tags=["connectors"])


class CreateConnectorBody(BaseModel):
    provider: str = "google"
    kind: str
    selection: dict | None = None


class PatchConnectorBody(BaseModel):
    selection: dict | None = None
    cadence_minutes: int | None = None
    status: str | None = None


class GoogleOAuthBody(BaseModel):
    client_id: str
    client_secret: str = ""


@router.get("/connectors/oauth/callback")
def oauth_callback(code: str, state: str, hub: Hub = Depends(get_hub)) -> RedirectResponse:
    complete_consent(hub, state, code)
    return RedirectResponse(url="/connectors?connected=1", status_code=303)


@router.get("/connectors/oauth/status")
def oauth_status(hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)) -> dict:
    return {"configured": google_oauth_configured(hub.data_dir)}


@router.put("/connectors/oauth/credentials")
def put_oauth_credentials(
    body: GoogleOAuthBody, hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)
) -> dict:
    save_google_oauth(hub.data_dir, body.client_id, body.client_secret)
    return {"configured": True}


@router.post("/connectors", status_code=202)
def create_connector(
    body: CreateConnectorBody, hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)
) -> dict:
    if body.kind not in ("calendar", "email"):
        raise ValidationFailed("kind must be calendar or email")
    if body.kind == "email" and body.selection is not None:
        if not (
            body.selection.get("labels")
            or body.selection.get("senders")
            or body.selection.get("after")
            or body.selection.get("before")
        ):
            raise ValidationFailed("email selection must include labels, senders, or a date range")
    require_google_oauth(hub.data_dir)
    stored = hub.create_connector(body.provider, body.kind, body.selection)
    consent_url = start_consent(hub, stored["id"], body.kind)
    return {"connector_id": stored["id"], "consent_url": consent_url, "status": stored["status"]}


@router.get("/connectors")
def list_connectors(hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)) -> list[dict]:
    return hub.list_connectors()


@router.get("/connectors/{connector_id}")
def get_connector(
    connector_id: str, hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)
) -> dict:
    return hub.get(connector_id)


@router.patch("/connectors/{connector_id}")
def patch_connector(
    connector_id: str,
    body: PatchConnectorBody,
    hub: Hub = Depends(get_hub),
    _o: str = Depends(require_owner),
) -> dict:
    patch = {k: v for k, v in body.model_dump().items() if v is not None}
    current = hub.get(connector_id)
    if current.get("kind") == "email" and "selection" in patch:
        sel = patch["selection"] or {}
        if not (sel.get("labels") or sel.get("senders") or sel.get("after") or sel.get("before")):
            raise ValidationFailed("email selection must include labels, senders, or a date range")
    return hub.patch(connector_id, patch, None)


@router.post("/connectors/{connector_id}/sync")
def sync_now(
    connector_id: str, hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)
) -> dict:
    return run_connector_sync(hub, connector_id)


@router.post("/connectors/{connector_id}/pause")
def pause(connector_id: str, hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)) -> dict:
    stored = hub.patch(connector_id, {"status": "paused"}, None)
    from pch_core.schema.audit import EventKind

    hub.ledger.append(EventKind.CONNECTOR_PAUSED, "owner", "connector paused", [connector_id])
    hub.engine.conn.commit()
    return stored


@router.post("/connectors/{connector_id}/resume")
def resume(
    connector_id: str, hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)
) -> dict:
    return hub.patch(connector_id, {"status": "active"}, None)


@router.delete("/connectors/{connector_id}")
def disconnect(
    connector_id: str,
    purge: bool = Query(default=False),
    hub: Hub = Depends(get_hub),
    _o: str = Depends(require_owner),
) -> dict:
    return hub.disconnect_connector(connector_id, purge=purge)
