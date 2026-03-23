"""System log API manager."""

from __future__ import annotations

from aiounifiaccess.api.base import BaseAPIManager
from aiounifiaccess.models.system_log import LogResource, LogTopic, SystemLogEntry


class SystemLogManager(BaseAPIManager):
    """Manages system log endpoints (API sections 9.2-9.5)."""

    _BASE = "/api/v1/developer/system/logs"

    async def fetch(
        self,
        *,
        topic: LogTopic | str = LogTopic.ALL,
        since: int | None = None,
        until: int | None = None,
        actor_id: str = "",
        page_num: int = 1,
        page_size: int = 25,
    ) -> list[SystemLogEntry]:
        body: dict = {"topic": topic, "page_num": page_num, "page_size": page_size}
        if since is not None:
            body["since"] = since
        if until is not None:
            body["until"] = until
        if actor_id:
            body["actor_id"] = actor_id
        data = await self._session._request("POST", self._BASE, json=body)
        return [SystemLogEntry.model_validate(item) for item in (data or [])]

    async def export(
        self,
        *,
        topic: LogTopic | str = LogTopic.ALL,
        since: int | None = None,
        until: int | None = None,
        timezone: str = "",
        actor_id: str = "",
    ) -> bytes:
        body: dict = {"topic": str(topic)}
        if since is not None:
            body["since"] = since
        if until is not None:
            body["until"] = until
        if timezone:
            body["timezone"] = timezone
        if actor_id:
            body["actor_id"] = actor_id
        return await self._get_bytes(f"{self._BASE}/export", json=body)

    async def get_resource(self, resource_id: str) -> LogResource:
        return await self._get(f"{self._BASE}/resource/{resource_id}", LogResource)

    async def get_static_resource(self, path: str) -> bytes:
        return await self._get_bytes(f"/api/v1/developer/system/static/{path}")
