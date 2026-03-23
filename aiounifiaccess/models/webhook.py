"""Webhook domain models."""

from __future__ import annotations

from aiounifiaccess.models.common import BaseAPIModel


class WebhookEndpoint(BaseAPIModel):
    id: str = ""
    endpoint: str = ""
    name: str = ""
    secret: str = ""
    events: list[str] = []
    headers: dict[str, str] = {}
