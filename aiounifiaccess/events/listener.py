"""WebSocket listener with auto-reconnect."""

from __future__ import annotations

import asyncio
import logging
import random
from typing import TYPE_CHECKING, AsyncIterator

import aiohttp

from aiounifiaccess.events.handler import EventHandler
from aiounifiaccess.events.models import BaseEvent, parse_event

if TYPE_CHECKING:
    from aiounifiaccess.session import APISession

logger = logging.getLogger(__name__)

# Reconnection backoff settings
_INITIAL_DELAY = 1.0
_MAX_DELAY = 60.0
_MULTIPLIER = 2.0


class WebSocketListener:
    """WebSocket connection manager for real-time event notifications."""

    def __init__(self, session: APISession) -> None:
        self._session = session
        self._running = False

    async def events(self) -> AsyncIterator[BaseEvent]:
        """Connect to WebSocket and yield parsed events.

        Handles reconnection automatically with exponential backoff.
        Runs indefinitely until the client is closed.
        """
        self._running = True
        delay = _INITIAL_DELAY

        while self._running:
            try:
                http_session = self._session._ensure_session()
                headers = {
                    "Authorization": f"Bearer {self._session._api_token}",
                }
                ssl_ctx = self._session._build_ssl_context()

                async with http_session.ws_connect(
                    self._session.ws_url,
                    headers=headers,
                    ssl=ssl_ctx,
                ) as ws:
                    logger.info("WebSocket connected to %s", self._session.ws_url)
                    delay = _INITIAL_DELAY  # Reset on successful connect

                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            try:
                                data = msg.json()
                                if not isinstance(data, dict):
                                    if data != "Hello":
                                        logger.warning(
                                            "Unexpected non-dict WebSocket"
                                            " message: %r",
                                            data,
                                        )
                                    continue
                                yield parse_event(data)
                            except Exception:
                                logger.error(
                                    "Failed to parse WebSocket message",
                                    exc_info=True,
                                )
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            logger.warning("WebSocket error: %s", ws.exception())
                            break
                        elif msg.type in (
                            aiohttp.WSMsgType.CLOSE,
                            aiohttp.WSMsgType.CLOSING,
                            aiohttp.WSMsgType.CLOSED,
                        ):
                            break

            except asyncio.CancelledError:
                self._running = False
                return
            except Exception:
                if not self._running:
                    return
                logger.warning(
                    "WebSocket disconnected, reconnecting in %.1fs",
                    delay,
                    exc_info=True,
                )

            if not self._running:
                return

            # Exponential backoff with jitter
            jitter = random.uniform(0, delay * 0.1)
            await asyncio.sleep(delay + jitter)
            delay = min(delay * _MULTIPLIER, _MAX_DELAY)

    async def listen(self, handler: EventHandler) -> None:
        """Run the event loop and dispatch to registered handlers."""
        async for event in self.events():
            await handler.dispatch(event)

    def stop(self) -> None:
        """Signal the listener to stop."""
        self._running = False
