"""Tests for Identity models."""

from aiounifiaccess.models.identity import IdentityResource, ResourceType


class TestResourceType:
    def test_values(self):
        assert ResourceType.WIFI == "wifi"
        assert ResourceType.CAMERA == "camera"


class TestIdentityResource:
    def test_parse(self):
        r = IdentityResource.model_validate(
            {"id": "r1", "name": "WiFi Net", "deleted": False}
        )
        assert r.name == "WiFi Net"
