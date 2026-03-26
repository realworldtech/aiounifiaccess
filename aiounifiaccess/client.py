"""Main client for UniFi Access API."""

from __future__ import annotations

import asyncio
import ssl
from typing import AsyncIterator, Callable

from aiounifiaccess.events.handler import EventCallback, EventHandler
from aiounifiaccess.events.listener import WebSocketListener
from aiounifiaccess.events.models import BaseEvent
from aiounifiaccess.events.receiver import WebhookReceiver
from aiounifiaccess.session import APISession


class UniFiAccessClient:
    """Async client for the UniFi Access API.

    Usage::

        async with UniFiAccessClient(host, api_token) as client:
            users = await client.users.list()

            @client.on(DoorPositionEvent)
            async def handle(event):
                print(event.data.object.status)

            await client.listen()

    To also receive webhook events (e.g. credential-based door unlocks),
    pass ``webhook_secret``::

        async with UniFiAccessClient(
            host, api_token,
            webhook_secret="secret_from_endpoint_registration",
            webhook_port=8080,
        ) as client:
            @client.on(DoorUnlockEvent)
            async def handle(event):
                print(event.data.actor.name)

            await client.listen()  # runs both WebSocket + webhook
    """

    def __init__(
        self,
        host: str,
        api_token: str,
        port: int = 12445,
        verify_ssl: bool = False,
        ssl_context: ssl.SSLContext | str | None = None,
        request_timeout: int = 30,
        webhook_secret: str | None = None,
        webhook_host: str = "0.0.0.0",
        webhook_port: int = 8080,
        webhook_path: str = "/webhook",
    ) -> None:
        self._session = APISession(
            host=host,
            api_token=api_token,
            port=port,
            verify_ssl=verify_ssl,
            ssl_context=ssl_context,
            request_timeout=request_timeout,
        )
        self._event_handler = EventHandler()
        self._listener = WebSocketListener(self._session)

        if webhook_secret is not None:
            self._webhook_receiver: WebhookReceiver | None = WebhookReceiver(
                webhook_secret,
                host=webhook_host,
                port=webhook_port,
                path=webhook_path,
            )
        else:
            self._webhook_receiver = None

        # API managers
        from aiounifiaccess.api.access_policies import AccessPolicyManager
        from aiounifiaccess.api.credentials import CredentialManager
        from aiounifiaccess.api.devices import DeviceManager
        from aiounifiaccess.api.doors import DoorManager
        from aiounifiaccess.api.identity import IdentityManager
        from aiounifiaccess.api.server import ServerManager
        from aiounifiaccess.api.system_logs import SystemLogManager
        from aiounifiaccess.api.users import UserManager
        from aiounifiaccess.api.visitors import VisitorManager
        from aiounifiaccess.api.webhooks import WebhookManager

        self.users = UserManager(self._session)
        self.visitors = VisitorManager(self._session)
        self.access_policies = AccessPolicyManager(self._session)
        self.credentials = CredentialManager(self._session)
        self.doors = DoorManager(self._session)
        self.devices = DeviceManager(self._session)
        self.system_logs = SystemLogManager(self._session)
        self.identity = IdentityManager(self._session)
        self.webhooks = WebhookManager(self._session)
        self.server = ServerManager(self._session)

    def on(
        self, event_type: type[BaseEvent] | str
    ) -> Callable[[EventCallback], EventCallback]:
        """Register an event handler via decorator.

        Can register by event model class or event name string::

            @client.on(DoorUnlockEvent)
            async def handle(event: DoorUnlockEvent):
                ...
        """
        return self._event_handler.on(event_type)

    async def setup_webhook(
        self,
        endpoint_url: str,
        name: str = "aiounifiaccess",
        events: list[str] | None = None,
        *,
        host: str = "0.0.0.0",
        port: int = 8080,
        path: str = "/webhook",
    ) -> None:
        """Register a webhook on the controller and start the receiver.

        This is a convenience method that:
        1. Calls ``webhooks.ensure_endpoint()`` to idempotently register
           (or update) the webhook subscription on the UniFi controller.
        2. Creates a ``WebhookReceiver`` using the returned secret.

        The receiver is started automatically when ``listen()`` is called.

        Args:
            endpoint_url: The public URL the controller will POST to
                (e.g. ``"https://myserver:8080/webhook"``).
            name: Display name for the webhook subscription.
            events: Event types to subscribe to. Defaults to all known types.
            host: Bind address for the webhook receiver server.
            port: Port for the webhook receiver server.
            path: URL path the receiver listens on.
        """
        ep = await self.webhooks.ensure_endpoint(endpoint_url, name, events=events)
        self._webhook_receiver = WebhookReceiver(
            ep.secret, host=host, port=port, path=path
        )

    async def events(self) -> AsyncIterator[BaseEvent]:
        """Async iterator yielding parsed events from the WebSocket."""
        async for event in self._listener.events():
            yield event

    async def listen(self) -> None:
        """Start the event loop, dispatching to registered handlers.

        When ``webhook_secret`` was provided at construction, this runs
        both the WebSocket listener and the webhook HTTP receiver
        concurrently so all event types are covered.
        """
        if self._webhook_receiver is not None:
            await asyncio.gather(
                self._listener.listen(self._event_handler),
                self._webhook_receiver.listen(self._event_handler),
            )
        else:
            await self._listener.listen(self._event_handler)

    async def connect(self) -> None:
        """Create the underlying HTTP session."""
        await self._session.connect()

    async def close(self) -> None:
        """Close the underlying HTTP session and stop event listener."""
        self._listener.stop()
        if self._webhook_receiver is not None:
            await self._webhook_receiver.stop()
        await self._session.close()

    async def __aenter__(self) -> UniFiAccessClient:
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
