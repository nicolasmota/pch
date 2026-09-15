from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pch_core.service import Hub

from pch_server.rest.auth import get_hub, require_owner

router = APIRouter(tags=["operational"])


@router.get("/operational-proposals")
def list_operational_proposals(
    status: str | None = Query(default=None),
    hub: Hub = Depends(get_hub),
    _o: str = Depends(require_owner),
) -> list[dict]:
    return hub.list_operational_proposals(status)


@router.post("/operational-proposals/{proposal_id}/accept")
def accept_operational_proposal(
    proposal_id: str,
    hub: Hub = Depends(get_hub),
    _o: str = Depends(require_owner),
) -> dict:
    return hub.decide_operational_proposal(proposal_id, True)


@router.post("/operational-proposals/{proposal_id}/reject")
def reject_operational_proposal(
    proposal_id: str,
    hub: Hub = Depends(get_hub),
    _o: str = Depends(require_owner),
) -> dict:
    return hub.decide_operational_proposal(proposal_id, False)
