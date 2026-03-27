import tempfile
import unittest
from pathlib import Path

from scripts.node_miner_weekly_scan import (
    classify_miner_age,
    classify_node_host,
    load_expected_miners,
)


class NodeMinerWeeklyScanTests(unittest.TestCase):
    def test_classify_node_host_payout_online(self):
        eligible, action = classify_node_host(
            is_active=True,
            online=True,
            node_version="2.2.1-rip200",
            network_version="2.2.1-rip200",
        )
        self.assertTrue(eligible)
        self.assertEqual(action, "pay_weekly")

    def test_classify_node_host_mismatch_still_pays(self):
        eligible, action = classify_node_host(
            is_active=True,
            online=True,
            node_version="2.1.0-rip200",
            network_version="2.2.1-rip200",
        )
        self.assertTrue(eligible)
        self.assertEqual(action, "pay_weekly_and_upgrade_node")

    def test_classify_node_host_offline(self):
        eligible, action = classify_node_host(
            is_active=True,
            online=False,
            node_version="2.2.1-rip200",
            network_version="2.2.1-rip200",
        )
        self.assertFalse(eligible)
        self.assertEqual(action, "investigate_offline")

    def test_classify_miner_age_active(self):
        now = 1_700_000_000
        result = classify_miner_age(now - 900, now_ts=now, active_window_h=2.0, weekly_window_h=168.0)
        self.assertEqual(result["state"], "active")
        self.assertTrue(result["weekly_eligible"])

    def test_classify_miner_age_stale_but_weekly(self):
        now = 1_700_000_000
        result = classify_miner_age(
            now - int(72 * 3600),
            now_ts=now,
            active_window_h=2.0,
            weekly_window_h=168.0,
        )
        self.assertEqual(result["state"], "stale_but_weekly_eligible")
        self.assertTrue(result["weekly_eligible"])

    def test_classify_miner_age_inactive(self):
        now = 1_700_000_000
        result = classify_miner_age(
            now - int(200 * 3600),
            now_ts=now,
            active_window_h=2.0,
            weekly_window_h=168.0,
        )
        self.assertEqual(result["state"], "inactive")
        self.assertFalse(result["weekly_eligible"])

    def test_load_expected_miners(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "expected_miners.txt"
            p.write_text(
                """# known miners
alpha-miner
beta-miner, gamma-miner

delta-miner # inline comment
""",
                encoding="utf-8",
            )
            loaded = load_expected_miners(str(p))
            self.assertEqual(
                loaded,
                {"alpha-miner", "beta-miner", "gamma-miner", "delta-miner"},
            )


if __name__ == "__main__":
    unittest.main()
