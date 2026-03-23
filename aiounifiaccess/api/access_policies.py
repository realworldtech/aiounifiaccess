"""Access policy API manager."""

from __future__ import annotations

from aiounifiaccess.api.base import BaseAPIManager
from aiounifiaccess.models.access_policy import (
    AccessPolicy,
    HolidayGroup,
    Schedule,
)


class AccessPolicyManager(BaseAPIManager):
    """Manages access policy endpoints (API sections 5.2-5.18)."""

    _BASE = "/api/v1/developer/access_policies"
    _HOLIDAYS = "/api/v1/developer/holiday_groups"
    _SCHEDULES = "/api/v1/developer/schedules"

    async def create(
        self,
        name: str,
        resources: list[dict],
        schedule_id: str = "",
    ) -> AccessPolicy:
        body: dict = {"name": name, "resource": resources}
        if schedule_id:
            body["schedule_id"] = schedule_id
        return await self._post(self._BASE, json=body, model_cls=AccessPolicy)

    async def update(
        self,
        policy_id: str,
        *,
        name: str | None = None,
        resources: list[dict] | None = None,
        schedule_id: str | None = None,
    ) -> None:
        body: dict = {}
        if name is not None:
            body["name"] = name
        if resources is not None:
            body["resource"] = resources
        if schedule_id is not None:
            body["schedule_id"] = schedule_id
        await self._put(f"{self._BASE}/{policy_id}", json=body)

    async def delete(self, policy_id: str) -> None:
        await self._delete(f"{self._BASE}/{policy_id}")

    async def get(self, policy_id: str) -> AccessPolicy:
        return await self._get(f"{self._BASE}/{policy_id}", AccessPolicy)

    async def list_all(self) -> list[AccessPolicy]:
        return await self._get_list_unpaginated(self._BASE, AccessPolicy)

    async def create_holiday_group(
        self, name: str, holidays: list[dict]
    ) -> HolidayGroup:
        return await self._post(
            self._HOLIDAYS,
            json={"name": name, "holidays": holidays},
            model_cls=HolidayGroup,
        )

    async def update_holiday_group(
        self,
        group_id: str,
        *,
        name: str | None = None,
        holidays: list[dict] | None = None,
    ) -> None:
        body: dict = {}
        if name is not None:
            body["name"] = name
        if holidays is not None:
            body["holidays"] = holidays
        await self._put(f"{self._HOLIDAYS}/{group_id}", json=body)

    async def delete_holiday_group(self, group_id: str) -> None:
        await self._delete(f"{self._HOLIDAYS}/{group_id}")

    async def get_holiday_group(self, group_id: str) -> HolidayGroup:
        return await self._get(f"{self._HOLIDAYS}/{group_id}", HolidayGroup)

    async def list_holiday_groups(self) -> list[HolidayGroup]:
        return await self._get_list_unpaginated(self._HOLIDAYS, HolidayGroup)

    async def create_schedule(self, name: str, week_schedule: dict) -> Schedule:
        return await self._post(
            self._SCHEDULES,
            json={"name": name, "week_schedule": week_schedule},
            model_cls=Schedule,
        )

    async def update_schedule(
        self,
        schedule_id: str,
        *,
        name: str | None = None,
        week_schedule: dict | None = None,
    ) -> None:
        body: dict = {}
        if name is not None:
            body["name"] = name
        if week_schedule is not None:
            body["week_schedule"] = week_schedule
        await self._put(f"{self._SCHEDULES}/{schedule_id}", json=body)

    async def get_schedule(self, schedule_id: str) -> Schedule:
        return await self._get(f"{self._SCHEDULES}/{schedule_id}", Schedule)

    async def list_schedules(self) -> list[Schedule]:
        return await self._get_list_unpaginated(self._SCHEDULES, Schedule)

    async def delete_schedule(self, schedule_id: str) -> None:
        await self._delete(f"{self._SCHEDULES}/{schedule_id}")
