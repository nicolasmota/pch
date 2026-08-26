from enum import StrEnum

from pydantic import BaseModel, Field

from pcl_core.schema.memory import Memory


class ProposalStatus(StrEnum):
    PENDING = "pending"
    AUTO_ACCEPTED = "auto_accepted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class MemoryProposal(BaseModel):
    id: str
    space_id: str = "personal"
    proposed_memory: Memory
    evidence_refs: list[str] = Field(default_factory=list)
    submitted_by: str
    status: ProposalStatus = ProposalStatus.PENDING
    policy_verdict: str = "needs_review"
    conflict_ids: list[str] = Field(default_factory=list)
    created_at: str
