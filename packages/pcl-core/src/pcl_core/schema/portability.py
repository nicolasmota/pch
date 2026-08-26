from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class StagingStatus(StrEnum):
    STAGED = "staged"
    APPLIED = "applied"
    DISCARDED = "discarded"


class ResolutionChoice(StrEnum):
    MERGE = "merge"
    REPLACE = "replace"
    KEEP_SEPARATE = "keep_separate"
    SKIP = "skip"


class ExportRecord(BaseModel):
    id: str
    space_id: str = "personal"
    filters: dict[str, Any] = Field(default_factory=dict)
    pca_version: str = "0.1.0"
    manifest_hash: str = ""
    created_at: str
    path: str = ""


class ImportStaging(BaseModel):
    id: str
    space_id: str = "personal"
    archive_manifest: dict[str, Any] = Field(default_factory=dict)
    item_resolutions: list[dict[str, Any]] = Field(default_factory=list)
    conflicts: list[dict[str, Any]] = Field(default_factory=list)
    records: list[dict[str, Any]] = Field(default_factory=list)
    status: StagingStatus = StagingStatus.STAGED
    created_at: str
