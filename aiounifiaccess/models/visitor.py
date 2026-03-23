"""Visitor domain models."""

from __future__ import annotations

from enum import Enum
from typing import Any

from aiounifiaccess.models.common import BaseAPIModel


class VisitorStatus(int, Enum):
    UPCOMING = 1
    VISITED = 2
    VISITING = 3
    CANCELLED = 4
    NO_VISIT = 5
    ACTIVE = 6


class VisitReason(str, Enum):
    INTERVIEW = "Interview"
    BUSINESS = "Business"
    COOPERATION = "Cooperation"
    OTHERS = "Others"


class VisitorNFCCard(BaseAPIModel):
    id: str = ""
    token: str = ""
    type: str = ""


class VisitorLicensePlate(BaseAPIModel):
    id: str = ""
    credential: str = ""
    credential_type: str = ""
    credential_status: str = ""


class VisitorPINCode(BaseAPIModel):
    token: str = ""


class VisitorResource(BaseAPIModel):
    id: str = ""
    type: str = ""
    name: str = ""


class Visitor(BaseAPIModel):
    id: str = ""
    first_name: str = ""
    last_name: str = ""
    avatar: str = ""
    mobile_phone: str = ""
    email: str = ""
    company: str = ""
    status: VisitorStatus | None = None
    start_time: int | None = None
    end_time: int | None = None
    visit_reason: str = ""
    nfc_cards: list[VisitorNFCCard] = []
    pin_code: VisitorPINCode | None = None
    qr_code: Any = None
    license_plates: list[VisitorLicensePlate] = []
    access_policy_ids: list[str] = []
    resources: list[VisitorResource] = []
    remarks: str = ""
