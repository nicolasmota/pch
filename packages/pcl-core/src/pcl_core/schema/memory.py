from enum import StrEnum

from pydantic import Field

from pcl_core.schema.metadata import UniversalMetadata


class MemoryKind(StrEnum):
    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    PROCEDURAL = "procedural"
    SUMMARY = "summary"


class SensitivityFlag(StrEnum):
    FINANCIAL = "financial"
    HEALTH = "health"
    LEGAL = "legal"
    RELATIONSHIP = "relationship"


class Memory(UniversalMetadata):
    kind: MemoryKind = MemoryKind.SEMANTIC
    statement: str
    subject_ref: str | None = None
    project_id: str | None = None
    sensitivity_flags: list[SensitivityFlag] = Field(default_factory=list)
    tombstone: bool = False
