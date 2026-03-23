"""Tests for API session management."""

import logging

import pytest
from aresponses import ResponsesMockServer

from aiounifiaccess.errors import (
    AuthenticationError,
    RateLimitedError,
    ServerError,
    UniFiConnectionError,
)
from aiounifiaccess.session import APISession


@pytest.fixture
def session():
    return APISession(
        host="192.168.1.1",
        api_token="test-token-123",
        port=12445,
    )


class TestSessionProperties:
    def test_base_url(self, session):
        assert session.base_url == "https://192.168.1.1:12445"

    def test_ws_url(self, session):
        assert session.ws_url == (
            "wss://192.168.1.1:12445/api/v1/developer/devices/notifications"
        )

    def test_custom_port(self):
        s = APISession(host="10.0.0.1", api_token="tok", port=8443)
        assert s.base_url == "https://10.0.0.1:8443"


class TestSSLWarning:
    async def test_ssl_disabled_logs_warning(self, session, caplog):
        with caplog.at_level(logging.WARNING, logger="aiounifiaccess.session"):
            await session.connect()
            await session.close()
        assert "SSL verification is disabled" in caplog.text

    async def test_ssl_enabled_no_warning(self, caplog):
        s = APISession(host="x", api_token="t", verify_ssl=True)
        with caplog.at_level(logging.WARNING, logger="aiounifiaccess.session"):
            await s.connect()
            await s.close()
        assert "SSL verification is disabled" not in caplog.text


class TestRequest:
    async def test_success_returns_data(self, aresponses: ResponsesMockServer):
        aresponses.add(
            "192.168.1.1:12445",
            "/api/v1/developer/users",
            "GET",
            aresponses.Response(
                body=b'{"code":"SUCCESS","msg":"success","data":{"id":"abc"}}',
                content_type="application/json",
            ),
        )
        session = APISession(host="192.168.1.1", api_token="tok", port=12445)
        await session.connect()
        try:
            result = await session._request("GET", "/api/v1/developer/users")
            assert result == {"id": "abc"}
        finally:
            await session.close()

    async def test_error_code_raises_exception(self, aresponses: ResponsesMockServer):
        aresponses.add(
            "192.168.1.1:12445",
            "/api/v1/developer/users",
            "GET",
            aresponses.Response(
                body=b'{"code":"CODE_AUTH_FAILED","msg":"Authentication failed."}',
                content_type="application/json",
            ),
        )
        session = APISession(host="192.168.1.1", api_token="tok", port=12445)
        await session.connect()
        try:
            with pytest.raises(AuthenticationError) as exc_info:
                await session._request("GET", "/api/v1/developer/users")
            assert exc_info.value.code == "CODE_AUTH_FAILED"
        finally:
            await session.close()

    async def test_rate_limited(self, aresponses: ResponsesMockServer):
        aresponses.add(
            "192.168.1.1:12445",
            "/api/v1/developer/users",
            "GET",
            aresponses.Response(status=429, body=b"Too Many Requests"),
        )
        session = APISession(host="192.168.1.1", api_token="tok", port=12445)
        await session.connect()
        try:
            with pytest.raises(RateLimitedError) as exc_info:
                await session._request("GET", "/api/v1/developer/users")
            assert exc_info.value.http_status == 429
        finally:
            await session.close()

    async def test_server_error(self, aresponses: ResponsesMockServer):
        aresponses.add(
            "192.168.1.1:12445",
            "/api/v1/developer/users",
            "GET",
            aresponses.Response(status=500, body=b"Internal Server Error"),
        )
        session = APISession(host="192.168.1.1", api_token="tok", port=12445)
        await session.connect()
        try:
            with pytest.raises(ServerError) as exc_info:
                await session._request("GET", "/api/v1/developer/users")
            assert exc_info.value.http_status == 500
        finally:
            await session.close()

    async def test_request_raw_returns_full_response(
        self, aresponses: ResponsesMockServer
    ):
        aresponses.add(
            "192.168.1.1:12445",
            "/api/v1/developer/users",
            "GET",
            aresponses.Response(
                body=(
                    b'{"code":"SUCCESS","msg":"success",'
                    b'"data":[{"id":"1"}],'
                    b'"pagination":{"page_num":1,"page_size":25,"total":1}}'
                ),
                content_type="application/json",
            ),
        )
        session = APISession(host="192.168.1.1", api_token="tok", port=12445)
        await session.connect()
        try:
            raw = await session._request_raw("GET", "/api/v1/developer/users")
            assert raw["code"] == "SUCCESS"
            assert "pagination" in raw
            assert raw["data"] == [{"id": "1"}]
        finally:
            await session.close()


class TestSessionLifecycle:
    async def test_close_without_connect(self):
        session = APISession(host="x", api_token="t")
        await session.close()  # should not raise

    async def test_request_without_connect(self):
        session = APISession(host="x", api_token="t")
        with pytest.raises(UniFiConnectionError, match="not connected"):
            await session._request("GET", "/test")
