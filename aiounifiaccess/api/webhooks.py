"""Webhook API manager."""

from __future__ import annotations

import logging

from aiounifiaccess.api.base import BaseAPIManager
from aiounifiaccess.models.webhook import WebhookEndpoint, WebhookEventType

logger = logging.getLogger(__name__)


class WebhookManager(BaseAPIManager):
    """Manages webhook endpoints (API sections 11.3-11.6)."""

    _BASE = "/api/v1/developer/webhooks/endpoints"

    async def list_endpoints(self) -> list[WebhookEndpoint]:
        return await self._get_list_unpaginated(self._BASE, WebhookEndpoint)

    async def create_endpoint(
        self,
        endpoint: str,
        name: str,
        events: list[str],
        headers: dict[str, str] | None = None,
    ) -> WebhookEndpoint:
        body: dict = {"endpoint": endpoint, "name": name, "events": events}
        if headers:
            body["headers"] = headers
        return await self._post(self._BASE, json=body, model_cls=WebhookEndpoint)

    async def update_endpoint(
        self,
        endpoint_id: str,
        *,
        endpoint: str | None = None,
        name: str | None = None,
        events: list[str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> WebhookEndpoint:
        body: dict = {}
        if endpoint is not None:
            body["endpoint"] = endpoint
        if name is not None:
            body["name"] = name
        if events is not None:
            body["events"] = events
        if headers is not None:
            body["headers"] = headers
        return await self._put(
            f"{self._BASE}/{endpoint_id}", json=body, model_cls=WebhookEndpoint
        )

    async def delete_endpoint(self, endpoint_id: str) -> None:
        await self._delete(f"{self._BASE}/{endpoint_id}")

    async def ensure_endpoint(
        self,
        endpoint: str,
        name: str,
        events: list[str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> WebhookEndpoint:
        """Ensure a webhook endpoint is registered, creating it if needed.

        If an existing endpoint matches the same URL and event set, it is
        returned as-is. If the URL matches but events differ, the existing
        endpoint is updated. Otherwise a new endpoint is created.

        Pass ``events=None`` (the default) to subscribe to all known
        webhook event types.

        Returns the ``WebhookEndpoint`` including the ``secret`` needed
        by ``WebhookReceiver``.
        """
        if events is None:
            events = WebhookEventType.all()

        desired_events = sorted(events)
        existing = await self.list_endpoints()

        for ep in existing:
            if ep.endpoint != endpoint:
                continue

            # Same URL — check if events match
            if sorted(ep.events) == desired_events:
                logger.info(
                    "Webhook endpoint already registered: %s (%s)",
                    ep.endpoint,
                    ep.id,
                )
                return ep

            # Same URL, different events — update
            logger.info(
                "Updating webhook endpoint %s events: %s -> %s",
                ep.id,
                ep.events,
                events,
            )
            return await self.update_endpoint(
                ep.id, events=events, name=name, headers=headers
            )

        # No match — create new
        logger.info("Creating webhook endpoint: %s", endpoint)
        return await self.create_endpoint(endpoint, name, events, headers=headers)
