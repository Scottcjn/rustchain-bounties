#!/usr/bin/env python3
import unittest
from solution import DeterministicBountySolver


class TestBountyDeliverable(unittest.TestCase):
    def test_01_commit_and_idempotency(self):
        solver = DeterministicBountySolver(":memory:")
        res1 = solver.apply_idempotent_mutation("tx-001", {"node": "VoidSpace", "tick": 1})
        self.assertEqual(res1["status"], "COMMITTED")
        res2 = solver.apply_idempotent_mutation("tx-001", {"node": "VoidSpace", "tick": 1})
        self.assertEqual(res2["status"], "SKIPPED_IDEMPOTENT")
        self.assertEqual(res1["sha256"], res2["sha256"])
        solver.close()

    def test_02_conflict_detection_and_merkle_replay(self):
        solver = DeterministicBountySolver(":memory:")
        solver.apply_idempotent_mutation("tx-100", {"value": 42})
        with self.assertRaises(ValueError):
            solver.apply_idempotent_mutation("tx-100", {"value": 99})
        ok, head_hash = solver.verify_merkle_integrity()
        self.assertTrue(ok)
        self.assertEqual(len(head_hash), 64)
        solver.close()


if __name__ == "__main__":
    unittest.main()
