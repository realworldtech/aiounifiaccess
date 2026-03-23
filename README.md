# aiounifiaccess

Async Python client for the [UniFi Access API](https://www.ui.com/door-access).

- **Full REST API coverage** — all endpoints from API v4.0.10
- **Real-time events** — WebSocket listener with auto-reconnect and typed event models
- **Webhook support** — HMAC-SHA256 signature verification utility
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

## Event Listener

```python
import asyncio
import os
from aiounifiaccess import UniFiAccessClient, DoorPositionEvent, DoorUnlockEvent

async def main():
    async with UniFiAccessClient(
        host=os.environ["UNIFI_ACCESS_HOST"],
        api_token=os.environ["UNIFI_ACCESS_TOKEN"],
    ) as client:

        @client.on(DoorPositionEvent)
        async def handle_dps(event: DoorPositionEvent):
            status = event.data.object.status
            door = event.data.location.name
            print(f"{door} is now {status}")

        @client.on(DoorUnlockEvent)
        async def handle_unlock(event: DoorUnlockEvent):
            actor = event.data.actor.name
            door = event.data.location.name
            print(f"{actor} unlocked {door}")

        await client.listen()

asyncio.run(main())
```

## Webhook Verification

```python
from aiounifiaccess import verify_webhook_signature

is_valid = verify_webhook_signature(
    secret="your_webhook_secret",
    signature_header=request.headers["Signature"],
    body=await request.read(),
)
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
| Webhooks | `client.webhooks` | 4 |
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
