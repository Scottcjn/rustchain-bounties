# SPDX-License-Identifier: MIT
"""Unit tests for the Ergo Anchor Chain Proof Verifier."""

import json
import os
import sqlite3
import tempfile

import pytest

from verify_anchors import (
    blake2b256_hex, canonical_json, recompute_commitment,
    load_anchors, verify_anchors, AnchorRecord, VerifyResult,
    ErgoNodeClient,
)


# --- Crypto Tests ---

class TestCrypto:
    def test_blake2b256_deterministic(self):
        h1 = blake2b256_hex("hello")
        h2 = blake2b256_hex("hello")
        assert h1 == h2
        assert len(h1) == 64

    def test_blake2b256_different_inputs(self):
        assert blake2b256_hex("a") != blake2b256_hex("b")

    def test_canonical_json_sorted(self):
        result = canonical_json({"z": 1, "a": 2})
        assert result == '{"a":2,"z":1}'

    def test_canonical_json_no_spaces(self):
        result = canonical_json({"key": "value"})
        assert " " not in result

    def test_recompute_commitment_deterministic(self):
        h1 = recompute_commitment(100, "abc", "def", "ghi", 12345)
        h2 = recompute_commitment(100, "abc", "def", "ghi", 12345)
        assert h1 == h2

    def test_recompute_commitment_changes_with_height(self):
        h1 = recompute_commitment(100, "abc", "def", "ghi", 12345)
        h2 = recompute_commitment(101, "abc", "def", "ghi", 12345)
        assert h1 != h2


# --- Database Tests ---

def _create_test_db(tmp_path, anchors=None, blocks=None):
    db_path = os.path.join(tmp_path, "test.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""CREATE TABLE ergo_anchors (
        id INTEGER PRIMARY KEY, rustchain_height INTEGER,
        rustchain_hash TEXT, commitment_hash TEXT,
        ergo_tx_id TEXT, ergo_height INTEGER,
        confirmations INTEGER DEFAULT 0, status TEXT DEFAULT 'pending',
        created_at INTEGER)""")

    c.execute("""CREATE TABLE blocks (
        height INTEGER PRIMARY KEY, block_hash TEXT,
        state_root TEXT, attestations_hash TEXT, timestamp INTEGER)""")

    if anchors:
        for a in anchors:
            c.execute("INSERT INTO ergo_anchors VALUES (?,?,?,?,?,?,?,?,?)", a)
    if blocks:
        for b in blocks:
            c.execute("INSERT INTO blocks VALUES (?,?,?,?,?)", b)
    conn.commit()
    conn.close()
    return db_path


class TestDatabase:
    def test_load_anchors_empty(self, tmp_path):
        db = _create_test_db(str(tmp_path))
        anchors = load_anchors(db)
        assert anchors == []

    def test_load_anchors_single(self, tmp_path):
        commitment = blake2b256_hex(canonical_json({
            "attestations_root": "0" * 64,
            "rc_hash": "blockhash1",
            "rc_height": 100,
            "state_root": "0" * 64,
            "timestamp": 1000,
        }))
        db = _create_test_db(str(tmp_path), anchors=[
            (1, 100, "blockhash1", commitment, "ergotx1", 500, 10, "confirmed", 1000)
        ])
        anchors = load_anchors(db)
        assert len(anchors) == 1
        assert anchors[0].rustchain_height == 100

    def test_load_anchors_ordered(self, tmp_path):
        db = _create_test_db(str(tmp_path), anchors=[
            (1, 200, "bh2", "ch2", "tx2", 600, 5, "confirmed", 2000),
            (2, 100, "bh1", "ch1", "tx1", 500, 10, "confirmed", 1000),
        ])
        anchors = load_anchors(db)
        assert anchors[0].rustchain_height == 100
        assert anchors[1].rustchain_height == 200


# --- Verification Tests ---

class TestVerification:
    def test_offline_verification_match(self, tmp_path):
        commitment = blake2b256_hex(canonical_json({
            "attestations_root": "a" * 64,
            "rc_hash": "blockhash1",
            "rc_height": 100,
            "state_root": "s" * 64,
            "timestamp": 1000,
        }))
        db = _create_test_db(str(tmp_path),
            anchors=[(1, 100, "blockhash1", commitment, "ergotx1", 500, 10, "confirmed", 1000)],
            blocks=[(100, "blockhash1", "s" * 64, "a" * 64, 1000)])
        results = verify_anchors(db, offline=True)
        assert len(results) == 1
        assert results[0].status == "OFFLINE_SKIP"

    def test_offline_recompute_mismatch(self, tmp_path):
        db = _create_test_db(str(tmp_path),
            anchors=[(1, 100, "blockhash1", "wrong_hash", "ergotx1", 500, 10, "confirmed", 1000)],
            blocks=[(100, "blockhash1", "s" * 64, "a" * 64, 1000)])
        results = verify_anchors(db, offline=True)
        assert results[0].status == "RECOMPUTE_MISMATCH"

    def test_no_block_data_graceful(self, tmp_path):
        db = _create_test_db(str(tmp_path),
            anchors=[(1, 999, "bh", "ch", "tx", None, 0, "pending", 1000)])
        results = verify_anchors(db, offline=True)
        assert len(results) == 1
        assert results[0].status == "OFFLINE_SKIP"


# --- ErgoNodeClient Tests ---

class TestErgoClient:
    def test_extract_commitment_r5(self):
        client = ErgoNodeClient()
        tx = {"outputs": [{"additionalRegisters": {"R5": "0e40" + "ab" * 32}}]}
        result = client.extract_commitment_from_tx(tx)
        assert result == "ab" * 32

    def test_extract_commitment_missing_registers(self):
        client = ErgoNodeClient()
        tx = {"outputs": [{"additionalRegisters": {}}]}
        result = client.extract_commitment_from_tx(tx)
        assert result is None

    def test_extract_commitment_no_outputs(self):
        client = ErgoNodeClient()
        tx = {"outputs": []}
        result = client.extract_commitment_from_tx(tx)
        assert result is None


# --- Report Tests ---

class TestReport:
    def test_all_match_returns_true(self, tmp_path, capsys):
        from verify_anchors import print_report
        results = [VerifyResult(1, "tx1", 100, "abc", "abc", "abc", "MATCH")]
        assert print_report(results) is True
        captured = capsys.readouterr()
        assert "1/1" in captured.out

    def test_mismatch_returns_false(self, tmp_path, capsys):
        from verify_anchors import print_report
        results = [VerifyResult(1, "tx1", 100, "abc", "def", "abc", "MISMATCH")]
        assert print_report(results) is False
