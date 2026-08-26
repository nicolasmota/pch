from __future__ import annotations

from pcl_core.errors import PolicyDenied
from pcl_core.schema.action import ActionIntent, IntentStatus


def assert_executable(intent: ActionIntent | dict) -> None:
    status = intent.status if isinstance(intent, ActionIntent) else intent.get("status")
    if status != IntentStatus.APPROVED and status != "approved":
        raise PolicyDenied("action is not approved")
