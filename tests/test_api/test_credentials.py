"""Tests for CredentialManager."""

from unittest.mock import AsyncMock

import pytest

from aiounifiaccess.api.credentials import CredentialManager
from aiounifiaccess.models.credential import NFCCard, NFCCardEnrollmentStatus, TouchPass


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def manager(mock_session):
    return CredentialManager(mock_session)


class TestNFCOperations:
    async def test_enroll(self, manager, mock_session):
        mock_session._request.return_value = {"status": "reading", "session_id": "s1"}
        result = await manager.enroll_nfc_card("dev1")
        assert isinstance(result, NFCCardEnrollmentStatus)

    async def test_get_nfc_card(self, manager, mock_session):
        mock_session._request.return_value = {"token": "tok1", "type": "ua_card"}
        card = await manager.get_nfc_card("tok1")
        assert isinstance(card, NFCCard)

    async def test_list_nfc_cards(self, manager, mock_session):
        mock_session._request_raw.return_value = {
            "code": "SUCCESS",
            "msg": "success",
            "data": [{"token": "t1"}, {"token": "t2"}],
            "pagination": {"page_num": 1, "page_size": 25, "total": 2},
        }
        cards, resp = await manager.list_nfc_cards()
        assert len(cards) == 2


class TestTouchPass:
    async def test_get(self, manager, mock_session):
        mock_session._request.return_value = {"id": "t1", "card_id": "C1"}
        tp = await manager.get_touch_pass("C1")
        assert isinstance(tp, TouchPass)


class TestPINCode:
    async def test_generate(self, manager, mock_session):
        mock_session._request.return_value = "12345678"
        pin = await manager.generate_pin_code()
        assert pin == "12345678"
