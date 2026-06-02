"""
Tests for GPU render protocol escrow atomicity under concurrent access.

This module verifies that escrow status transitions (locked -> released|refunded)
are atomic and that concurrent operations cannot both succeed.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union
from unittest.mock import patch

import pytest
from pytest_mock import MockerFixture

from node.gpu_render_protocol import (
    release_escrow,
    refund_escrow,
    _authorize_escrow_action,
)

logger = logging.getLogger(__name__)


class EscrowAtomicityError(Exception):
    """Custom exception for escrow atomicity test failures."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the exception with message and optional details.

        Args:
            message: Human-readable error description
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.details = details or {}


class MockDatabaseConnection:
    """Mock database connection with rowcount tracking for testing."""

    def __init__(self) -> None:
        """Initialize mock database connection with default state."""
        self._cursor: Optional[MockDatabaseCursor] = None
        self._closed: bool = False
        self._autocommit: bool = False
        self._transactions: List[str] = []

    def cursor(self) -> "MockDatabaseCursor":
        """Get or create mock cursor instance.

        Returns:
            MockDatabaseCursor instance

        Raises:
            RuntimeError: If connection is closed
        """
        if self._closed:
            raise RuntimeError("Cannot create cursor on closed connection")
        if self._cursor is None:
            self._cursor = MockDatabaseCursor()
        return self._cursor

    def close(self) -> None:
        """Close the database connection."""
        self._closed = True
        if self._cursor:
            self._cursor.close()

    def commit(self) -> None:
        """Commit current transaction."""
        if self._closed:
            raise RuntimeError("Cannot commit on closed connection")
        self._transactions.append("COMMIT")

    def rollback(self) -> None:
        """Rollback current transaction."""
        if self._closed:
            raise RuntimeError("Cannot rollback on closed connection")
        self._transactions.append("ROLLBACK")

    @property
    def is_closed(self) -> bool:
        """Check if connection is closed.

        Returns:
            True if connection is closed, False otherwise
        """
        return self._closed

    def reset(self) -> None:
        """Reset mock state to initial values."""
        self._cursor = None
        self._closed = False
        self._autocommit = False
        self._transactions.clear()


