"""Server API manager."""

from __future__ import annotations

import asyncio
import pathlib

import aiohttp

from aiounifiaccess.api.base import BaseAPIManager


class ServerManager(BaseAPIManager):
    """Manages server endpoints (API sections 12.1-12.2)."""

    async def upload_certificate(self, file_path: str) -> None:
        path = pathlib.Path(file_path)
        file_bytes = await asyncio.to_thread(path.read_bytes)
        data = aiohttp.FormData()
        data.add_field("file", file_bytes, filename=path.name)
        await self._post_file("/api/v1/developer/certs", data)

    async def delete_certificate(self) -> None:
        await self._delete("/api/v1/developer/certs")
