from __future__ import annotations

from typing import Any

from pcl_core.service import Hub


def attach_tools(mcp, hub: Hub) -> None:
    @mcp.tool()
    def search_personal_context(query: str, purpose: str, scope: dict[str, Any] | None = None) -> dict:
        actor = mcp._current_actor  # set per-request
        project = (scope or {}).get("project")
        types = (scope or {}).get("types")
        type_ = types[0] if types else None
        return hub.search(query, type_=type_, project_id=project, actor=actor, purpose=purpose)

    @mcp.tool()
    def get_context_manifest(
        purpose: str,
        requested_capabilities: list[str],
        selectors: dict[str, str] | None = None,
        ttl_seconds: int = 900,
    ) -> dict:
        actor = mcp._current_actor
        return hub.create_manifest(actor, purpose, requested_capabilities, selectors or {}, ttl_seconds)

    @mcp.tool()
    def propose_memory(memory: dict, evidence_refs: list[str], retention: dict | None = None) -> dict:
        actor = mcp._current_actor
        if retention:
            memory = {**memory, "retention": retention}
        return hub.propose_memory(memory, actor, evidence_refs)

    @mcp.tool()
    def set_shared_state(key: str, value: object, ttl_seconds: int, visibility: str) -> dict:
        actor = mcp._current_actor
        return hub.set_state(key, value, ttl_seconds, visibility, actor)

    @mcp.tool()
    def get_shared_state(key: str) -> dict:
        actor = mcp._current_actor
        return hub.get_state(key, actor)

    @mcp.tool()
    def request_approval(intent_summary: str, rationale: str, impact: str) -> dict:
        actor = mcp._current_actor
        return hub.propose_action(
            actor, "approval", intent_summary, {"rationale": rationale, "impact": impact}, [], intent_summary
        )

    @mcp.tool()
    def propose_action(
        kind: str, summary_human: str, payload: dict, basis_refs: list[str], idempotency_key: str
    ) -> dict:
        actor = mcp._current_actor
        return hub.propose_action(actor, kind, summary_human, payload, basis_refs, idempotency_key)

    @mcp.tool()
    def check_action_status(intent_id: str) -> dict:
        intent = hub.get(intent_id)
        return {"status": intent.get("status"), "decided_at": intent.get("decided_at")}
