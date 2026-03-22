import sys
import unittest
from unittest.mock import MagicMock

# Mock the github module before importing ai_agent to prevent real API calls
# at module level (ai_agent.py runs Github() and get_repo() on import).
sys.modules['github'] = MagicMock()

import ai_agent
from ai_agent import get_open_bounties, fork_repo_and_create_branch, implement_solution


class TestAIWorkflow(unittest.TestCase):

    def setUp(self):
        # Provide a fresh mock repo before each test
        ai_agent.repo = MagicMock()

    def test_get_open_bounties(self):
        mock_issues = [
            MagicMock(title="Bounty 1", body="This is a software-only bounty"),
            MagicMock(title="Bounty 2", body="This requires hardware"),
        ]
        ai_agent.repo.get_issues.return_value = mock_issues

        bounties = get_open_bounties()

        self.assertEqual(len(bounties), 1)
        self.assertEqual(bounties[0].title, "Bounty 1")

    def test_fork_repo_and_create_branch(self):
        mock_fork = MagicMock()
        mock_fork.get_branch.return_value = MagicMock(commit=MagicMock(sha="dummy_sha"))
        ai_agent.repo.create_fork.return_value = mock_fork

        forked_repo, branch_name = fork_repo_and_create_branch()

        self.assertEqual(forked_repo, mock_fork)
        self.assertTrue(branch_name.startswith("ai-agent-RTC-agent-"))

    def test_implement_solution(self):
        mock_fork = MagicMock()

        implement_solution(mock_fork, "ai-agent-DUMMYHASH")

        mock_fork.create_file.assert_called_once()
        args, kwargs = mock_fork.create_file.call_args
        self.assertEqual(args[0], "solution.py")
        self.assertEqual(args[1], "Implementing solution")
        self.assertIn("placeholder solution", args[2])
        self.assertEqual(kwargs['branch'], "ai-agent-DUMMYHASH")


if __name__ == '__main__':
    unittest.main()
