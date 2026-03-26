"""Webhook receiver for UniFi Access event notifications."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import TYPE_CHECKING

from aiohttp import web

from aiounifiaccess.events.models import parse_event
from aiounifiaccess.events.signature import verify_webhook_signature

if TYPE_CHECKING:
    from aiounifiaccess.events.handler import EventHandler

logger = logging.getLogger(__name__)

_SIGNATURE_HEADER = "Signature"


class WebhookReceiver:
    """HTTP server that receives webhook events from UniFi Access.

    The UniFi Access controller POSTs JSON event payloads to registered
    webhook endpoints. This receiver verifies signatures, parses events,
    and dispatches them through an ``EventHandler``.

    Usage::

        receiver = WebhookReceiver(webhook_secret="...")

        @handler.on(DoorUnlockEvent)
        async def handle(event):
            print(event)

        await receiver.listen(handler)

    Or as part of a ``UniFiAccessClient`` via the ``webhook_secret``
    parameter, which runs both WebSocket and webhook listeners together.
    """

    def __init__(
        self,
        webhook_secret: str,
        *,
        host: str = "0.0.0.0",
        port: int = 8080,
        path: str = "/webhook",
        max_age_seconds: int | None = 300,
    ) -> None:
        self._secret = webhook_secret
        self._host = host
        self._port = port
        self._path = path
        self._max_age_seconds = max_age_seconds
        self._handler: EventHandler | None = None
        self._runner: web.AppRunner | None = None
        self._shutdown_event: asyncio.Event | None = None

        self._app = web.Application()
        self._app.router.add_post(self._path, self._handle_webhook)

    async def _handle_webhook(self, request: web.Request) -> web.Response:
        """Handle an incoming webhook POST from the UniFi controller."""
        body = await request.read()

        # Verify signature
        sig_header = request.headers.get(_SIGNATURE_HEADER)
        if not sig_header:
            logger.warning("Webhook request missing %s header", _SIGNATURE_HEADER)
            return web.Response(status=401, text="Missing signature")

        if not verify_webhook_signature(
            self._secret,
            sig_header,
            body,
            max_age_seconds=self._max_age_seconds,
        ):
            logger.warning("Webhook signature verification failed")
            return web.Response(status=401, text="Invalid signature")

        # Parse JSON
        try:
            data = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            logger.warning("Webhook request with malformed JSON body")
            return web.Response(status=400, text="Malformed JSON")

        logger.debug("Webhook event received: %r", data)

        # Parse and dispatch event
        try:
            event = parse_event(data)
        except Exception:
            logger.error("Failed to parse webhook event: %r", data, exc_info=True)
            return web.Response(status=200)

        if self._handler is not None:
            await self._handler.dispatch(event)

        return web.Response(status=200)

    def set_handler(self, handler: EventHandler) -> None:
        """Set the event handler for dispatching received events."""
        self._handler = handler

    async def start(self) -> None:
        """Start the webhook HTTP server."""
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, self._host, self._port)
        await site.start()
        logger.info(
            "Webhook receiver listening on %s:%d%s",
            self._host,
            self._port,
            self._path,
        )

    async def stop(self) -> None:
        """Stop the webhook HTTP server."""
        if self._shutdown_event is not None:
            self._shutdown_event.set()
        if self._runner is not None:
            await self._runner.cleanup()
            self._runner = None
        logger.info("Webhook receiver stopped")

    async def listen(self, handler: EventHandler) -> None:
        """Start the server and dispatch events to the handler.

        Blocks until ``stop()`` is called.
        """
        self._handler = handler
        self._shutdown_event = asyncio.Event()
        await self.start()
        try:
            await self._shutdown_event.wait()
        finally:
            await self.stop()

    async def __aenter__(self) -> WebhookReceiver:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()
