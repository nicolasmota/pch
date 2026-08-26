from enum import StrEnum

from pydantic import BaseModel, Field


class EventKind(StrEnum):
    CONTEXT_REQUEST = "context.request"
    CONTEXT_DISCLOSE = "context.disclose"
    CONTEXT_CONTRACT = "context.contract"
    POLICY_DECISION = "policy.decision"
    MEMORY_PROPOSED = "memory.proposed"
    MEMORY_ACCEPTED = "memory.accepted"
    MEMORY_REJECTED = "memory.rejected"
    STATE_WRITE = "state.write"
    APPROVAL_DECIDED = "approval.decided"
    ACTION_INTENT = "action.intent"
    ACTION_EXECUTED = "action.executed"
    ACTION_FAILED = "action.failed"
    GRANT_CREATED = "grant.created"
    GRANT_REVOKED = "grant.revoked"
    CONNECTION_PAIRED = "connection.paired"
    CONNECTION_REVOKED = "connection.revoked"
    OBJECT_WRITE = "object.write"
    EXPORT_CREATED = "export.created"
    IMPORT_STAGED = "import.staged"
    IMPORT_APPLIED = "import.applied"
    SETUP = "setup"
    CONNECTOR_CONNECTED = "connector.connected"
    CONNECTOR_DISCONNECTED = "connector.disconnected"
    CONNECTOR_PAUSED = "connector.paused"
    CONNECTOR_SYNC = "connector.sync"
    CONNECTION_RECIPE_ISSUED = "connection.recipe_issued"
    PLUGIN_INSTALL = "plugin.install"
    PLUGIN_CONSENT = "plugin.consent"
    PLUGIN_LIFECYCLE = "plugin.lifecycle"
    PLUGIN_SYNC = "plugin.sync"
    PLUGIN_DENIED = "plugin.denied"
    PLUGIN_KILLSWITCH = "plugin.killswitch"
    MARKETPLACE_CATALOG_CHECK = "marketplace.catalog_check"


class AuditEvent(BaseModel):
    seq: int
    kind: EventKind
    actor: str
    refs: list[str] = Field(default_factory=list)
    summary_human: str
    prev_hash: str
    hash: str
    created_at: str
    extra: dict = Field(default_factory=dict)
