"""Tests for event model parsing."""

from aiounifiaccess.events.models import (
    BaseInfoEvent,
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
