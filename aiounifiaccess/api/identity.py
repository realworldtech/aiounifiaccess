"""Identity API manager."""

from __future__ import annotations

from aiounifiaccess.api.base import BaseAPIManager
from aiounifiaccess.models.identity import IdentityResource, ResourceType


class IdentityManager(BaseAPIManager):
    """Manages identity endpoints (API sections 10.1-10.6)."""

    _BASE_USERS = "/api/v1/developer/users"
    _BASE_GROUPS = "/api/v1/developer/user_groups"

    def _parse_resource_map(
        self, data: dict | list | None
    ) -> dict[str, list[IdentityResource]]:
        result: dict[str, list[IdentityResource]] = {}
        if isinstance(data, dict):
            for key, items in data.items():
                result[key] = [IdentityResource.model_validate(item) for item in items]
        return result

    async def send_invitations(self, invitations: list[dict]) -> None:
        await self._post(f"{self._BASE_USERS}/identity/invitations", json=invitations)

    async def list_resources(
        self, resource_type: ResourceType | str = ""
    ) -> dict[str, list[IdentityResource]]:
        params = {}
        if resource_type:
            params["resource_type"] = str(resource_type)
        data = await self._session._request(
            "GET",
            f"{self._BASE_USERS}/identity/assignments",
            params=params or None,
        )
        return self._parse_resource_map(data)

    async def assign_to_user(
        self,
        user_id: str,
        resource_type: ResourceType | str,
        resource_ids: list[str],
    ) -> None:
        await self._post(
            f"{self._BASE_USERS}/{user_id}/identity/assignments",
            json={
                "resource_type": str(resource_type),
                "resource_ids": resource_ids,
            },
        )

    async def get_user_assignments(
        self, user_id: str
    ) -> dict[str, list[IdentityResource]]:
        data = await self._session._request(
            "GET", f"{self._BASE_USERS}/{user_id}/identity/assignments"
        )
        return self._parse_resource_map(data)

    async def assign_to_group(
        self,
        group_id: str,
        resource_type: ResourceType | str,
        resource_ids: list[str],
    ) -> None:
        await self._post(
            f"{self._BASE_GROUPS}/{group_id}/identity/assignments",
            json={
                "resource_type": str(resource_type),
                "resource_ids": resource_ids,
            },
        )

    async def get_group_assignments(
        self, group_id: str
    ) -> dict[str, list[IdentityResource]]:
        data = await self._session._request(
            "GET", f"{self._BASE_GROUPS}/{group_id}/identity/assignments"
        )
        return self._parse_resource_map(data)
