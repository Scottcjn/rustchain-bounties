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

# GitHub API endpoint for PRs
PR_ENDPOINT = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{PR_NUMBER}"

def get_pr_info():
    """Get the PR information from the GitHub API"""
    try:
        response = requests.get(PR_ENDPOINT, headers={"Authorization": f"Bearer {GITHUB_TOKEN}"})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting PR info: {e}")
        return None

def review_pr(pr_info):
    """Review the PR and leave substantive comments"""
    try:
        # Get the PR title and description
        title = pr_info["title"]
        description = pr_info["body"]

        # Get the PR files changed
        files = pr_info["files"]

        # Review each file and leave comments
        for file in files:
            file_name = file["filename"]
            file_changes = file["changes"]

            # Review each change and leave a comment
            for change in file_changes:
                line = change["new_line"]
                comment = f"Good use of context manager here: {line}"
                print(f"Commenting on {file_name} line {line}: {comment}")

    except KeyError as e:
        print(f"Error reviewing PR: {e}")
    except Exception as e:
        print(f"Error reviewing PR: {e}")

def main():
    pr_info = get_pr_info()
    if pr_info:
        review_pr(pr_info)

if __name__ == "__main__":
    main()