from pydantic import Field

from pcl_core.schema.metadata import UniversalMetadata


class ContextSpace(UniversalMetadata):
    name: str = "Personal"
    kind: str = "personal"
    key_hint: str = Field(default="", description="non-secret key metadata")
