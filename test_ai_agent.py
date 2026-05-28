import unittest
from unittest.mock import patch, MagicMock
from ai_agent import get_open_bounties, fork_repo_and_create_branch, implement_solution

class TestAIWorkflow(unittest.TestCase):

    @patch('github.Github.get_repo')
    def test_get_open_bounties(self, mock_get_repo):
        # Mocking the repository and issue list
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_issues = [MagicMock(title="Bounty 1", body="This is a non-hardware bounty"),
                       MagicMock(title="RustChain Animated Explainer Video — How Proof of Antiquity Works (50 RTC)", body="This requires hardware")]
        mock_repo.get_issues.return_value = mock_issues
        
        bounties = get_open_bounties()
        self.assertEqual(len(bounties), 1)
        self.assertEqual(bounties[0].title, "RustChain Animated Explainer Video — How Proof of Antiquity Works (50 RTC)")
    
    @patch('github.Github.get_repo')
    @patch('github.Github.Github.create_fork')
    def test_fork_repo_and_create_branch(self, mock_create_fork, mock_get_repo):
        # Mocking the repository and fork creation
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_fork = MagicMock()
        mock_create_fork.return_value = mock_fork
        mock_fork.get_branch.return_value = MagicMock(commit=MagicMock(sha="dummy_sha"))
        
        forked_repo, branch_name = fork_repo_and_create_branch()
        
        self.assertEqual(branch_name, f"ai-agent-dummy_sha-{RTC_WALLET[:10]}")

    @patch('ai_agent.repo')
    @patch('github.Github.Github.create_fork')
    def test_implement_solution(self, mock_create_fork, mock_repo):
        # Mocking the repository and file creation
        mock_fork = MagicMock()
        mock_create_fork.return_value = mock_fork
        mock_issue = MagicMock(title="RustChain Animated Explainer Video — How Proof of Antiquity Works (50 RTC)", number=2304)
        mock_repo.get_issue.return_value = mock_issue
        
        implement_solution(mock_fork, "ai-agent-dummy_hash")

        mock_fork.create_file.assert_called_with("solutions/2304.txt", "Implementing solution", f"This is a simple placeholder solution by AI agent for {mock_issue.title}.", branch="ai-agent-dummy_hash")

if __name__ == '__main__':
    unittest.main()
