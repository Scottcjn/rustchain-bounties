#!/usr/bin/env python3
"""
Unit tests for ai_agent.py
Covers: get_open_bounties, claim_bounty, fork_repo_and_create_branch,
        implement_solution, submit_pr, receive_rtc_payment, run_agent
Bounty: https://github.com/Scottcjn/rustchain-bounties/issues/1589 (2 RTC)
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import string


# ── get_open_bounties ──────────────────────────────────────────────

class TestGetOpenBounties:
    """Tests for get_open_bounties filtering logic."""

    @patch("ai_agent.repo")
    def test_returns_only_non_hardware_issues(self, mock_repo):
        """Issues with 'hardware' in body are excluded."""
        issue_hw = MagicMock()
        issue_hw.body = "This requires hardware setup on Raspberry Pi."
        issue_sw = MagicMock()
        issue_sw.body = "Software-only bounty: fix the badge generator."

        mock_repo.get_issues.return_value = [issue_hw, issue_sw]

        from ai_agent import get_open_bounties
        result = get_open_bounties()

        assert issue_sw in result
        assert issue_hw not in result

    @patch("ai_agent.repo")
    def test_case_insensitive_hardware_filter(self, mock_repo):
        """'Hardware' with capital H is still filtered."""
        issue = MagicMock()
        issue.body = "Hardware compatibility required"

        mock_repo.get_issues.return_value = [issue]

        from ai_agent import get_open_bounties
        result = get_open_bounties()

        assert len(result) == 0

    @patch("ai_agent.repo")
    def test_empty_issues_returns_empty_list(self, mock_repo):
        """No open issues → empty list."""
        mock_repo.get_issues.return_value = []

        from ai_agent import get_open_bounties
        result = get_open_bounties()

        assert result == []

    @patch("ai_agent.repo")
    def test_all_software_issues_returned(self, mock_repo):
        """All non-hardware issues are included."""
        issues = []
        for i in range(5):
            issue = MagicMock()
            issue.body = f"Software task number {i}"
            issues.append(issue)

        mock_repo.get_issues.return_value = issues

        from ai_agent import get_open_bounties
        result = get_open_bounties()

        assert len(result) == 5


# ── claim_bounty ───────────────────────────────────────────────────

class TestClaimBounty:
    """Tests for claim_bounty comment posting."""

    @patch("ai_agent.RTC_WALLET", "RTC-AGENT-TEST123")
    def test_posts_comment_with_wallet(self):
        """claim_bounty creates a comment containing the wallet address."""
        issue = MagicMock()
        issue.title = "Fix badge generator"

        from ai_agent import claim_bounty
        claim_bounty(issue)

        issue.create_comment.assert_called_once()
        call_args = issue.create_comment.call_args[0][0]
        assert "RTC-AGENT-TEST123" in call_args
        assert "Claiming this bounty" in call_args

    @patch("ai_agent.RTC_WALLET", "RTC-XYZ")
    def test_comment_includes_wallet_label(self):
        """Comment mentions 'Wallet:' label."""
        issue = MagicMock()

        from ai_agent import claim_bounty
        claim_bounty(issue)

        comment_text = issue.create_comment.call_args[0][0]
        assert "Wallet:" in comment_text


# ── RTC_WALLET format ─────────────────────────────────────────────

class TestRTCWalletFormat:
    """Edge case: verify RTC_WALLET format follows spec."""

    def test_wallet_prefix(self):
        """Wallet starts with RTC-agent-."""
        import ai_agent
        assert ai_agent.RTC_WALLET.startswith("RTC-agent-")

    def wallet_suffix_chars(self):
        """Suffix is alphanumeric uppercase."""
        import ai_agent
        suffix = ai_agent.RTC_WALLET.replace("RTC-agent-", "")
        assert all(c in string.ascii_uppercase + string.digits for c in suffix)

    def test_wallet_length(self):
        """Total wallet length is 20 (prefix 10 + suffix 10)."""
        import ai_agent
        assert len(ai_agent.RTC_WALLET) == 20


# ── implement_solution ─────────────────────────────────────────────

class TestImplementSolution:
    """Tests for implement_solution file creation."""

    def test_creates_solution_file(self):
        """Creates solution.py on the correct branch."""
        forked_repo = MagicMock()
        branch_name = "ai-agent-TEST123"

        from ai_agent import implement_solution
        implement_solution(forked_repo, branch_name)

        forked_repo.create_file.assert_called_once()
        call_kwargs = forked_repo.create_file.call_args
        assert call_kwargs[0][0] == "solution.py"
        assert call_kwargs[1]["branch"] == branch_name

    def test_file_content_contains_marker(self):
        """Solution file contains 'AI Agent Solution' marker."""
        forked_repo = MagicMock()

        from ai_agent import implement_solution
        implement_solution(forked_repo, "test-branch")

        content = forked_repo.create_file.call_args[0][1]
        assert "AI Agent Solution" in content


# ── submit_pr ──────────────────────────────────────────────────────

class TestSubmitPR:
    """Tests for submit_pr pull request creation."""

    def test_creates_pr_with_correct_head(self):
        """PR head matches the branch name."""
        forked_repo = MagicMock()
        mock_pr = MagicMock()
        mock_pr.title = "AI Agent Solution for Bounty"
        forked_repo.create_pull.return_value = mock_pr

        from ai_agent import submit_pr
        pr = submit_pr(forked_repo, "ai-agent-XYZ")

        forked_repo.create_pull.assert_called_once()
        call_kwargs = forked_repo.create_pull.call_args[1]
        assert call_kwargs["head"] == "ai-agent-XYZ"
        assert call_kwargs["base"] == "main"

    def test_returns_pull_request_object(self):
        """Returns the PR object for downstream use."""
        forked_repo = MagicMock()
        mock_pr = MagicMock()
        forked_repo.create_pull.return_value = mock_pr

        from ai_agent import submit_pr
        result = submit_pr(forked_repo, "branch")

        assert result is mock_pr


# ── receive_rtc_payment ────────────────────────────────────────────

class TestReceiveRTCPayment:
    """Tests for receive_rtc_payment (placeholder)."""

    @patch("builtins.print")
    @patch("ai_agent.RTC_WALLET", "RTC-PAID001")
    def test_prints_wallet_address(self, mock_print):
        """Prints the wallet address when 'receiving' payment."""
        from ai_agent import receive_rtc_payment
        receive_rtc_payment()

        mock_print.assert_called()
        printed = " ".join(str(c) for call in mock_print.call_args_list for c in call[0])
        assert "RTC-PAID001" in printed


# ── run_agent ──────────────────────────────────────────────────────

class TestRunAgent:
    """Tests for the main run_agent workflow."""

    @patch("ai_agent.receive_rtc_payment")
    @patch("ai_agent.submit_pr")
    @patch("ai_agent.implement_solution")
    @patch("ai_agent.fork_repo_and_create_branch")
    @patch("ai_agent.claim_bounty")
    @patch("ai_agent.get_open_bounties")
    def test_full_workflow_with_bounties(self, mock_bounties, mock_claim,
                                         mock_fork, mock_impl, mock_pr, mock_pay):
        """Full workflow executes all steps when bounties exist."""
        mock_issue = MagicMock()
        mock_bounties.return_value = [mock_issue]
        mock_fork.return_value = (MagicMock(), "branch")

        from ai_agent import run_agent
        run_agent()

        mock_bounties.assert_called_once()
        mock_claim.assert_called_once_with(mock_issue)
        mock_fork.assert_called_once()
        mock_impl.assert_called_once()
        mock_pr.assert_called_once()
        mock_pay.assert_called_once()

    @patch("ai_agent.get_open_bounties")
    @patch("builtins.print")
    def test_no_bounties_exits_early(self, mock_print, mock_bounties):
        """Prints message and returns when no bounties available."""
        mock_bounties.return_value = []

        from ai_agent import run_agent
        result = run_agent()

        mock_print.assert_called_with("No open bounties available.")
