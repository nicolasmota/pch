from __future__ import annotations

from fastapi import APIRouter, Depends

from pcl_core.service import Hub
from pcl_server.rest.auth import current_actor, get_hub, require_owner

router = APIRouter(tags=["briefs"])


@router.get("/projects/{project_id}/brief")
def brief(
    project_id: str,
    hub: Hub = Depends(get_hub),
    actor: tuple[str, bool] = Depends(current_actor),
) -> dict:
    name, is_owner = actor
    return hub.brief(project_id, actor="owner" if is_owner else name)
