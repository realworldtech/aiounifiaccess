"""Tests for webhook signature verification."""

import hashlib
import hmac
import time

from aiounifiaccess.events.signature import verify_webhook_signature


class TestVerifyWebhookSignature:
    def _make_signature(
        self, secret: str, body: bytes, timestamp: int | None = None
    ) -> str:
        ts = timestamp or int(time.time())
        signed_payload = str(ts).encode() + b"." + body
        mac = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
        return f"t={ts},v1={mac}"

    def test_valid_signature(self):
        secret = "6601f1243d2ff70f"
        body = b'{"event": "access.door.unlock"}'
        sig = self._make_signature(secret, body)
        assert verify_webhook_signature(secret, sig, body) is True

    def test_invalid_signature(self):
        secret = "6601f1243d2ff70f"
        body = b'{"event": "access.door.unlock"}'
        assert verify_webhook_signature(secret, "t=123,v1=badmac", body) is False

    def test_malformed_header(self):
        assert verify_webhook_signature("secret", "garbage", b"body") is False

    def test_empty_body(self):
        secret = "test"
        body = b""
        sig = self._make_signature(secret, body)
        assert verify_webhook_signature(secret, sig, body) is True

    def test_different_secret_fails(self):
        body = b"test body"
        sig = self._make_signature("secret1", body)
        assert verify_webhook_signature("secret2", sig, body) is False

    def test_expired_signature_rejected(self):
        secret = "test"
        body = b"payload"
        old_timestamp = int(time.time()) - 600  # 10 minutes ago
        sig = self._make_signature(secret, body, timestamp=old_timestamp)
        assert verify_webhook_signature(secret, sig, body, max_age_seconds=300) is False

    def test_replay_protection_disabled(self):
        secret = "test"
        body = b"payload"
        old_timestamp = int(time.time()) - 600
        sig = self._make_signature(secret, body, timestamp=old_timestamp)
        assert verify_webhook_signature(secret, sig, body, max_age_seconds=None) is True

    def test_recent_signature_accepted(self):
        secret = "test"
        body = b"payload"
        recent = int(time.time()) - 10  # 10 seconds ago
        sig = self._make_signature(secret, body, timestamp=recent)
        assert verify_webhook_signature(secret, sig, body, max_age_seconds=300) is True
