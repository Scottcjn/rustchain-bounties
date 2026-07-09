# complete code
import github3
import requests

# GitHub API credentials
GITHUB_TOKEN = "your_github_token"
GITHUB_USERNAME = "your_github_username"

# GitHub repository and PR information
REPO_OWNER = "Scottcjn"
REPO_NAME = "rustchain-bounties"
PR_NUMBER = 123  # Replace with the PR number you want to review
COMMENT = "Good use of context manager here: #42"

def submit_review_comment():
    """Submit a review comment on the PR"""
    try:
        # Create a GitHub client
        client = github3.login(token=GITHUB_TOKEN)

        # Get the PR information
        repo = client.repository(REPO_OWNER, REPO_NAME)
        pr = repo.pull_request(PR_NUMBER)

        # Submit a review comment
        pr.create_comment(COMMENT)

        print("Review comment submitted successfully")

    except github3.exceptions.GitHubError as e:
        print(f"Error submitting review comment: {e}")

def main():
    submit_review_comment()

if __name__ == "__main__":
    main()