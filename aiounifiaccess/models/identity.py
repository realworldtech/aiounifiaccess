"""Identity domain models."""

from __future__ import annotations

from enum import Enum
from typing import Any

from aiounifiaccess.models.common import BaseAPIModel


class ResourceType(str, Enum):
    EV_STATION = "ev_station"
    VPN = "vpn"
    WIFI = "wifi"
    CAMERA = "camera"


class IdentityResource(BaseAPIModel):
    id: str = ""
    name: str = ""
    short_name: str = ""
    deleted: bool = False
    metadata: Any = None
