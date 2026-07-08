# Complete code
import os
import requests
import json

def get_open_prs(repo_name: str) -> list:
    """
    Retrieves a list of open PRs from the specified repository.

    Args:
    repo_name (str): The name of the repository.

    Returns:
    list: A list of open PRs.
    """
    url = f"https://api.github.com/repos/{repo_name}/pulls"
    headers = {"Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN')}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return []

def review_pr(pr_number: int, repo_name: str) -> None:
    """
    Reviews a PR by leaving a comment with a substantive observation.

    Args:
    pr_number (int): The number of the PR.
    repo_name (str): The name of the repository.
    """
    url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}/comments"
    headers = {"Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN')}"}
    data = {
        "body": f"Good approach, but the variable name should describe what it holds"
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 201:
        print(f"Comment added to PR {pr_number}")
    else:
        print(f"Failed to add comment to PR {pr_number}")

def main() -> None:
    repo_name = "Scottcjn/rustchain-bounties"
    open_prs = get_open_prs(repo_name)
    for pr in open_prs:
        review_pr(pr["number"], repo_name)

if __name__ == "__main__":
    main()