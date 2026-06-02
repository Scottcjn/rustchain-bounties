"""
Tests for OTC bridge payout idempotency behavior.

Verifies:
- Stable idempotency key generation
- Retry handling with key stability
- HTTP transport refusal for admin credentials
- TLS verification refusal for non-local hosts
- Loopback and explicit opt-out scenarios
"""

import json
import logging
import re
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union
from unittest.mock import MagicMock, patch

import pytest
import requests
from flask import Flask
from flask.testing import FlaskClient
from requests.exceptions import ConnectionError, Timeout, RequestException

# Import the module under test
from otc_bridge import (
    _admin_transport_block_reason,
    _generate_payout_idempotency_key,
    app,
    process_payout,
    PayoutError,
    ConfigurationError,
    TransportError,
)

# Configure logging for tests
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@pytest.fixture
def client() -> FlaskClient:
    """Create a test client for the Flask application.

    Returns:
        FlaskClient: Configured test client with testing mode enabled.

    Raises:
        RuntimeError: If test client creation fails.
    """
    try:
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client
    except Exception as e:
        logger.error(f"Failed to create test client: {e}")
        raise RuntimeError(f"Test client creation failed: {e}") from e


class TestIdempotencyKeyGeneration:
    """Tests for stable idempotency key generation."""

    def test_stable_key_generation(self) -> None:
        """Verify that the same order_id always produces the same key.

        This test ensures idempotency by checking that identical inputs
        produce identical outputs, which is critical for retry safety.

        Raises:
            AssertionError: If keys for the same order_id are not identical.
        """
        try:
            order_id: str = "order_12345"
            key1: str = _generate_payout_idempotency_key(order_id)
            key2: str = _generate_payout_idempotency_key(order_id)
            assert key1 == key2, (
                f"Keys for same order_id must be identical, "
                f"got '{key1}' and '{key2}'"
            )
            logger.debug(f"Stable key generation verified for order_id={order_id}")
        except Exception as e:
            logger.error(f"Stable key generation test failed: {e}")
            raise

    def test_different_orders_different_keys(self) -> None:
        """Verify that different order_ids produce different keys.

        This ensures that each unique order gets a unique idempotency key,
        preventing accidental idempotency collisions.

        Raises:
            AssertionError: If keys for different order_ids are identical.
        """
        try:
            key1: str = _generate_payout_idempotency_key("order_abc")
            key2: str = _generate_payout_idempotency_key("order_xyz")
            assert key1 != key2, (
                f"Keys for different order_ids must differ, "
                f"got '{key1}' and '{key2}'"
            )
            logger.debug("Different order IDs produce different keys")
        except Exception as e:
            logger.error(f"Different keys test failed: {e}")
            raise

    def test_key_format(self) -> None:
        """Verify the key matches the node's validation pattern [A-Za-z0-9._:-]{1,128}.

        This ensures compatibility with the node's idempotency key validation.

        Raises:
            AssertionError: If key does not match the required pattern.
        """
        try:
            pattern: re.Pattern = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
            order_id: str = "test_order_42"
            key: str = _generate_payout_idempotency_key(order_id)
            assert pattern.match(key), (
                f"Key '{key}' does not match required pattern"
            )
            logger.debug(f"Key format validated for key={key}")
        except Exception as e:
            logger.error(f"Key format test failed: {e}")
            raise

    def test_key_contains_order_id(self) -> None:
        """Verify the key contains the order_id for traceability.

        This ensures that the idempotency key is human-readable and
        traceable back to the original order.

        Raises:
            AssertionError: If key does not contain the order_id.
        """
        try:
            order_id: str = "order_789"
            key: str = _generate_payout_idempotency_key(order_id)
            assert order_id in key, (
                f"Key should contain the order_id for traceability, "
                f"got '{key}'"
            )
            logger.debug(f"Order ID containment verified for key={key}")
        except Exception as e:
            logger.error(f"Order ID containment test failed: {e}")
            raise

    def test_key_length_within_limit(self) -> None:
        """Verify the key length does not exceed 128 characters.

        This ensures compliance with the node's maximum key length constraint.

        Raises:
            AssertionError: If key length exceeds 128 characters.
        """
        try:
            order_id: str = "order_" + "a" * 200  # Very long order ID
            key: str = _generate_payout_idempotency_key(order_id)
            assert len(key) <= 128, (
                f"Key length {len(key)} exceeds 128 characters"
            )
            logger.debug(f"Key length within limit: {len(key)} chars")
        except Exception as e:
            logger.error(f"Key length test failed: {e}")
            raise

    def test_key_with_special_characters(self) -> None:
        """Verify keys with special characters in order_id are handled correctly.

        This ensures that special characters are sanitized or handled
        appropriately to maintain key validity.

        Raises:
            AssertionError: If key does not match the required pattern after sanitization.
        """
        try:
            order_id: str = "order_@#$%^&*()"
            key: str = _generate_payout_idempotency_key(order_id)
            pattern: re.Pattern = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
            assert pattern.match(key), (
                f"Key '{key}' does not match required pattern after sanitization"
            )
            logger.debug(f"Special characters handled correctly for key={key}")
        except Exception as e:
            logger.error(f"Special characters test failed: {e}")
            raise


