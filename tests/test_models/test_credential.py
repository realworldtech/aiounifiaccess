"""Tests for Credential models."""

from aiounifiaccess.models.credential import NFCCard, NFCCardEnrollmentStatus, TouchPass


class TestNFCCard:
    def test_parse(self):
        c = NFCCard.model_validate(
            {
                "token": "tok1",
                "type": "ua_card",
                "holder_id": "u1",
                "status": "assigned",
            }
        )
        assert c.token == "tok1"
        assert c.holder_id == "u1"


class TestEnrollment:
    def test_parse(self):
        e = NFCCardEnrollmentStatus.model_validate(
            {"status": "reading", "session_id": "s1"}
        )
        assert e.status == "reading"


class TestTouchPass:
    def test_parse(self):
        t = TouchPass.model_validate(
            {
                "id": "t1",
                "card_id": "C1",
                "status": "ACTIVE",
                "bundles": [
                    {
                        "bundle_id": "b1",
                        "bundle_status": "ACTIVE",
                        "device_id": "d1",
                        "device_name": "Phone",
                        "device_type": 20,
                        "source": "google",
                    }
                ],
            }
        )
        assert t.card_id == "C1"
        assert len(t.bundles) == 1
