import unittest

from scripts.agent_bounty_hunter import (
    parse_reward,
    estimate_difficulty,
    capability_fit,
    classify_payout_action,
    payout_signal_from_comments,
    discover_monitor_targets,
)


class AgentHunterTests(unittest.TestCase):
    def test_parse_reward_rtc(self):
        rtc, usd = parse_reward("Reward: 75 RTC", "[BOUNTY] Test")
        self.assertEqual(rtc, 75.0)
        self.assertGreater(usd, 0)

    def test_parse_reward_usd(self):
        rtc, usd = parse_reward("Bounty: $200", "High payout")
        self.assertEqual(usd, 200.0)
        self.assertGreater(rtc, 0)

    def test_parse_reward_ignores_pool_lines(self):
        body = "Reward: 4 RTC\nCommunity support bounty pool: 75 RTC Pool"
        rtc, usd = parse_reward(body, "[MICRO-BOUNTY] Social task")
        self.assertEqual(rtc, 4.0)
        self.assertGreater(usd, 0)

    def test_parse_reward_prefers_title_parentheses(self):
        body = "May include larger campaign pool 200 RTC."
        rtc, _ = parse_reward(body, "[BOUNTY] wRTC Visibility Pack (75 RTC)")
        self.assertEqual(rtc, 75.0)

    def test_parse_reward_prefers_title_inline_rtc_token(self):
        body = "Reward: 300 RTC\nPool cap: 1200 RTC"
        rtc, _ = parse_reward(body, "[BOUNTY] parser cleanup (75 RTC bonus)")
        self.assertEqual(rtc, 75.0)

    def test_parse_reward_supports_commas_and_k_suffix(self):
        rtc, usd = parse_reward("Reward: 1,500 RTC", "[BOUNTY] Parser upgrade")
        self.assertEqual(rtc, 1500.0)
        self.assertEqual(usd, 150.0)

        rtc2, usd2 = parse_reward("Bounty: $2k", "[BOUNTY] DevRel sprint")
        self.assertEqual(usd2, 2000.0)
        self.assertEqual(rtc2, 20000.0)

    def test_parse_reward_supports_m_suffix(self):
        rtc, usd = parse_reward("Reward: 1.2m RTC", "[BOUNTY] Mega campaign")
        self.assertEqual(rtc, 1200000.0)
        self.assertEqual(usd, 120000.0)

    def test_difficulty(self):
        self.assertEqual(estimate_difficulty("critical security hardening", ""), "high")
        self.assertEqual(estimate_difficulty("tooling bot", "api integration"), "medium")

    def test_capability_fit_bounds(self):
        score = capability_fit("Documentation update", "python script and markdown")
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_payout_signal_and_action(self):
        comments = [{"body": "Verification complete. payout queued with pending id 34"}]
        signal = payout_signal_from_comments(comments)
        self.assertEqual(signal, "queued")
        action = classify_payout_action(merged=True, pr_state="closed", issue_state="open", payout_signal=signal)
        self.assertEqual(action, "wait_payout_queue")

    def test_discover_monitor_targets(self):
        from scripts import agent_bounty_hunter as hunter

        search_payload = {
            "items": [
                {
                    "repository_url": "https://api.github.com/repos/Scottcjn/rustchain-bounties",
                    "number": 34,
                },
                {
                    "repository_url": "https://api.github.com/repos/Scottcjn/rustchain-bounties",
                    "number": 19,
                },
            ]
        }
        comment_payload_34 = [
            {
                "user": {"login": "David-code-tang"},
                "body": "Submission: https://github.com/Scottcjn/rustchain-bounties/pull/127",
            }
        ]
        comment_payload_19 = [
            {
                "user": {"login": "David-code-tang"},
                "body": "PR: https://github.com/Scottcjn/Rustchain/pull/119",
            }
        ]

        original = hunter.gh_get
        def fake_get(path, token=""):
            if path.startswith("/search/issues"):
                return search_payload
            if "/issues/34/comments" in path:
                return comment_payload_34
            if "/issues/19/comments" in path:
                return comment_payload_19
            return []
        hunter.gh_get = fake_get  # type: ignore[assignment]
        try:
            targets = discover_monitor_targets("Scottcjn", "rustchain-bounties", "David-code-tang")
        finally:
            hunter.gh_get = original  # type: ignore[assignment]
        self.assertEqual(len(targets), 2)
        self.assertEqual(targets[0]["issue"], 34)


if __name__ == "__main__":
    unittest.main()
