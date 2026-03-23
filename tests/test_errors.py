"""Tests for the exception hierarchy and error code mapping."""

from aiounifiaccess.errors import (
    AccessPolicyError,
    APIError,
    APINotSupportedError,
    AuthenticationError,
    CredentialError,
    DeviceBusyError,
    DeviceError,
    DeviceNotFoundError,
    DeviceOfflineError,
    DeviceVersionError,
    HolidayGroupError,
    InvalidParametersError,
    NFCCardBoundError,
    NFCCardInvalidError,
    NFCCardProvisionError,
    PINCodeExistsError,
    RateLimitedError,
    ResourceConflictError,
    ResourceNotFoundError,
    ServerError,
    UnauthorizedError,
    UniFiAccessError,
    UniFiConnectionError,
    map_error_code,
)


class TestExceptionHierarchy:
    def test_base_exception(self):
        err = UniFiAccessError("something broke")
        assert str(err) == "something broke"
        assert isinstance(err, Exception)

    def test_api_error_carries_context(self):
        err = APIError(
            code="CODE_PARAMS_INVALID",
            message="Invalid parameters.",
            http_status=400,
        )
        assert err.code == "CODE_PARAMS_INVALID"
        assert err.message == "Invalid parameters."
        assert err.http_status == 400
        assert isinstance(err, UniFiAccessError)

    def test_device_error_inheritance(self):
        err = DeviceOfflineError(
            code="CODE_DEVICE_DEVICE_OFFLINE",
            message="The device is currently offline.",
            http_status=400,
        )
        assert isinstance(err, DeviceError)
        assert isinstance(err, APIError)
        assert isinstance(err, UniFiAccessError)

    def test_credential_error_inheritance(self):
        err = NFCCardBoundError(
            code="CODE_CREDS_NFC_HAS_BIND_USER",
            message="The NFC card is already registered.",
            http_status=400,
        )
        assert isinstance(err, CredentialError)
        assert isinstance(err, APIError)

    def test_rate_limited_not_api_error(self):
        """RateLimitedError is a UniFiAccessError but not an APIError."""
        err = RateLimitedError("Too many requests", http_status=429)
        assert isinstance(err, UniFiAccessError)
        assert not isinstance(err, APIError)

    def test_connection_error_does_not_shadow_builtin(self):
        """UniFiConnectionError is distinct from Python's ConnectionError."""
        err = UniFiConnectionError("WebSocket disconnected")
        assert isinstance(err, UniFiAccessError)
        assert not isinstance(err, ConnectionError)  # Python builtin


