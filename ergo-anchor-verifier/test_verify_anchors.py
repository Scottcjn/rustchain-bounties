"""
Unit tests for verify_anchors.py (RustChain Bounty #2278)
"""

import unittest
import json
import tempfile
import sqlite3
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from verify_anchors import (
    blake2b_256, blake2b256_hex, canonical_json, MerkleTree,
    AnchorVerifier, AnchorRecord, VerificationResult,
    ErgoNodeClient
)


class TestBlake2b(unittest.TestCase):
    def test_blake2b_256_returns_64_hex_chars(self):
        h = blake2b_256(b"test")
        self.assertEqual(len(h), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in h))

    def test_blake2b_256_deterministic(self):
        h1 = blake2b_256(b"hello world")
        h2 = blake2b_256(b"hello world")
        self.assertEqual(h1, h2)

    def test_blake2b_256_different_inputs_different_output(self):
        h1 = blake2b_256(b"a")
        h2 = blake2b_256(b"b")
        self.assertNotEqual(h1, h2)

    def test_blake2b256_hex_dict(self):
        data = {"rc_height": 1, "rc_hash": "abc123", "timestamp": 1000}
        h = blake2b256_hex(data)
        self.assertEqual(len(h), 64)


class TestCanonicalJson(unittest.TestCase):
    def test_preserves_order_independently(self):
        d = {"z": 1, "a": 2, "b": 3}
        c1 = canonical_json(d)
        d2 = {"a": 2, "b": 3, "z": 1}
        c2 = canonical_json(d2)
        self.assertEqual(c1, c2)

    def test_no_extra_whitespace(self):
        d = {"key": "value"}
        c = canonical_json(d)
        self.assertNotIn(b"\n", c)
        self.assertNotIn(b" ", c)


class TestMerkleTree(unittest.TestCase):
    def test_empty_root(self):
        root = MerkleTree.root([])
        self.assertEqual(len(root), 64)

    def test_single_item(self):
        items = ["aabbccdd"]
        root = MerkleTree.root(items)
        self.assertEqual(len(root), 64)

    def test_two_items(self):
        items = ["aabbccdd", "11223344"]
        root = MerkleTree.root(items)
        self.assertEqual(len(root), 64)

    def test_three_items_dup(self):
        items = ["aabbccdd", "11223344", "aabbccdd"]
        root = MerkleTree.root(items)
        self.assertEqual(len(root), 64)

    def test_commit_items_alias(self):
        items = ["hash1", "hash2"]
        self.assertEqual(MerkleTree.commit_items(items), MerkleTree.root(items))


class TestAnchorRecord(unittest.TestCase):
    def test_from_row(self):
        row = (1, "tx123", "comm456", 10, 5, 1700000000)
        record = AnchorRecord.from_row(row)
        self.assertEqual(record.id, 1)
        self.assertEqual(record.tx_id, "tx123")
        self.assertEqual(record.commitment, "comm456")
        self.assertEqual(record.miner_count, 10)
        self.assertEqual(record.rc_slot, 5)
        self.assertEqual(record.created_at, 1700000000)


class TestVerificationResult(unittest.TestCase):
    def test_match_str(self):
        result = VerificationResult(
            anchor_id=1, tx_id="tx123456789abcdef",
            rc_slot=5, stored_commitment="abc123",
            onchain_commitment="abc123",
            recomputed_commitment="abc123",
            miner_count=10, status="MATCH"
        )
        s = str(result)
        self.assertIn("MATCH", s)
        self.assertIn("TX tx1234567", s)

    def test_mismatch_str(self):
        result = VerificationResult(
            anchor_id=2, tx_id="tx999",
            rc_slot=6, stored_commitment="abc",
            onchain_commitment="xyz",
            recomputed_commitment="abc",
            miner_count=5, status="MISMATCH",
            error="stored != on-chain"
        )
        s = str(result)
        self.assertIn("MISMATCH", s)
        self.assertIn("stored != on-chain", s)


class TestOfflineRecompute(unittest.TestCase):
    """Test recompute_commitment without Ergo node access."""

    def setUp(self):
        # Create in-memory DB with ergo_anchors and miner_attest_recent
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("""
            CREATE TABLE ergo_anchors (
                id INTEGER PRIMARY KEY,
                tx_id TEXT NOT NULL,
                commitment TEXT NOT NULL,
                miner_count INTEGER,
                rc_slot INTEGER,
                created_at INTEGER
            )
        """)
        self.conn.execute("""
            CREATE TABLE miner_attest_recent (
                miner TEXT,
                device_arch TEXT,
                rtc_earned REAL,
                attested_at INTEGER,
                rc_slot INTEGER
            )
        """)
        # Insert test anchor
        self.conn.execute(
            "INSERT INTO ergo_anchors (id, tx_id, commitment, miner_count, rc_slot, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (1, "abc123", "deadbeef", 3, 1, 1700000000)
        )
        # Insert test attestations
        self.conn.execute(
            "INSERT INTO miner_attest_recent VALUES (?, ?, ?, ?, ?)",
            ("miner1", "x86_64", 10.0, 1700000000, 1)
        )
        self.conn.execute(
            "INSERT INTO miner_attest_recent VALUES (?, ?, ?, ?, ?)",
            ("miner2", "arm64", 20.0, 1700000000, 1)
        )
        self.conn.execute(
            "INSERT INTO miner_attest_recent VALUES (?, ?, ?, ?, ?)",
            ("miner3", "ppc64", 15.0, 1700000000, 1)
        )
        self.conn.commit()

    def test_recompute_returns_64_char_hash(self):
        class MockClient:
            def get_transaction(self, tx_id): return None
            def get_box(self, box_id): return None
            def get_epoch_height(self): return None

        class MockVerifier(AnchorVerifier):
            def _connect(self):
                return self.conn

        verifier = MockVerifier(":memory:", MockClient())
        verifier._conn = self.conn

        anchor = AnchorRecord(id=1, tx_id="abc123", commitment="deadbeef",
                               miner_count=3, rc_slot=1, created_at=1700000000)
        attestations = verifier.read_epoch_attestations(1)
        recomputed = verifier.recompute_commitment(anchor, attestations)
        self.assertEqual(len(recomputed), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in recomputed))

    def test_read_anchors(self):
        class MockClient:
            def get_transaction(self, tx_id): return None
            def get_box(self, box_id): return None
            def get_epoch_height(self): return None

        class MockVerifier(AnchorVerifier):
            def _connect(self):
                return self.conn

        verifier = MockVerifier(":memory:", MockClient())
        verifier._conn = self.conn
        anchors = verifier.read_anchors()
        self.assertEqual(len(anchors), 1)
        self.assertEqual(anchors[0].tx_id, "abc123")


class TestErgoNodeClient(unittest.TestCase):
    def test_client_init(self):
        client = ErgoNodeClient("http://localhost:9053", "test-key")
        self.assertEqual(client.node_url, "http://localhost:9053")
        self.assertEqual(client.api_key, "test-key")

    def test_client_strips_trailing_slash(self):
        client = ErgoNodeClient("http://localhost:9053/")
        self.assertEqual(client.node_url, "http://localhost:9053")


if __name__ == "__main__":
    unittest.main()
