"""Webhook API manager."""

from __future__ import annotations

from aiounifiaccess.api.base import BaseAPIManager
from aiounifiaccess.models.webhook import WebhookEndpoint


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
