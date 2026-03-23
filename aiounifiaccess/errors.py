"""Exception hierarchy for the UniFi Access API client."""

from __future__ import annotations


class UniFiAccessError(Exception):
    """Base exception for all aiounifiaccess errors."""


class APIError(UniFiAccessError):
    """Base for all API response errors (non-SUCCESS code)."""

    def __init__(self, *, code: str, message: str, http_status: int) -> None:
        self.code = code
        self.message = message
        self.http_status = http_status
        super().__init__(f"{code}: {message}")


# --- Authentication & Authorization ---


class AuthenticationError(APIError):
    """CODE_AUTH_FAILED, CODE_ACCESS_TOKEN_INVALID."""


class UnauthorizedError(APIError):
    """CODE_UNAUTHORIZED, CODE_OPERATION_FORBIDDEN."""


# --- Resource errors ---


class ResourceNotFoundError(APIError):
    """CODE_RESOURCE_NOT_FOUND, CODE_NOT_EXISTS, etc."""


class ResourceConflictError(APIError):
    """CODE_USER_NAME_DUPLICATED, CODE_DEVICE_WEBHOOK_ENDPOINT_DUPLICATED, etc."""


class InvalidParametersError(APIError):
    """CODE_PARAMS_INVALID, CODE_USER_EMAIL_ERROR, etc."""


# --- Device errors ---


class DeviceError(APIError):
    """Base for device-related issues."""


class DeviceNotFoundError(DeviceError):
    """CODE_DEVICE_DEVICE_NOT_FOUND."""


class DeviceOfflineError(DeviceError):
    """CODE_DEVICE_DEVICE_OFFLINE."""


class DeviceBusyError(DeviceError):
    """CODE_DEVICE_DEVICE_BUSY."""


class DeviceVersionError(DeviceError):
    """CODE_DEVICE_DEVICE_VERSION_NOT_FOUND, CODE_DEVICE_DEVICE_VERSION_TOO_OLD."""


class APINotSupportedError(DeviceError):
    """CODE_DEVICE_API_NOT_SUPPORTED."""


# --- Credential errors ---


class CredentialError(APIError):
    """Base for NFC/PIN issues."""


class NFCCardBoundError(CredentialError):
    """CODE_CREDS_NFC_HAS_BIND_USER."""


class NFCCardInvalidError(CredentialError):
    """CODE_CREDS_NFC_CARD_INVALID."""


class NFCCardProvisionError(CredentialError):
    """CODE_CREDS_NFC_CARD_IS_PROVISION, CODE_CREDS_NFC_CARD_PROVISION_FAILED."""


class PINCodeExistsError(CredentialError):
    """CODE_CREDS_PIN_CODE_CREDS_ALREADY_EXIST."""


# --- Access policy errors ---


class AccessPolicyError(APIError):
    """CODE_ACCESS_POLICY_* family."""


class HolidayGroupError(APIError):
    """CODE_HOLIDAY_GROUP_CAN_NOT_DELETE, CODE_HOLIDAY_GROUP_CAN_NOT_EDIT."""


# --- HTTP-level errors (not from API error code system) ---


class RateLimitedError(UniFiAccessError):
    """HTTP 429 Too Many Requests."""

    def __init__(
        self, message: str, *, http_status: int, headers: dict | None = None
    ) -> None:
        self.message = message
        self.http_status = http_status
        self.headers = headers or {}
        super().__init__(message)


class RequestFailedError(UniFiAccessError):
    """HTTP 402 Payment Required."""

    def __init__(self, message: str, *, http_status: int) -> None:
        self.message = message
        self.http_status = http_status
        super().__init__(message)


class ServerError(UniFiAccessError):
    """HTTP 500/502/503/504 or CODE_SYSTEM_ERROR."""

    def __init__(self, message: str, *, http_status: int) -> None:
        self.message = message
        self.http_status = http_status
        super().__init__(message)


class UniFiConnectionError(UniFiAccessError):
    """WebSocket or HTTP connection failures."""


# --- Error code mapping ---

