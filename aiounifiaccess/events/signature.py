"""Webhook signature verification."""

import hashlib
import hmac
import time


def verify_webhook_signature(
    secret: str,
    signature_header: str,
    body: bytes,
    *,
    max_age_seconds: int | None = 300,
) -> bool:
    """Verify a webhook signature from UniFi Access.

    The Signature header format is: ``t=<unix_timestamp>,v1=<hmac_sha256_hex>``

    The HMAC is computed over ``<timestamp>.<body>`` using the webhook
    secret as key (SHA-256).

    Args:
        secret: The webhook secret from endpoint registration.
        signature_header: The raw Signature header value.
        body: The raw request body bytes.
        max_age_seconds: Maximum age of the signature in seconds. Set to None
            to disable replay protection. Defaults to 300 (5 minutes).

    Returns:
        True if the signature is valid and not expired.
    """
    try:
        parts = dict(part.split("=", 1) for part in signature_header.split(","))
        received_mac = parts.get("v1", "")
        timestamp_str = parts.get("t", "0")
        timestamp = int(timestamp_str)
    except (ValueError, AttributeError):
        return False

    if max_age_seconds is not None and timestamp > 0:
        if abs(time.time() - timestamp) > max_age_seconds:
            return False

    # Sign timestamp + "." + body (standard webhook pattern)
    signed_payload = timestamp_str.encode() + b"." + body
    expected_mac = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_mac, received_mac)
