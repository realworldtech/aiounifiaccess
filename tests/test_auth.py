"""Tests for auth header construction."""

from aiounifiaccess.auth import build_headers


class TestBuildHeaders:
    def test_basic_headers(self):
        headers = build_headers("my-token-123")
        assert headers["Authorization"] == "Bearer my-token-123"
        assert headers["Accept"] == "application/json"
        assert headers["Content-Type"] == "application/json"

    def test_different_token(self):
        headers = build_headers("wHFmHRuX4I7sB2oDkD6wHg")
        assert headers["Authorization"] == "Bearer wHFmHRuX4I7sB2oDkD6wHg"

    def test_no_content_type_for_multipart(self):
        headers = build_headers("my-token-123", content_type=None)
        assert "Content-Type" not in headers
        assert headers["Authorization"] == "Bearer my-token-123"
