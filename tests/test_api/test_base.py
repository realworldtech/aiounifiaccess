"""Tests for BaseAPIManager typed request methods."""

from unittest.mock import AsyncMock

import pytest
from pydantic import BaseModel

from aiounifiaccess.api.base import BaseAPIManager


class SampleModel(BaseModel):
    id: str
    name: str = ""


@pytest.fixture
def mock_session():
    session = AsyncMock()
    return session


@pytest.fixture
def manager(mock_session):
    return BaseAPIManager(mock_session)


class TestGet:
    async def test_get_returns_model(self, manager, mock_session):
        mock_session._request.return_value = {"id": "abc", "name": "Test"}
        result = await manager._get("/api/v1/test", SampleModel)
        assert isinstance(result, SampleModel)
        assert result.id == "abc"
        assert result.name == "Test"
        mock_session._request.assert_called_once_with(
            "GET", "/api/v1/test", params=None
        )

    async def test_get_with_params(self, manager, mock_session):
        mock_session._request.return_value = {"id": "x"}
        await manager._get("/api/v1/test", SampleModel, page_num=1)
        mock_session._request.assert_called_once_with(
            "GET", "/api/v1/test", params={"page_num": 1}
        )


class TestGetList:
    async def test_get_list_returns_typed_items(self, manager, mock_session):
        mock_session._request_raw.return_value = {
            "code": "SUCCESS",
            "msg": "success",
            "data": [{"id": "1", "name": "A"}, {"id": "2", "name": "B"}],
            "pagination": {"page_num": 1, "page_size": 25, "total": 2},
        }
        items, resp = await manager._get_list("/api/v1/test", SampleModel)
        assert len(items) == 2
        assert isinstance(items[0], SampleModel)
        assert items[0].id == "1"
        assert resp.pagination.total == 2


class TestGetListAll:
    async def test_auto_pagination(self, manager, mock_session):
        # Page 1: 2 items, total 3
        # Page 2: 1 item
        mock_session._request_raw.side_effect = [
            {
                "code": "SUCCESS",
                "msg": "success",
                "data": [{"id": "1"}, {"id": "2"}],
                "pagination": {"page_num": 1, "page_size": 2, "total": 3},
            },
            {
                "code": "SUCCESS",
                "msg": "success",
                "data": [{"id": "3"}],
                "pagination": {"page_num": 2, "page_size": 2, "total": 3},
            },
        ]
        items = []
        async for item in manager._get_list_all(
            "/api/v1/test", SampleModel, page_size=2
        ):
            items.append(item)
        assert len(items) == 3
        assert items[2].id == "3"
        assert mock_session._request_raw.call_count == 2

    async def test_single_page(self, manager, mock_session):
        mock_session._request_raw.return_value = {
            "code": "SUCCESS",
            "msg": "success",
            "data": [{"id": "1"}],
            "pagination": {"page_num": 1, "page_size": 25, "total": 1},
        }
        items = []
        async for item in manager._get_list_all("/api/v1/test", SampleModel):
            items.append(item)
        assert len(items) == 1
        assert mock_session._request_raw.call_count == 1


class TestPost:
    async def test_post_with_model(self, manager, mock_session):
        mock_session._request.return_value = {"id": "new", "name": "Created"}
        result = await manager._post(
            "/api/v1/test", json={"name": "Created"}, model_cls=SampleModel
        )
        assert isinstance(result, SampleModel)
        assert result.id == "new"

    async def test_post_without_model(self, manager, mock_session):
        mock_session._request.return_value = None
        result = await manager._post("/api/v1/test", json={"action": "do"})
        assert result is None


class TestPut:
    async def test_put_sends_body(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager._put("/api/v1/test/123", json={"name": "Updated"})
        mock_session._request.assert_called_once_with(
            "PUT", "/api/v1/test/123", json={"name": "Updated"}
        )


class TestDelete:
    async def test_delete(self, manager, mock_session):
        mock_session._request.return_value = None
        await manager._delete("/api/v1/test/123")
        mock_session._request.assert_called_once_with("DELETE", "/api/v1/test/123")
