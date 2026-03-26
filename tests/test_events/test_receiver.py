"""Tests for webhook receiver."""

import asyncio
import hashlib
import hmac
import json
import time

import pytest
from aiohttp.test_utils import TestClient

from aiounifiaccess.events.handler import EventHandler
from aiounifiaccess.events.models import DoorUnlockEvent, RawEvent
from aiounifiaccess.events.receiver import WebhookReceiver


def _make_signature(secret: str, body: bytes, timestamp: int | None = None) -> str:
    ts = timestamp or int(time.time())
    mac = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"t={ts},v1={mac}"


SECRET = "test_webhook_secret"

DOOR_UNLOCK_PAYLOAD = json.dumps(
    {
        "event": "access.door.unlock",
        "event_object_id": "abc123",
        "data": {
            "location": {"id": "loc1", "name": "Front Door"},
            "device": {"id": "dev1", "name": "UA-HUB"},
            "actor": {"id": "user1", "name": "Alice", "type": "user"},
            "object": {
                "authentication_type": "NFC",
                "result": "Access Granted",
            },
        },
    }
).encode()


@pytest.fixture
def receiver():
    return WebhookReceiver(SECRET, port=0)


@pytest.fixture
async def cli(aiohttp_client, receiver):
    return await aiohttp_client(receiver._app)


class TestWebhookReceiverConfig:
    def test_defaults(self):
        r = WebhookReceiver("secret")
        assert r._host == "0.0.0.0"
        assert r._port == 8080
        assert r._path == "/webhook"
        assert r._max_age_seconds == 300

    def test_custom(self):
        r = WebhookReceiver(
            "secret",
            host="127.0.0.1",
            port=9090,
            path="/events",
            max_age_seconds=600,
        )
        assert r._host == "127.0.0.1"
        assert r._port == 9090
        assert r._path == "/events"
        assert r._max_age_seconds == 600


class TestWebhookHandling:
    async def test_valid_webhook_dispatches_event(
        self, cli: TestClient, receiver: WebhookReceiver
    ):
        handler = EventHandler()
        received: list = []

        @handler.on(DoorUnlockEvent)
        async def callback(event):
            received.append(event)

        receiver.set_handler(handler)

        sig = _make_signature(SECRET, DOOR_UNLOCK_PAYLOAD)
        resp = await cli.post(
            "/webhook",
            data=DOOR_UNLOCK_PAYLOAD,
            headers={"Signature": sig},
        )
        assert resp.status == 200
        await asyncio.sleep(0.05)
        assert len(received) == 1
        assert isinstance(received[0], DoorUnlockEvent)
        assert received[0].data.actor.name == "Alice"
        assert received[0].data.object.authentication_type == "NFC"

    async def test_missing_signature_returns_401(
        self, cli: TestClient, receiver: WebhookReceiver
    ):
        receiver.set_handler(EventHandler())
        resp = await cli.post("/webhook", data=DOOR_UNLOCK_PAYLOAD)
        assert resp.status == 401

    async def test_invalid_signature_returns_401(
        self, cli: TestClient, receiver: WebhookReceiver
    ):
        receiver.set_handler(EventHandler())
        resp = await cli.post(
            "/webhook",
            data=DOOR_UNLOCK_PAYLOAD,
            headers={"Signature": "t=123,v1=badmac"},
        )
        assert resp.status == 401

    async def test_malformed_json_returns_400(
        self, cli: TestClient, receiver: WebhookReceiver
    ):
        body = b"not json"
        sig = _make_signature(SECRET, body)
        receiver.set_handler(EventHandler())
        resp = await cli.post("/webhook", data=body, headers={"Signature": sig})
        assert resp.status == 400

    async def test_unknown_event_returns_200_as_raw(
        self, cli: TestClient, receiver: WebhookReceiver
    ):
        handler = EventHandler()
        received: list = []

        @handler.on("")
        async def catch_raw(event):
            received.append(event)

        receiver.set_handler(handler)

        body = json.dumps(
            {"event": "access.future.thing", "data": {"key": "val"}}
        ).encode()
        sig = _make_signature(SECRET, body)
        resp = await cli.post("/webhook", data=body, headers={"Signature": sig})
        assert resp.status == 200

    async def test_get_request_returns_405(
        self, cli: TestClient, receiver: WebhookReceiver
    ):
        resp = await cli.get("/webhook")
        assert resp.status == 405

    async def test_no_handler_still_returns_200(
        self, cli: TestClient, receiver: WebhookReceiver
    ):
        sig = _make_signature(SECRET, DOOR_UNLOCK_PAYLOAD)
        resp = await cli.post(
            "/webhook",
            data=DOOR_UNLOCK_PAYLOAD,
            headers={"Signature": sig},
        )
        assert resp.status == 200

    async def test_null_data_event_accepted(
        self, cli: TestClient, receiver: WebhookReceiver
    ):
        handler = EventHandler()
        received: list = []

        @handler.on("access.unknown.event")
        async def callback(event):
            received.append(event)

        receiver.set_handler(handler)

        body = json.dumps({"event": "access.unknown.event", "data": None}).encode()
        sig = _make_signature(SECRET, body)
        resp = await cli.post("/webhook", data=body, headers={"Signature": sig})
        assert resp.status == 200
        await asyncio.sleep(0.05)
        assert len(received) == 1
        assert isinstance(received[0], RawEvent)
        assert received[0].data is None

    async def test_expired_signature_returns_401(
        self, cli: TestClient, receiver: WebhookReceiver
    ):
        receiver.set_handler(EventHandler())
        old_ts = int(time.time()) - 600
        sig = _make_signature(SECRET, DOOR_UNLOCK_PAYLOAD, timestamp=old_ts)
        resp = await cli.post(
            "/webhook",
            data=DOOR_UNLOCK_PAYLOAD,
            headers={"Signature": sig},
        )
        assert resp.status == 401
