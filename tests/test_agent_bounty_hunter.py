import unittest

from scripts.agent_bounty_hunter import parse_reward, estimate_difficulty, capability_fit


class AgentHunterTests(unittest.TestCase):
    def test_parse_reward_rtc(self):
        rtc, usd = parse_reward("Reward: 75 RTC", "[BOUNTY] Test")
        self.assertEqual(rtc, 75.0)
        self.assertGreater(usd, 0)

    def test_parse_reward_usd(self):
        rtc, usd = parse_reward("Bounty: $200", "High payout")
        self.assertEqual(usd, 200.0)
        self.assertGreater(rtc, 0)

    def test_difficulty(self):
        self.assertEqual(estimate_difficulty("critical security hardening", ""), "high")
        self.assertEqual(estimate_difficulty("tooling bot", "api integration"), "medium")

    def test_capability_fit_bounds(self):
        score = capability_fit("Documentation update", "python script and markdown")
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)


if __name__ == "__main__":
    unittest.main()
