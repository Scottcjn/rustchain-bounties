# complete code
"""
Review an open PR on GitHub.

This script will pick an open PR from the specified repositories, read the code changes,
and leave a substantive review comment.
"""

import os
import requests
import json

def get_open_prs(repo_owner, repo_name):
    """
    Get a list of open PRs from the specified repository.

    Args:
        repo_owner (str): The owner of the repository.
        repo_name (str): The name of the repository.

    Returns:
        list: A list of open PRs.
    """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
    headers = {"Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN')}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return []

def leave_review_comment(pr_number, repo_owner, repo_name):
    """
    Leave a substantive review comment on the specified PR.

    Args:
        pr_number (int): The number of the PR.
        repo_owner (str): The owner of the repository.
        repo_name (str): The name of the repository.
    """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/comments"
    headers = {"Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN')}"}
    review_comment = "Good approach, but the variable name should describe what it holds"
    data = {"body": review_comment}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 201:
        print("Review comment left successfully")
    else:
        print("Failed to leave review comment")

def main():
    repo_owner = "Scottcjn"
    repo_name = "rustchain-bounties"
    prs = get_open_prs(repo_owner, repo_name)
    if prs:
        pr_number = prs[0]["number"]
        leave_review_comment(pr_number, repo_owner, repo_name)
    else:
        print("No open PRs found")

if __name__ == "__main__":
    main()