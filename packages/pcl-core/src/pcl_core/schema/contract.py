from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator

from pcl_core.timeutil import parse_instant


class OmissionCategory(StrEnum):
    SCOPE_NOT_GRANTED = "scope_not_granted"
    CLASSIFICATION_CEILING = "classification_ceiling"
    CAPABILITY_MISSING = "capability_missing"
    POLICY_EXCLUSION = "policy_exclusion"


class ContextQuery(BaseModel):
    purpose: str
    subject_ref: str | None = None
    max_items: int | None = Field(default=None, ge=1)
    as_of: str | None = None

    model_config = {"extra": "forbid"}

    @field_validator("purpose")
    @classmethod
    def purpose_must_be_nonempty(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("purpose is required")
        return stripped

    @field_validator("as_of")
    @classmethod
    def as_of_must_be_instant(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            return None
        try:
            parse_instant(stripped)
        except ValueError as exc:
            raise ValueError("as_of must be an ISO-8601 UTC instant") from exc
        return stripped


class ItemRef(BaseModel):
    id: str
    type: str
    summary: str


class SituationRef(BaseModel):
    project_id: str
    title: str
    status: str
    operational_phase: str | None = None
    current_step: str | None = None
    situation_intent: str | None = None


class ConflictPair(BaseModel):
    item_ids: list[str] = Field(min_length=2)
    reason: str


class ScopeSummary(BaseModel):
    grant_id: str
    selectors: dict[str, Any] = Field(default_factory=dict)
    classification_ceiling: str
    capabilities: list[str] = Field(default_factory=list)
    summary_human: str | None = None


class OmissionNote(BaseModel):
    category: OmissionCategory
    label: str
    count: int = Field(ge=1)


class Citation(BaseModel):
    id: str
    role: str = "self"
    version: str | None = None


class ContractItem(BaseModel):
    ref: ItemRef
    body: dict[str, Any]
    citation: list[Citation] = Field(min_length=1)
    authority: str
    confidence: float | None = None
    freshness: datetime
    untrusted: bool = False


class RelationRef(BaseModel):
    id: str
    relation_type: str
    from_: ItemRef = Field(alias="from")
    to: ItemRef

    model_config = {"populate_by_name": True, "serialize_by_alias": True}


class ContextContract(BaseModel):
    contract_id: str
    purpose: str
    situation: SituationRef | None
    candidates: list[SituationRef] = Field(default_factory=list)
    goals: list[ContractItem] = Field(default_factory=list)
    preferences: list[ContractItem] = Field(default_factory=list)
    memories: list[ContractItem] = Field(default_factory=list)
    decisions: list[ContractItem] = Field(default_factory=list)
    constraints: list[ContractItem] = Field(default_factory=list)
    state: list[ContractItem] = Field(default_factory=list)
    relations: list[RelationRef] = Field(default_factory=list)
    references: list[ItemRef] = Field(default_factory=list)
    conflicts: list[ConflictPair] = Field(default_factory=list)
    granted_scope: ScopeSummary
    omissions: list[OmissionNote] = Field(default_factory=list)
    assembled_at: datetime
