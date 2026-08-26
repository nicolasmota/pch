from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from pcl_core.service import Hub
from pcl_server.rest.auth import current_actor, get_hub

router = APIRouter(tags=["state"])


class StateBody(BaseModel):
    value: object
    ttl_seconds: int = 900
    visibility: str = "private_to_connection"


@router.put("/state/{key}")
def put_state(
    key: str,
    body: StateBody,
    hub: Hub = Depends(get_hub),
    actor: tuple[str, bool] = Depends(current_actor),
) -> dict:
    name, is_owner = actor
    return hub.set_state(key, body.value, body.ttl_seconds, body.visibility, "owner" if is_owner else name)


@router.get("/state/{key}")
def get_state(
    key: str,
    hub: Hub = Depends(get_hub),
    actor: tuple[str, bool] = Depends(current_actor),
) -> dict:
    name, is_owner = actor
    return hub.get_state(key, "owner" if is_owner else name)
