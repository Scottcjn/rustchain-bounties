"""Regression tests for duplicate-miner stress-test mode."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

from stress_test.harness import StressHarness


def test_duplicate_ratio_generates_shared_miner_id(monkeypatch):
    """--dupes should not crash before sessions are launched."""
    seen_force_ids = []

    async def fake_run_miner_session(self, simulator, force_duplicate_id=None, malformed=False):
        seen_force_ids.append(force_duplicate_id)
        return {
            "success": True,
            "total_time": 0.001,
            "steps": {},
            "is_duplicate": force_duplicate_id is not None,
            "is_malformed": malformed,
        }

    monkeypatch.setattr(StressHarness, "run_miner_session", fake_run_miner_session)

    harness = StressHarness(node_url="http://127.0.0.1:1", concurrency=2, timeout=1)
    asyncio.run(harness.run_test(num_miners=4, duplicate_ratio=0.5))

    duplicate_ids = [miner_id for miner_id in seen_force_ids if miner_id is not None]
    assert len(duplicate_ids) == 2
    assert len(set(duplicate_ids)) == 1
    assert duplicate_ids[0].startswith("duplicate-miner-")
