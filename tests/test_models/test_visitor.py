"""Tests for Visitor models."""

from aiounifiaccess.models.visitor import Visitor, VisitorStatus


class TestVisitor:
    def test_parse_full(self):
        v = Visitor.model_validate(
            {
                "id": "abc",
                "first_name": "Jane",
                "last_name": "Doe",
                "status": 6,
                "nfc_cards": [{"id": "1", "token": "tok", "type": "ua_card"}],
                "pin_code": {"token": "hash"},
                "resources": [{"id": "r1", "type": "door", "name": "Front"}],
            }
        )
        assert v.id == "abc"
        assert v.status == VisitorStatus.ACTIVE
        assert len(v.nfc_cards) == 1
        assert v.pin_code.token == "hash"

    def test_minimal(self):
        v = Visitor.model_validate({"id": "x", "first_name": "A", "last_name": "B"})
        assert v.nfc_cards == []
        assert v.pin_code is None
