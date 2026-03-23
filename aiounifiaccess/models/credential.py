"""Credential domain models."""

from __future__ import annotations

from typing import Any

from aiounifiaccess.models.common import BaseAPIModel


class NFCCard(BaseAPIModel):
    alias: str = ""
    nfc_id: str = ""
    token: str = ""
    type: str = ""
    is_uid: bool = False
    uid_key: str = ""
    create_time: int = 0
    update_time: int = 0
    status: str = ""
    holder_id: str = ""
    holder_name: str = ""


class NFCCardEnrollmentStatus(BaseAPIModel):
    status: str = ""
    token: str = ""
    nfc_id: str = ""
    session_id: str = ""


class TouchPassBundle(BaseAPIModel):
    bundle_id: str = ""
    bundle_status: str = ""
    device_id: str = ""
    device_name: str = ""
    device_type: int = 0
    source: str = ""


class TouchPass(BaseAPIModel):
    id: str = ""
    card_id: str = ""
    card_name: str = ""
    status: str = ""
    user_name: str = ""
    user_email: str = ""
    user_id: str = ""
    user_status: str = ""
    user_avatar: str = ""
    last_activity: str = ""
    activated_at: Any = None
    expired_at: Any = None
    bundles: list[TouchPassBundle] = []
