"""Tests for VisitorManager."""

from unittest.mock import AsyncMock

import pytest

from aiounifiaccess.api.visitors import VisitorManager
from aiounifiaccess.models.visitor import Visitor


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def manager(mock_session):
    return VisitorManager(mock_session)


class TestVisitorCRUD:
    async def test_create(self, manager, mock_session):
        mock_session._request.return_value = {
            "id": "v1",
            "first_name": "A",
            "last_name": "B",
        }
        v = await manager.create("A", "B")
        assert isinstance(v, Visitor)
        mock_session._request.assert_called_once()

    async def test_get(self, manager, mock_session):
        mock_session._request.return_value = {"id": "v1"}
        v = await manager.get("v1")
        assert v.id == "v1"

    async def test_delete(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager.delete("v1")
        mock_session._request.assert_called_once_with(
            "DELETE", "/api/v1/developer/visitors/v1"
        )

    async def test_assign_nfc_card(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager.assign_nfc_card("v1", "tok123", force_add=True)
        mock_session._request.assert_called_once_with(
            "PUT",
            "/api/v1/developer/visitors/v1/nfc_cards",
            json={"token": "tok123", "force_add": True},
        )
