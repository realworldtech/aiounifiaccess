"""Tests for common API response models."""

from aiounifiaccess.models.common import APIResponse, PaginatedResponse


class TestAPIResponse:
    def test_success_response(self):
        raw = {"code": "SUCCESS", "msg": "success", "data": {"id": "abc123"}}
        resp = APIResponse.model_validate(raw)
        assert resp.code == "SUCCESS"
        assert resp.msg == "success"
        assert resp.data == {"id": "abc123"}

    def test_success_null_data(self):
        raw = {"code": "SUCCESS", "msg": "success", "data": None}
        resp = APIResponse.model_validate(raw)
        assert resp.data is None

    def test_error_response(self):
        raw = {"code": "CODE_PARAMS_INVALID", "msg": "Invalid parameters."}
        resp = APIResponse.model_validate(raw)
        assert resp.code == "CODE_PARAMS_INVALID"
        assert resp.data is None

    def test_is_success(self):
        success = APIResponse(code="SUCCESS", msg="success", data={})
        error = APIResponse(code="CODE_PARAMS_INVALID", msg="Invalid")
        assert success.is_success is True
        assert error.is_success is False


class TestPaginatedResponse:
    def test_pagination_fields(self):
        raw = {
            "code": "SUCCESS",
            "msg": "success",
            "data": [{"id": "1"}, {"id": "2"}],
            "pagination": {"page_num": 1, "page_size": 25, "total": 97},
        }
        resp = PaginatedResponse.from_raw(raw)
        assert resp.pagination.page_num == 1
        assert resp.pagination.page_size == 25
        assert resp.pagination.total == 97
        assert len(resp.items) == 2
        assert resp.items[0] == {"id": "1"}
