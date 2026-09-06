"""Unit test suite for Issue #16863 contributor feedback validator."""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "submissions", "16863-contributor-feedback")))

from feedback_validator import FeedbackValidationError, FeedbackValidator


class TestFeedbackValidator(unittest.TestCase):
    """Verifies all validation rules for Issue #16863 feedback submissions."""

    def setUp(self) -> None:
        """Initialize the validator and standard valid submission fixtures."""
        self.validator = FeedbackValidator()
        self.valid_agent_response = (
            "I am an autonomous coding agent operating on behalf of @s6pa1rta3n-lab. "
            "We started on `rustchain-bounties` with the RIP-302 agent economy (#683, #685) and the 300 RTC payments stack (#35). "
            "We nearly abandoned the workflow when manual review latency and unscheduled tier adjudication meant substantial, verified pull requests remained in limbo without a predictable automated gate or escrow release signal. "
            "Introducing an automated CI webhook or real-time claim status endpoint that confirms bounty eligibility upon green tests—rather than relying on batch sweeps and manual label gates—would significantly accelerate our intake throughput. "
            "Hosted wallet GitHub handle: `s6pa1rta3n-lab` (or EVM Base: `0xF46C9F6d70C50BF81ef3588AB523a90a594a2F89`)."
        )

    def test_split_into_sentences_exact_count(self) -> None:
        """Verify that sentence splitting accurately parses 5 distinct sentences."""
        sentences = self.validator.split_into_sentences(self.valid_agent_response)
        self.assertEqual(len(sentences), 5)
        self.assertTrue(sentences[0].startswith("I am an autonomous coding agent"))
        self.assertTrue(sentences[4].endswith("`0xF46C9F6d70C50BF81ef3588AB523a90a594a2F89`)."))

    def test_validate_sentence_count_within_bounds(self) -> None:
        """Verify that a 5-sentence response passes the sentence count check."""
        count = self.validator.validate_sentence_count(self.valid_agent_response)
        self.assertEqual(count, 5)

    def test_validate_sentence_count_too_short_raises_error(self) -> None:
        """Verify that a single-sentence response raises FeedbackValidationError."""
        one_sentence = "I liked working on rustchain-bounties."
        with self.assertRaises(FeedbackValidationError) as ctx:
            self.validator.validate_sentence_count(one_sentence)
        self.assertIn("Sentence count must be between 2 and 6", str(ctx.exception))

    def test_validate_sentence_count_too_long_raises_error(self) -> None:
        """Verify that a 7-sentence response raises FeedbackValidationError."""
        seven_sentences = (
            "Sentence one. Sentence two. Sentence three. "
            "Sentence four. Sentence five. Sentence six. Sentence seven."
        )
        with self.assertRaises(FeedbackValidationError) as ctx:
            self.validator.validate_sentence_count(seven_sentences)
        self.assertIn("Sentence count must be between 2 and 6", str(ctx.exception))

    def test_agent_disclosure_detected(self) -> None:
        """Verify that agent disclosure is recognized in agent submissions."""
        result = self.validator.validate_agent_disclosure(self.valid_agent_response, is_agent=True)
        self.assertTrue(result)

    def test_agent_disclosure_missing_raises_error(self) -> None:
        """Verify that agent submissions without disclosure raise FeedbackValidationError."""
        undisclosed = (
            "We started on rustchain #35. We almost left when tests failed. "
            "Adding a webhook would help. Handle: user1."
        )
        with self.assertRaises(FeedbackValidationError) as ctx:
            self.validator.validate_agent_disclosure(undisclosed, is_agent=True)
        self.assertIn("Agent submissions must disclose agent identity", str(ctx.exception))

    def test_non_agent_submission_does_not_require_agent_keyword(self) -> None:
        """Verify that human submissions do not require agent keywords."""
        human_text = (
            "I started on rustchain #35. I almost left when tests failed. "
            "Adding a webhook would help. Handle: human1."
        )
        self.assertTrue(self.validator.validate_agent_disclosure(human_text, is_agent=False))

    def test_starting_context_identified(self) -> None:
        """Verify that mentions of rustchain, bottube, or issue numbers are accepted."""
        self.assertTrue(self.validator.validate_starting_context(self.valid_agent_response))

    def test_starting_context_missing_raises_error(self) -> None:
        """Verify that lack of repo or bounty mention raises FeedbackValidationError."""
        text = "I did a project somewhere. It was hard. Please change the interface. Handle: user1."
        with self.assertRaises(FeedbackValidationError) as ctx:
            self.validator.validate_starting_context(text)
        self.assertIn("Submission must mention which repo or bounty", str(ctx.exception))

    def test_friction_point_detected(self) -> None:
        """Verify that friction and near-quit descriptions are recognized."""
        self.assertTrue(self.validator.validate_friction_point(self.valid_agent_response))

    def test_friction_point_missing_raises_error(self) -> None:
        """Verify that absence of friction point description raises FeedbackValidationError."""
        text = (
            "I am an agent working on rustchain #35. "
            "Everything was totally fine. "
            "Please add webhooks. Handle: user1."
        )
        with self.assertRaises(FeedbackValidationError) as ctx:
            self.validator.validate_friction_point(text)
        self.assertIn("Submission must explain what nearly made you leave", str(ctx.exception))

    def test_improvement_suggestion_detected(self) -> None:
        """Verify that constructive improvement proposals are recognized."""
        self.assertTrue(self.validator.validate_improvement_suggestion(self.valid_agent_response))

    def test_anti_boilerplate_rejects_generic_praise(self) -> None:
        """Verify that generic praise one-liners are rejected."""
        with self.assertRaises(FeedbackValidationError) as ctx:
            self.validator.validate_anti_boilerplate("great project!")
        self.assertIn("Generic praise and copy-paste answers are not eligible", str(ctx.exception))

    def test_extract_payout_identifier_all_sources(self) -> None:
        """Verify extraction of GitHub handle, EVM address, and fallback handle."""
        res = self.validator.extract_payout_identifier(self.valid_agent_response, fallback_handle="s6pa1rta3n-lab")
        self.assertEqual(res["github_handle"], "s6pa1rta3n-lab")
        self.assertEqual(res["evm_wallet"], "0xF46C9F6d70C50BF81ef3588AB523a90a594a2F89")

    def test_extract_payout_identifier_rtc_address(self) -> None:
        """Verify extraction of standard RTC 40-hex address."""
        text = "My wallet is RTCc8cdaa67b90f9b06987135b8b65ab037bfb603a9."
        res = self.validator.extract_payout_identifier(text)
        self.assertEqual(res["rtc_wallet"], "RTCc8cdaa67b90f9b06987135b8b65ab037bfb603a9")

    def test_validate_submission_full_workflow(self) -> None:
        """Verify complete end-to-end submission payload validation."""
        payload = {
            "response_text": self.valid_agent_response,
            "is_agent": True,
            "claimant": "s6pa1rta3n-lab",
        }
        res = self.validator.validate_submission(payload)
        self.assertTrue(res["valid"])
        self.assertEqual(res["sentence_count"], 5)
        self.assertEqual(len(res["checks_passed"]), 7)

    def test_committed_feedback_json_is_valid(self) -> None:
        """Verify that the committed feedback.json file passes full validation."""
        json_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "submissions", "16863-contributor-feedback", "feedback.json")
        )
        self.assertTrue(os.path.exists(json_path))
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        res = self.validator.validate_submission(data)
        self.assertTrue(res["valid"])
        self.assertEqual(data["sentence_count"], 5)
        self.assertEqual(data["claimant"], "s6pa1rta3n-lab")


if __name__ == "__main__":
    unittest.main()
