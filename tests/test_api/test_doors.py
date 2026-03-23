"""Tests for DoorManager."""

from unittest.mock import AsyncMock

import pytest

from aiounifiaccess.api.doors import DoorManager
from aiounifiaccess.models.door import (
    Door,
    DoorGroup,
    DoorGroupTopology,
    EmergencyStatus,
    LockRule,
)


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def manager(mock_session):
    return DoorManager(mock_session)


class TestDoorCRUD:
    async def test_get(self, manager, mock_session):
        mock_session._request.return_value = {
            "id": "d1",
            "name": "Front Door",
            "door_lock_relay_status": "lock",
        }
        door = await manager.get("d1")
        assert isinstance(door, Door)
        assert door.name == "Front Door"
        mock_session._request.assert_called_once_with(
            "GET", "/api/v1/developer/doors/d1", params=None
        )

    async def test_list_all(self, manager, mock_session):
        mock_session._request.return_value = [
            {"id": "d1", "name": "Door 1"},
            {"id": "d2", "name": "Door 2"},
        ]
        doors = await manager.list_all()
        assert len(doors) == 2
        assert isinstance(doors[0], Door)

    async def test_unlock(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager.unlock("d1", actor_id="user1", actor_name="Admin")
        mock_session._request.assert_called_once_with(
            "PUT",
            "/api/v1/developer/doors/d1/unlock",
            json={"actor_id": "user1", "actor_name": "Admin"},
        )


class TestDoorGroups:
    async def test_create_group(self, manager, mock_session):
        mock_session._request.return_value = {
            "id": "g1",
            "name": "Building A",
        }
        group = await manager.create_group("Building A")
        assert isinstance(group, DoorGroup)
        assert group.name == "Building A"

    async def test_list_groups(self, manager, mock_session):
        mock_session._request.return_value = [
            {"id": "g1", "name": "A"},
            {"id": "g2", "name": "B"},
        ]
        groups = await manager.list_groups()
        assert len(groups) == 2

    async def test_get_topology(self, manager, mock_session):
        mock_session._request.return_value = [
            {
                "id": "t1",
                "name": "Building",
                "type": "building",
                "resource_topologies": [],
            }
        ]
        topo = await manager.get_topology()
        assert len(topo) == 1
        assert isinstance(topo[0], DoorGroupTopology)


class TestLockRules:
    async def test_set_lock_rule(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager.set_lock_rule("d1", "keep_lock")
        mock_session._request.assert_called_once_with(
            "PUT",
            "/api/v1/developer/doors/d1/lock_rule",
            json={"type": "keep_lock"},
        )

    async def test_set_lock_rule_with_interval(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager.set_lock_rule("d1", "custom", interval=3600)
        mock_session._request.assert_called_once_with(
            "PUT",
            "/api/v1/developer/doors/d1/lock_rule",
            json={"type": "custom", "interval": 3600},
        )

    async def test_get_lock_rule(self, manager, mock_session):
        mock_session._request.return_value = {"type": "keep_lock"}
        rule = await manager.get_lock_rule("d1")
        assert isinstance(rule, LockRule)


class TestEmergency:
    async def test_set_emergency(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager.set_emergency(lockdown=True)
        mock_session._request.assert_called_once_with(
            "PUT",
            "/api/v1/developer/doors/emergency",
            json={"lockdown": True, "evacuation": False},
        )

    async def test_get_emergency(self, manager, mock_session):
        mock_session._request.return_value = {
            "lockdown": False,
            "evacuation": False,
        }
        status = await manager.get_emergency()
        assert isinstance(status, EmergencyStatus)
        assert status.lockdown is False
