"""Access policy domain models."""

from __future__ import annotations

from aiounifiaccess.models.common import BaseAPIModel


class PolicyResource(BaseAPIModel):
    id: str = ""
    type: str = ""


class AccessPolicy(BaseAPIModel):
    id: str = ""
    name: str = ""
    resources: list[PolicyResource] = []
    schedule_id: str = ""


class Holiday(BaseAPIModel):
    name: str = ""
    start: int = 0
    end: int = 0
    is_all_day: bool = False


class HolidayGroup(BaseAPIModel):
    id: str = ""
    name: str = ""
    holidays: list[Holiday] = []


class TimeRange(BaseAPIModel):
    start: str = ""
    end: str = ""


class Schedule(BaseAPIModel):
    id: str = ""
    name: str = ""
    week_schedule: dict[str, list[TimeRange]] = {}
