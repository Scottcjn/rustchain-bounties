"""
Tests for GPU Render Protocol escrow manager with real SQLite.

Tests atomic state transitions, authorization enforcement,
concurrent access safety, and edge cases.
"""

import os
import sqlite3
import tempfile
import threading
from typing import List

import pytest


@pytest.fixture
def db_path() -> str:
    """Temporary database for each test."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["ESCROW_AUTH_SECRET"] = "test_secret_key"
    os.environ["ESCROW_DB_PATH"] = path
    yield path
    if os.path.exists(path):
        os.unlink(path)
    # Clean up env
    for key in ["ESCROW_AUTH_SECRET", "ESCROW_DB_PATH"]:
        os.environ.pop(key, None)


@pytest.fixture
def manager(db_path: str):
    """EscrowManager with temporary DB."""
    from node.gpu_render_protocol import EscrowManager
    mgr = EscrowManager(db_path)
    # Initialize test escrow
    mgr.initialize_escrow("job_test_1", "wallet_abc", 100.0)
    mgr.initialize_escrow("job_test_2", "wallet_def", 200.0)
    yield mgr


def _gen_auth_token() -> str:
    """Generate an auth token for testing."""
    from hashlib import sha256
    secret = os.environ.get("ESCROW_AUTH_SECRET", "test_secret_key")
    return sha256(f"escrow_operator:{secret}".encode()).hexdigest()


class TestAuthorization:
    """Test that authorization is enforced (not allow-all)."""

    def test_release_without_auth_raises(self, manager):
        """Should raise EscrowAuthorizationError without auth token."""
        from node.gpu_render_protocol import EscrowAuthorizationError
        with pytest.raises(EscrowAuthorizationError, match="No authorization provided"):
            manager.release_escrow("job_test_1", "wallet_abc", 100.0)

    def test_release_with_valid_auth_succeeds(self, manager):
        """Should succeed with valid auth token."""
        token = _gen_auth_token()
        result = manager.release_escrow(
            "job_test_1", "wallet_abc", 100.0, auth_token=token
        )
        assert result["status"] == "released"

    def test_release_with_invalid_auth_raises(self, manager):
        """Should raise with invalid auth token."""
        from node.gpu_render_protocol import EscrowAuthorizationError
        with pytest.raises(EscrowAuthorizationError, match="Invalid auth token"):
            manager.release_escrow(
                "job_test_1", "wallet_abc", 100.0, auth_token="wrong_token"
            )


class TestAtomicTransitions:
    """Test that state transitions are atomic."""

    def test_release_succeeds(self, manager):
        """Release should transition from locked to released."""
        token = _gen_auth_token()
        result = manager.release_escrow(
            "job_test_1", "wallet_abc", 100.0, auth_token=token
        )
        assert result["status"] == "released"
        assert result["job_id"] == "job_test_1"

    def test_refund_succeeds(self, manager):
        """Refund should transition from locked to refunded."""
        token = _gen_auth_token()
        result = manager.refund_escrow(
            "job_test_1", "wallet_abc", 100.0, auth_token=token
        )
        assert result["status"] == "refunded"

    def test_double_release_raises_race_condition(self, manager):
        """Second release should detect race condition."""
        token = _gen_auth_token()
        from node.gpu_render_protocol import EscrowRaceConditionError
        manager.release_escrow("job_test_1", "wallet_abc", 100.0, auth_token=token)
        with pytest.raises(EscrowRaceConditionError, match="already transitioned"):
            manager.release_escrow("job_test_1", "wallet_abc", 100.0, auth_token=token)

    def test_release_after_refund_raises(self, manager):
        """Release after refund should detect race condition."""
        token = _gen_auth_token()
        from node.gpu_render_protocol import EscrowRaceConditionError
        manager.refund_escrow("job_test_1", "wallet_abc", 100.0, auth_token=token)
        with pytest.raises(EscrowRaceConditionError, match="already transitioned"):
            manager.release_escrow("job_test_1", "wallet_abc", 100.0, auth_token=token)


class TestWalletAndAmountVerification:
    """Test that wallet and amount are verified."""

    def test_wallet_mismatch_raises(self, manager):
        """Wrong wallet should raise authorization error."""
        token = _gen_auth_token()
        from node.gpu_render_protocol import EscrowAuthorizationError
        with pytest.raises(EscrowAuthorizationError, match="Wallet mismatch"):
            manager.release_escrow(
                "job_test_1", "wrong_wallet", 100.0, auth_token=token
            )

    def test_amount_mismatch_raises(self, manager):
        """Wrong amount should raise validation error."""
        token = _gen_auth_token()
        from node.gpu_render_protocol import EscrowValidationError
        with pytest.raises(EscrowValidationError, match="Amount mismatch"):
            manager.release_escrow(
                "job_test_1", "wallet_abc", 999.0, auth_token=token
            )


class TestConcurrentAccess:
    """Test that concurrent transitions are safe."""

    def test_concurrent_release_and_refund(self, manager):
        """Concurrent release/refund should not both succeed."""
        token = _gen_auth_token()
        # Initialize a third escrow for this test
        manager.initialize_escrow("job_concurrent", "wallet_xyz", 300.0)

        results: List[str] = []
        errors: List[str] = []

        def try_release():
            try:
                manager.release_escrow(
                    "job_concurrent", "wallet_xyz", 300.0, auth_token=token
                )
                results.append("release")
            except Exception as e:
                errors.append(f"release: {e}")

        def try_refund():
            try:
                manager.refund_escrow(
                    "job_concurrent", "wallet_xyz", 300.0, auth_token=token
                )
                results.append("refund")
            except Exception as e:
                errors.append(f"refund: {e}")

        t1 = threading.Thread(target=try_release)
        t2 = threading.Thread(target=try_refund)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Only one should have succeeded
        assert len(results) == 1, (
            f"Both succeeded! results={results} errors={errors}"
        )
        assert len(errors) == 1


class TestEscrowLifecycle:
    """Test full escrow lifecycle."""

    def test_initialize_then_release(self, db_path):
        """Full lifecycle: create -> release -> verify."""
        from node.gpu_render_protocol import EscrowManager
        mgr = EscrowManager(db_path)
        mgr.initialize_escrow("job_lifecycle", "wallet_life", 500.0)

        record = mgr.get_escrow("job_lifecycle")
        assert record is not None
        assert record["status"] == "locked"

        token = _gen_auth_token()
        released = mgr.release_escrow(
            "job_lifecycle", "wallet_life", 500.0, auth_token=token
        )
        assert released["status"] == "released"
        assert released["version"] == 2  # Incremented

    def test_get_all_escrows(self, manager):
        """Should list all escrow records."""
        all_e = manager.get_all_escrows()
        assert len(all_e) == 2

    def test_get_all_escrows_filtered(self, manager):
        """Should filter escrows by status."""
        locked = manager.get_all_escrows(status="locked")
        assert len(locked) == 2
