from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from pcl_core.service import Hub
from pcl_server.rest.auth import current_actor, get_hub, require_owner

router = APIRouter(tags=["actions"])


class IntentBody(BaseModel):
    kind: str
    summary_human: str
    payload: dict = {}
    basis_refs: list[str] = []
    idempotency_key: str


class DecideBody(BaseModel):
    decision: str


class ResultBody(BaseModel):
    status: str


@router.post("/actions/intents")
def propose(
    body: IntentBody,
    hub: Hub = Depends(get_hub),
    actor: tuple[str, bool] = Depends(current_actor),
) -> dict:
    name, is_owner = actor
    if is_owner:
        from pcl_core.errors import ValidationFailed

        raise ValidationFailed("owner does not propose agent actions")
    return hub.propose_action(name, body.kind, body.summary_human, body.payload, body.basis_refs, body.idempotency_key)


@router.get("/approvals")
def approvals(
    status: str | None = Query(default=None),
    hub: Hub = Depends(get_hub),
    _o: str = Depends(require_owner),
) -> list[dict]:
    rows = hub.list("action_intent")
    if status:
        rows = [r for r in rows if r.get("status") == status]
    return rows


@router.post("/approvals/{intent_id}/decide")
def decide(
    intent_id: str, body: DecideBody, hub: Hub = Depends(get_hub), _o: str = Depends(require_owner)
) -> dict:
    return hub.decide_approval(intent_id, body.decision == "approved")


@router.post("/actions/intents/{intent_id}/result")
def result(
    intent_id: str,
    body: ResultBody,
    hub: Hub = Depends(get_hub),
    actor: tuple[str, bool] = Depends(current_actor),
) -> dict:
    name, is_owner = actor
    return hub.action_result(intent_id, body.status, "owner" if is_owner else name)