class TestErrorCodeMapping:
    def test_auth_failed(self):
        cls = map_error_code("CODE_AUTH_FAILED")
        assert cls is AuthenticationError

    def test_access_token_invalid(self):
        cls = map_error_code("CODE_ACCESS_TOKEN_INVALID")
        assert cls is AuthenticationError

    def test_unauthorized(self):
        cls = map_error_code("CODE_UNAUTHORIZED")
        assert cls is UnauthorizedError

    def test_operation_forbidden(self):
        cls = map_error_code("CODE_OPERATION_FORBIDDEN")
        assert cls is UnauthorizedError

    def test_resource_not_found(self):
        cls = map_error_code("CODE_RESOURCE_NOT_FOUND")
        assert cls is ResourceNotFoundError

    def test_not_exists(self):
        cls = map_error_code("CODE_NOT_EXISTS")
        assert cls is ResourceNotFoundError

    def test_user_account_not_exist(self):
        cls = map_error_code("CODE_USER_ACCOUNT_NOT_EXIST")
        assert cls is ResourceNotFoundError

    def test_user_worker_not_exists(self):
        cls = map_error_code("CODE_USER_WORKER_NOT_EXISTS")
        assert cls is ResourceNotFoundError

    def test_user_name_duplicated(self):
        cls = map_error_code("CODE_USER_NAME_DUPLICATED")
        assert cls is ResourceConflictError

    def test_params_invalid(self):
        cls = map_error_code("CODE_PARAMS_INVALID")
        assert cls is InvalidParametersError

    def test_user_email_error(self):
        cls = map_error_code("CODE_USER_EMAIL_ERROR")
        assert cls is InvalidParametersError

    def test_pin_code_length_invalid(self):
        cls = map_error_code("CODE_CREDS_PIN_CODE_CREDS_LENGTH_INVALID")
        assert cls is InvalidParametersError

    def test_device_not_found(self):
        cls = map_error_code("CODE_DEVICE_DEVICE_NOT_FOUND")
        assert cls is DeviceNotFoundError

    def test_device_offline(self):
        cls = map_error_code("CODE_DEVICE_DEVICE_OFFLINE")
        assert cls is DeviceOfflineError

    def test_device_busy(self):
        cls = map_error_code("CODE_DEVICE_DEVICE_BUSY")
        assert cls is DeviceBusyError

    def test_device_version_not_found(self):
        cls = map_error_code("CODE_DEVICE_DEVICE_VERSION_NOT_FOUND")
        assert cls is DeviceVersionError

    def test_device_version_too_old(self):
        cls = map_error_code("CODE_DEVICE_DEVICE_VERSION_TOO_OLD")
        assert cls is DeviceVersionError

    def test_nfc_card_bound(self):
        cls = map_error_code("CODE_CREDS_NFC_HAS_BIND_USER")
        assert cls is NFCCardBoundError

    def test_nfc_card_invalid(self):
        cls = map_error_code("CODE_CREDS_NFC_CARD_INVALID")
        assert cls is NFCCardInvalidError

    def test_nfc_card_provision(self):
        cls = map_error_code("CODE_CREDS_NFC_CARD_IS_PROVISION")
        assert cls is NFCCardProvisionError

    def test_nfc_card_provision_failed(self):
        cls = map_error_code("CODE_CREDS_NFC_CARD_PROVISION_FAILED")
        assert cls is NFCCardProvisionError

    def test_pin_code_exists(self):
        cls = map_error_code("CODE_CREDS_PIN_CODE_CREDS_ALREADY_EXIST")
        assert cls is PINCodeExistsError

    def test_api_not_supported(self):
        cls = map_error_code("CODE_DEVICE_API_NOT_SUPPORTED")
        assert cls is APINotSupportedError

    def test_unknown_code_falls_back_to_api_error(self):
        cls = map_error_code("CODE_SOME_FUTURE_ERROR")
        assert cls is APIError

    def test_system_error(self):
        cls = map_error_code("CODE_SYSTEM_ERROR")
        assert cls is ServerError

    def test_webhook_endpoint_duplicated(self):
        cls = map_error_code("CODE_DEVICE_WEBHOOK_ENDPOINT_DUPLICATED")
        assert cls is ResourceConflictError

    def test_holiday_group_cant_delete(self):
        cls = map_error_code("CODE_HOLIDAY_GROUP_CAN_NOT_DELETE")
        assert cls is HolidayGroupError

    def test_holiday_group_cant_edit(self):
        cls = map_error_code("CODE_HOLIDAY_GROUP_CAN_NOT_EDIT")
        assert cls is HolidayGroupError

    def test_access_policy_schedule_not_found(self):
        cls = map_error_code("CODE_ACCESS_POLICY_SCHEDULE_NOT_FOUND")
        assert cls is AccessPolicyError

    def test_access_policy_holiday_name_exist(self):
        cls = map_error_code("CODE_ACCESS_POLICY_HOLIDAY_NAME_EXIST")
        assert cls is AccessPolicyError

    def test_access_policy_schedule_cant_delete(self):
        cls = map_error_code("CODE_ACCESS_POLICY_SCHEDULE_CAN_NOT_DELETE")
        assert cls is AccessPolicyError
