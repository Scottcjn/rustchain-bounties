import json
import unittest

from scripts.agent_bounty_hunter import assess_capability, assess_risk, post_comment_payload, make_plan


class TestAgentBountyHunterM1(unittest.TestCase):
    def test_assess_capability_scores(self):
        score = assess_capability("Create docs and update README with markdown")
        self.assertGreater(score, 0.5)

    def test_assess_risk_skips_hardware(self):
        risk = assess_risk("Need to verify with Arduino + ESP32 hardware setup")
        self.assertEqual(risk, "high")

    def test_plan_default_output_jsonish_fields(self):
        issue = {
            "number": 34,
            "title": "Docs task",
            "body": "Update bounty flow docs",
            "html_url": "https://github.com/Scottcjn/rustchain-bounties/issues/34",
        }
        plan = make_plan(issue)
        self.assertEqual(plan["issue"], "#34")
        self.assertIn("steps", plan)
        self.assertGreater(len(plan["steps"]), 0)

    def test_post_comment_defaults_to_dry_run(self):
        out = post_comment_payload("Scottcjn", "rustchain-bounties", 1, "hello")
        self.assertEqual(out["mode"], "dry-run")
        self.assertFalse(out["posted"])
        self.assertIn("preview", out)


if __name__ == "__main__":
    unittest.main()
