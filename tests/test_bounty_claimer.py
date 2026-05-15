import subprocess
import unittest
from unittest.mock import patch

from agent_framework import bounty_claimer


class BountyClaimerTests(unittest.TestCase):
    @patch("agent_framework.bounty_claimer.print")
    @patch("agent_framework.bounty_claimer.subprocess.run")
    def test_claim_bounty_posts_expected_github_comment(self, mock_run, mock_print):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="https://github.com/owner/repo/issues/42#issuecomment-1\n",
            stderr="",
        )

        bounty_claimer.claim_bounty(
            "owner/repo",
            42,
            "miner_007",
            "Add focused unit tests for the bounty claimer helper.",
        )

        mock_run.assert_called_once()
        cmd = mock_run.call_args.args[0]
        self.assertEqual(cmd[:5], ["gh", "issue", "comment", "42", "-R"])
        self.assertEqual(cmd[5], "owner/repo")
        self.assertEqual(cmd[6], "-b")
        self.assertIn("miner_007", cmd[7])
        self.assertIn("Add focused unit tests", cmd[7])
        self.assertIn("Starting implementation now", cmd[7])
        self.assertTrue(mock_run.call_args.kwargs["capture_output"])
        self.assertTrue(mock_run.call_args.kwargs["text"])
        self.assertTrue(mock_run.call_args.kwargs["check"])
        printed = " ".join(str(arg) for call in mock_print.call_args_list for arg in call.args)
        self.assertIn("Successfully claimed bounty owner/repo#42", printed)
        self.assertIn("https://github.com/owner/repo/issues/42#issuecomment-1", printed)

    @patch("agent_framework.bounty_claimer.print")
    @patch("agent_framework.bounty_claimer.subprocess.run")
    def test_claim_bounty_reports_cli_failure_without_raising(self, mock_run, mock_print):
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["gh"],
            stderr="authentication failed",
        )

        bounty_claimer.claim_bounty("owner/repo", 7, "miner_007", "Plan")

        printed = " ".join(str(arg) for call in mock_print.call_args_list for arg in call.args)
        self.assertIn("Failed to claim bounty", printed)
        self.assertIn("authentication failed", printed)


if __name__ == "__main__":
    unittest.main()
