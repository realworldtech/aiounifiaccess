"""Pydantic models for UniFi Access API resources."""

from aiounifiaccess.models.access_policy import (
    AccessPolicy,
    Holiday,
    HolidayGroup,
    PolicyResource,
    Schedule,
    TimeRange,
)
from aiounifiaccess.models.credential import (
    NFCCard,
    NFCCardEnrollmentStatus,
    TouchPass,
    TouchPassBundle,
)
from aiounifiaccess.models.device import (
    AccessMethods,
    AccessMethodSettings,
    Device,
    FaceSettings,
    PinCodeSettings,
)
from aiounifiaccess.models.door import (
    Door,
    DoorGroup,
    DoorGroupTopology,
    DoorGroupType,
    DoorLockStatus,
    DoorPositionStatus,
    EmergencyStatus,
    Floor,
    LockRule,
    LockRuleType,
)
from aiounifiaccess.models.identity import IdentityResource, ResourceType
from aiounifiaccess.models.system_log import (
    LogActor,
    LogEvent,
    LogResource,
    LogTopic,
    SystemLogEntry,
)
from aiounifiaccess.models.user import (
    AccessPolicyRef,
    User,
    UserGroup,
    UserStatus,
)
from aiounifiaccess.models.visitor import Visitor, VisitorStatus
from aiounifiaccess.models.webhook import WebhookEndpoint, WebhookEventType

__all__ = [
    "AccessMethodSettings",
    "AccessMethods",
    "AccessPolicy",
    "AccessPolicyRef",
    "Device",
    "Door",
    "DoorGroup",
    "DoorGroupTopology",
    "DoorGroupType",
    "DoorLockStatus",
    "DoorPositionStatus",
    "EmergencyStatus",
    "FaceSettings",
    "Floor",
    "Holiday",
    "HolidayGroup",
    "IdentityResource",
    "LockRule",
    "LockRuleType",
    "LogActor",
    "LogEvent",
    "LogResource",
    "LogTopic",
    "NFCCard",
    "NFCCardEnrollmentStatus",
    "PinCodeSettings",
    "PolicyResource",
    "ResourceType",
    "Schedule",
    "SystemLogEntry",
    "TimeRange",
    "TouchPass",
    "TouchPassBundle",
    "User",
    "UserGroup",
    "UserStatus",
    "Visitor",
    "VisitorStatus",
    "WebhookEndpoint",
    "WebhookEventType",
]
