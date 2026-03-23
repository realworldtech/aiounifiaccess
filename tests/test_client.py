"""Tests for UniFiAccessClient."""

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
from aiounifiaccess.client import UniFiAccessClient
from aiounifiaccess.events.handler import EventHandler
from aiounifiaccess.events.listener import WebSocketListener
from aiounifiaccess.events.models import DoorUnlockEvent


class TestClientConstruction:
    def test_creates_with_host_and_token(self):
        client = UniFiAccessClient(host="192.168.1.1", api_token="tok")
        assert client._session._host == "192.168.1.1"

    def test_users_manager(self):
        client = UniFiAccessClient(host="x", api_token="t")
        assert isinstance(client.users, UserManager)

    def test_doors_manager(self):
        client = UniFiAccessClient(host="x", api_token="t")
        assert isinstance(client.doors, DoorManager)

    def test_all_managers_wired(self):
        client = UniFiAccessClient(host="x", api_token="t")
        assert isinstance(client.visitors, VisitorManager)
        assert isinstance(client.access_policies, AccessPolicyManager)
        assert isinstance(client.credentials, CredentialManager)
        assert isinstance(client.devices, DeviceManager)
        assert isinstance(client.system_logs, SystemLogManager)
        assert isinstance(client.identity, IdentityManager)
        assert isinstance(client.webhooks, WebhookManager)
        assert isinstance(client.server, ServerManager)

    def test_event_handler_created(self):
        client = UniFiAccessClient(host="x", api_token="t")
        assert isinstance(client._event_handler, EventHandler)

    def test_listener_created(self):
        client = UniFiAccessClient(host="x", api_token="t")
        assert isinstance(client._listener, WebSocketListener)


class TestClientEvents:
    def test_on_registers_by_class(self):
        client = UniFiAccessClient(host="x", api_token="t")

        @client.on(DoorUnlockEvent)
        async def handler(event):
            pass

        assert "access.door.unlock" in client._event_handler._handlers

    def test_on_registers_by_string(self):
        client = UniFiAccessClient(host="x", api_token="t")

        @client.on("access.door.unlock")
        async def handler(event):
            pass

        assert "access.door.unlock" in client._event_handler._handlers


class TestClientLifecycle:
    async def test_context_manager(self):
        async with UniFiAccessClient(host="x", api_token="t") as client:
            assert client._session._session is not None
        assert client._session._session is None

    async def test_manual_connect_close(self):
        client = UniFiAccessClient(host="x", api_token="t")
        await client.connect()
        assert client._session._session is not None
        await client.close()
        assert client._session._session is None

    async def test_close_without_connect(self):
        client = UniFiAccessClient(host="x", api_token="t")
        await client.close()  # should not raise
