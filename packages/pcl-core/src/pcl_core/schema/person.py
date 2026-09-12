from pydantic import Field

from pcl_core.schema.metadata import UniversalMetadata


class Person(UniversalMetadata):
    name: str = ""
    time_zone: str = "UTC"
    identities: list[str] = Field(default_factory=list)
