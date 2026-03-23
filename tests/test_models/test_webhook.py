"""Tests for Webhook models."""

from aiounifiaccess.models.webhook import WebhookEndpoint


class TestWebhookEndpoint:
    def test_parse(self):
        w = WebhookEndpoint.model_validate(
            {
                "id": "w1",
                "endpoint": "https://example.com/hook",
                "name": "My Hook",
                "secret": "abc123",
                "events": ["access.door.unlock", "access.device.dps_status"],
                "headers": {"X-Custom": "value"},
            }
        )
        assert w.endpoint == "https://example.com/hook"
        assert len(w.events) == 2
        assert w.headers["X-Custom"] == "value"
