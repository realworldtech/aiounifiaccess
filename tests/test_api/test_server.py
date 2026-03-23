"""Tests for ServerManager."""

from unittest.mock import AsyncMock

import pytest

from aiounifiaccess.api.server import ServerManager


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def manager(mock_session):
    return ServerManager(mock_session)


class TestServer:
    async def test_delete_certificate(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager.delete_certificate()
        mock_session._request.assert_called_once_with(
            "DELETE", "/api/v1/developer/certs"
        )
