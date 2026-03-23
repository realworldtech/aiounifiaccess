"""Tests for Device models."""

from aiounifiaccess.models.device import AccessMethodSettings, Device


class TestDevice:
    def test_parse(self):
        d = Device.model_validate(
            {"id": "dev1", "name": "UA-HUB", "type": "UAH", "online": True}
        )
        assert d.id == "dev1"
        assert d.online is True


class TestAccessMethodSettings:
    def test_parse(self):
        s = AccessMethodSettings.model_validate(
            {
                "device_id": "dev1",
                "access_methods": {
                    "nfc": {"enabled": "true"},
                    "face": {
                        "enabled": "true",
                        "anti_spoofing_level": "high",
                        "detect_distance": "medium",
                    },
                    "pin_code": {"enabled": "false", "pin_code_shuffle": True},
                },
            }
        )
        assert s.device_id == "dev1"
        assert s.access_methods.nfc.enabled == "true"
        assert s.access_methods.face.anti_spoofing_level == "high"
        assert s.access_methods.pin_code.pin_code_shuffle is True
