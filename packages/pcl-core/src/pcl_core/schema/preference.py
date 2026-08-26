from typing import Any

from pcl_core.schema.metadata import UniversalMetadata


class Preference(UniversalMetadata):
    key: str
    value: Any = None
    rationale: str | None = None
