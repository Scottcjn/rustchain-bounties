import unittest
from unittest.mock import patch, MagicMock
from ai_agent import get_open_bounties, fork_repo_and_create_branch, implement_solution

class TestAIWorkflow(unittest.TestCase):

    @patch('ai_agent.repo')
    def test_get_open_bounties(self, mock_repo):
        # Mocking the repository and issue list
        mock_issues = [MagicMock(title="Bounty 1", body="This is a non-hardware bounty"),
                       MagicMock(title="Bounty 2", body="This requires hardware")]
        mock_repo.get_issues.return_value = mock_issues

        bounties = get_open_bounties()
        self.assertEqual(len(bounties), 1)
        self.assertEqual(bounties[0].title, "Bounty 1")

    @patch('ai_agent.repo')
    def test_fork_repo_and_create_branch(self, mock_repo):
        # Mocking the repository and fork creation
        mock_fork = MagicMock()
        mock_repo.create_fork.return_value = mock_fork
        mock_fork.get_branch.return_value = MagicMock(commit=MagicMock(sha="dummy_sha"))

        forked_repo, branch_name = fork_repo_and_create_branch()

        self.assertEqual(forked_repo, mock_fork)
        self.assertTrue(branch_name.startswith("ai-agent-RTC-agent-"))

    @patch('ai_agent.repo')
    def test_implement_solution(self, mock_repo):
        # Mocking the repository and file creation
        mock_fork = MagicMock()

        implement_solution(mock_fork, "ai-agent-DUMMYHASH")

        mock_fork.create_file.assert_called_once()
        call_args = mock_fork.create_file.call_args
        self.assertEqual(call_args[0][0], "solution.py")
        self.assertEqual(call_args[0][1], "Implementing solution")
        self.assertEqual(call_args[1]["branch"], "ai-agent-DUMMYHASH")

if __name__ == '__main__':
    unittest.main()
