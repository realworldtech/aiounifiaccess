"""Door domain models."""

from __future__ import annotations

from enum import Enum

from aiounifiaccess.models.common import BaseAPIModel


class DoorLockStatus(str, Enum):
    LOCK = "lock"
    UNLOCK = "unlock"


class DoorPositionStatus(str, Enum):
    NONE = "none"
    OPEN = "open"
    CLOSE = "close"


class LockRuleType(str, Enum):
    KEEP_LOCK = "keep_lock"
    KEEP_UNLOCK = "keep_unlock"
    CUSTOM = "custom"
    RESET = "reset"
    LOCK_EARLY = "lock_early"
    LOCK_NOW = "lock_now"
    SCHEDULE = "schedule"


class DoorGroupType(str, Enum):
    BUILDING = "building"
    ACCESS = "access"


class Door(BaseAPIModel):
    id: str = ""
    name: str = ""
    full_name: str = ""
    floor_id: str = ""
    type: str = ""
    is_bind_hub: bool = False
    door_lock_relay_status: DoorLockStatus | None = None
    door_position_status: DoorPositionStatus | None = None
    camera_resource_ids: list[str] = []
    timezone: str = ""
    location_type: str = ""
    extras: dict = {}


class DoorGroupResource(BaseAPIModel):
    id: str = ""
    type: str = ""
    name: str = ""


class DoorGroup(BaseAPIModel):
    id: str = ""
    name: str = ""
    type: DoorGroupType | None = None
    resources: list[DoorGroupResource] = []


class FloorResource(BaseAPIModel):
    id: str = ""
    name: str = ""
    type: str = ""
    is_bind_hub: bool = False


class Floor(BaseAPIModel):
    id: str = ""
    name: str = ""
    type: str = ""
    resources: list[FloorResource] = []


class DoorGroupTopology(BaseAPIModel):
    id: str = ""
    name: str = ""
    type: str = ""
    resource_topologies: list[Floor] = []


class LockRule(BaseAPIModel):
    type: LockRuleType | None = None
    ended_time: int | None = None


class EmergencyStatus(BaseAPIModel):
    lockdown: bool = False
    evacuation: bool = False
