#!/usr/bin/env python3
"""
Tests for verify_anchors.py
"""

import hashlib
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from verify_anchors import (
    AnchorRecord,
    AttestationRecord,
    compute_epoch_commitment,
    verify_single_anchor_offline_mode,
    format_result,
    VerificationResult,
)


class TestCommitmentComputation(unittest.TestCase):
    """Tests for commitment computation logic."""
    
    def test_compute_empty_epoch(self):
        """Empty attestations should return zero hash."""
        result = compute_epoch_commitment([])
        self.assertEqual(result, "0" * 64)
    
    def test_compute_single_miner(self):
        """Single miner commitment should be deterministic."""
        attestations = [
            AttestationRecord(
                miner_id="miner-001",
                wallet="WALLET123RTC",
                commitment="abc123",
                nonce="nonce-001",
                epoch=100,
                arch="g4",
                timestamp=1000
            )
        ]
        result = compute_epoch_commitment(attestations)
        # Should be a 64-char hex string (Blake2b256)
        self.assertEqual(len(result), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in result))
    
    def test_compute_multiple_miners_deterministic(self):
        """Multiple miners should produce deterministic output regardless of input order."""
        att1 = AttestationRecord(
            miner_id="miner-001", wallet="WALLET1", commitment="c1", nonce="n1", epoch=100, arch="g4", timestamp=1000
        )
        att2 = AttestationRecord(
            miner_id="miner-002", wallet="WALLET2", commitment="c2", nonce="n2", epoch=100, arch="g5", timestamp=1001
        )
        att3 = AttestationRecord(
            miner_id="miner-003", wallet="WALLET3", commitment="c3", nonce="n3", epoch=100, arch="x86", timestamp=1002
        )
        
        # Same attestations in different order should produce same result
        result1 = compute_epoch_commitment([att1, att2, att3])
        result2 = compute_epoch_commitment([att3, att1, att2])
        result3 = compute_epoch_commitment([att2, att3, att1])
        
        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)
    
    def test_compute_different_epochs_different_results(self):
        """Different miners (different IDs) should produce different commitments."""
        # Same attestation data, different miner_id produces different commitment
        att1 = AttestationRecord(
            miner_id="miner-001", wallet="WALLET1", commitment="c1", nonce="n1", epoch=100, arch="g4", timestamp=1000
        )
        att2 = AttestationRecord(
            miner_id="miner-002", wallet="WALLET1", commitment="c1", nonce="n1", epoch=100, arch="g4", timestamp=1000
        )
        
        result1 = compute_epoch_commitment([att1])
        result2 = compute_epoch_commitment([att2])
        
        self.assertNotEqual(result1, result2)


