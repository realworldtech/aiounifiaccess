"""Tests for AccessPolicyManager."""

from unittest.mock import AsyncMock

import pytest

from aiounifiaccess.api.access_policies import AccessPolicyManager
from aiounifiaccess.models.access_policy import (
    AccessPolicy,
    HolidayGroup,
    Schedule,
)


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def manager(mock_session):
    return AccessPolicyManager(mock_session)


class TestPolicyCRUD:
    async def test_create(self, manager, mock_session):
        mock_session._request.return_value = {
            "id": "p1",
            "name": "test",
            "resources": [],
        }
        p = await manager.create("test", [{"id": "d1", "type": "door"}])
        assert isinstance(p, AccessPolicy)

    async def test_get(self, manager, mock_session):
        mock_session._request.return_value = {
            "id": "p1",
            "name": "test",
        }
        p = await manager.get("p1")
        assert p.name == "test"

    async def test_list_all(self, manager, mock_session):
        mock_session._request.return_value = [
            {"id": "p1"},
            {"id": "p2"},
        ]
        policies = await manager.list_all()
        assert len(policies) == 2

    async def test_delete(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager.delete("p1")


class TestHolidayGroups:
    async def test_create(self, manager, mock_session):
        mock_session._request.return_value = {
            "id": "h1",
            "name": "Holidays",
        }
        g = await manager.create_holiday_group("Holidays", [])
        assert isinstance(g, HolidayGroup)


class TestSchedules:
    async def test_create(self, manager, mock_session):
        mock_session._request.return_value = {
            "id": "s1",
            "name": "Weekday",
        }
        s = await manager.create_schedule("Weekday", {})
        assert isinstance(s, Schedule)
