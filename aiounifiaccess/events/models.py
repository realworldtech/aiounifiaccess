"""Pydantic models for WebSocket and webhook event payloads."""

from __future__ import annotations

from typing import Any

from aiounifiaccess.models.common import BaseAPIModel

# --- Base event ---


class BaseEvent(BaseAPIModel):
    """Base for all events."""

    event: str = ""
    event_object_id: str = ""
    receiver_id: str = ""
    save_to_history: bool = False


# --- WebSocket notification events (flat data) ---


class RemoteViewData(BaseAPIModel):
    channel: str = ""
    token: str = ""
    device_id: str = ""
    device_type: str = ""
    device_name: str = ""
    door_name: str = ""
    controller_id: str = ""
    floor_name: str = ""
    request_id: str = ""
    clear_request_id: str = ""
    in_or_out: str = ""
    create_time: int = 0
    reason_code: int = 0
    door_guard_ids: list[str] = []
    connected_uah_id: str = ""
    room_id: str = ""
    host_device_mac: str = ""


class RemoteViewEvent(BaseEvent):
    """access.remote_view - doorbell ring notification."""

    event: str = "access.remote_view"
    data: RemoteViewData = RemoteViewData()


class RemoteViewChangeData(BaseAPIModel):
    reason_code: int = 0
    remote_call_request_id: str = ""


class RemoteViewChangeEvent(BaseEvent):
    """access.remote_view.change - doorbell status change."""

    event: str = "access.remote_view.change"
    data: RemoteViewChangeData = RemoteViewChangeData()


class RemoteUnlockData(BaseAPIModel):
    unique_id: str = ""
    name: str = ""
    up_id: str = ""
    timezone: str = ""
    location_type: str = ""
    extra_type: str = ""
    full_name: str = ""
    level: int = 0
    work_time: str = ""
    work_time_id: str = ""
    extras: dict[str, Any] = {}


class RemoteUnlockEvent(BaseEvent):
    """access.data.device.remote_unlock - admin unlocked a door remotely."""

    event: str = "access.data.device.remote_unlock"
    data: RemoteUnlockData = RemoteUnlockData()


# --- Connection / status events ---


class BaseInfoData(BaseAPIModel):
    top_log_count: int = 0


class BaseInfoEvent(BaseEvent):
    """access.base.info - connection handshake / status."""

    event: str = "access.base.info"
    data: BaseInfoData = BaseInfoData()


# --- Webhook events (structured location/device/actor/object data) ---


class EventLocation(BaseAPIModel):
    id: str = ""
    location_type: str = ""
    name: str = ""
    up_id: str = ""
    extras: dict[str, Any] = {}
    device_ids: list[str] | None = None


class EventDevice(BaseAPIModel):
    name: str = ""
    alias: str = ""
    id: str = ""
    ip: str = ""
    mac: str = ""
    online: bool = False
    device_type: str = ""
    connected_hub_id: str = ""
    location_id: str = ""
    firmware: str = ""
    version: str = ""
    guid: str = ""
    start_time: int = 0
    hw_type: str = ""
    revision: str = ""
    cap: Any = None


class EventActor(BaseAPIModel):
    id: str = ""
    name: str = ""
    type: str = ""


class EventObject(BaseAPIModel):
    authentication_type: str = ""
    authentication_value: str = ""
    policy_id: str = ""
    policy_name: str = ""
    reader_id: str = ""
    result: str = ""
    reason_code: int | None = None
    status: str = ""


class WebhookEventData(BaseAPIModel):
    location: EventLocation = EventLocation()
    device: EventDevice = EventDevice()
    actor: EventActor = EventActor()
    object: EventObject = EventObject()


class BaseWebhookEvent(BaseEvent):
    """Base for webhook events with structured data."""

    data: WebhookEventData = WebhookEventData()


class DoorUnlockEvent(BaseWebhookEvent):
    """access.door.unlock"""

    event: str = "access.door.unlock"


class DoorPositionEvent(BaseWebhookEvent):
    """access.device.dps_status"""

    event: str = "access.device.dps_status"


class DoorbellIncomingEvent(BaseWebhookEvent):
    """access.doorbell.incoming"""

    event: str = "access.doorbell.incoming"


class DoorbellCompletedEvent(BaseWebhookEvent):
    """access.doorbell.completed"""

    event: str = "access.doorbell.completed"


class DoorbellRENEvent(BaseWebhookEvent):
    """access.doorbell.incoming.REN"""

    event: str = "access.doorbell.incoming.REN"


class EmergencyStatusEvent(BaseWebhookEvent):
    """access.device.emergency_status"""

    event: str = "access.device.emergency_status"


class UnlockScheduleActivateEvent(BaseWebhookEvent):
    """access.unlock_schedule.activate"""

    event: str = "access.unlock_schedule.activate"


class UnlockScheduleDeactivateEvent(BaseWebhookEvent):
    """access.unlock_schedule.deactivate"""

    event: str = "access.unlock_schedule.deactivate"


class TemporaryUnlockStartEvent(BaseWebhookEvent):
    """access.temporary_unlock.start"""

    event: str = "access.temporary_unlock.start"


class TemporaryUnlockEndEvent(BaseWebhookEvent):
    """access.temporary_unlock.end"""

    event: str = "access.temporary_unlock.end"


class VisitorStatusChangedEvent(BaseWebhookEvent):
    """access.visitor.status.changed"""

    event: str = "access.visitor.status.changed"


class RawEvent(BaseEvent):
    """Fallback for unrecognised event types. Preserves raw JSON."""

    data: dict[str, Any] = {}


# --- Event routing ---

_EVENT_MAP: dict[str, type[BaseEvent]] = {
    "access.base.info": BaseInfoEvent,
    "access.remote_view": RemoteViewEvent,
    "access.remote_view.change": RemoteViewChangeEvent,
    "access.data.device.remote_unlock": RemoteUnlockEvent,
    "access.door.unlock": DoorUnlockEvent,
    "access.device.dps_status": DoorPositionEvent,
    "access.doorbell.incoming": DoorbellIncomingEvent,
    "access.doorbell.completed": DoorbellCompletedEvent,
    "access.doorbell.incoming.REN": DoorbellRENEvent,
    "access.device.emergency_status": EmergencyStatusEvent,
    "access.unlock_schedule.activate": UnlockScheduleActivateEvent,
    "access.unlock_schedule.deactivate": UnlockScheduleDeactivateEvent,
    "access.temporary_unlock.start": TemporaryUnlockStartEvent,
    "access.temporary_unlock.end": TemporaryUnlockEndEvent,
    "access.visitor.status.changed": VisitorStatusChangedEvent,
}


def parse_event(data: dict) -> BaseEvent:
    """Parse a raw event dict into a typed event model.

    Unknown event types are returned as RawEvent.
    """
    event_type = data.get("event", "")
    model_cls = _EVENT_MAP.get(event_type, RawEvent)
    return model_cls.model_validate(data)
