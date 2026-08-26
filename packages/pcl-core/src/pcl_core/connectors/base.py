from __future__ import annotations

from typing import Any, Protocol


class Connector(Protocol):
    kind: str

    def source_key(self, raw: dict[str, Any], account: dict[str, Any]) -> str: ...

    def map_item(self, raw: dict[str, Any], account: dict[str, Any]) -> dict[str, Any] | None: ...
