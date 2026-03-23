"""User API manager."""

from __future__ import annotations

from typing import AsyncIterator

import aiohttp

from aiounifiaccess.api.base import BaseAPIManager
from aiounifiaccess.models.common import PaginatedResponse
from aiounifiaccess.models.user import AccessPolicyRef, User, UserGroup, UserStatus


class UserManager(BaseAPIManager):
    """Manages user endpoints (API sections 3.2-3.30)."""

    _BASE = "/api/v1/developer/users"

    # --- User CRUD ---

    async def create(
        self,
        first_name: str,
        last_name: str,
        user_email: str = "",
        employee_number: str = "",
        onboard_time: int | None = None,
    ) -> User:
        """Register a new user (3.2)."""
        body: dict = {"first_name": first_name, "last_name": last_name}
        if user_email:
            body["user_email"] = user_email
        if employee_number:
            body["employee_number"] = employee_number
        if onboard_time is not None:
            body["onboard_time"] = onboard_time
        return await self._post(self._BASE, json=body, model_cls=User)

    async def update(
        self,
        user_id: str,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        user_email: str | None = None,
        employee_number: str | None = None,
        onboard_time: int | None = None,
        status: UserStatus | str | None = None,
    ) -> None:
        """Update user details (3.3)."""
        body: dict = {}
        if first_name is not None:
            body["first_name"] = first_name
        if last_name is not None:
            body["last_name"] = last_name
        if user_email is not None:
            body["user_email"] = user_email
        if employee_number is not None:
            body["employee_number"] = employee_number
        if onboard_time is not None:
            body["onboard_time"] = onboard_time
        if status is not None:
            body["status"] = status
        await self._put(f"{self._BASE}/{user_id}", json=body)

    async def get(self, user_id: str, *, expand_access_policy: bool = False) -> User:
        """Fetch user details (3.4)."""
        params = {}
        if expand_access_policy:
            params["expand[]"] = "access_policy"
        return await self._get(f"{self._BASE}/{user_id}", User, **params)

    async def list(
        self,
        *,
        page_num: int = 1,
        page_size: int = 25,
        expand_access_policy: bool = False,
    ) -> tuple[list[User], PaginatedResponse]:
        """Fetch all users with pagination (3.5)."""
        params = {"page_num": page_num, "page_size": page_size}
        if expand_access_policy:
            params["expand[]"] = "access_policy"
        return await self._get_list(self._BASE, User, **params)

    async def list_all(
        self, *, expand_access_policy: bool = False, page_size: int = 25
    ) -> AsyncIterator[User]:
        """Auto-paginate through all users (3.5)."""
        params = {}
        if expand_access_policy:
            params["expand[]"] = "access_policy"
        async for user in self._get_list_all(
            self._BASE, User, page_size=page_size, **params
        ):
            yield user

    async def delete(self, user_id: str) -> None:
        """Delete a user (3.23)."""
        await self._delete(f"{self._BASE}/{user_id}")

    async def search(
        self,
        keyword: str,
        *,
        page_num: int = 1,
        page_size: int = 25,
    ) -> tuple[list[User], PaginatedResponse]:
        """Search users by keyword (3.24)."""
        raw = await self._session._request_raw(
            "POST",
            f"{self._BASE}/search",
            json={"keyword": keyword},
            params={"page_num": page_num, "page_size": page_size},
        )
        resp = PaginatedResponse.from_raw(raw)
        items = [User.model_validate(item) for item in resp.items]
        return items, resp

    # --- Access Policies ---

    async def assign_access_policy(
        self, user_id: str, access_policy_ids: list[str]
    ) -> None:
        """Assign access policies to user (3.6)."""
        await self._put(
            f"{self._BASE}/{user_id}/access_policies",
            json={"access_policy_ids": access_policy_ids},
        )

    async def get_access_policies(
        self, user_id: str, *, only_user_policies: bool = False
    ) -> list[AccessPolicyRef]:
        """Get access policies for user (3.20)."""
        params = {}
        if only_user_policies:
            params["only_user_policies"] = "true"
        return await self._get_list_unpaginated(
            f"{self._BASE}/{user_id}/access_policies", AccessPolicyRef, **params
        )

    # --- NFC Cards ---

    async def assign_nfc_card(
        self, user_id: str, token: str, *, force_add: bool = False
    ) -> None:
        """Assign NFC card to user (3.7)."""
        body: dict = {"token": token}
        if force_add:
            body["force_add"] = True
        await self._put(f"{self._BASE}/{user_id}/nfc_cards", json=body)

    async def unassign_nfc_card(self, user_id: str, token: str) -> None:
        """Unassign NFC card from user (3.8). Uses PUT per API."""
        await self._put(
            f"{self._BASE}/{user_id}/nfc_cards/delete", json={"token": token}
        )

    # --- PIN Codes ---

    async def assign_pin_code(self, user_id: str, pin_code: str) -> None:
        """Assign PIN code to user (3.9)."""
        await self._put(f"{self._BASE}/{user_id}/pin_code", json={"pin_code": pin_code})

    async def unassign_pin_code(self, user_id: str) -> None:
        """Unassign PIN code from user (3.10)."""
        await self._put(f"{self._BASE}/{user_id}/pin_code/delete")

    # --- Touch Passes ---

    async def assign_touch_pass(self, user_id: str, card_id: str) -> None:
        """Assign touch pass to user (3.25)."""
        await self._put(f"{self._BASE}/{user_id}/touch_pass", json={"card_id": card_id})

    async def unassign_touch_pass(self, user_id: str, card_id: str) -> None:
        """Unassign touch pass from user (3.26)."""
        await self._put(
            f"{self._BASE}/{user_id}/touch_pass/delete", json={"card_id": card_id}
        )

    async def batch_assign_touch_passes(self, assignments: list[dict]) -> None:
        """Batch assign touch passes (3.27)."""
        await self._post(f"{self._BASE}/touch_passes", json=assignments)

    # --- License Plates ---

    async def assign_license_plates(
        self, user_id: str, license_plates: list[str]
    ) -> None:
        """Assign license plates to user (3.28)."""
        await self._put(
            f"{self._BASE}/{user_id}/license_plates",
            json={"license_plates": license_plates},
        )

    async def unassign_license_plates(
        self, user_id: str, license_plate_ids: list[str]
    ) -> None:
        """Unassign license plates from user (3.29)."""
        await self._put(
            f"{self._BASE}/{user_id}/license_plates/delete",
            json={"license_plate_ids": license_plate_ids},
        )

    # --- Profile Picture ---

    async def upload_profile_picture(self, user_id: str, file_path: str) -> None:
        """Upload profile picture for user (3.30)."""
        import asyncio
        import pathlib

        path = pathlib.Path(file_path)
        file_bytes = await asyncio.to_thread(path.read_bytes)
        data = aiohttp.FormData()
        data.add_field("file", file_bytes, filename=path.name)
        await self._post_file(f"{self._BASE}/{user_id}/profile_picture", data)

    # --- User Groups ---

    async def create_group(self, name: str, up_id: str = "") -> UserGroup:
        """Create a user group (3.11)."""
        body: dict = {"name": name}
        if up_id:
            body["up_id"] = up_id
        return await self._post(f"{self._BASE}_groups", json=body, model_cls=UserGroup)

    async def list_groups(self) -> list[UserGroup]:
        """List all user groups (3.12)."""
        return await self._get_list_unpaginated(f"{self._BASE}_groups", UserGroup)

    async def get_group(self, group_id: str) -> UserGroup:
        """Get user group details (3.13)."""
        return await self._get(f"{self._BASE}_groups/{group_id}", UserGroup)

    async def update_group(
        self, group_id: str, *, name: str | None = None, up_id: str | None = None
    ) -> None:
        """Update a user group (3.14)."""
        body: dict = {}
        if name is not None:
            body["name"] = name
        if up_id is not None:
            body["up_id"] = up_id
        await self._put(f"{self._BASE}_groups/{group_id}", json=body)

    async def delete_group(self, group_id: str) -> None:
        """Delete a user group (3.15)."""
        await self._delete(f"{self._BASE}_groups/{group_id}")

    async def assign_to_group(self, group_id: str, user_ids: list[str]) -> None:
        """Assign users to group (3.16)."""
        await self._post(
            f"{self._BASE}_groups/{group_id}/users",
            json={"user_ids": user_ids},
        )

    async def unassign_from_group(self, group_id: str, user_ids: list[str]) -> None:
        """Remove users from group (3.17)."""
        await self._put(
            f"{self._BASE}_groups/{group_id}/users/delete",
            json={"user_ids": user_ids},
        )

    async def get_group_users(self, group_id: str) -> list[User]:
        """Get users in a group (3.18)."""
        return await self._get_list_unpaginated(
            f"{self._BASE}_groups/{group_id}/users", User
        )

    async def get_group_all_users(self, group_id: str) -> list[User]:
        """Get all users in group and subgroups (3.19)."""
        return await self._get_list_unpaginated(
            f"{self._BASE}_groups/{group_id}/all_users", User
        )

    async def assign_group_access_policy(
        self, group_id: str, access_policy_ids: list[str]
    ) -> None:
        """Assign access policies to group (3.21)."""
        await self._put(
            f"{self._BASE}_groups/{group_id}/access_policies",
            json={"access_policy_ids": access_policy_ids},
        )

    async def get_group_access_policies(self, group_id: str) -> list[AccessPolicyRef]:
        """Get access policies for group (3.22)."""
        return await self._get_list_unpaginated(
            f"{self._BASE}_groups/{group_id}/access_policies", AccessPolicyRef
        )