class TestRetryKeyStability:
    """Tests for retry handling with key stability."""

    @patch("otc_bridge.requests.post")
    def test_retry_uses_same_key(
        self, mock_post: MagicMock, client: FlaskClient
    ) -> None:
        """Verify that retries use the same idempotency key.

        This ensures that retry attempts are idempotent and won't
        cause duplicate transactions.

        Args:
            mock_post: Mock for requests.post
            client: Flask test client

        Raises:
            AssertionError: If retry does not use the same idempotency key.
        """
        try:
            order_id: str = "order_retry_test"
            payout_data: Dict[str, Any] = {
                "order_id": order_id,
                "amount": "100.0",
                "currency": "RTC",
                "destination": "RTCtest123",
            }

            # First attempt fails with 500
            mock_post.return_value.status_code = 500
            mock_post.return_value.text = "Internal Server Error"

            response1 = client.post(
                "/api/v1/payout",
                data=json.dumps(payout_data),
                content_type="application/json",
            )
            assert response1.status_code == 500, (
                f"Expected 500, got {response1.status_code}"
            )

            # Second attempt should use the same key
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"tx_hash": "abc123"}

            response2 = client.post(
                "/api/v1/payout",
                data=json.dumps(payout_data),
                content_type="application/json",
            )
            assert response2.status_code == 200, (
                f"Expected 200, got {response2.status_code}"
            )

            # Verify both calls used the same idempotency key
            call_args_list = mock_post.call_args_list
            assert len(call_args_list) == 2, (
                f"Expected 2 calls, got {len(call_args_list)}"
            )

            key1: Optional[str] = (
                call_args_list[0][1].get("headers", {}).get("Idempotency-Key")
            )
            key2: Optional[str] = (
                call_args_list[1][1].get("headers", {}).get("Idempotency-Key")
            )
            assert key1 == key2, (
                f"Retry must use the same idempotency key, "
                f"got '{key1}' and '{key2}'"
            )
            logger.debug("Retry key stability verified")
        except AssertionError:
            raise
        except Exception as e:
            logger.error(f"Retry key stability test failed: {e}")
            raise

    @patch("otc_bridge.requests.post")
    def test_retry_with_different_amount_blocked(
        self, mock_post: MagicMock, client: FlaskClient
    ) -> None:
        """Verify that retrying with different amount is blocked (409).

        This ensures that idempotency key conflicts are properly detected
        and reported when request parameters change.

        Args:
            mock_post: Mock for requests.post
            client: Flask test client

        Raises:
            AssertionError: If different amount retry is not blocked.
        """
        try:
            order_id: str = "order_amount_mismatch"
            payout_data: Dict[str, Any] = {
                "order_id": order_id,
                "amount": "100.0",
                "currency": "RTC",
                "destination": "RTCtest123",
            }

            # First attempt succeeds
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"tx_hash": "abc123"}
            response1 = client.post(
                "/api/v1/payout",
                data=json.dumps(payout_data),
                content_type="application/json",
            )
            assert response1.status_code == 200, (
                f"Expected 200, got {response1.status_code}"
            )

            # Second attempt with different amount should get 409
            payout_data["amount"] = "200.0"
            mock_post.return_value.status_code = 409
            mock_post.return_value.text = "Conflict: idempotency key mismatch"

            response2 = client.post(
                "/api/v1/payout",
                data=json.dumps(payout_data),
                content_type="application/json",
            )
            assert response2.status_code == 409, (
                f"Expected 409, got {response2.status_code}"
            )
            logger.debug("Different amount retry correctly blocked with 409")
        except AssertionError:
            raise
        except Exception as e:
            logger.error(f"Amount mismatch test failed: {e}")
            raise

    @patch("otc_bridge.requests.post")
    def test_retry_with_same_data_succeeds(
        self, mock_post: MagicMock, client: FlaskClient
    ) -> None:
        """Verify that retrying with same data succeeds after temporary failure.

        This ensures that transient failures don't permanently prevent
        successful payout processing.

        Args:
            mock_post: Mock for requests.post
            client: Flask test client

        Raises:
            AssertionError: If retry with same data does not succeed.
        """
        try:
            order_id: str = "order_retry_success"
            payout_data: Dict[str, Any] = {
                "order_id": order_id,
                "amount": "75.0",
                "currency": "RTC",
                "destination": "RTCtest789",
            }

            # First attempt fails with network error
            mock_post.side_effect = ConnectionError("Connection refused")

            with pytest.raises(ConnectionError):
                client.post(
                    "/api/v1/payout",
                    data=json.dumps(payout_data),
                    content_type="application/json",
                )

            # Second attempt succeeds
            mock_post.side_effect = None
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "tx_hash": "tx_retry_success"
            }

            response = client.post(
                "/api/v1/payout",
                data=json.dumps(payout_data),
                content_type="application/json",
            )
            assert response.status_code == 200, (
                f"Expected 200, got {response.status_code}"
            )

            # Verify both calls used the same key
            call_args_list = mock_post.call_args_list
            assert len(call_args_list) == 2
            key1: Optional[str] = (
                call_args_list[0][1].get("headers", {}).get("Idempotency-Key")
            )
            key2: Optional[str] = (
                call_args_list[1][1].get("headers", {}).get("Idempotency-Key")
            )
            assert key1 == key2, (
                f"Retry must use the same idempotency key, "
                f"got '{key1}' and '{key2}'"
            )
            logger.debug("Retry with same data succeeded after temporary failure")
        except AssertionError:
            raise
        except Exception as e:
            logger.error(f"Retry success test failed: {e}")
            raise


