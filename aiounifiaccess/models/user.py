"""User domain models."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import field_validator

from aiounifiaccess.models.common import BaseAPIModel
from aiounifiaccess.models.credential import TouchPass


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    DEACTIVATED = "DEACTIVATED"


class NFCCard(BaseAPIModel):
    id: str = ""
    token: str = ""
    type: str = ""


class LicensePlate(BaseAPIModel):
    id: str = ""
    credential: str = ""
    credential_type: str = ""
    credential_status: str = ""


class PINCode(BaseAPIModel):
    token: str = ""


class AccessPolicyResource(BaseAPIModel):
    id: str = ""
    type: str = ""


class AccessPolicyRef(BaseAPIModel):
    id: str = ""
    name: str = ""
    resources: list[AccessPolicyResource] = []
    schedule_id: str = ""


class User(BaseAPIModel):
    id: str = ""
    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    alias: str = ""
    user_email: str = ""
    email_status: str = ""
    phone: str = ""
    employee_number: str = ""
    onboard_time: datetime | None = None
    status: UserStatus = UserStatus.ACTIVE
    nfc_cards: list[NFCCard] = []
    license_plates: list[LicensePlate] = []
    pin_code: PINCode | None = None
    touch_pass: TouchPass | None = None
    access_policy_ids: list[str] = []
    access_policies: list[AccessPolicyRef] = []

    @field_validator("onboard_time", mode="before")
    @classmethod
    def parse_onboard_time(cls, v):
        if v is None or v == 0:
            return None
        if isinstance(v, (int, float)):
            return datetime.fromtimestamp(v, tz=timezone.utc)
        return v


class UserGroup(BaseAPIModel):
    id: str = ""
    name: str = ""
    full_name: str = ""
    up_id: str = ""
    up_ids: list[str] = []
