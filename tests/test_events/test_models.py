"""Tests for event model parsing."""

from aiounifiaccess.events.models import (
    BaseInfoEvent,
    DeviceUpdateEvent,
    DeviceUpdateV2Event,
    DoorbellCompletedEvent,
    DoorbellIncomingEvent,
    DoorbellRENEvent,
    DoorPositionEvent,
    DoorUnlockEvent,
    EmergencyStatusEvent,
    RawEvent,
    RemoteUnlockEvent,
    RemoteViewChangeEvent,
    RemoteViewEvent,
    VisitorStatusChangedEvent,
    parse_event,
)


class TestBaseInfoEvent:
    def test_parse(self):
        raw = {
            "event": "access.base.info",
            "receiver_id": "",
            "event_object_id": "a120562b-4370-41f3-9adb-8ca069473bcf",
            "save_to_history": False,
            "data": {"top_log_count": 0},
        }
        event = parse_event(raw)
        assert isinstance(event, BaseInfoEvent)
        assert event.event == "access.base.info"
        assert event.data.top_log_count == 0

    def test_nonzero_log_count(self):
        event = parse_event(
            {"event": "access.base.info", "data": {"top_log_count": 42}}
        )
        assert isinstance(event, BaseInfoEvent)
        assert event.data.top_log_count == 42


class TestRemoteViewEvent:
    def test_parse(self):
        raw = {
            "event": "access.remote_view",
            "receiver_id": "",
            "event_object_id": "535b6125-860c-489a-b0a1-0ba01906afa9",
            "save_to_history": False,
            "data": {
                "channel": "4513899f-0370-4116-9731-63a6b0feea23",
                "token": "6dff120f-2688-497d-856f-0ca08b383d1d",
                "device_id": "e4388386be1d",
                "device_type": "UA-G2-PRO",
                "device_name": "UA-G2-PRO-BE1D",
                "door_name": "Door 236b",
                "controller_id": "68d79a1f494f",
                "floor_name": "1F",
                "in_or_out": "in",
                "create_time": 1694771479,
                "reason_code": 0,
                "door_guard_ids": ["guard1", "guard2"],
                "connected_uah_id": "e4388384236b",
                "room_id": "WR-e4388386be1d",
                "host_device_mac": "68D79A1F494B",
            },
        }
        event = parse_event(raw)
        assert isinstance(event, RemoteViewEvent)
        assert event.event == "access.remote_view"
        assert event.data.device_id == "e4388386be1d"
        assert event.data.door_name == "Door 236b"
        assert len(event.data.door_guard_ids) == 2


class TestRemoteViewChangeEvent:
    def test_parse(self):
        raw = {
            "event": "access.remote_view.change",
            "event_object_id": "450a6c0f",
            "data": {
                "reason_code": 108,
                "remote_call_request_id": "J0FeDJc8ZNzHjxr1",
            },
        }
        event = parse_event(raw)
        assert isinstance(event, RemoteViewChangeEvent)
        assert event.data.reason_code == 108
        assert event.data.remote_call_request_id == "J0FeDJc8ZNzHjxr1"


class TestRemoteUnlockEvent:
    def test_parse(self):
        raw = {
            "event": "access.data.device.remote_unlock",
            "event_object_id": "e4388384236b",
            "data": {
                "unique_id": "5d600936-8618-4f2d-a1b7-d786865b70ba",
                "name": "Door 236b",
                "up_id": "913a35bc",
                "timezone": "",
                "location_type": "door",
                "extra_type": "",
                "full_name": "UDR-ML - 1F - Door 236b",
                "level": 0,
                "work_time": "[]",
                "work_time_id": "",
                "extras": {"uah-input_state_dps": "off"},
            },
        }
        event = parse_event(raw)
        assert isinstance(event, RemoteUnlockEvent)
        assert event.data.name == "Door 236b"
        assert event.data.location_type == "door"
        assert event.data.extras["uah-input_state_dps"] == "off"


class TestDoorUnlockEvent:
    SAMPLE = {
        "event": "access.door.unlock",
        "event_object_id": "4a98adf6",
        "data": {
            "location": {
                "id": "d2b87427",
                "location_type": "door",
                "name": "Door 3855",
                "up_id": "62ff3aa1",
                "extras": {"uah-input_state_dps": "on"},
            },
            "device": {
                "name": "UA-HUB-3855",
                "alias": "Door 3855",
                "id": "7483c2773855",
                "device_type": "UAH",
            },
            "actor": {
                "id": "d62e92fd",
                "name": "Admin",
                "type": "user",
            },
            "object": {
                "authentication_type": "NFC",
                "result": "Access Granted",
            },
        },
    }

    def test_parse(self):
        event = parse_event(self.SAMPLE)
        assert isinstance(event, DoorUnlockEvent)
        assert event.data.location.name == "Door 3855"
        assert event.data.actor.name == "Admin"
        assert event.data.object.authentication_type == "NFC"
        assert event.data.object.result == "Access Granted"
        assert event.data.device.device_type == "UAH"


