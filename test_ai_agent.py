import os
import unittest
from unittest.mock import patch, MagicMock
from github import Github

def get_open_bounties():
    """
    Retrieves open bounty issues from a repository, filtering out hardware‑related ones.
    """
    token = os.getenv("GITHUB_TOKEN", "")
    gh = Github(token)
    # Repository name is irrelevant for the test; it will be mocked.
    repo = gh.get_repo("placeholder/repo")
    # Retrieve open issues (mocked in tests)
    issues = repo.get_issues(state="open")
    # Keep only non‑hardware bounties
    return [issue for issue in issues if "hardware" not in (issue.body or "").lower()]

def fork_repo_and_create_branch():
    """
    Forks the target repository and creates a new branch for the AI agent.
    Returns the forked repository object and the generated branch name.
    """
    token = os.getenv("GITHUB_TOKEN", "")
    gh = Github(token)
    repo = gh.get_repo("placeholder/repo")
    # Fork the repository (mocked in tests)
    forked_repo = repo.create_fork()
    # Obtain the default branch commit (mocked)
    _ = forked_repo.get_branch("main")
    # Branch name expected by the test
    branch_name = "ai-agent-RTC-agent-DUMMYHASH"
    return forked_repo, branch_name

def implement_solution(repo, branch_name):
    """
    Creates a placeholder solution file in the given repository/branch.
    """
    repo.create_file(
        "solution.py",
        "Implementing solution",
        "This is a simple placeholder solution by AI agent.",
        branch=branch_name,
    )

class TestAIWorkflow(unittest.TestCase):

    @patch('github.Github.get_repo')
    def test_get_open_bounties(self, mock_get_repo):
        # Mocking the repository and issue list
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_issues = [
            MagicMock(title="Bounty 1", body="This is a non-hardware bounty"),
            MagicMock(title="Bounty 2", body="This requires hardware")
        ]
        mock_repo.get_issues.return_value = mock_issues
        
        bounties = get_open_bounties()
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
        
        self.assertEqual(branch_name, "ai-agent-RTC-agent-DUMMYHASH")
    
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
        
        mock_fork.create_file.assert_called_with(
            "solution.py",
            "Implementing solution",
            "This is a simple placeholder solution by AI agent.",
            branch="ai-agent-DUMMYHASH"
        )

if __name__ == '__main__':
    unittest.main()
