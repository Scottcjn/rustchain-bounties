"""
Tests for rustchain.errors — exception hierarchy.
"""

from __future__ import annotations

import pytest

from rustchain.errors import (
    RustChainAPIError,
    RustChainAuthError,
    RustChainConnectionError,
    RustChainError,
    RustChainTimeoutError,
    RustChainValidationError,
)


class TestRustChainError:
    def test_base_exception(self):
        err = RustChainError("something broke")
        assert str(err) == "something broke"
        assert err.message == "something broke"
        assert err.details is None

    def test_with_details(self):
        err = RustChainError("fail", details={"code": 42})
        assert err.details == {"code": 42}

    def test_repr(self):
        err = RustChainError("test")
        assert "RustChainError" in repr(err)


class TestConnectionError:
    def test_inherits_base(self):
        err = RustChainConnectionError("no route to host")
        assert isinstance(err, RustChainError)


class TestTimeoutError:
    def test_inherits_base(self):
        err = RustChainTimeoutError("timed out")
        assert isinstance(err, RustChainError)


class TestAPIError:
    def test_status_code(self):
        err = RustChainAPIError("not found", status_code=404, response_body='{"error":"nf"}')
        assert err.status_code == 404
        assert err.response_body == '{"error":"nf"}'
        assert isinstance(err, RustChainError)

    def test_repr(self):
        err = RustChainAPIError("bad", status_code=500)
        assert "500" in repr(err)


class TestAuthError:
    def test_defaults(self):
        err = RustChainAuthError()
        assert err.status_code == 401
        assert isinstance(err, RustChainAPIError)
        assert isinstance(err, RustChainError)

    def test_custom_status(self):
        err = RustChainAuthError("forbidden", status_code=403)
        assert err.status_code == 403


class TestValidationError:
    def test_field_message(self):
        err = RustChainValidationError("wallet_id", "must not be empty")
        assert "wallet_id" in str(err)
        assert "must not be empty" in str(err)
        assert err.field == "wallet_id"
        assert isinstance(err, RustChainError)