class TestDoorPositionEvent:
    def test_parse(self):
        raw = {
            "event": "access.device.dps_status",
            "event_object_id": "x",
            "data": {
                "location": {"id": "d1", "name": "Front Door"},
                "device": {"id": "dev1"},
                "actor": {},
                "object": {"status": "open"},
            },
        }
        event = parse_event(raw)
        assert isinstance(event, DoorPositionEvent)
        assert event.data.object.status == "open"

    def test_null_actor_and_event_type_in_object(self):
        """Real payload from UniFi controller — actor is null for DPS events."""
        raw = {
            "event": "access.device.dps_status",
            "event_object_id": "00a1d6f6",
            "data": {
                "location": {
                    "id": "5d97c3e3",
                    "location_type": "door",
                    "name": "Front Door",
                    "up_id": "578f37b4",
                    "extras": {},
                    "device_ids": None,
                },
                "device": {
                    "name": "EAH-8-F95A",
                    "id": "58d61f48f95a",
                    "device_type": "UAH-Ent",
                },
                "actor": None,
                "object": {"event_type": "dps_change", "status": "open"},
            },
        }
        event = parse_event(raw)
        assert isinstance(event, DoorPositionEvent)
        assert event.data.actor is None
        assert event.data.object.status == "open"
        assert event.data.location.name == "Front Door"

    def test_null_actor_and_null_object(self):
        """Some events have both actor and object as null."""
        raw = {
            "event": "access.device.dps_status",
            "event_object_id": "x",
            "data": {
                "location": {"name": "Door"},
                "device": {"id": "dev1"},
                "actor": None,
                "object": None,
            },
        }
        event = parse_event(raw)
        assert isinstance(event, DoorPositionEvent)
        assert event.data.actor is None
        assert event.data.object is None


class TestDoorbellEvents:
    def test_incoming(self):
        event = parse_event(
            {
                "event": "access.doorbell.incoming",
                "data": {
                    "location": {"name": "Front"},
                    "device": {},
                    "actor": {},
                    "object": {},
                },
            }
        )
        assert isinstance(event, DoorbellIncomingEvent)

    def test_completed(self):
        event = parse_event(
            {
                "event": "access.doorbell.completed",
                "data": {
                    "location": {},
                    "device": {},
                    "actor": {},
                    "object": {"reason_code": 107},
                },
            }
        )
        assert isinstance(event, DoorbellCompletedEvent)
        assert event.data.object.reason_code == 107

    def test_ren(self):
        event = parse_event(
            {
                "event": "access.doorbell.incoming.REN",
                "data": {
                    "location": {},
                    "device": {},
                    "actor": {},
                    "object": {},
                },
            }
        )
        assert isinstance(event, DoorbellRENEvent)


class TestOtherWebhookEvents:
    def test_emergency_status(self):
        event = parse_event(
            {
                "event": "access.device.emergency_status",
                "data": {
                    "location": {},
                    "device": {},
                    "actor": {},
                    "object": {},
                },
            }
        )
        assert isinstance(event, EmergencyStatusEvent)

    def test_visitor_status_changed(self):
        event = parse_event(
            {
                "event": "access.visitor.status.changed",
                "data": {
                    "location": {},
                    "device": {},
                    "actor": {},
                    "object": {},
                },
            }
        )
        assert isinstance(event, VisitorStatusChangedEvent)


