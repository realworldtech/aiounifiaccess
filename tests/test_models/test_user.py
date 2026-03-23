"""Tests for User models."""

from datetime import datetime, timezone

from aiounifiaccess.models.user import (
    AccessPolicyRef,
    LicensePlate,
    NFCCard,
    PINCode,
    TouchPass,
    User,
    UserGroup,
    UserStatus,
)


class TestUserStatus:
    def test_enum_values(self):
        assert UserStatus.ACTIVE == "ACTIVE"
        assert UserStatus.PENDING == "PENDING"
        assert UserStatus.DEACTIVATED == "DEACTIVATED"


class TestUserParsing:
    FULL_USER_JSON = {
        "id": "17d2f099-99df-429b-becb-1399a6937e5a",
        "first_name": "Test",
        "last_name": "User",
        "user_email": "test@example.com",
        "employee_number": "EMP001",
        "onboard_time": 1689047588,
        "status": "ACTIVE",
        "access_policy_ids": ["edbc80df-3698-49fd-8b53-f1867f104947"],
        "access_policies": [
            {
                "id": "edbc80df-3698-49fd-8b53-f1867f104947",
                "name": "test",
                "resources": [
                    {
                        "id": "d5573467-d6b3-4e8f-8e48-8a322b91664a",
                        "type": "door_group",
                    },
                ],
                "schedule_id": "73facd6c-839e-4521-a4f4-c07e1d44e748",
            }
        ],
        "nfc_cards": [{"id": "100001", "token": "d27822fc682b478d", "type": "ua_card"}],
        "license_plates": [
            {
                "id": "5cac1825-f5e9-410d-a32e-a1fb9fc83b92",
                "credential": "jq178",
                "credential_type": "license",
                "credential_status": "active",
            }
        ],
        "pin_code": {"token": "5f742ee4424e5a7d"},
        "touch_pass": {
            "id": "c83b69ff-1992-4e7f-9287-1e6a161adeea",
            "card_id": "70A3-2FAD-181B-4CC9",
            "card_name": "Test",
            "status": "SUSPENDED",
            "user_name": "Example Name",
            "user_email": "example@ui.com",
            "user_id": "3e763e5d-6804-437d-ae8d-3fee74119b80",
            "user_status": "ACTIVE",
            "user_avatar": "",
            "last_activity": "2025-04-10T00:46:20+08:00",
            "activated_at": {},
            "expired_at": {},
            "bundles": [
                {
                    "bundle_id": "caf6bd5b-6b8d-409a-b500-977a0f02b181",
                    "bundle_status": "SUSPENDED",
                    "device_id": "device-id-1",
                    "device_name": "Example Android",
                    "device_type": 20,
                    "source": "google",
                }
            ],
        },
    }

    def test_full_user_parses(self):
        user = User.model_validate(self.FULL_USER_JSON)
        assert user.id == "17d2f099-99df-429b-becb-1399a6937e5a"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.status == UserStatus.ACTIVE
        assert user.employee_number == "EMP001"

    def test_onboard_time_converts_to_datetime(self):
        user = User.model_validate(self.FULL_USER_JSON)
        assert isinstance(user.onboard_time, datetime)
        assert user.onboard_time == datetime(2023, 7, 11, 3, 53, 8, tzinfo=timezone.utc)

    def test_onboard_time_zero_is_none(self):
        user = User.model_validate({"onboard_time": 0})
        assert user.onboard_time is None

    def test_onboard_time_missing_is_none(self):
        user = User.model_validate({})
        assert user.onboard_time is None

    def test_nfc_cards_parsed(self):
        user = User.model_validate(self.FULL_USER_JSON)
        assert len(user.nfc_cards) == 1
        assert isinstance(user.nfc_cards[0], NFCCard)
        assert user.nfc_cards[0].token == "d27822fc682b478d"
        assert user.nfc_cards[0].type == "ua_card"

    def test_pin_code_parsed(self):
        user = User.model_validate(self.FULL_USER_JSON)
        assert isinstance(user.pin_code, PINCode)
        assert user.pin_code.token == "5f742ee4424e5a7d"

    def test_pin_code_null(self):
        user = User.model_validate({"pin_code": None})
        assert user.pin_code is None

    def test_license_plates_parsed(self):
        user = User.model_validate(self.FULL_USER_JSON)
        assert len(user.license_plates) == 1
        assert isinstance(user.license_plates[0], LicensePlate)
        assert user.license_plates[0].credential == "jq178"

    def test_access_policies_parsed(self):
        user = User.model_validate(self.FULL_USER_JSON)
        assert len(user.access_policies) == 1
        policy = user.access_policies[0]
        assert isinstance(policy, AccessPolicyRef)
        assert policy.name == "test"
        assert len(policy.resources) == 1

    def test_touch_pass_parsed(self):
        user = User.model_validate(self.FULL_USER_JSON)
        assert isinstance(user.touch_pass, TouchPass)
        assert user.touch_pass.card_id == "70A3-2FAD-181B-4CC9"
        assert len(user.touch_pass.bundles) == 1
        assert user.touch_pass.bundles[0].source == "google"

    def test_minimal_user(self):
        user = User.model_validate({"id": "abc", "first_name": "A", "last_name": "B"})
        assert user.id == "abc"
        assert user.nfc_cards == []
        assert user.pin_code is None


class TestUserGroup:
    def test_parse_group(self):
        group = UserGroup.model_validate(
            {
                "id": "g1",
                "name": "Engineering",
                "full_name": "Engineering",
                "up_id": "root",
                "up_ids": ["root"],
            }
        )
        assert group.id == "g1"
        assert group.name == "Engineering"
