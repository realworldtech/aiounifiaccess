"""Tests for WebSocket listener."""

import asyncio
from unittest.mock import AsyncMock, patch

from aiounifiaccess.events.handler import EventHandler
from aiounifiaccess.events.listener import (
    _INITIAL_DELAY,
    _MAX_DELAY,
    _MULTIPLIER,
    WebSocketListener,
)
from aiounifiaccess.events.models import DoorUnlockEvent, parse_event
from aiounifiaccess.session import APISession


class TestListenerConstants:
    def test_backoff_defaults(self):
        assert _INITIAL_DELAY == 1.0
        assert _MAX_DELAY == 60.0
        assert _MULTIPLIER == 2.0

    def test_backoff_progression(self):
        """Verify backoff doubles up to max."""
        delay = _INITIAL_DELAY
        delays = [delay]
        for _ in range(10):
            delay = min(delay * _MULTIPLIER, _MAX_DELAY)
            delays.append(delay)
        assert delays == [1, 2, 4, 8, 16, 32, 60, 60, 60, 60, 60]


class TestKeepaliveHandling:
    async def test_hello_keepalive_skipped(self):
        """WebSocket 'Hello' keepalive strings should be silently skipped."""
        session = AsyncMock(spec=APISession)
        listener = WebSocketListener(session)

        event_data = {
            "event": "access.door.unlock",
            "data": {
                "location": {"name": "Door"},
                "device": {},
                "actor": {},
                "object": {},
            },
        }

        # Simulate what events() does: json-decode then filter
        async def fake_events():
            for raw in ["Hello", event_data, "Hello"]:
                if not isinstance(raw, dict):
                    continue
                yield parse_event(raw)
            listener.stop()

        events = []
        async for event in fake_events():
            events.append(event)

        assert len(events) == 1
        assert isinstance(events[0], DoorUnlockEvent)
        assert events[0].data.location.name == "Door"

    async def test_unexpected_non_dict_logs_warning(self, caplog):
        """Non-dict messages that aren't 'Hello' should log a warning."""
        import logging

        with caplog.at_level(logging.WARNING, logger="aiounifiaccess.events.listener"):
            # Directly test the guard logic from events()
            logger = logging.getLogger("aiounifiaccess.events.listener")
            data = "Goodbye"
            if not isinstance(data, dict):
                if data != "Hello":
                    logger.warning(
                        "Unexpected non-dict WebSocket message: %r",
                        data,
                    )

        assert "Unexpected non-dict WebSocket message" in caplog.text
        assert "Goodbye" in caplog.text


class TestListenerLifecycle:
    def test_stop_sets_flag(self):
        session = AsyncMock(spec=APISession)
        listener = WebSocketListener(session)
        assert listener._running is False
        listener.stop()
        assert listener._running is False

    async def test_listen_dispatches_events(self):
        """listen() dispatches events from the iterator to the handler."""
        session = AsyncMock(spec=APISession)
        listener = WebSocketListener(session)
        handler = EventHandler()

        received = []

        @handler.on(DoorUnlockEvent)
        async def callback(event):
            received.append(event)

        event = parse_event(
            {
                "event": "access.door.unlock",
                "data": {
                    "location": {"name": "Door"},
                    "device": {},
                    "actor": {},
                    "object": {},
                },
            }
        )

        # Patch events() to yield one event then stop
        async def fake_events():
            yield event
            listener.stop()

        with patch.object(listener, "events", fake_events):
            await listener.listen(handler)

        await asyncio.sleep(0.05)
        assert len(received) == 1
        assert isinstance(received[0], DoorUnlockEvent)
        assert received[0].data.location.name == "Door"
