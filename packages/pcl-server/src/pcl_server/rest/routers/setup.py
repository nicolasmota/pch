from __future__ import annotations

from fastapi import APIRouter, Depends, Header
from pcl_core.errors import Revoked
from pcl_core.service import Hub

from pcl_server.rest.auth import get_hub, require_owner

router = APIRouter(tags=["setup"])


@router.post("/setup")
def setup(
    body: dict | None = None,
    hub: Hub = Depends(get_hub),
    authorization: str | None = Header(default=None),
) -> dict:
    payload = body or {}
    status = hub.setup_status()
    if status["initialized"] and not payload.get("restart"):
        if not authorization:
            raise Revoked("already initialized")
        actor, is_owner = hub.actor_from_token(authorization.split(" ", 1)[-1])
        if not is_owner:
            raise Revoked()
    return hub.setup(payload.get("name", "Me"), restart=bool(payload.get("restart")))


@router.get("/setup")
def setup_status(hub: Hub = Depends(get_hub)) -> dict:
    return hub.setup_status()


@router.get("/spaces")
def spaces(_owner: str = Depends(require_owner)) -> list[dict]:
    return [{"id": "personal", "kind": "personal"}]


@router.get("/bootstrap")
def bootstrap(hub: Hub = Depends(get_hub)) -> dict:
    """Loopback UI bootstrap: owner token lives in the local process only."""
    return {"owner_token": hub.owner_token, "setup": hub.setup_status()}