class TestAdminTransportBlock:
    """Tests for admin transport blocking behavior."""

    def test_http_transport_refused(self) -> None:
        """Verify that HTTP transport is refused for admin credentials.

        This ensures that admin credentials are never sent over
        unencrypted HTTP connections.

        Raises:
            AssertionError: If HTTP transport is not refused.
        """
        try:
            result: Optional[str] = _admin_transport_block_reason(
                url="http://example.com/api",
                tls_verify=True
            )
            assert result is not None, (
                "HTTP transport should be refused for admin credentials"
            )
            assert "HTTP" in result or "http" in result, (
                f"Block reason should mention HTTP, got '{result}'"
            )
            logger.debug(f"HTTP transport correctly refused: {result}")
        except Exception as e:
            logger.error(f"HTTP transport test failed: {e}")
            raise

    def test_tls_verify_disabled_nonlocal_refused(self) -> None:
        """Verify that TLS verification disabled for non-local hosts is refused.

        This ensures that admin credentials are not sent to non-local
        hosts with TLS verification disabled.

        Raises:
            AssertionError: If non-local TLS-disabled transport is not refused.
        """
        try:
            result: Optional[str] = _admin_transport_block_reason(
                url="https://external-host.com/api",
                tls_verify=False
            )
            assert result is not None, (
                "Non-local TLS-disabled transport should be refused"
            )
            assert "TLS" in result or "tls" in result, (
                f"Block reason should mention TLS, got '{result}'"
            )
            logger.debug(f"Non-local TLS-disabled transport correctly refused: {result}")
        except Exception as e:
            logger.error(f"TLS verify test failed: {e}")
            raise

    def test_loopback_allowed(self) -> None:
        """Verify that loopback connections are allowed.

        This ensures that local development and testing scenarios
        are not blocked unnecessarily.

        Raises:
            AssertionError: If loopback connection is blocked.
        """
        try:
            result: Optional[str] = _admin_transport_block_reason(
                url="https://127.0.0.1/api",
                tls_verify=False
            )
            assert result is None, (
                f"Loopback connection should be allowed, got '{result}'"
            )
            logger.debug("Loopback connection correctly allowed")
        except Exception as e:
            logger.error(f"Loopback test failed: {e}")
            raise

    def test_explicit_opt_out_allowed(self) -> None:
        """Verify that explicit opt-out scenarios are handled correctly.

        This ensures that explicitly configured exceptions to the
        transport rules are respected.

        Raises:
            AssertionError: If explicit opt-out is not handled correctly.
        """
        try:
            result: Optional[str] = _admin_transport_block_reason(
                url="https://trusted-host.com/api",
                tls_verify=True,
                allowlist=["trusted-host.com"]
            )
            assert result is None, (
                f"Explicit opt-out should be allowed, got '{result}'"
            )
            logger.debug("Explicit opt-out correctly allowed")
        except Exception as e:
            logger.error(f"Explicit opt-out test failed: {e}")
            raise

    def test_invalid_url_handling(self) -> None:
        """Verify that invalid URLs are handled gracefully.

        This ensures that malformed URLs don't cause crashes.

        Raises:
            AssertionError: If invalid URL is not handled gracefully.
        """
        try:
            result: Optional[str] = _admin_transport_block_reason(
                url="not-a-valid-url",
                tls_verify=True
            )
            assert result is not None, (
                "Invalid URL should be blocked"
            )
            logger.debug(f"Invalid URL correctly handled: {result}")
        except Exception as e:
            logger.error(f"Invalid URL test failed: {e}")
            raise


class TestPayoutProcessing:
    """Tests for payout processing functionality."""

    @patch("otc_bridge.requests.post")
    def test_successful_payout(
        self, mock_post: MagicMock, client: FlaskClient
    ) -> None:
        """Verify successful payout processing.

        Args:
            mock_post: Mock for requests.post
            client: Flask test client

        Raises:
            AssertionError: If payout processing fails unexpectedly.
        """
        try:
            payout_data: Dict[str, Any] = {
                "order_id": "order_success_1",
                "