class MockDatabaseCursor:
    """Mock database cursor with configurable behavior for testing."""

    def __init__(self) -> None:
        """Initialize mock cursor with default state."""
        self.rowcount: int = 1
        self._fetchone_result: Optional[Dict[str, Any]] = None
        self._fetchall_result: List[Dict[str, Any]] = []
        self._executed_queries: List[str] = []
        self._executed_params: List[Tuple[Any, ...]] = []
        self._closed: bool = False
        self._arraysize: int = 1

    def execute(
        self,
        query: str,
        params: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None
    ) -> None:
        """Record executed query and parameters.

        Args:
            query: SQL query string
            params: Query parameters (tuple or dict)

        Raises:
            RuntimeError: If cursor is closed
            ValueError: If query is empty
        """
        if self._closed:
            raise RuntimeError("Cannot execute on closed cursor")
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        self._executed_queries.append(query)
        self._executed_params.append(params or ())

    def executemany(
        self,
        query: str,
        seq_of_params: List[Union[Tuple[Any, ...], Dict[str, Any]]]
    ) -> None:
        """Record executed query with multiple parameter sets.

        Args:
            query: SQL query string
            seq_of_params: List of parameter sets

        Raises:
            RuntimeError: If cursor is closed
            ValueError: If query is empty or params list is empty
        """
        if self._closed:
            raise RuntimeError("Cannot execute on closed cursor")
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        if not seq_of_params:
            raise ValueError("Parameters list cannot be empty")

        for params in seq_of_params:
            self._executed_queries.append(query)
            self._executed_params.append(params)

    def fetchone(self) -> Optional[Dict[str, Any]]:
        """Return configured fetch result.

        Returns:
            Single row as dictionary or None
        """
        return self._fetchone_result

    def fetchall(self) -> List[Dict[str, Any]]:
        """Return configured fetch all result.

        Returns:
            List of rows as dictionaries
        """
        return self._fetchall_result

    def fetchmany(self, size: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return configured fetch many result.

        Args:
            size: Number of rows to fetch (defaults to arraysize)

        Returns:
            List of rows as dictionaries
        """
        fetch_size = size or self._arraysize
        return self._fetchall_result[:fetch_size]

    def set_fetchone_result(self, result: Optional[Dict[str, Any]]) -> None:
        """Set the result for fetchone calls.

        Args:
            result: Dictionary representing a single row or None
        """
        self._fetchone_result = result

    def set_fetchall_result(self, results: List[Dict[str, Any]]) -> None:
        """Set the result for fetchall calls.

        Args:
            results: List of dictionaries representing rows
        """
        self._fetchall_result = results

    def close(self) -> None:
        """Close the cursor."""
        self._closed = True

    @property
    def last_query(self) -> Optional[str]:
        """Get the last executed query.

        Returns:
            Last query string or None if no queries executed
        """
        return self._executed_queries[-1] if self._executed_queries else None

    @property
    def last_params(self) -> Optional[Union[Tuple[Any, ...], Dict[str, Any]]]:
        """Get the last executed parameters.

        Returns:
            Last parameters or None if no queries executed
        """
        return self._executed_params[-1] if self._executed_params else None

    @property
    def query_count(self) -> int:
        """Get total number of executed queries.

        Returns:
            Number of executed queries
        """
        return len(self._executed_queries)

    def reset(self) -> None:
        """Reset cursor state to initial values."""
        self.rowcount = 1
        self._fetchone_result = None
        self._fetchall_result = []
        self._executed_queries.clear()
        self._executed_params.clear()
        self._closed = False
        self._arraysize = 1


class TestEscrowAtomicity:
    """Test suite for escrow transition atomicity under concurrent access."""

    # Constants for validation
    VALID_JOB_ID_PATTERN: str = r"^[a-zA-Z0-9_-]+$"
    MAX_JOB_ID_LENGTH: int = 255
    DEFAULT_AMOUNT_RTC: int = 1000
    DEFAULT_WALLET: str = "test_wallet_address"
    VALID_STATUSES: List[str] = ["locked", "released", "refunded"]

    @pytest.fixture
    def mock_db(
        self,
        mocker: MockerFixture
    ) -> Tuple[MockDatabaseConnection, MockDatabaseCursor]:
        """Create a mock database connection with rowcount tracking.

        Args:
            mocker: Pytest mocker fixture for monkeypatching

        Returns:
            Tuple of (mock_connection, mock_cursor)

        Raises:
            RuntimeError: If mock creation fails
        """
        try:
            mock_conn = MockDatabaseConnection()
            mock_cursor = mock_conn.cursor()
            logger.debug("Created mock database connection and cursor")
            return mock_conn, mock_cursor
        except Exception as e:
            logger.error(f"Failed to create mock database: {e}")
            raise RuntimeError(f"Mock database creation failed: {e}") from e

    def _setup_escrow_data(
        self,
        mock_cursor: MockDatabaseCursor,
        job_id: str = "test_job_123",
        status: str = "locked",
        amount_rtc: Optional[int] = None,
        wallet: Optional[str] = None,
    ) -> None:
        """Set up escrow data in mock cursor for testing.

        Args:
            mock_cursor: Mock database cursor to configure
            job_id: Job identifier for the escrow
            status: Current escrow status (must be in VALID_STATUSES)
            amount_rtc: Amount in RTC (defaults to DEFAULT_AMOUNT_RTC)
            wallet: Wallet address (defaults to DEFAULT_WALLET)

        Raises:
            ValueError: If status is invalid or job_id is malformed
        """
        # Validate inputs
        self._validate_job_id(job_id)
        if status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'. Must be one of {self.VALID_STATUSES}"
            )

        # Set up mock data
        mock_cursor.set_fetchone_result({
            "job_id": job_id,
            "status": status,
            "amount_rtc": amount_rtc if amount_rtc is not None else self.DEFAULT_AMOUNT_RTC,
            "wallet": wallet if wallet is not None else self.DEFAULT_WALLET,
        })

        logger.debug(
            f"Set up escrow data: job_id={job_id}, status={status}, "
            f"amount_rtc={amount_rtc or self.DEFAULT_AMOUNT_RTC}"
        )

    def _validate_job_id(self, job_id: str) -> None:
        """Validate job ID format and length.

        Args:
            job_id: Job identifier to validate

        Raises:
            ValueError: If job ID is invalid, empty, or too long
        """
        if not job_id:
            raise ValueError("job_id cannot be empty")
        if not isinstance(job_id, str):
            raise ValueError(f"job_id must be a string, got {type(job_id).__name__}")
        if len(job_id) > self.MAX_JOB_ID_LENGTH:
            raise ValueError(
                f"job_id too long: {len(job_id)} characters "
                f"(max {self.MAX_JOB_ID_LENGTH})"
            )
        if not re.match(self.VALID_JOB_ID_PATTERN, job_id):
            raise ValueError(
                f"job_id '{job_id}' contains invalid characters. "
                f"Must match pattern: {self.VALID_JOB_ID_PATTERN}"
            )

    def _verify_success_result(
        self,
        result: Dict[str, Any],
        job_id: str,
        expected_status: str,
    ) -> None:
        """Verify a successful escrow operation result.

        Args:
            result: Operation result dictionary to verify
            job_id: Expected job identifier
            expected_status: Expected status after operation

        Raises:
            AssertionError: If result doesn't match expectations
            ValueError: If inputs are invalid
        """
        # Validate inputs
        if not isinstance(result, dict):
            raise ValueError(f"Result must be a dict, got {type(result).__name__}")
        self._validate_job_id(job_id)
        if expected_status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid expected status '{expected_status}'"
            )

        # Verify result
        assert "error" not in result, (
            f"Unexpected error in result: {result.get('error')}"
        )
        assert result.get("status") == expected_status, (
            f"Expected status '{expected_status}', got '{result.get('status')}'"
        )
        assert result.get("job_id") == job_id, (
            f"Expected job_id '{job_id}', got '{result.get('job_id')}'"
        )
        assert "amount_rtc" in result, "Missing amount_rtc in result"
        assert isinstance(result["amount_rtc"], (int, float)), (
            f"amount_rtc must be numeric, got {type(result['amount_rtc']).__name__}"
        )
        assert "wallet" in result, "Missing wallet in result"
        assert isinstance(result["wallet"], str), (
            f"wallet must be string, got {type(result['wallet']).__name__}"
        )

        logger.debug(
            f"Verified success result: job_id={job_id}, "
            f"status={expected_status}, amount_rtc={result.get('amount_rtc')}"
        )

    def _verify_error_result(
        self,
        result: Dict[str, Any],
        expected_error_terms: Optional[List[str]] = None,
    ) -> None:
        """Verify an error result from escrow operation.

        Args:
            result: Operation result dictionary to verify
            expected_error_terms: List of terms expected in error message

        Raises:
            AssertionError: If result doesn't match expectations
            ValueError: If inputs are invalid
        """
        # Validate inputs
        if not isinstance(result, dict):
            raise ValueError(f"Result must be a dict, got {type(result).__name__}")

        # Verify error exists
        assert "error" in result, "Expected error in result but none found"
        error_msg = result["error"]
        assert isinstance(error_msg, str), (
            f"Error message must be string, got {type(error_msg).__name__}"
        )
        assert error_msg.strip(), "Error message cannot be empty"

        # Verify error content
        if expected_error_terms:
            error_msg_lower = error_msg.lower()
            assert any(
                term.lower() in error_msg_lower for term in expected_error_terms
            ), (
                f"Error message should contain one of {expected_error_terms}: "
                f"'{error_msg}'"
            )

        logger.debug(
            f"Verified error result: error='{error_msg}', "
            f"expected_terms={expected_error_terms}"
        )

    def test_escrow_transition_is_atomic_under_race(self) -> None:
        """Verify that concurrent release/refund operations are atomic.

        This test uses monkeypatching to simulate a race condition where
        two operations attempt to transition the same escrow simultaneously.
        Only one should succeed; the other should detect the lost race.

        The test validates:
        - First operation succeeds with correct status transition
        - Second operation fails with appropriate error
        - No double-spending or inconsistent state occurs

        Raises:
            AssertionError: If atomicity is violated
            RuntimeError: If test setup fails
        """
        job_id = "race_test_job_001"
        logger.info(f"Testing escrow atomicity for job: {job_id}")

        try:
            # Validate job ID
            self._validate_job_id(job_id)

            # Store original function for restoration
            original_authorize = _authorize_escrow_action
            race_state: Dict[str, int] = {"call_count": 0}

            def racing_authorize(
                conn: Any,
                job_id_param: str,
                expected_status: str,
            ) -> Dict[str, Any]:
                """Simulate a race condition by mutating status between check and update.

                Args:
                    conn: Database connection object
                    job_id_param: Job identifier to authorize
                    expected_status: Expected current status of escrow

                Returns:
                    Escrow data dictionary with potentially mutated status

                Raises:
                    RuntimeError: If called more than expected times
                """
                race_state["call_count"] += 1
                logger.debug(
                    f"Racing authorize call #{race_state['call_count']} "
                    f"for job {job_id_param}"
                )

                # First call succeeds normally
                if race_state["call_count"] == 1:
                    result = original_authorize(conn, job_id_param, expected_status)
                    logger.debug("First authorize call succeeded")
                    return result

                # Second call simulates the race being lost
                # The status was already changed by the first call
                if race_state["call_count"] == 2:
                    logger.debug("Second authorize call simulating lost race")
                    # Return data with already-changed status
                    return {
                        "job_id": job_id_param,
                        "status": "released",  # Already changed by first call
                        "amount_rtc": self.DEFAULT_AMOUNT_RTC,
                        "wallet": self.DEFAULT_WALLET,
                    }

                raise RuntimeError(
                    f"Unexpected authorize call #{race_state['call_count']}"
                )

            # Apply monkeypatch
            with patch(
                "node.gpu_render_protocol._authorize_escrow_action",
                side_effect=racing_authorize
            ):
                # First call should succeed
                logger.info("Executing first release_escrow call")
                result1 = release_escrow(job_id)
                self._verify_success_result(
                    result1,
                    job_id,
                    "released"
                )
                logger.info("First release_escrow succeeded")

                # Second call should fail due to race condition
                logger.info("Executing second release_escrow call (should fail)")
                result2 = release_escrow(job_id)
                self._verify_error_result(
                    result2,
                    expected_error_terms=[
                        "race",
                        "concurrent",
                        "already",
                        "status",
                        "conflict"
                    ]
                )
                logger.info("Second release_escrow correctly failed")

        except ValueError as e:
            logger.error(f"Validation error in test: {e}")
            raise
        except AssertionError as e:
            logger.error(f"Assertion failed in test: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in test: {e}")
            raise RuntimeError(f"Test failed with unexpected error: {e}") from e

    def test_concurrent_release_and_refund_race(self) -> None:
        """Verify that concurrent