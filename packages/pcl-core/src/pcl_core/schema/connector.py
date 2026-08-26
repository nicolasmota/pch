from enum import StrEnum
from typing import Any

from pydantic import Field

from pcl_core.schema.metadata import UniversalMetadata


class ConnectorProvider(StrEnum):
    GOOGLE = "google"


class ConnectorKind(StrEnum):
    CALENDAR = "calendar"
    EMAIL = "email"


class ConnectorStatus(StrEnum):
    PENDING_CONSENT = "pending_consent"
    ACTIVE = "active"
    PAUSED = "paused"
    RECONNECT_NEEDED = "reconnect_needed"
    DISCONNECTED = "disconnected"


class ConnectorAccount(UniversalMetadata):
    provider: ConnectorProvider = ConnectorProvider.GOOGLE
    kind: ConnectorKind
    account_label: str = ""
    status: ConnectorStatus = ConnectorStatus.PENDING_CONSENT
    selection: dict[str, Any] = Field(default_factory=dict)
    cadence_minutes: int = 15
    sync_cursor: str | None = None
    last_sync: dict[str, Any] | None = None
