"""Base API manager with typed request methods."""

from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator, TypeVar

import aiohttp
from pydantic import BaseModel

from aiounifiaccess.models.common import PaginatedResponse

if TYPE_CHECKING:
    from aiounifiaccess.session import APISession

T = TypeVar("T", bound=BaseModel)


class BaseAPIManager:
    """Base class for all API domain managers."""

    def __init__(self, session: APISession) -> None:
        self._session = session

    async def _get(self, path: str, model_cls: type[T], **params) -> T:
        data = await self._session._request("GET", path, params=params or None)
        return model_cls.model_validate(data)

    async def _get_optional(self, path: str, model_cls: type[T], **params) -> T | None:
        data = await self._session._request("GET", path, params=params or None)
        if data is None:
            return None
        return model_cls.model_validate(data)

    async def _get_list(
        self, path: str, model_cls: type[T], **params
    ) -> tuple[list[T], PaginatedResponse]:
        """Fetch a paginated list. Returns (typed_items, pagination_info)."""
        raw = await self._session._request_raw("GET", path, params=params or None)
        resp = PaginatedResponse.from_raw(raw)
        items = [model_cls.model_validate(item) for item in resp.items]
        return items, resp

    async def _get_list_unpaginated(
        self, path: str, model_cls: type[T], **params
    ) -> list[T]:
        data = await self._session._request("GET", path, params=params or None)
        return [model_cls.model_validate(item) for item in data]

    async def _get_list_all(
        self, path: str, model_cls: type[T], page_size: int = 25, **params
    ) -> AsyncIterator[T]:
        """Auto-paginate through all results. Fetches lazily - next page
        requested only when current page exhausted. Safe to break out of."""
        page_num = 1
        while True:
            raw = await self._session._request_raw(
                "GET",
                path,
                params={
                    **(params or {}),
                    "page_num": page_num,
                    "page_size": page_size,
                },
            )
            resp = PaginatedResponse.from_raw(raw)
            items_on_page = len(resp.items)
            for item in resp.items:
                yield model_cls.model_validate(item)
            # Stop if we've reached the end by count or received a short page
            if (
                page_num * resp.pagination.page_size >= resp.pagination.total
                or items_on_page < page_size
            ):
                break
            page_num += 1

    async def _post(
        self,
        path: str,
        json: dict | list | None = None,
        model_cls: type[T] | None = None,
    ) -> T | None:
        data = await self._session._request("POST", path, json=json)
        if model_cls is not None and data is not None:
            return model_cls.model_validate(data)
        return None

    async def _put(
        self,
        path: str,
        json: dict | None = None,
        model_cls: type[T] | None = None,
    ) -> T | None:
        data = await self._session._request("PUT", path, json=json)
        if model_cls is not None and data is not None:
            return model_cls.model_validate(data)
        return None

    async def _delete(self, path: str) -> None:
        await self._session._request("DELETE", path)

    async def _post_file(
        self,
        path: str,
        data: aiohttp.FormData,
        model_cls: type[T] | None = None,
    ) -> T | None:
        result = await self._session._request_file("POST", path, data=data)
        if model_cls is not None and result is not None:
            return model_cls.model_validate(result)
        return None

    async def _get_bytes(
        self,
        path: str,
        *,
        json: dict | None = None,
        **params,
    ) -> bytes:
        return await self._session._request_bytes(
            "GET" if json is None else "POST",
            path,
            json=json,
            params=params or None,
        )
