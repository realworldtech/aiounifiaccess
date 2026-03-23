"""aiohttp session management, SSL config, and base request methods."""

from __future__ import annotations

import logging
import ssl
from typing import Any

import aiohttp

from aiounifiaccess.auth import build_headers
from aiounifiaccess.errors import (
    RateLimitedError,
    RequestFailedError,
    ServerError,
    UniFiConnectionError,
    map_error_code,
)

logger = logging.getLogger(__name__)


class APISession:
    """Wraps aiohttp.ClientSession with auth, SSL, and response handling."""

    def __init__(
        self,
        host: str,
        api_token: str,
        port: int = 12445,
        verify_ssl: bool = False,
        ssl_context: ssl.SSLContext | str | None = None,
        request_timeout: int = 30,
    ) -> None:
        self._host = host
        self._api_token = api_token
        self._port = port
        self._verify_ssl = verify_ssl
        self._ssl_context = ssl_context
        self._request_timeout = request_timeout
        self._session: aiohttp.ClientSession | None = None
        self.base_url = f"https://{self._host}:{self._port}"
        self.ws_url = (
            f"wss://{self._host}:{self._port}"
            f"/api/v1/developer/devices/notifications"
        )
        # Pre-built headers (avoids dict allocation per request)
        self._json_headers = build_headers(self._api_token)
        self._file_headers = build_headers(self._api_token, content_type=None)

    def _build_ssl_context(self) -> ssl.SSLContext | bool:
        """Build SSL context for requests."""
        if self._ssl_context is not None:
            if isinstance(self._ssl_context, str):
                ctx = ssl.create_default_context(cafile=self._ssl_context)
                return ctx
            return self._ssl_context
        if not self._verify_ssl:
            return False
        return True

    async def connect(self) -> None:
        """Create the aiohttp ClientSession."""
        if not self._verify_ssl and self._ssl_context is None:
            logger.warning(
                "SSL verification is disabled. This is insecure and should "
                "only be used with trusted networks or self-signed certificates."
            )
        timeout = aiohttp.ClientTimeout(total=self._request_timeout)
        connector = aiohttp.TCPConnector(ssl=self._build_ssl_context())
        self._session = aiohttp.ClientSession(
            base_url=self.base_url,
            timeout=timeout,
            connector=connector,
        )

    async def close(self) -> None:
        """Close the aiohttp ClientSession."""
        if self._session is not None:
            await self._session.close()
            self._session = None

    def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            raise UniFiConnectionError(
                "Session not connected. Call connect() or use async with."
            )
        return self._session

    def _check_http_status(self, resp: aiohttp.ClientResponse) -> None:
        """Check HTTP status and raise appropriate errors for non-JSON cases."""
        if resp.status == 429:
            raise RateLimitedError(
                "Rate limited by UniFi Access API",
                http_status=429,
                headers=dict(resp.headers),
            )
        if resp.status == 402:
            raise RequestFailedError(
                "Request failed (402)",
                http_status=402,
            )
        if resp.status >= 500:
            raise ServerError(
                f"Server error: HTTP {resp.status}",
                http_status=resp.status,
            )

    async def _parse_json_response(self, resp: aiohttp.ClientResponse) -> dict:
        """Parse JSON from response, handling non-JSON error responses."""
        try:
            return await resp.json()
        except (aiohttp.ContentTypeError, ValueError):
            # Non-JSON response for a 4xx error
            text = await resp.text()
            if resp.status >= 400:
                raise RequestFailedError(
                    f"HTTP {resp.status}: {text}",
                    http_status=resp.status,
                )
            raise UniFiConnectionError(f"Unexpected non-JSON response: {text[:200]}")

    def _unwrap_envelope(self, raw: dict) -> dict | list | None:
        """Unwrap the API response envelope, raising on error codes."""
        code = raw.get("code", "")
        if code == "SUCCESS":
            return raw.get("data")
        msg = raw.get("msg", "Unknown error")
        exc_cls = map_error_code(code)
        if exc_cls is ServerError:
            raise ServerError(msg, http_status=500)
        raise exc_cls(code=code, message=msg, http_status=400)

    async def _request_raw(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, Any] | None = None,
    ) -> dict:
        """Make an HTTP request and return the full JSON response dict.

        Does NOT unwrap the envelope. Used by BaseAPIManager for pagination.
        """
        session = self._ensure_session()

        try:
            async with session.request(
                method, path, json=json, params=params, headers=self._json_headers
            ) as resp:
                self._check_http_status(resp)
                return await self._parse_json_response(resp)
        except aiohttp.ClientError as exc:
            raise UniFiConnectionError(str(exc)) from exc

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, Any] | None = None,
    ) -> dict | list | None:
        """Make an HTTP request, unwrap the envelope, and return the data.

        Raises typed exceptions for API error codes.
        """
        raw = await self._request_raw(method, path, json=json, params=params)
        return self._unwrap_envelope(raw)

    async def _request_file(
        self,
        method: str,
        path: str,
        *,
        data: aiohttp.FormData | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict | list | None:
        """Make an HTTP request with multipart form data."""
        session = self._ensure_session()

        try:
            async with session.request(
                method, path, data=data, params=params, headers=self._file_headers
            ) as resp:
                self._check_http_status(resp)
                raw = await self._parse_json_response(resp)
                return self._unwrap_envelope(raw)
        except aiohttp.ClientError as exc:
            raise UniFiConnectionError(str(exc)) from exc

    async def _request_bytes(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, Any] | None = None,
    ) -> bytes:
        """Make an HTTP request and return raw bytes (for file downloads)."""
        session = self._ensure_session()

        try:
            async with session.request(
                method, path, json=json, params=params, headers=self._json_headers
            ) as resp:
                self._check_http_status(resp)
                return await resp.read()
        except aiohttp.ClientError as exc:
            raise UniFiConnectionError(str(exc)) from exc
