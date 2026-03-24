"""Tests for Door models."""

from aiounifiaccess.models.door import (
    Door,
    DoorGroup,
    DoorGroupTopology,
    DoorGroupType,
    DoorLockStatus,
    DoorPositionStatus,
    EmergencyStatus,
    LockRule,
    LockRuleType,
)


class TestDoorEnums:
    def test_lock_status(self):
        assert DoorLockStatus.LOCK == "lock"
        assert DoorLockStatus.UNLOCK == "unlock"

    def test_position_status(self):
        assert DoorPositionStatus.NONE == "none"
        assert DoorPositionStatus.OPEN == "open"
        assert DoorPositionStatus.CLOSE == "close"

    def test_lock_rule_types(self):
        assert LockRuleType.KEEP_LOCK == "keep_lock"
        assert LockRuleType.KEEP_UNLOCK == "keep_unlock"
        assert LockRuleType.CUSTOM == "custom"
        assert LockRuleType.SCHEDULE == "schedule"

    def test_door_group_type(self):
        assert DoorGroupType.BUILDING == "building"
        assert DoorGroupType.ACCESS == "access"


class TestDoorParsing:
    def test_full_door(self):
        door = Door.model_validate(
            {
                "id": "d1",
                "name": "Front Door",
                "full_name": "Building A - Front Door",
                "floor_id": "f1",
                "type": "door",
                "is_bind_hub": True,
                "door_lock_relay_status": "lock",
                "door_position_status": "close",
            }
        )
        assert door.id == "d1"
        assert door.name == "Front Door"
        assert door.is_bind_hub is True
        assert door.door_lock_relay_status == DoorLockStatus.LOCK
        assert door.door_position_status == DoorPositionStatus.CLOSE

    def test_door_position_null(self):
        door = Door.model_validate(
            {
                "id": "d2",
                "door_position_status": None,
            }
        )
        assert door.door_position_status is None

    def test_door_position_none_string(self):
        door = Door.model_validate(
            {"id": "d4", "door_position_status": "none"}
        )
        assert door.door_position_status == DoorPositionStatus.NONE

    def test_door_minimal(self):
        door = Door.model_validate({"id": "d3"})
        assert door.id == "d3"
        assert door.is_bind_hub is False
        assert door.door_lock_relay_status is None


class TestDoorGroup:
    def test_parse_group(self):
        group = DoorGroup.model_validate(
            {
                "id": "g1",
                "name": "Building A",
                "type": "building",
                "resources": [
                    {"id": "d1", "type": "door", "name": "Front Door"},
                ],
            }
        )
        assert group.id == "g1"
        assert group.type == DoorGroupType.BUILDING
        assert len(group.resources) == 1


class TestTopology:
    def test_parse_topology(self):
        topo = DoorGroupTopology.model_validate(
            {
                "id": "t1",
                "name": "Main Building",
                "type": "building",
                "resource_topologies": [
                    {
                        "id": "f1",
                        "name": "Floor 1",
                        "type": "floor",
                        "resources": [
                            {
                                "id": "d1",
                                "name": "Door 1",
                                "type": "door",
                                "is_bind_hub": True,
                            },
                        ],
                    },
                ],
            }
        )
        assert topo.id == "t1"
        assert len(topo.resource_topologies) == 1
        assert len(topo.resource_topologies[0].resources) == 1


class TestLockRule:
    def test_keep_lock(self):
        rule = LockRule.model_validate({"type": "keep_lock"})
        assert rule.type == LockRuleType.KEEP_LOCK
        assert rule.ended_time is None

    def test_custom_with_time(self):
        rule = LockRule.model_validate({"type": "custom", "ended_time": 1700000000})
        assert rule.type == LockRuleType.CUSTOM
        assert rule.ended_time == 1700000000


class TestEmergencyStatus:
    def test_normal(self):
        status = EmergencyStatus.model_validate(
            {"lockdown": False, "evacuation": False}
        )
        assert status.lockdown is False
        assert status.evacuation is False

    def test_lockdown(self):
        status = EmergencyStatus.model_validate({"lockdown": True, "evacuation": False})
        assert status.lockdown is True
