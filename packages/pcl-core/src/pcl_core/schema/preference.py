from typing import Any

from pydantic import model_validator

from pcl_core.schema.metadata import UniversalMetadata
from pcl_core.timeutil import validate_interval


class Preference(UniversalMetadata):
    key: str
    value: Any = None
    rationale: str | None = None
    valid_from: str | None = None
    valid_until: str | None = None
    never_true: bool = False

    @model_validator(mode="after")
    def _interval_order(self) -> Preference:
        validate_interval(self.valid_from, self.valid_until)
        return self
