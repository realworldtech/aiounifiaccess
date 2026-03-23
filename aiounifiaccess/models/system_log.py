"""System log domain models."""

from __future__ import annotations

from enum import Enum

from aiounifiaccess.models.common import BaseAPIModel


class LogTopic(str, Enum):
    ALL = "all"
    DOOR_OPENINGS = "door_openings"
    CRITICAL = "critical"
    UPDATES = "updates"
    DEVICE_EVENTS = "device_events"
    ADMIN_ACTIVITY = "admin_activity"
    VISITOR = "visitor"


class LogEvent(BaseAPIModel):
    type: str = ""
    display_message: str = ""
    result: str = ""
    published: str = ""
    tag: str = ""
    reason: str = ""


class LogActor(BaseAPIModel):
    id: str = ""
    type: str = ""
    display_name: str = ""
    alternate_id: str = ""
    alternate_name: str = ""
    avatar: str = ""
    sso_picture: str = ""


class LogAuthentication(BaseAPIModel):
    credential_provider: str = ""
    issuer: str = ""


class LogTarget(BaseAPIModel):
    type: str = ""
    id: str = ""
    display_name: str = ""
    alternate_id: str = ""
    alternate_name: str = ""


class LogSource(BaseAPIModel):
    event: LogEvent = LogEvent()
    actor: LogActor = LogActor()
    authentication: LogAuthentication = LogAuthentication()
    target: LogTarget = LogTarget()


class SystemLogEntry(BaseAPIModel):
    timestamp: str = ""
    id: str = ""
    source: LogSource = LogSource()


class LogResource(BaseAPIModel):
    video_record: str = ""
    video_record_thumbnail: str = ""
    created_at: str = ""
    updated_at: str = ""
