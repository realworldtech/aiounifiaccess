"""Tests for event callback registry and dispatch."""

import asyncio

from aiounifiaccess.events.handler import EventHandler
from aiounifiaccess.events.models import (
    DoorUnlockEvent,
    RemoteViewEvent,
    parse_event,
)


class TestEventRegistration:
    def test_register_by_class(self):
        handler = EventHandler()

        @handler.on(DoorUnlockEvent)
        async def callback(event):
            pass

        assert "access.door.unlock" in handler._handlers
        assert callback in handler._handlers["access.door.unlock"]

    def test_register_by_string(self):
        handler = EventHandler()

        @handler.on("access.door.unlock")
        async def callback(event):
            pass

        assert "access.door.unlock" in handler._handlers

    def test_multiple_handlers(self):
        handler = EventHandler()

        @handler.on(DoorUnlockEvent)
        async def cb1(event):
            pass

        @handler.on(DoorUnlockEvent)
        async def cb2(event):
            pass

        assert len(handler._handlers["access.door.unlock"]) == 2


class TestEventDispatch:
    async def test_dispatch_calls_handler(self):
        handler = EventHandler()
        received = []

        @handler.on(DoorUnlockEvent)
        async def callback(event):
            received.append(event)

        event = parse_event(
            {
                "event": "access.door.unlock",
                "data": {
                    "location": {"name": "Test Door"},
                    "device": {},
                    "actor": {},
                    "object": {},
                },
            }
        )
        await handler.dispatch(event)
        # Give the task a chance to run
        await asyncio.sleep(0.05)
        assert len(received) == 1
        assert isinstance(received[0], DoorUnlockEvent)

    async def test_unregistered_event_not_dispatched(self):
        handler = EventHandler()
        received = []

        @handler.on(DoorUnlockEvent)
        async def callback(event):
            received.append(event)

        event = parse_event(
            {
                "event": "access.remote_view",
                "data": {"channel": "test"},
            }
        )
        await handler.dispatch(event)
        await asyncio.sleep(0.05)
        assert len(received) == 0

    async def test_handler_receives_typed_event(self):
        handler = EventHandler()
        received = []

        @handler.on(RemoteViewEvent)
        async def callback(event):
            received.append(event)

        event = parse_event(
            {
                "event": "access.remote_view",
                "data": {
                    "channel": "ch1",
                    "device_id": "dev1",
                },
            }
        )
        await handler.dispatch(event)
        await asyncio.sleep(0.05)
        assert len(received) == 1
        assert isinstance(received[0], RemoteViewEvent)
        assert received[0].data.channel == "ch1"

    async def test_handler_error_does_not_crash(self):
        handler = EventHandler()

        @handler.on(DoorUnlockEvent)
        async def bad_handler(event):
            raise ValueError("intentional error")

        event = parse_event(
            {
                "event": "access.door.unlock",
                "data": {
                    "location": {},
                    "device": {},
                    "actor": {},
                    "object": {},
                },
            }
        )
        # Should not raise
        await handler.dispatch(event)
        await asyncio.sleep(0.05)

    async def test_handler_error_is_logged(self, caplog):
        """Verify handler exceptions are caught and logged, not silently dropped."""
        import logging

        handler = EventHandler()

        @handler.on(DoorUnlockEvent)
        async def bad_handler(event):
            raise ValueError("intentional error")

        event = parse_event(
            {
                "event": "access.door.unlock",
                "data": {
                    "location": {},
                    "device": {},
                    "actor": {},
                    "object": {},
                },
            }
        )
        with caplog.at_level(logging.ERROR, logger="aiounifiaccess.events.handler"):
            await handler.dispatch(event)
            await asyncio.sleep(0.05)
        assert "intentional error" in caplog.text

    async def test_dispatch_raw(self):
        """dispatch_raw parses from dict and dispatches."""
        handler = EventHandler()
        received = []

        @handler.on(DoorUnlockEvent)
        async def callback(event):
            received.append(event)

        await handler.dispatch_raw(
            {
                "event": "access.door.unlock",
                "data": {
                    "location": {},
                    "device": {},
                    "actor": {},
                    "object": {},
                },
            }
        )
        await asyncio.sleep(0.05)
        assert len(received) == 1
        assert isinstance(received[0], DoorUnlockEvent)