_ERROR_CODE_MAP: dict[str, type[APIError]] = {
    # Authentication
    "CODE_AUTH_FAILED": AuthenticationError,
    "CODE_ACCESS_TOKEN_INVALID": AuthenticationError,
    # Authorization
    "CODE_UNAUTHORIZED": UnauthorizedError,
    "CODE_OPERATION_FORBIDDEN": UnauthorizedError,
    # Resource not found
    "CODE_RESOURCE_NOT_FOUND": ResourceNotFoundError,
    "CODE_NOT_EXISTS": ResourceNotFoundError,
    "CODE_USER_ACCOUNT_NOT_EXIST": ResourceNotFoundError,
    "CODE_USER_WORKER_NOT_EXISTS": ResourceNotFoundError,
    "CODE_SPACE_DEVICE_BOUND_LOCATION_NOT_FOUND": ResourceNotFoundError,
    # Resource conflict
    "CODE_USER_NAME_DUPLICATED": ResourceConflictError,
    "CODE_DEVICE_WEBHOOK_ENDPOINT_DUPLICATED": ResourceConflictError,
    # Invalid parameters
    "CODE_PARAMS_INVALID": InvalidParametersError,
    "CODE_USER_EMAIL_ERROR": InvalidParametersError,
    "CODE_USER_CSV_IMPORT_INCOMPLETE_PROP": InvalidParametersError,
    "CODE_CREDS_PIN_CODE_CREDS_LENGTH_INVALID": InvalidParametersError,
    # Device errors
    "CODE_DEVICE_DEVICE_NOT_FOUND": DeviceNotFoundError,
    "CODE_DEVICE_DEVICE_OFFLINE": DeviceOfflineError,
    "CODE_DEVICE_DEVICE_BUSY": DeviceBusyError,
    "CODE_DEVICE_DEVICE_VERSION_NOT_FOUND": DeviceVersionError,
    "CODE_DEVICE_DEVICE_VERSION_TOO_OLD": DeviceVersionError,
    "CODE_DEVICE_API_NOT_SUPPORTED": APINotSupportedError,
    "CODE_OTHERS_UID_ADOPTED_NOT_SUPPORTED": APINotSupportedError,
    # Credential errors
    "CODE_CREDS_NFC_HAS_BIND_USER": NFCCardBoundError,
    "CODE_CREDS_DISABLE_TRANSFER_UID_USER_NFC": NFCCardBoundError,
    "CODE_CREDS_NFC_CARD_INVALID": NFCCardInvalidError,
    "CODE_CREDS_NFC_CARD_IS_PROVISION": NFCCardProvisionError,
    "CODE_CREDS_NFC_CARD_PROVISION_FAILED": NFCCardProvisionError,
    "CODE_CREDS_NFC_READ_SESSION_NOT_FOUND": CredentialError,
    "CODE_CREDS_NFC_READ_POLL_TOKEN_EMPTY": CredentialError,
    "CODE_CREDS_NFC_CARD_CANNOT_BE_DELETE": CredentialError,
    "CODE_CREDS_PIN_CODE_CREDS_ALREADY_EXIST": PINCodeExistsError,
    # Access policy errors
    "CODE_ACCESS_POLICY_USER_TIMEZONE_NOT_FOUND": AccessPolicyError,
    "CODE_ACCESS_POLICY_HOLIDAY_TIMEZONE_NOT_FOUND": AccessPolicyError,
    "CODE_ACCESS_POLICY_HOLIDAY_GROUP_NOT_FOUND": AccessPolicyError,
    "CODE_ACCESS_POLICY_HOLIDAY_NOT_FOUND": AccessPolicyError,
    "CODE_ACCESS_POLICY_SCHEDULE_NOT_FOUND": AccessPolicyError,
    "CODE_ACCESS_POLICY_HOLIDAY_NAME_EXIST": AccessPolicyError,
    "CODE_ACCESS_POLICY_HOLIDAY_GROUP_NAME_EXIST": AccessPolicyError,
    "CODE_ACCESS_POLICY_SCHEDULE_NAME_EXIST": AccessPolicyError,
    "CODE_ACCESS_POLICY_SCHEDULE_CAN_NOT_DELETE": AccessPolicyError,
    "CODE_ACCESS_POLICY_HOLIDAY_GROUP_CAN_NOT_DELETE": AccessPolicyError,
    # Holiday group errors
    "CODE_HOLIDAY_GROUP_CAN_NOT_DELETE": HolidayGroupError,
    "CODE_HOLIDAY_GROUP_CAN_NOT_EDIT": HolidayGroupError,
    # System error (maps to ServerError but through API code path)
    "CODE_SYSTEM_ERROR": ServerError,
}


def map_error_code(code: str) -> type[APIError] | type[ServerError]:
    """Map an API error code string to the appropriate exception class.

    Unknown codes fall back to APIError.
    """
    return _ERROR_CODE_MAP.get(code, APIError)
