"""Tests for WebhookManager."""

from unittest.mock import AsyncMock, patch

import pytest

from aiounifiaccess.api.webhooks import WebhookManager
from aiounifiaccess.models.webhook import WebhookEndpoint, WebhookEventType


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def manager(mock_session):
    return WebhookManager(mock_session)


class TestWebhookCRUD:
    async def test_list(self, manager, mock_session):
        mock_session._request.return_value = [
            {"id": "w1", "endpoint": "https://x.com", "name": "Hook", "events": []}
        ]
        endpoints = await manager.list_endpoints()
        assert len(endpoints) == 1
        assert isinstance(endpoints[0], WebhookEndpoint)

    async def test_create(self, manager, mock_session):
        mock_session._request.return_value = {
            "id": "w2",
            "endpoint": "https://x.com",
            "name": "New",
            "secret": "s1",
            "events": ["access.door.unlock"],
        }
        ep = await manager.create_endpoint(
            "https://x.com", "New", ["access.door.unlock"]
        )
        assert isinstance(ep, WebhookEndpoint)
        assert ep.secret == "s1"

    async def test_delete(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager.delete_endpoint("w1")
        mock_session._request.assert_called_once_with(
            "DELETE", "/api/v1/developer/webhooks/endpoints/w1"
        )


class TestEnsureEndpoint:
    async def test_creates_when_none_exist(self, manager):
        all_events = WebhookEventType.all()
        created = WebhookEndpoint(
            id="new1",
            endpoint="https://me:8080/webhook",
            name="myapp",
            secret="generated_secret",
            events=all_events,
        )

        with (
            patch.object(manager, "list_endpoints", return_value=[]),
            patch.object(
                manager, "create_endpoint", return_value=created
            ) as mock_create,
        ):
            result = await manager.ensure_endpoint("https://me:8080/webhook", "myapp")

        assert result.secret == "generated_secret"
        mock_create.assert_called_once_with(
            "https://me:8080/webhook", "myapp", all_events, headers=None
        )

    async def test_returns_existing_when_url_and_events_match(self, manager):
        all_events = WebhookEventType.all()
        existing = WebhookEndpoint(
            id="existing1",
            endpoint="https://me:8080/webhook",
            name="myapp",
            secret="existing_secret",
            events=all_events,
        )

        with (
            patch.object(manager, "list_endpoints", return_value=[existing]),
            patch.object(manager, "create_endpoint") as mock_create,
            patch.object(manager, "update_endpoint") as mock_update,
        ):
            result = await manager.ensure_endpoint("https://me:8080/webhook", "myapp")

        assert result.id == "existing1"
        assert result.secret == "existing_secret"
        mock_create.assert_not_called()
        mock_update.assert_not_called()

    async def test_updates_when_url_matches_but_events_differ(self, manager):
        existing = WebhookEndpoint(
            id="existing1",
            endpoint="https://me:8080/webhook",
            name="myapp",
            secret="old_secret",
            events=["access.door.unlock"],
        )
        updated = WebhookEndpoint(
            id="existing1",
            endpoint="https://me:8080/webhook",
            name="myapp",
            secret="old_secret",
            events=WebhookEventType.all(),
        )

        with (
            patch.object(manager, "list_endpoints", return_value=[existing]),
            patch.object(
                manager, "update_endpoint", return_value=updated
            ) as mock_update,
            patch.object(manager, "create_endpoint") as mock_create,
        ):
            result = await manager.ensure_endpoint("https://me:8080/webhook", "myapp")

        assert result.events == WebhookEventType.all()
        mock_update.assert_called_once()
        mock_create.assert_not_called()

    async def test_creates_when_url_doesnt_match(self, manager):
        existing = WebhookEndpoint(
            id="other1",
            endpoint="https://other:9090/hook",
            name="other",
            secret="other_secret",
            events=WebhookEventType.all(),
        )
        created = WebhookEndpoint(
            id="new1",
            endpoint="https://me:8080/webhook",
            name="myapp",
            secret="new_secret",
            events=WebhookEventType.all(),
        )

        with (
            patch.object(manager, "list_endpoints", return_value=[existing]),
            patch.object(
                manager, "create_endpoint", return_value=created
            ) as mock_create,
        ):
            result = await manager.ensure_endpoint("https://me:8080/webhook", "myapp")

        assert result.secret == "new_secret"
        mock_create.assert_called_once()

    async def test_custom_events_list(self, manager):
        custom_events = ["access.door.unlock", "access.device.dps_status"]
        created = WebhookEndpoint(
            id="new1",
            endpoint="https://me:8080/webhook",
            name="myapp",
            secret="s1",
            events=custom_events,
        )

        with (
            patch.object(manager, "list_endpoints", return_value=[]),
            patch.object(
                manager, "create_endpoint", return_value=created
            ) as mock_create,
        ):
            result = await manager.ensure_endpoint(
                "https://me:8080/webhook", "myapp", events=custom_events
            )

        assert result.events == custom_events
        mock_create.assert_called_once_with(
            "https://me:8080/webhook", "myapp", custom_events, headers=None
        )

    async def test_events_order_insensitive(self, manager):
        """Matching should work regardless of event list ordering."""
        existing = WebhookEndpoint(
            id="existing1",
            endpoint="https://me:8080/webhook",
            name="myapp",
            secret="s1",
            events=["access.device.dps_status", "access.door.unlock"],
        )

        with (
            patch.object(manager, "list_endpoints", return_value=[existing]),
            patch.object(manager, "create_endpoint") as mock_create,
            patch.object(manager, "update_endpoint") as mock_update,
        ):
            result = await manager.ensure_endpoint(
                "https://me:8080/webhook",
                "myapp",
                events=["access.door.unlock", "access.device.dps_status"],
            )

        assert result.id == "existing1"
        mock_create.assert_not_called()
        mock_update.assert_not_called()
