"""Webhook domain models."""

from __future__ import annotations

from enum import Enum

from aiounifiaccess.models.common import BaseAPIModel


class WebhookEventType(str, Enum):
    """Known webhook event types supported by UniFi Access.

    Use ``WebhookEventType.ALL`` to get every subscribable event type.
    """

    DOORBELL_INCOMING = "access.doorbell.incoming"
    DOORBELL_COMPLETED = "access.doorbell.completed"
    DOORBELL_INCOMING_REN = "access.doorbell.incoming.REN"
    DEVICE_DPS_STATUS = "access.device.dps_status"
    DOOR_UNLOCK = "access.door.unlock"
    DEVICE_EMERGENCY_STATUS = "access.device.emergency_status"
    UNLOCK_SCHEDULE_ACTIVATE = "access.unlock_schedule.activate"
    UNLOCK_SCHEDULE_DEACTIVATE = "access.unlock_schedule.deactivate"
    TEMPORARY_UNLOCK_START = "access.temporary_unlock.start"
    TEMPORARY_UNLOCK_END = "access.temporary_unlock.end"
    VISITOR_STATUS_CHANGED = "access.visitor.status.changed"

    @classmethod
    def all(cls) -> list[str]:
        """Return all known webhook event type strings."""
        return [e.value for e in cls]


class WebhookEndpoint(BaseAPIModel):
    id: str = ""
    endpoint: str = ""
    name: str = ""
    secret: str = ""
    events: list[str] = []
    headers: dict[str, str] = {}
