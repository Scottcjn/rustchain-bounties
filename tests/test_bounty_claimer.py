#!/usr/bin/env python3
"""
Unit tests for agent_framework/bounty_claimer.py
Covers: claim_bounty function edge cases
"""
import subprocess
import sys
from unittest.mock import patch, MagicMock
import pytest

# Import the module
sys.path.insert(0, 'agent_framework')
from bounty_claimer import claim_bounty


class TestClaimBounty:
    """Test suite for claim_bounty function."""

    @patch('bounty_claimer.subprocess.run')
    def test_claim_success(self, mock_run):
        """Test successful bounty claim."""
        mock_run.return_value = MagicMock(returncode=0, stdout="https://github.com/Scottcjn/rustchain-bounties/issues/1611#issuecomment-4442567317")
        
        result = claim_bounty("Scottcjn/rustchain-bounties", 1611, "NemoMi", "Will add emoji reactions")
        
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "gh"
        assert args[1] == "issue"
        assert args[2] == "comment"
        assert args[3] == "1611"
        assert "-R" in args
        assert "Scottcjn/rustchain-bounties" in args

    @patch('bounty_claimer.subprocess.run')
    def test_claim_failure(self, mock_run):
        """Test bounty claim when gh command fails."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "gh", stderr="Not authenticated")
        
        # Should not raise, just print error
        result = claim_bounty("Scottcjn/rustchain-bounties", 1611, "NemoMi", "Plan")
        
        # Check that error was logged (stderr contains the message)
        # The function catches CalledProcessError and prints to stderr
        assert True  # If we got here, no exception was raised

    @patch('bounty_claimer.subprocess.run')
    def test_claim_format(self, mock_run):
        """Test that claim body is formatted correctly."""
        mock_run.return_value = MagicMock(returncode=0, stdout="OK")
        
        claim_bounty("Scottcjn/rustchain-bounties", 100, "Miner001", "Run unit tests")
        
        call_args = mock_run.call_args[0][0]
        body_index = call_args.index("-b") + 1
        body = call_args[body_index]
        
        assert "**Claim**" in body
        assert "Miner001" in body
        assert "Run unit tests" in body

    @patch('bounty_claimer.subprocess.run')
    def test_claim_multiple_issues(self, mock_run):
        """Test claiming multiple bounties in sequence."""
        mock_run.return_value = MagicMock(returncode=0, stdout="OK")
        
        issues = [1611, 2103, 1589]
        for issue in issues:
            claim_bounty("Scottcjn/rustchain-bounties", issue, "NemoMi", "Multi-issue test")
        
        assert mock_run.call_count == 3


class TestEdgeCases:
    """Test edge cases."""

    @patch('bounty_claimer.subprocess.run')
    def test_empty_miner_id(self, mock_run):
        """Test with empty miner ID."""
        mock_run.return_value = MagicMock(returncode=0, stdout="OK")
        
        result = claim_bounty("Scottcjn/rustchain-bounties", 1, "", "Empty miner test")
        
        # Should still call gh
        assert mock_run.called

    @patch('bounty_claimer.subprocess.run')
    def test_special_chars_in_plan(self, mock_run):
        """Test plan with special characters."""
        mock_run.return_value = MagicMock(returncode=0, stdout="OK")
        
        result = claim_bounty("Scottcjn/rustchain-bounties", 1, "Miner", "Test with 'quotes' and \n newlines")
        
        # Should handle without crashing
        assert mock_run.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
