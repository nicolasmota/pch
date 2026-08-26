from __future__ import annotations

from fastapi import APIRouter, Depends, Header

from pcl_core.service import Hub
from pcl_server.rest.auth import get_hub, require_owner

router = APIRouter(tags=["memories"])


def _if_match(if_match: str | None) -> int | None:
    if not if_match:
        return None
    try:
        return int(if_match)
    except ValueError:
        return None


@router.get("/memories")
def list_mem(hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)) -> list[dict]:
    return hub.list("memory")


@router.post("/memories")
def create_mem(body: dict, hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)) -> dict:
    return hub.create("memory", body)


@router.get("/memories/{item_id}")
def get_mem(item_id: str, hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)) -> dict:
    return hub.get(item_id)


@router.patch("/memories/{item_id}")
def patch_mem(item_id: str, body: dict, hub: Hub = Depends(get_hub), _o: str = Depends(require_owner), if_match: str | None = Header(default=None, alias="If-Match")) -> dict:
    return hub.patch(item_id, body, _if_match(if_match))


@router.delete("/memories/{item_id}")
def del_mem(item_id: str, hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)) -> dict:
    return hub.delete(item_id)


@router.get("/artifacts")
def list_art(hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)) -> list[dict]:
    return hub.list("artifact")


@router.post("/artifacts")
def create_art(body: dict, hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)) -> dict:
    return hub.create("artifact", body)


@router.get("/preferences")
def list_pref(hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)) -> list[dict]:
    return hub.list("preference")


@router.post("/preferences")
def create_pref(body: dict, hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)) -> dict:
    return hub.create("preference", body)


@router.get("/profile")
def list_prof(hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)) -> list[dict]:
    return hub.list("profile")
