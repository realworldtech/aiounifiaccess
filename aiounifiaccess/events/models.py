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


# --- Device update events (WebSocket, undocumented) ---


class DeviceConfig(BaseAPIModel):
    """A single config entry from a device update event."""

    device_id: str = ""
    key: str = ""
    value: str = ""
    tag: str = ""
    update_time: str = ""
    create_time: str = ""


class DeviceLocation(BaseAPIModel):
    """Location info nested in device update events."""

    unique_id: str = ""
    name: str = ""
    up_id: str = ""
    timezone: str = ""
    location_type: str = ""
    extra_type: str = ""
    full_name: str = ""
    level: int = 0


class DeviceUpdateData(BaseAPIModel):
    """Full device state from access.data.device.update.

    The ``configs`` list contains key/value pairs grouped by ``tag``:

    - ``hub_action``: DPS states (``input_dX_dps``), lock relays
      (``output_dX_lock_relay``), buttons, emergency inputs
    - ``hub_power``: power supply readings, PoE port power
    - ``wiring_state``: wiring detection for each port
    - ``device_setting``: alarm sound, capture settings
    - ``credential``: SSH, cert fingerprint, NaCl keys
    - ``uah_config``: emergency mode settings
    - ``device_extra``: device alias
    """

    unique_id: str = ""
    name: str = ""
    alias: str = ""
    device_type: str = ""
    connected_uah_id: str = ""
    location_id: str = ""
    firmware: str = ""
    version: str = ""
    ip: str = ""
    mac: str = ""
    hw_type: str = ""
    start_time: int = 0
    last_seen: int = 0
    is_online: bool = False
    is_connected: bool = False
    is_adopted: bool = False
    is_managed: bool = False
    is_rebooting: bool = False
    is_unavailable: bool = False
    location: DeviceLocation = DeviceLocation()
    configs: list[DeviceConfig] = []
    capabilities: list[str] = []
    model: str = ""
    revision: str = ""


class DeviceUpdateEvent(BaseEvent):
    """access.data.device.update - periodic full device state.

    Sent over WebSocket when device state changes. The ``configs``
    list contains DPS states, lock relay states, power readings, and
    wiring states for all ports on the hub.

    Example: check door position sensor state::

        @client.on(DeviceUpdateEvent)
        async def handle(event: DeviceUpdateEvent):
            for cfg in event.data.configs:
                if cfg.tag == "hub_action" and cfg.key.endswith("_dps"):
                    print(f"{cfg.key}: {cfg.value}")
    """

    event: str = "access.data.device.update"
    data: DeviceUpdateData = DeviceUpdateData()


class DeviceUpdateV2Meta(BaseAPIModel):
    """Metadata from v2 device update events."""

    object_type: str = ""
    target_field: list[str] | None = None
    all_field: bool = False
    id: str = ""
    source: str = ""


class DeviceUpdateV2Data(BaseAPIModel):
    """Lightweight device info from access.data.v2.device.update."""

    name: str = ""
    alias: str = ""
    id: str = ""
    ip: str = ""
    mac: str = ""
    online: bool = False
    adopting: bool = False
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
    category: list[str] | None = None


class DeviceUpdateV2Event(BaseEvent):
    """access.data.v2.device.update - lightweight device state change.

    A lighter variant of ``DeviceUpdateEvent`` with a ``meta`` field
    indicating which fields changed.
    """

    event: str = "access.data.v2.device.update"
    data: DeviceUpdateV2Data = DeviceUpdateV2Data()
    meta: DeviceUpdateV2Meta = DeviceUpdateV2Meta()


# --- Location update events (WebSocket, undocumented) ---


class LocationState(BaseAPIModel):
    """State info from a location update."""

    dps_connected: bool = False
    emergency: dict[str, Any] = {}


class LocationUpdateV2Data(BaseAPIModel):
    """Location state from access.data.v2.location.update."""

    id: str = ""
    location_type: str = ""
    name: str = ""
    up_id: str = ""
    extras: dict[str, Any] | None = None
    device_ids: list[str] | None = None
    state: LocationState = LocationState()


class LocationUpdateV2Event(BaseEvent):
    """access.data.v2.location.update - location state change.

    Sent frequently over WebSocket with door/building state updates.
    """

    event: str = "access.data.v2.location.update"
    data: LocationUpdateV2Data = LocationUpdateV2Data()
    meta: DeviceUpdateV2Meta = DeviceUpdateV2Meta()


class LocationUpdateEvent(BaseEvent):
    """access.data.location.update - full location state."""

    event: str = "access.data.location.update"
    data: dict[str, Any] | None = None


# --- Settings update events (WebSocket, undocumented) ---


class SettingUpdateEvent(BaseEvent):
    """access.data.setting.update - controller settings change."""

    event: str = "access.data.setting.update"
    data: dict[str, Any] | None = None


class RawEvent(BaseEvent):
    """Fallback for unrecognised event types. Preserves raw JSON."""

    data: dict[str, Any] | None = None


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
    "access.data.device.update": DeviceUpdateEvent,
    "access.data.v2.device.update": DeviceUpdateV2Event,
    "access.data.v2.location.update": LocationUpdateV2Event,
    "access.data.location.update": LocationUpdateEvent,
    "access.data.setting.update": SettingUpdateEvent,
}


def parse_event(data: dict) -> BaseEvent:
    """Parse a raw event dict into a typed event model.

    Unknown event types are returned as RawEvent.
    """
    event_type = data.get("event", "")
    model_cls = _EVENT_MAP.get(event_type, RawEvent)
    return model_cls.model_validate(data)