class TestDeviceUpdateEvent:
    SAMPLE = {
        "event": "access.data.device.update",
        "receiver_id": "",
        "event_object_id": "58d61f48f95a",
        "save_to_history": False,
        "data": {
            "unique_id": "58d61f48f95a",
            "name": "EAH-8-F95A",
            "alias": "EAH U12 2 Eden Park Comms Room",
            "device_type": "UAH-Ent",
            "ip": "10.66.70.216",
            "mac": "58:d6:1f:48:f9:5a",
            "firmware": "v5.9.20.0",
            "version": "v2.5.149",
            "is_online": True,
            "is_connected": True,
            "is_adopted": True,
            "location": {
                "unique_id": "60742bd8-4014-4975-9e9e-2d7c3c68f5a2",
                "name": "U3-2-Eden-Park-Drv",
                "location_type": "building",
                "full_name": "U3-2-Eden-Park-Drv",
            },
            "configs": [
                {
                    "device_id": "58d61f48f95a",
                    "key": "input_d1_dps",
                    "value": "on",
                    "tag": "hub_action",
                    "update_time": "2026-03-25T16:32:09+11:00",
                    "create_time": "2026-03-20T04:05:00+11:00",
                },
                {
                    "device_id": "58d61f48f95a",
                    "key": "output_d8_lock_relay",
                    "value": "on",
                    "tag": "hub_action",
                    "update_time": "2026-03-27T08:07:09+11:00",
                    "create_time": "2026-03-20T04:05:00+11:00",
                },
            ],
            "capabilities": ["pin_code", "dps_alarm", "is_hub"],
            "model": "EAH 8",
        },
    }

    def test_parse(self):
        event = parse_event(self.SAMPLE)
        assert isinstance(event, DeviceUpdateEvent)
        assert event.event == "access.data.device.update"
        assert event.data.name == "EAH-8-F95A"
        assert event.data.alias == "EAH U12 2 Eden Park Comms Room"
        assert event.data.device_type == "UAH-Ent"
        assert event.data.is_online is True

    def test_location(self):
        event = parse_event(self.SAMPLE)
        assert isinstance(event, DeviceUpdateEvent)
        assert event.data.location.name == "U3-2-Eden-Park-Drv"
        assert event.data.location.location_type == "building"

    def test_configs(self):
        event = parse_event(self.SAMPLE)
        assert isinstance(event, DeviceUpdateEvent)
        assert len(event.data.configs) == 2
        dps = event.data.configs[0]
        assert dps.key == "input_d1_dps"
        assert dps.value == "on"
        assert dps.tag == "hub_action"

    def test_dps_configs_extraction(self):
        """Extract DPS states from configs — the door-left-open use case."""
        event = parse_event(self.SAMPLE)
        assert isinstance(event, DeviceUpdateEvent)
        dps_states = {
            cfg.key: cfg.value
            for cfg in event.data.configs
            if cfg.tag == "hub_action" and cfg.key.endswith("_dps")
        }
        assert dps_states == {"input_d1_dps": "on"}

    def test_lock_relay_extraction(self):
        event = parse_event(self.SAMPLE)
        assert isinstance(event, DeviceUpdateEvent)
        relays = {
            cfg.key: cfg.value
            for cfg in event.data.configs
            if cfg.tag == "hub_action" and "lock_relay" in cfg.key
        }
        assert relays == {"output_d8_lock_relay": "on"}

    def test_capabilities(self):
        event = parse_event(self.SAMPLE)
        assert isinstance(event, DeviceUpdateEvent)
        assert "is_hub" in event.data.capabilities


class TestDeviceUpdateV2Event:
    SAMPLE = {
        "event": "access.data.v2.device.update",
        "receiver_id": "",
        "event_object_id": "3d03f1ac-7d79-4a70-8cae-c3fc738cb9ad",
        "save_to_history": False,
        "data": {
            "name": "EAH-8-F95A",
            "alias": "EAH U12 2 Eden Park Comms Room",
            "id": "58d61f48f95a",
            "ip": "10.66.70.216",
            "mac": "58:d6:1f:48:f9:5a",
            "online": True,
            "adopting": False,
            "device_type": "UAH-Ent",
            "firmware": "v5.9.20.0",
            "version": "v2.5.149",
            "category": ["hub"],
        },
        "meta": {
            "object_type": "device",
            "target_field": ["access_method", "settings"],
            "all_field": False,
            "id": "58d61f48f95a",
            "source": "",
        },
    }

    def test_parse(self):
        event = parse_event(self.SAMPLE)
        assert isinstance(event, DeviceUpdateV2Event)
        assert event.data.name == "EAH-8-F95A"
        assert event.data.online is True
        assert event.data.category == ["hub"]

    def test_meta(self):
        event = parse_event(self.SAMPLE)
        assert isinstance(event, DeviceUpdateV2Event)
        assert event.meta.object_type == "device"
        assert event.meta.id == "58d61f48f95a"
        assert "access_method" in event.meta.target_field


class TestRawEvent:
    def test_unknown_event_type(self):
        raw = {
            "event": "access.future.new_event",
            "event_object_id": "x",
            "data": {"some": "payload"},
        }
        event = parse_event(raw)
        assert isinstance(event, RawEvent)
        assert event.event == "access.future.new_event"
        assert event.data["some"] == "payload"

    def test_null_data(self):
        raw = {
            "event": "access.something.unknown",
            "event_object_id": "y",
            "data": None,
        }
        event = parse_event(raw)
        assert isinstance(event, RawEvent)
        assert event.data is None

    def test_missing_data_field(self):
        raw = {"event": "access.something.unknown", "event_object_id": "z"}
        event = parse_event(raw)
        assert isinstance(event, RawEvent)
        assert event.data is None

    def test_missing_event_field(self):
        event = parse_event({"data": {"key": "val"}})
        assert isinstance(event, RawEvent)
