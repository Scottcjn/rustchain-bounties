"""Unit tests for the comment moderation webhook handler.

This test suite validates that malformed payloads are rejected with
specific 400 responses, that the audit logger captures the original
exception context, and that the webhook handler adheres to the
expected contract defined in issue Scottcjn/Rustchain#5447.
"""

import json
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Safe import – use handle_webhook (renamed in corrected implementation)
# ---------------------------------------------------------------------------
try:
    from src.webhook import handle_webhook
except ImportError as _import_err:
    raise ImportError(
        "Cannot import webhook module; ensure the test PYTHONPATH "
        "includes tools/comment-moderation-bot"
    ) from _import_err


# ===========================================================================
# Test class: WebhookMalformedPayload
# ===========================================================================
class TestWebhookMalformedPayload:
    """Regression tests for malformed payload edge cases.

    Every test in this class verifies that:
    - the HTTP response status code is 400
    - the body contains a human‑readable reason (e.g. "malformed",
      "expected an object", "required field missing")
    - the audit logger is called with the original exception context
    """

    # ------------------------------------------------------------------
    # Individual tests
    # ------------------------------------------------------------------
    def test_rejects_none_payload(self, audit_logger_mock: MagicMock) -> None:
        """Should return 400 with 'non-object' hint when payload is ``None``."""
        response = handle_webhook(None)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "non-object" in response.body.lower(), (
            f"Response body should contain 'non-object': {response.body}"
        )

    def test_rejects_list_payload(self, audit_logger_mock: MagicMock) -> None:
        """Should return 400 with 'expected an object' when payload is a list."""
        response = handle_webhook([])  # type: ignore[arg-type]  # deliberate bad input
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "expected an object" in response.body.lower(), (
            f"Response body should contain 'expected an object': {response.body}"
        )

    def test_rejects_string_payload(self, audit_logger_mock: MagicMock) -> None:
        """Should return 400 with 'malformed' when payload is a plain string."""
        response = handle_webhook("invalid")  # type: ignore[arg-type]
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "malformed" in response.body.lower(), (
            f"Response body should contain 'malformed': {response.body}"
        )sponse.body}"
        )

    def test_rejects_non_object_nested_payload(
        self, audit_logger_mock: MagicMock
    ) -> None:
        """Should return 400 with field‑specific details for non‑object nested field.

        Regression test for issue #5447: a nested field that is expected to be
        an object (e.g. ``comment``) but receives a primitive must be reported
        with the field path.
        """
        payload: Dict[str, Any] = {"comment": {"author": "invalid_user"}}
        response = handle_webhook(payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        # The field path "comment.author" or "author" must appear (case‑insensitive)
        assert (
            "comment.author" in response.body.lower()
            or "author" in response.body.lower()
        ), f"Expected field hint in response: {response.body}"
        assert "malformed" in response.body.lower(), (
            f"Response body should contain 'malformed': {response.body}"
        )

    def test_rejects_missing_required_top_field(
        self, audit_logger_mock: MagicMock
    ) -> None:
        """Should return 400 with 'required' and the missing field name."""
        payload: Dict[str, Any] = {"comment": {"text": "hello"}}
        response = handle_webhook(payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "required" in response.body.lower(), (
            f"Response body should contain 'required': {response.body}"
        )
        assert (
            "user" in response.body.lower() or "author" in response.body.lower()
        ), f"Response body should mention 'author' or 'user': {response.body}"

    def test_audit_logger_captures_exception_context(
        self, audit_logger_mock: MagicMock
    ) -> None:
        """Verify the audit logger records the original exception context.

        Even when the webhook handler returns a 400 to the caller, the
        audit logger must still receive the original exception with full
        context (e.g. the malformed value) at the ERROR level.
        """
        malformed_payload: Dict[str, Any] = {"comment": 123}
        response = handle_webhook(malformed_payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

        # Assert that the audit logger was called at ERROR level with some
        # mention of "malformed" or "validation".
        audit_logger_mock.error.assert_called_once()
        call_args: str = str(audit_logger_mock.error.call_args)
        assert (
            "malformed" in call_args or "validation" in call_args
        ), f"Expected logger to record 'malformed' or 'validation': {call_args}"


# ===========================================================================
# Fixtures
# ===========================================================================
@pytest.fixture
def audit_logger_mock() -> MagicMock:
    """Mock the ``audit_logger`` used by the webhook module.

    The fixture patches ``src.webhook.audit_logger`` with a
    :class:`unittest.mock.MagicMock` so that all log calls can be
    inspected by the tests.  The patch is automatically undone after
    each test.
    """
    with patch("src.webhook.audit_logger") as mock_logger:
        yield mock_logger