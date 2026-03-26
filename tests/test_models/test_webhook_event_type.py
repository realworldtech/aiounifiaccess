"""Tests for WebhookEventType enum."""

from aiounifiaccess.models.webhook import WebhookEventType


class TestWebhookEventType:
    def test_all_returns_all_values(self):
        all_events = WebhookEventType.all()
        assert len(all_events) == len(WebhookEventType)
        for event in WebhookEventType:
            assert event.value in all_events

    def test_all_returns_strings(self):
        for event in WebhookEventType.all():
            assert isinstance(event, str)

    def test_door_unlock_value(self):
        assert WebhookEventType.DOOR_UNLOCK == "access.door.unlock"

    def test_known_event_types(self):
        expected = {
            "access.doorbell.incoming",
            "access.doorbell.completed",
            "access.doorbell.incoming.REN",
            "access.device.dps_status",
            "access.door.unlock",
            "access.device.emergency_status",
            "access.unlock_schedule.activate",
            "access.unlock_schedule.deactivate",
            "access.temporary_unlock.start",
            "access.temporary_unlock.end",
            "access.visitor.status.changed",
        }
        assert set(WebhookEventType.all()) == expected

    def test_str_enum_comparison(self):
        assert WebhookEventType.DOOR_UNLOCK == "access.door.unlock"
        assert "access.door.unlock" == WebhookEventType.DOOR_UNLOCK