class TestOfflineVerification(unittest.TestCase):
    """Tests for offline anchor verification."""
    
    def setUp(self):
        """Create a temporary test database."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create ergo_anchors table
        cursor.execute("""
            CREATE TABLE ergo_anchors (
                id INTEGER PRIMARY KEY,
                tx_id TEXT NOT NULL,
                epoch INTEGER NOT NULL,
                slot_height INTEGER,
                commitment TEXT NOT NULL,
                miner_count INTEGER,
                miner_ids TEXT,
                architectures TEXT,
                timestamp INTEGER,
                confirmations INTEGER DEFAULT 0
            )
        """)
        
        # Create miner_attest_recent table
        cursor.execute("""
            CREATE TABLE miner_attest_recent (
                miner_id TEXT PRIMARY KEY,
                wallet TEXT NOT NULL,
                commitment TEXT NOT NULL,
                nonce TEXT NOT NULL,
                epoch INTEGER NOT NULL,
                arch TEXT,
                timestamp INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
    
    def tearDown(self):
        """Clean up temporary database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_verify_matching_commitment(self):
        """Anchor with matching stored and recomputed commitment should verify."""
        # Create test data
        attestations = [
            AttestationRecord(
                miner_id="miner-001",
                wallet="WALLET1RTC",
                commitment="abc123def456",
                nonce="nonce123",
                epoch=100,
                arch="g4",
                timestamp=1000
            ),
            AttestationRecord(
                miner_id="miner-002",
                wallet="WALLET2RTC",
                commitment="def789ghi012",
                nonce="nonce456",
                epoch=100,
                arch="g5",
                timestamp=1001
            ),
        ]
        
        # Compute the expected commitment
        expected_commitment = compute_epoch_commitment(attestations)
        
        # Create anchor record with matching commitment
        anchor = AnchorRecord(
            id=1,
            tx_id="tx123abc456def789",
            epoch=100,
            slot_height=1000,
            stored_commitment=expected_commitment,
            miner_count=2,
            miner_ids="miner-001,miner-002",
            architectures="g4,g5",
            timestamp=1000
        )
        
        # Verify
        result = verify_single_anchor_offline_mode(anchor, attestations)
        
        self.assertEqual(result.status, "MATCH")
        self.assertEqual(result.stored_commitment, result.recomputed_commitment)
    
    def test_verify_mismatched_commitment(self):
        """Anchor with mismatched commitment should report mismatch."""
        attestations = [
            AttestationRecord(
                miner_id="miner-001",
                wallet="WALLET1RTC",
                commitment="abc123def456",
                nonce="nonce123",
                epoch=100,
                arch="g4",
                timestamp=1000
            ),
        ]
        
        anchor = AnchorRecord(
            id=1,
            tx_id="tx123abc456def789",
            epoch=100,
            slot_height=1000,
            stored_commitment="wrong_commitment_value_1234567890abcdef",
            miner_count=1,
            miner_ids="miner-001",
            architectures="g4",
            timestamp=1000
        )
        
        result = verify_single_anchor_offline_mode(anchor, attestations)
        
        self.assertEqual(result.status, "MISMATCH")
        self.assertNotEqual(result.stored_commitment, result.recomputed_commitment)
    
    def test_verify_missing_attestations(self):
        """Anchor with no attestation data should report error."""
        anchor = AnchorRecord(
            id=1,
            tx_id="tx123abc456def789",
            epoch=100,
            slot_height=1000,
            stored_commitment="abc123",
            miner_count=5,
            miner_ids="miner-001",
            architectures="g4",
            timestamp=1000
        )
        
        result = verify_single_anchor_offline_mode(anchor, [])
        
        self.assertEqual(result.status, "ERROR")
        self.assertIn("No attestation data", result.reason)


class TestOutputFormatting(unittest.TestCase):
    """Tests for output formatting."""
    
    def test_format_match(self):
        """MATCH results should format correctly."""
        result = VerificationResult(
            anchor_id=1,
            tx_id="731d5d87abcdef1234567890",
            epoch=424,
            status="MATCH",
            stored_commitment="abc123" * 10 + "abcd",
            on_chain_commitment="abc123" * 10 + "abcd",
            recomputed_commitment="abc123" * 10 + "abcd",
            miner_count_stored=10,
            miner_count_on_chain=10,
            miner_count_recomputed=10,
            reason="Verified: 10 miners"
        )
        
        output = format_result(result)
        
        self.assertIn("Anchor #1", output)
        self.assertIn("731d5d87", output)
        self.assertIn("Commitment MATCH ✓", output)
        self.assertIn("10 miners", output)
        self.assertIn("Epoch 424", output)
    
    def test_format_mismatch(self):
        """MISMATCH results should format correctly."""
        result = VerificationResult(
            anchor_id=2,
            tx_id="a8f3c912abcdef1234567890",
            epoch=425,
            status="MISMATCH",
            stored_commitment="abc123",
            on_chain_commitment="def456",
            recomputed_commitment="abc123",
            reason="Stored differs from on-chain"
        )
        
        output = format_result(result)
        
        self.assertIn("Anchor #2", output)
        self.assertIn("Commitment MISMATCH ✗", output)
        self.assertIn("Expected:", output)
        self.assertIn("Got:", output)


class TestDatabaseOperations(unittest.TestCase):
    """Tests for database operations."""
    
    def setUp(self):
        """Create a temporary test database."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE ergo_anchors (
                id INTEGER PRIMARY KEY,
                tx_id TEXT NOT NULL,
                epoch INTEGER NOT NULL,
                slot_height INTEGER,
                commitment TEXT NOT NULL,
                miner_count INTEGER,
                miner_ids TEXT,
                architectures TEXT,
                timestamp INTEGER,
                confirmations INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE miner_attest_recent (
                miner_id TEXT PRIMARY KEY,
                wallet TEXT NOT NULL,
                commitment TEXT NOT NULL,
                nonce TEXT NOT NULL,
                epoch INTEGER NOT NULL,
                arch TEXT,
                timestamp INTEGER
            )
        """)
        
        # Insert test data
        cursor.execute("""
            INSERT INTO ergo_anchors 
            (id, tx_id, epoch, slot_height, commitment, miner_count, miner_ids, architectures, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (1, "tx123", 100, 1000, "comm123", 2, "m1,m2", "g4,g5", 1000))
        
        cursor.execute("""
            INSERT INTO miner_attest_recent
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("m1", "w1", "c1", "n1", 100, "g4", 1000))
        
        conn.commit()
        conn.close()
    
    def tearDown(self):
        """Clean up temporary database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_open_db(self):
        """Database should open successfully."""
        import verify_anchors
        conn = verify_anchors.open_db(self.db_path)
        self.assertIsNotNone(conn)
        conn.close()
    
    def test_open_db_not_found(self):
        """Non-existent database should raise FileNotFoundError."""
        import verify_anchors
        with self.assertRaises(FileNotFoundError):
            verify_anchors.open_db("/nonexistent/path/db.db")
    
    def test_get_anchor_records(self):
        """Should retrieve anchor records correctly."""
        import verify_anchors
        conn = verify_anchors.open_db(self.db_path)
        anchors = verify_anchors.get_anchor_records(conn)
        conn.close()
        
        self.assertEqual(len(anchors), 1)
        self.assertEqual(anchors[0].id, 1)
        self.assertEqual(anchors[0].tx_id, "tx123")
        self.assertEqual(anchors[0].epoch, 100)
    
    def test_get_anchor_records_by_epoch(self):
        """Should filter anchor records by epoch."""
        import verify_anchors
        conn = verify_anchors.open_db(self.db_path)
        
        # Add another anchor
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ergo_anchors 
            (id, tx_id, epoch, slot_height, commitment, miner_count, miner_ids, architectures, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (2, "tx456", 200, 2000, "comm456", 1, "m3", "x86", 2000))
        conn.commit()
        
        anchors = verify_anchors.get_anchor_records(conn, epoch=100)
        self.assertEqual(len(anchors), 1)
        self.assertEqual(anchors[0].epoch, 100)
        
        conn.close()


if __name__ == "__main__":
    unittest.main()
