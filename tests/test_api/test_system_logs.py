"""Tests for SystemLogManager."""

from unittest.mock import AsyncMock

import pytest

from aiounifiaccess.api.system_logs import SystemLogManager
from aiounifiaccess.models.system_log import LogResource, SystemLogEntry


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def manager(mock_session):
    return SystemLogManager(mock_session)


class TestFetch:
    async def test_fetch(self, manager, mock_session):
        mock_session._request.return_value = [
            {
                "timestamp": "2024-01-01",
                "id": "l1",
                "source": {
                    "event": {},
                    "actor": {},
                    "authentication": {},
                    "target": {},
                },
            },
        ]
        logs = await manager.fetch(topic="door_openings")
        assert len(logs) == 1
        assert isinstance(logs[0], SystemLogEntry)


class TestResource:
    async def test_get_resource(self, manager, mock_session):
        mock_session._request.return_value = {
            "video_record": "url",
            "created_at": "2024-01-01",
        }
        r = await manager.get_resource("r1")
        assert isinstance(r, LogResource)
