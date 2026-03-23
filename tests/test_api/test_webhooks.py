"""Tests for WebhookManager."""

from unittest.mock import AsyncMock

import pytest

from aiounifiaccess.api.webhooks import WebhookManager
from aiounifiaccess.models.webhook import WebhookEndpoint


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
