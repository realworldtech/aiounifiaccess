"""Tests for DeviceManager."""

from unittest.mock import AsyncMock

import pytest

from aiounifiaccess.api.devices import DeviceManager
from aiounifiaccess.models.device import AccessMethodSettings, Device


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def manager(mock_session):
    return DeviceManager(mock_session)


class TestDeviceList:
    async def test_list(self, manager, mock_session):
        mock_session._request.return_value = [[{"id": "d1", "name": "Hub"}]]
        result = await manager.list()
        assert len(result) == 1
        assert isinstance(result[0][0], Device)


class TestSettings:
    async def test_get_settings(self, manager, mock_session):
        mock_session._request.return_value = {
            "device_id": "d1",
            "access_methods": {"nfc": {"enabled": "true"}},
        }
        s = await manager.get_settings("d1")
        assert isinstance(s, AccessMethodSettings)

    async def test_update_settings(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager.update_settings("d1", {"nfc": {"enabled": "false"}})
        mock_session._request.assert_called_once()


class TestDoorbell:
    async def test_trigger(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager.trigger_doorbell("d1", room_name="Lobby")
        mock_session._request.assert_called_once()
