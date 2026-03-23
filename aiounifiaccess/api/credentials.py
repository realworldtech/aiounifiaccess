"""Credential API manager."""

from __future__ import annotations

import aiohttp

from aiounifiaccess.api.base import BaseAPIManager
from aiounifiaccess.models.common import PaginatedResponse
from aiounifiaccess.models.credential import NFCCard, NFCCardEnrollmentStatus, TouchPass


class CredentialManager(BaseAPIManager):
    """Manages credential endpoints (API sections 6.1-6.19)."""

    async def generate_pin_code(self) -> str:
        data = await self._session._request("POST", "/api/v1/developer/pin_codes")
        return data if isinstance(data, str) else str(data)

    async def enroll_nfc_card(self, device_id: str) -> NFCCardEnrollmentStatus:
        return await self._post(
            "/api/v1/developer/nfc_cards/sessions",
            json={"device_id": device_id},
            model_cls=NFCCardEnrollmentStatus,
        )

    async def get_nfc_enrollment_status(
        self, session_id: str
    ) -> NFCCardEnrollmentStatus:
        return await self._get(
            f"/api/v1/developer/nfc_cards/sessions/{session_id}",
            NFCCardEnrollmentStatus,
        )

    async def cancel_nfc_enrollment(self, session_id: str) -> None:
        await self._delete(f"/api/v1/developer/nfc_cards/sessions/{session_id}")

    async def get_nfc_card(self, token: str) -> NFCCard:
        return await self._get(f"/api/v1/developer/nfc_cards/{token}", NFCCard)

    async def list_nfc_cards(
        self, *, page_num: int = 1, page_size: int = 25
    ) -> tuple[list[NFCCard], PaginatedResponse]:
        return await self._get_list(
            "/api/v1/developer/nfc_cards",
            NFCCard,
            page_num=page_num,
            page_size=page_size,
        )

    async def delete_nfc_card(self, token: str) -> None:
        await self._delete(f"/api/v1/developer/nfc_cards/{token}")

    async def update_nfc_card(self, token: str, *, alias: str) -> None:
        await self._put(f"/api/v1/developer/nfc_cards/{token}", json={"alias": alias})

    async def list_touch_passes(
        self, *, page_num: int = 1, page_size: int = 25
    ) -> tuple[list[TouchPass], PaginatedResponse]:
        return await self._get_list(
            "/api/v1/developer/touch_passes",
            TouchPass,
            page_num=page_num,
            page_size=page_size,
        )

    async def search_touch_pass(self, keyword: str) -> list[TouchPass]:
        data = await self._session._request(
            "POST", "/api/v1/developer/touch_passes/search", json={"keyword": keyword}
        )
        return [TouchPass.model_validate(item) for item in (data or [])]

    async def list_assignable_touch_passes(self) -> list[TouchPass]:
        return await self._get_list_unpaginated(
            "/api/v1/developer/touch_passes/assignable", TouchPass
        )

    async def update_touch_pass(
        self, card_id: str, *, card_name: str | None = None
    ) -> None:
        body: dict = {}
        if card_name is not None:
            body["card_name"] = card_name
        await self._put(f"/api/v1/developer/touch_passes/{card_id}", json=body)

    async def get_touch_pass(self, card_id: str) -> TouchPass:
        return await self._get(f"/api/v1/developer/touch_passes/{card_id}", TouchPass)

    async def purchase_touch_passes(self, quantity: int) -> None:
        await self._post(
            "/api/v1/developer/touch_passes/purchase", json={"quantity": quantity}
        )

    async def download_qr_code(self, user_or_visitor_id: str) -> bytes:
        return await self._get_bytes(f"/api/v1/developer/qr_codes/{user_or_visitor_id}")

    async def import_nfc_cards(self, file_path: str) -> list[NFCCard]:
        import asyncio
        import pathlib

        path = pathlib.Path(file_path)
        file_bytes = await asyncio.to_thread(path.read_bytes)
        data = aiohttp.FormData()
        data.add_field("file", file_bytes, filename=path.name)
        result = await self._session._request_file(
            "POST", "/api/v1/developer/nfc_cards/import", data=data
        )
        return [NFCCard.model_validate(item) for item in (result or [])]
