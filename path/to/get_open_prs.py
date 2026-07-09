# complete code
import github3
import requests

# GitHub API credentials
GITHUB_TOKEN = "your_github_token"
GITHUB_USERNAME = "your_github_username"

# GitHub repository information
REPO_OWNER = "Scottcjn"
REPO_NAME = "rustchain-bounties"

def get_open_prs():
    """Get the open PRs from the GitHub API"""
    try:
        # Create a GitHub client
        client = github3.login(token=GITHUB_TOKEN)

        # Get the repository
        repo = client.repository(REPO_OWNER, REPO_NAME)

        # Get the open PRs
        prs = repo.pull_requests(state="open")

        # Print the PR numbers
        for pr in prs:
            print(pr.number)

    except github3.exceptions.GitHubError as e:
        print(f"Error getting open PRs: {e}")

def main():
    get_open_prs()

if __name__ == "__main__":
    main()