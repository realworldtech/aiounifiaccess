"""Device API manager."""

from __future__ import annotations

from aiounifiaccess.api.base import BaseAPIManager
from aiounifiaccess.models.device import AccessMethodSettings, Device


class DeviceManager(BaseAPIManager):
    """Manages device endpoints (API sections 8.1-8.4)."""

    _BASE = "/api/v1/developer/devices"

    async def list(self, *, refresh: bool = False) -> list[list[Device]]:
        params = {}
        if refresh:
            params["refresh"] = "true"
        data = await self._session._request("GET", self._BASE, params=params or None)
        result = []
        for group in data or []:
            if isinstance(group, list):
                result.append([Device.model_validate(d) for d in group])
            else:
                result.append([Device.model_validate(group)])
        return result

    async def get_settings(self, device_id: str) -> AccessMethodSettings:
        return await self._get(
            f"{self._BASE}/{device_id}/settings", AccessMethodSettings
        )

    async def update_settings(self, device_id: str, access_methods: dict) -> None:
        await self._put(
            f"{self._BASE}/{device_id}/settings",
            json={"access_methods": access_methods},
        )

    async def trigger_doorbell(
        self, device_id: str, *, room_name: str = "", cancel: bool = False
    ) -> None:
        body: dict = {}
        if room_name:
            body["room_name"] = room_name
        if cancel:
            body["cancel"] = True
        await self._post(f"{self._BASE}/{device_id}/doorbell", json=body)
