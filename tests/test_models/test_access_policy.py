"""Tests for AccessPolicy models."""

from aiounifiaccess.models.access_policy import (
    AccessPolicy,
    HolidayGroup,
    Schedule,
)


class TestAccessPolicy:
    def test_parse(self):
        p = AccessPolicy.model_validate(
            {
                "id": "p1",
                "name": "test",
                "resources": [{"id": "d1", "type": "door"}],
                "schedule_id": "s1",
            }
        )
        assert p.name == "test"
        assert len(p.resources) == 1


class TestHolidayGroup:
    def test_parse(self):
        g = HolidayGroup.model_validate(
            {
                "id": "h1",
                "name": "Holidays",
                "holidays": [{"name": "NYE", "start": 100, "end": 200}],
            }
        )
        assert g.name == "Holidays"
        assert len(g.holidays) == 1


class TestSchedule:
    def test_parse(self):
        s = Schedule.model_validate(
            {"id": "s1", "name": "Weekday", "week_schedule": {}}
        )
        assert s.name == "Weekday"
