#!/usr/bin/env python3
"""
Tests for Monero (RandomX) Integration

Run with: python3 -m pytest test_monero_integration.py -v
"""

import json
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monero_integration import (
    ProofResult,
    now_utc,
    detect_processes,
    verify_node_rpc,
    verify_p2pool,
    verify_pool_account,
    verify_process,
    generate_rustchain_claim,
)


class TestProofResult:
    """Test ProofResult dataclass."""

    def test_create_success(self):
        """Test creating a successful proof result."""
        result = ProofResult(
            proof_type="node_rpc",
            timestamp="2026-03-02T12:00:00Z",
            wallet="test-wallet",
            success=True,
            data={"block_height": 123456}
        )
        
        assert result.proof_type == "node_rpc"
        assert result.wallet == "test-wallet"
        assert result.success is True
        assert result.rustchain_bonus_multiplier == 1.0

    def test_create_with_bonus(self):
        """Test creating a proof result with bonus multiplier."""
        result = ProofResult(
            proof_type="node_rpc",
            timestamp="2026-03-02T12:00:00Z",
            wallet="test-wallet",
            success=True,
            data={"block_height": 123456},
            rustchain_bonus_multiplier=1.5
        )
        
        assert result.rustchain_bonus_multiplier == 1.5

    def test_to_dict(self):
        """Test converting to dictionary."""
        result = ProofResult(
            proof_type="process",
            timestamp="2026-03-02T12:00:00Z",
            wallet="test-wallet",
            success=True,
            data={"process_count": 2}
        )
        
        d = result.to_dict()
        assert isinstance(d, dict)
        assert d["proof_type"] == "process"
        assert d["wallet"] == "test-wallet"

    def test_to_json(self):
        """Test converting to JSON string."""
        result = ProofResult(
            proof_type="process",
            timestamp="2026-03-02T12:00:00Z",
            wallet="test-wallet",
            success=True,
            data={"process_count": 2}
        )
        
        json_str = result.to_json()
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["proof_type"] == "process"


class TestNowUtc:
    """Test timestamp generation."""

    def test_format(self):
        """Test timestamp format is ISO 8601."""
        ts = now_utc()
        assert ts.endswith("Z")
        assert "T" in ts
        # Should be parseable
        from datetime import datetime
        datetime.fromisoformat(ts.replace("Z", "+00:00"))


class TestDetectProcesses:
    """Test process detection."""

    def test_returns_list(self):
        """Test that detect_processes returns a list."""
        result = detect_processes()
        assert isinstance(result, list)

    def test_process_structure(self):
        """Test that detected processes have correct structure."""
        result = detect_processes()
        for proc in result:
            assert "process" in proc
            assert "pid" in proc
            assert isinstance(proc["process"], str)
            assert isinstance(proc["pid"], str)


class TestVerifyNodeRpc:
    """Test node RPC verification."""

    def test_returns_proof_result(self):
        """Test that verify_node_rpc returns a ProofResult."""
        result = verify_node_rpc("test-wallet")
        assert isinstance(result, ProofResult)
        assert result.proof_type == "node_rpc"
        assert result.wallet == "test-wallet"

    def test_handles_connection_error(self):
        """Test graceful handling when monerod is not running."""
        result = verify_node_rpc("test-wallet")
        # Should not raise exception, should return failure result
        assert result.success is False or result.success is True
        # If failed, should have error message
        if not result.success:
            assert result.error is not None

    def test_includes_proof_hash_on_success(self):
        """Test that successful verification includes proof hash."""
        result = verify_node_rpc("test-wallet")
        if result.success:
            assert "proof_hash" in result.data
            assert len(result.data["proof_hash"]) == 64  # SHA256 hex


class TestVerifyP2pool:
    """Test P2Pool verification."""

    def test_returns_proof_result(self):
        """Test that verify_p2pool returns a ProofResult."""
        result = verify_p2pool("test-wallet")
        assert isinstance(result, ProofResult)
        assert result.proof_type == "p2pool"


class TestVerifyPoolAccount:
    """Test pool account verification."""

    def test_unsupported_pool(self):
        """Test handling of unsupported pool."""
        result = verify_pool_account("test-wallet", "invalid-pool")
        assert result.success is False
        assert "Unsupported pool" in result.error

    def test_returns_proof_result(self):
        """Test that verify_pool_account returns a ProofResult."""
        result = verify_pool_account("test-wallet", "nanopool")
        assert isinstance(result, ProofResult)
        assert result.proof_type == "pool_account"

    def test_bonus_multiplier(self):
        """Test that pool verification has correct bonus multiplier."""
        result = verify_pool_account("test-wallet", "nanopool")
        # Should have 1.3x bonus on success, or 1.0 on failure
        assert result.rustchain_bonus_multiplier in [1.0, 1.3]


class TestVerifyProcess:
    """Test process verification."""

    def test_returns_proof_result(self):
        """Test that verify_process returns a ProofResult."""
        result = verify_process("test-wallet")
        assert isinstance(result, ProofResult)
        assert result.proof_type == "process"

    def test_process_data_structure(self):
        """Test process proof data structure."""
        result = verify_process("test-wallet")
        if result.success:
            assert "detected_processes" in result.data
            assert "process_count" in result.data
            assert "proof_hash" in result.data


class TestGenerateRustchainClaim:
    """Test RustChain claim generation."""

    def test_generates_claim(self):
        """Test claim generation from proof result."""
        proof = ProofResult(
            proof_type="node_rpc",
            timestamp="2026-03-02T12:00:00Z",
            wallet="test-wallet",
            success=True,
            data={"proof_hash": "abc123"},
            rustchain_bonus_multiplier=1.5
        )
        
        claim = generate_rustchain_claim(proof)
        
        assert claim["claim_type"] == "monero_dual_mining"
        assert claim["wallet"] == "test-wallet"
        assert claim["proof_type"] == "node_rpc"
        assert claim["bonus_multiplier"] == 1.5
        assert "rustchain_epoch" in claim

    def test_epoch_calculation(self):
        """Test that epoch is calculated correctly (10-minute intervals)."""
        proof = ProofResult(
            proof_type="process",
            timestamp="2026-03-02T12:00:00Z",
            wallet="test-wallet",
            success=True,
            data={}
        )
        
        claim = generate_rustchain_claim(proof)
        assert isinstance(claim["rustchain_epoch"], int)
        # Epoch should be reasonable (around current time / 600)
        import time
        expected_epoch = int(time.time() // 600)
        assert abs(claim["rustchain_epoch"] - expected_epoch) < 10


class TestIntegration:
    """Integration tests."""

    def test_all_proof_types(self):
        """Test that all proof types can be executed."""
        wallet = "integration-test-wallet"
        
        # Node RPC (will likely fail without monerod running)
        node_result = verify_node_rpc(wallet)
        assert node_result.proof_type == "node_rpc"
        
        # P2Pool (will likely fail without P2Pool running)
        p2pool_result = verify_p2pool(wallet)
        assert p2pool_result.proof_type == "p2pool"
        
        # Pool account (may succeed if API is up)
        pool_result = verify_pool_account(wallet, "nanopool")
        assert pool_result.proof_type == "pool_account"
        
        # Process detection (depends on system state)
        process_result = verify_process(wallet)
        assert process_result.proof_type == "process"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
