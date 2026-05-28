import unittest
from unittest.mock import patch, MagicMock
from ai_agent import get_open_hardware_bounties, fork_repo_and_create_branch, implement_solution

class TestAIWorkflow(unittest.TestCase):

    @patch('github.Github.get_repo')
    def test_get_open_hardware_bounties(self, mock_get_repo):
        # Mocking the repository and issue list
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_issues = [MagicMock(title="Bounty 1", body="This requires hardware"),
                       MagicMock(title="Bounty 2", body="This is a non-hardware bounty")]
        mock_repo.get_issues.return_value = mock_issues
        
        bounties = get_open_hardware_bounties()
        self.assertEqual(len(bounties), 1)
        self.assertEqual(bounties[0].title, "Bounty 1")
    
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
        
        self.assertEqual(branch_name, f"ai-agent-AGENT-1234-DUMM")
    
    @patch('github.Github.get_repo')
    @patch('github.Github.Github.create_fork')
    @patch('github.Github.Repository.create_file')
    def test_implement_solution(self, mock_create_file, mock_create_fork, mock_get_repo):
        # Mocking the repository and file creation
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_fork = MagicMock()
        mock_create_fork.return_value = mock_fork
        
        implement_solution(mock_fork, "ai-agent-DUMMYHASH")
        
        mock_fork.create_file.assert_called_with("solution.py", "Implementing solution", "This is a simple placeholder solution by AI agent.", branch="ai-agent-DUMMYHASH")

if __name__ == '__main__':
    unittest.main()
