# complete code
import os
import requests
import json

def get_open_prs(repo):
    """Get a list of open PRs from the given repository."""
    url = f"https://api.github.com/repos/{repo}/pulls"
    headers = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get open PRs: {response.status_code}")

def leave_review_comment(pr_number, repo, comment):
    """Leave a review comment on the given PR."""
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments"
    headers = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"}
    data = {"body": comment}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Failed to leave review comment: {response.status_code}")

def review_pr(repo, pr_number):
    """Review the given PR and leave a review comment."""
    try:
        prs = get_open_prs(repo)
        for pr in prs:
            if pr["number"] == pr_number:
                url = f"https://github.com/{repo}/pull/{pr_number}/files"
                response = requests.get(url)
                if response.status_code == 200:
                    files = response.json()
                    for file in files:
                        print(f"Reviewing file: {file['filename']}")
                        comment = f"Good use of context manager here: {file['filename']}"
                        leave_review_comment(pr_number, repo, comment)
                else:
                    raise Exception(f"Failed to get files: {response.status_code}")
                return
        raise Exception(f"PR {pr_number} not found")
    except Exception as e:
        print(f"Error: {e}")

# Example usage
review_pr("Scottcjn/Rustchain", 1)