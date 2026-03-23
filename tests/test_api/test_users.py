"""Tests for UserManager."""

from unittest.mock import AsyncMock

import pytest

from aiounifiaccess.api.users import UserManager
from aiounifiaccess.models.user import User, UserGroup


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def manager(mock_session):
    return UserManager(mock_session)


class TestUserCRUD:
    async def test_create(self, manager, mock_session):
        mock_session._request.return_value = {
            "id": "abc",
            "first_name": "Jane",
            "last_name": "Smith",
        }
        user = await manager.create("Jane", "Smith")
        assert isinstance(user, User)
        assert user.first_name == "Jane"
        mock_session._request.assert_called_once_with(
            "POST",
            "/api/v1/developer/users",
            json={"first_name": "Jane", "last_name": "Smith"},
        )

    async def test_get(self, manager, mock_session):
        mock_session._request.return_value = {
            "id": "abc",
            "first_name": "Jane",
            "last_name": "Smith",
        }
        user = await manager.get("abc")
        assert user.id == "abc"
        mock_session._request.assert_called_once_with(
            "GET", "/api/v1/developer/users/abc", params=None
        )

    async def test_get_with_expand(self, manager, mock_session):
        mock_session._request.return_value = {"id": "abc"}
        await manager.get("abc", expand_access_policy=True)
        mock_session._request.assert_called_once_with(
            "GET",
            "/api/v1/developer/users/abc",
            params={"expand[]": "access_policy"},
        )

    async def test_update(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager.update("abc", first_name="Updated")
        mock_session._request.assert_called_once_with(
            "PUT",
            "/api/v1/developer/users/abc",
            json={"first_name": "Updated"},
        )

    async def test_delete(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager.delete("abc")
        mock_session._request.assert_called_once_with(
            "DELETE", "/api/v1/developer/users/abc"
        )

    async def test_list(self, manager, mock_session):
        mock_session._request_raw.return_value = {
            "code": "SUCCESS",
            "msg": "success",
            "data": [{"id": "1", "first_name": "A", "last_name": "B"}],
            "pagination": {"page_num": 1, "page_size": 25, "total": 1},
        }
        users, resp = await manager.list()
        assert len(users) == 1
        assert isinstance(users[0], User)

    async def test_list_all(self, manager, mock_session):
        mock_session._request_raw.return_value = {
            "code": "SUCCESS",
            "msg": "success",
            "data": [{"id": "1"}],
            "pagination": {"page_num": 1, "page_size": 25, "total": 1},
        }
        users = []
        async for user in manager.list_all():
            users.append(user)
        assert len(users) == 1


class TestUserCredentials:
    async def test_assign_nfc_card(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager.assign_nfc_card("uid", "tok123", force_add=True)
        mock_session._request.assert_called_once_with(
            "PUT",
            "/api/v1/developer/users/uid/nfc_cards",
            json={"token": "tok123", "force_add": True},
        )

    async def test_unassign_nfc_card(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager.unassign_nfc_card("uid", "tok123")
        mock_session._request.assert_called_once_with(
            "PUT",
            "/api/v1/developer/users/uid/nfc_cards/delete",
            json={"token": "tok123"},
        )

    async def test_assign_pin_code(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager.assign_pin_code("uid", "1234")
        mock_session._request.assert_called_once_with(
            "PUT",
            "/api/v1/developer/users/uid/pin_code",
            json={"pin_code": "1234"},
        )

    async def test_assign_access_policy(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager.assign_access_policy("uid", ["p1", "p2"])
        mock_session._request.assert_called_once_with(
            "PUT",
            "/api/v1/developer/users/uid/access_policies",
            json={"access_policy_ids": ["p1", "p2"]},
        )


class TestUserGroups:
    async def test_create_group(self, manager, mock_session):
        mock_session._request.return_value = {"id": "g1", "name": "Eng"}
        group = await manager.create_group("Eng")
        assert isinstance(group, UserGroup)
        assert group.name == "Eng"

    async def test_assign_to_group(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager.assign_to_group("g1", ["u1", "u2"])
        mock_session._request.assert_called_once_with(
            "POST",
            "/api/v1/developer/users_groups/g1/users",
            json={"user_ids": ["u1", "u2"]},
        )

    async def test_list_groups(self, manager, mock_session):
        mock_session._request.return_value = [
            {"id": "g1", "name": "A"},
            {"id": "g2", "name": "B"},
        ]
        groups = await manager.list_groups()
        assert len(groups) == 2
        assert isinstance(groups[0], UserGroup)
