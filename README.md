# aiounifiaccess

Async Python client for the [UniFi Access API](https://www.ui.com/door-access).

- **Full REST API coverage** — all endpoints from API v4.0.10
- **Real-time events** — WebSocket listener with auto-reconnect and typed event models
- **Webhook receiver** — built-in HTTP server for webhook events with signature verification
- **Idempotent webhook registration** — `ensure_endpoint()` and `setup_webhook()` handle subscription management
- **Pydantic v2 models** — fully typed request/response objects
- **Async-native** — built on aiohttp for composability with other async libraries

## Installation

```bash
pip install aiounifiaccess
```

## Quick Start

```python
import asyncio
import os
from aiounifiaccess import UniFiAccessClient

async def main():
    async with UniFiAccessClient(
        host=os.environ["UNIFI_ACCESS_HOST"],
        api_token=os.environ["UNIFI_ACCESS_TOKEN"],
    ) as client:
        # List all users
        users, pagination = await client.users.list()
        for user in users:
            print(f"{user.first_name} {user.last_name} ({user.status})")

        # Get a specific door
        door = await client.doors.get("door-id-here")
        print(f"{door.name}: {door.door_lock_relay_status}")

        # Remote unlock
        await client.doors.unlock("door-id-here", actor_name="API Script")

asyncio.run(main())
```

## Real-Time Events

UniFi Access delivers events through two channels:

| Channel | Delivery | Event types |
|---------|----------|-------------|
| **WebSocket** | Persistent connection | Doorbell rings, remote unlocks, device/location state updates |
| **Webhook** | Controller POSTs to your endpoint | Door unlocks (NFC/PIN/fingerprint), DPS status, schedules, visitors |

Notably, credential-based door unlock events (`access.door.unlock`) are **webhook-only** — they are not delivered over the WebSocket. To receive all event types, you need both channels.

The WebSocket also delivers **undocumented status events** not listed in the official API reference. These are typed and parsed by the library:

| Event | Model | Description |
|-------|-------|-------------|
| `access.data.device.update` | `DeviceUpdateEvent` | Full device state with DPS, lock relays, power, wiring |
| `access.data.v2.device.update` | `DeviceUpdateV2Event` | Lightweight device change notification with changed-field metadata |
| `access.data.v2.location.update` | `LocationUpdateV2Event` | Building/floor/door location state changes (most frequent) |
| `access.data.location.update` | `LocationUpdateEvent` | Full location state |
| `access.data.setting.update` | `SettingUpdateEvent` | Controller settings changes |

The `DeviceUpdateEvent` is particularly useful — its `configs` list contains key/value pairs for DPS states, lock relay states, and power readings. For example, detecting "door left open":

```python
from aiounifiaccess import DeviceUpdateEvent

@client.on(DeviceUpdateEvent)
async def handle_device_update(event: DeviceUpdateEvent):
    for cfg in event.data.configs:
        if cfg.tag == "hub_action" and cfg.key.endswith("_dps"):
            port = cfg.key.replace("input_", "").replace("_dps", "")
            state = "open" if cfg.value == "on" else "closed"
            print(f"Port {port} DPS: {state}")
```

### WebSocket Only

If you only need doorbell and remote unlock events:

```python
import asyncio
import os
from aiounifiaccess import UniFiAccessClient, RemoteViewEvent

async def main():
    async with UniFiAccessClient(
        host=os.environ["UNIFI_ACCESS_HOST"],
        api_token=os.environ["UNIFI_ACCESS_TOKEN"],
    ) as client:

        @client.on(RemoteViewEvent)
        async def handle_doorbell(event: RemoteViewEvent):
            print(f"Doorbell ring at {event.data.door_name}")

        await client.listen()

asyncio.run(main())
```

### WebSocket + Webhook (Recommended)

To receive all events including credential-based door unlocks, use `setup_webhook()`. This registers a webhook subscription on the UniFi controller, starts a local HTTP receiver, and runs both channels concurrently:

```python
import asyncio
import os
from aiounifiaccess import (
    UniFiAccessClient,
    DoorUnlockEvent,
    DoorPositionEvent,
    RemoteViewEvent,
)

async def main():
    async with UniFiAccessClient(
        host=os.environ["UNIFI_ACCESS_HOST"],
        api_token=os.environ["UNIFI_ACCESS_TOKEN"],
    ) as client:

        # Register webhook on the controller and start local receiver.
        # The controller will POST events to this URL.
        await client.setup_webhook("https://myserver:8080/webhook")

        @client.on(DoorUnlockEvent)
        async def handle_unlock(event: DoorUnlockEvent):
            actor = event.data.actor.name
            door = event.data.location.name
            method = event.data.object.authentication_type
            print(f"{actor} unlocked {door} via {method}")

        @client.on(DoorPositionEvent)
        async def handle_dps(event: DoorPositionEvent):
            print(f"{event.data.location.name}: {event.data.object.status}")

        @client.on(RemoteViewEvent)
        async def handle_doorbell(event: RemoteViewEvent):
            print(f"Doorbell ring at {event.data.door_name}")

        # Runs both WebSocket and webhook receiver until stopped
        await client.listen()

asyncio.run(main())
```

`setup_webhook()` is **idempotent** — if a webhook subscription already exists for the same URL and event set, it reuses it. If the URL matches but the events differ, it updates the existing subscription. By default it subscribes to all known webhook event types.

### Subscribing to Specific Events

Use `WebhookEventType` to subscribe to only the events you need:

```python
from aiounifiaccess import WebhookEventType

await client.setup_webhook(
    "https://myserver:8080/webhook",
    events=[
        WebhookEventType.DOOR_UNLOCK,
        WebhookEventType.DEVICE_DPS_STATUS,
    ],
)
```

Available event types:

| Enum value | Event string | Description |
|------------|-------------|-------------|
| `DOOR_UNLOCK` | `access.door.unlock` | All door unlock events (NFC, PIN, fingerprint, remote) |
| `DEVICE_DPS_STATUS` | `access.device.dps_status` | Door position sensor changes |
| `DOORBELL_INCOMING` | `access.doorbell.incoming` | Doorbell ring |
| `DOORBELL_COMPLETED` | `access.doorbell.completed` | Doorbell accepted/declined/cancelled |
| `DOORBELL_INCOMING_REN` | `access.doorbell.incoming.REN` | Request-to-Enter button |
| `DEVICE_EMERGENCY_STATUS` | `access.device.emergency_status` | Emergency mode changes |
| `UNLOCK_SCHEDULE_ACTIVATE` | `access.unlock_schedule.activate` | Unlock schedule activated |
| `UNLOCK_SCHEDULE_DEACTIVATE` | `access.unlock_schedule.deactivate` | Unlock schedule deactivated |
| `TEMPORARY_UNLOCK_START` | `access.temporary_unlock.start` | Temporary unlock started |
| `TEMPORARY_UNLOCK_END` | `access.temporary_unlock.end` | Temporary unlock ended |
| `VISITOR_STATUS_CHANGED` | `access.visitor.status.changed` | Visitor status changed |

### Manual Webhook Configuration

If you prefer to manage webhook registration separately (or already have one registered), pass the secret directly:

```python
async with UniFiAccessClient(
    host=os.environ["UNIFI_ACCESS_HOST"],
    api_token=os.environ["UNIFI_ACCESS_TOKEN"],
    webhook_secret="your_webhook_secret",
    webhook_port=8080,
) as client:
    # ...handlers...
    await client.listen()
```

Or use the webhook manager API directly:

```python
# Idempotent registration (create or reuse)
endpoint = await client.webhooks.ensure_endpoint(
    "https://myserver:8080/webhook",
    "my-app",
)
print(f"Secret: {endpoint.secret}")

# Or manual CRUD
endpoints = await client.webhooks.list_endpoints()
await client.webhooks.delete_endpoint(endpoint.id)
```

### Standalone Webhook Receiver

The `WebhookReceiver` can be used independently of the full client:

```python
import asyncio
from aiounifiaccess import WebhookReceiver, DoorUnlockEvent
from aiounifiaccess.events.handler import EventHandler

handler = EventHandler()

@handler.on(DoorUnlockEvent)
async def handle(event: DoorUnlockEvent):
    print(f"{event.data.actor.name} unlocked {event.data.location.name}")

async def main():
    receiver = WebhookReceiver("your_webhook_secret", port=8080)
    await receiver.listen(handler)

asyncio.run(main())
```

### Webhook Signature Verification

For custom webhook handling outside the built-in receiver:

```python
from aiounifiaccess import verify_webhook_signature

is_valid = verify_webhook_signature(
    secret="your_webhook_secret",
    signature_header=request.headers["Signature"],
    body=await request.read(),
)
```

## Debug Logging

To see all raw incoming messages on either channel:

```python
import logging

# Both channels
logging.getLogger("aiounifiaccess.events").setLevel(logging.DEBUG)

# Or individually
logging.getLogger("aiounifiaccess.events.listener").setLevel(logging.DEBUG)   # WebSocket
logging.getLogger("aiounifiaccess.events.receiver").setLevel(logging.DEBUG)   # Webhook
```

## API Managers

| Manager | Attribute | Endpoints |
|---------|-----------|-----------|
| Users | `client.users` | 29 |
| Visitors | `client.visitors` | 13 |
| Access Policies | `client.access_policies` | 15 |
| Credentials | `client.credentials` | 17 |
| Doors | `client.doors` | 13 |
| Devices | `client.devices` | 4 |
| System Logs | `client.system_logs` | 4 |
| Identity | `client.identity` | 6 |
| Webhooks | `client.webhooks` | 5 |
| Server | `client.server` | 2 |

## Compatibility

| Library Version | API Reference Version |
|----------------|----------------------|
| 0.1.x | 4.0.10 |

## Requirements

- Python 3.11+
- aiohttp >= 3.9
- pydantic >= 2.0

## License

MIT
