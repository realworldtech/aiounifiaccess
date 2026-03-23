"""Visitor API manager."""

from __future__ import annotations

from typing import AsyncIterator

from aiounifiaccess.api.base import BaseAPIManager
from aiounifiaccess.models.common import PaginatedResponse
from aiounifiaccess.models.visitor import Visitor, VisitorStatus


class VisitorManager(BaseAPIManager):
    """Manages visitor endpoints (API sections 4.2-4.14)."""

    _BASE = "/api/v1/developer/visitors"

    async def create(
        self,
        first_name: str,
        last_name: str,
        *,
        mobile_phone: str = "",
        email: str = "",
        company: str = "",
        start_time: int | None = None,
        end_time: int | None = None,
        visit_reason: str = "",
        remarks: str = "",
        access_policy_ids: list[str] | None = None,
    ) -> Visitor:
        """Register a new visitor (4.2)."""
        body: dict = {"first_name": first_name, "last_name": last_name}
        if mobile_phone:
            body["mobile_phone"] = mobile_phone
        if email:
            body["email"] = email
        if company:
            body["company"] = company
        if start_time is not None:
            body["start_time"] = start_time
        if end_time is not None:
            body["end_time"] = end_time
        if visit_reason:
            body["visit_reason"] = visit_reason
        if remarks:
            body["remarks"] = remarks
        if access_policy_ids is not None:
            body["access_policy_ids"] = access_policy_ids
        return await self._post(self._BASE, json=body, model_cls=Visitor)

    async def get(self, visitor_id: str) -> Visitor:
        return await self._get(f"{self._BASE}/{visitor_id}", Visitor)

    async def list(
        self,
        *,
        page_num: int = 1,
        page_size: int = 25,
        keyword: str = "",
    ) -> tuple[list[Visitor], PaginatedResponse]:
        params = {"page_num": page_num, "page_size": page_size}
        if keyword:
            params["keyword"] = keyword
        return await self._get_list(self._BASE, Visitor, **params)

    async def list_all(self, *, page_size: int = 25) -> AsyncIterator[Visitor]:
        async for v in self._get_list_all(self._BASE, Visitor, page_size=page_size):
            yield v

    async def update(
        self,
        visitor_id: str,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        mobile_phone: str | None = None,
        email: str | None = None,
        company: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        visit_reason: str | None = None,
        remarks: str | None = None,
        status: VisitorStatus | int | None = None,
    ) -> None:
        """Update visitor details (4.5)."""
        body: dict = {}
        if first_name is not None:
            body["first_name"] = first_name
        if last_name is not None:
            body["last_name"] = last_name
        if mobile_phone is not None:
            body["mobile_phone"] = mobile_phone
        if email is not None:
            body["email"] = email
        if company is not None:
            body["company"] = company
        if start_time is not None:
            body["start_time"] = start_time
        if end_time is not None:
            body["end_time"] = end_time
        if visit_reason is not None:
            body["visit_reason"] = visit_reason
        if remarks is not None:
            body["remarks"] = remarks
        if status is not None:
            body["status"] = status
        await self._put(f"{self._BASE}/{visitor_id}", json=body)

    async def delete(self, visitor_id: str) -> None:
        await self._delete(f"{self._BASE}/{visitor_id}")

    async def assign_nfc_card(
        self, visitor_id: str, token: str, *, force_add: bool = False
    ) -> None:
        body: dict = {"token": token}
        if force_add:
            body["force_add"] = True
        await self._put(f"{self._BASE}/{visitor_id}/nfc_cards", json=body)

    async def unassign_nfc_card(self, visitor_id: str, token: str) -> None:
        await self._put(
            f"{self._BASE}/{visitor_id}/nfc_cards/delete",
            json={"token": token},
        )

    async def assign_pin_code(self, visitor_id: str, pin_code: str) -> None:
        await self._put(
            f"{self._BASE}/{visitor_id}/pin_codes",
            json={"pin_code": pin_code},
        )

    async def unassign_pin_code(self, visitor_id: str) -> None:
        await self._delete(f"{self._BASE}/{visitor_id}/pin_codes")

    async def assign_qr_code(
        self, visitor_id: str, *, is_one_time: bool = False
    ) -> None:
        body: dict = {}
        if is_one_time:
            body["is_one_time"] = True
        await self._put(f"{self._BASE}/{visitor_id}/qr_codes", json=body)

    async def unassign_qr_code(self, visitor_id: str) -> None:
        await self._delete(f"{self._BASE}/{visitor_id}/qr_codes")

    async def assign_license_plates(
        self, visitor_id: str, license_plates: list[str]
    ) -> None:
        await self._put(
            f"{self._BASE}/{visitor_id}/license_plates",
            json={"license_plates": license_plates},
        )

    async def unassign_license_plate(
        self, visitor_id: str, license_plate_id: str
    ) -> None:
        await self._delete(
            f"{self._BASE}/{visitor_id}/license_plates/{license_plate_id}"
        )
