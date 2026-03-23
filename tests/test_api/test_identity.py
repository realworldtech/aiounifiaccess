"""Tests for IdentityManager."""

from unittest.mock import AsyncMock

import pytest

from aiounifiaccess.api.identity import IdentityManager


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def manager(mock_session):
    return IdentityManager(mock_session)


class TestIdentity:
    async def test_list_resources(self, manager, mock_session):
        mock_session._request.return_value = {"wifi": [{"id": "w1", "name": "Net"}]}
        result = await manager.list_resources()
        assert "wifi" in result
        assert result["wifi"][0].name == "Net"

    async def test_assign_to_user(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager.assign_to_user("u1", "wifi", ["w1"])
        mock_session._request.assert_called_once()

    async def test_send_invitations(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager.send_invitations([{"email": "test@test.com"}])
        mock_session._request.assert_called_once()
