"""Event callback registry and dispatch."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Coroutine

from aiounifiaccess.events.models import BaseEvent, parse_event

logger = logging.getLogger(__name__)

EventCallback = Callable[[Any], Coroutine[Any, Any, None]]


class EventHandler:
    """Manages event callback registration and dispatch."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventCallback]] = {}

    def on(
        self, event_type: type[BaseEvent] | str
    ) -> Callable[[EventCallback], EventCallback]:
        """Decorator to register an event handler.

        Can register by event model class or event name string::

            @handler.on(DoorUnlockEvent)
            async def handle(event):
                ...

            @handler.on("access.door.unlock")
            async def handle(event):
                ...
        """
        if isinstance(event_type, str):
            event_name = event_type
        else:
            # Get event name from model class default
            event_name = event_type.model_fields["event"].default

        def decorator(func: EventCallback) -> EventCallback:
            self._handlers.setdefault(event_name, []).append(func)
            return func

        return decorator

    async def _run_handler(self, handler: EventCallback, event: BaseEvent) -> None:
        """Run a handler with error catching so exceptions don't propagate."""
        try:
            await handler(event)
        except Exception:
            logger.error(
                "Error in event handler %s for %s",
                handler.__name__,
                event.event,
                exc_info=True,
            )

    async def dispatch(self, event: BaseEvent) -> None:
        """Dispatch a parsed event to registered handlers."""
        event_name = event.event

        # Dispatch to specific handlers
        handlers = list(self._handlers.get(event_name, []))

        for handler in handlers:
            asyncio.create_task(self._run_handler(handler, event))

    async def dispatch_raw(self, raw_data: dict) -> None:
        """Parse raw event data and dispatch to registered handlers."""
        event = parse_event(raw_data)
        await self.dispatch(event)
