"""Common API response models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class BaseAPIModel(BaseModel):
    """Base for all API models with shared config."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )


class Pagination(BaseAPIModel):
    """Pagination metadata from list endpoints."""

    page_num: int
    page_size: int
    total: int


class APIResponse(BaseAPIModel):
    """Standard API response envelope."""

    code: str
    msg: str
    data: dict | list | None = None

    @property
    def is_success(self) -> bool:
        return self.code == "SUCCESS"


class PaginatedResponse(BaseAPIModel):
    """API response with pagination. Items are raw dicts at this level;
    BaseAPIManager._get_list() deserializes them into typed models."""

    code: str
    msg: str
    items: list[dict] = []
    pagination: Pagination

    @classmethod
    def from_raw(cls, raw: dict) -> PaginatedResponse:
        """Parse from raw API JSON, mapping 'data' to 'items'."""
        return cls(
            code=raw["code"],
            msg=raw["msg"],
            items=raw.get("data", []),
            pagination=Pagination.model_validate(raw["pagination"]),
        )
