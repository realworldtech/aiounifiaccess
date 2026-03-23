"""Door/Space API manager."""

from __future__ import annotations

from aiounifiaccess.api.base import BaseAPIManager
from aiounifiaccess.models.door import (
    Door,
    DoorGroup,
    DoorGroupTopology,
    EmergencyStatus,
    LockRule,
    LockRuleType,
)


class DoorManager(BaseAPIManager):
    """Manages door/space endpoints (API sections 7.1-7.13)."""

    _BASE_GROUPS = "/api/v1/developer/door_groups"
    _BASE_DOORS = "/api/v1/developer/doors"

    # --- Topology ---

    async def get_topology(self) -> list[DoorGroupTopology]:
        """Get door group topology (7.1)."""
        return await self._get_list_unpaginated(
            f"{self._BASE_GROUPS}/topology", DoorGroupTopology
        )

    # --- Door Groups ---

    async def create_group(
        self, group_name: str, resources: list[dict] | None = None
    ) -> DoorGroup:
        """Create a door group (7.2)."""
        body: dict = {"name": group_name}
        if resources:
            body["resources"] = resources
        return await self._post(self._BASE_GROUPS, json=body, model_cls=DoorGroup)

    async def get_group(self, group_id: str) -> DoorGroup:
        """Get door group details (7.3)."""
        return await self._get(f"{self._BASE_GROUPS}/{group_id}", DoorGroup)

    async def update_group(
        self,
        group_id: str,
        *,
        group_name: str | None = None,
        resources: list[dict] | None = None,
    ) -> None:
        """Update a door group (7.4)."""
        body: dict = {}
        if group_name is not None:
            body["name"] = group_name
        if resources is not None:
            body["resources"] = resources
        await self._put(f"{self._BASE_GROUPS}/{group_id}", json=body)

    async def list_groups(self) -> list[DoorGroup]:
        """List all door groups (7.5)."""
        return await self._get_list_unpaginated(self._BASE_GROUPS, DoorGroup)

    async def delete_group(self, group_id: str) -> None:
        """Delete a door group (7.6)."""
        await self._delete(f"{self._BASE_GROUPS}/{group_id}")

    # --- Doors ---

    async def get(self, door_id: str) -> Door:
        """Get door details (7.7)."""
        return await self._get(f"{self._BASE_DOORS}/{door_id}", Door)

    async def list_all(self) -> list[Door]:
        """List all doors (7.8)."""
        return await self._get_list_unpaginated(self._BASE_DOORS, Door)

    async def unlock(
        self,
        door_id: str,
        *,
        actor_id: str = "",
        actor_name: str = "",
        extra: dict | None = None,
    ) -> None:
        """Remote unlock a door (7.9)."""
        body: dict = {}
        if actor_id:
            body["actor_id"] = actor_id
        if actor_name:
            body["actor_name"] = actor_name
        if extra:
            body["extra"] = extra
        await self._put(f"{self._BASE_DOORS}/{door_id}/unlock", json=body)

    # --- Lock Rules ---

    async def set_lock_rule(
        self,
        door_id: str,
        rule_type: LockRuleType | str,
        *,
        interval: int | None = None,
    ) -> None:
        """Set lock rule for a door (7.10)."""
        body: dict = {"type": str(rule_type)}
        if interval is not None:
            body["interval"] = interval
        await self._put(f"{self._BASE_DOORS}/{door_id}/lock_rule", json=body)

    async def get_lock_rule(self, door_id: str) -> LockRule:
        """Get lock rule for a door (7.11)."""
        return await self._get(f"{self._BASE_DOORS}/{door_id}/lock_rule", LockRule)

    # --- Emergency ---

    async def set_emergency(
        self, *, lockdown: bool = False, evacuation: bool = False
    ) -> None:
        """Set emergency status (7.12)."""
        await self._put(
            f"{self._BASE_DOORS}/emergency",
            json={"lockdown": lockdown, "evacuation": evacuation},
        )

    async def get_emergency(self) -> EmergencyStatus:
        """Get emergency status (7.13)."""
        return await self._get(f"{self._BASE_DOORS}/emergency", EmergencyStatus)
