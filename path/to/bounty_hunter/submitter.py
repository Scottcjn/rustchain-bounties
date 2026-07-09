# complete code
import os
import requests

# GitHub API credentials
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME")

def submit_review_comment(review_comment):
    """Submit the review comment to the PR"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{PR_NUMBER}/comments"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Content-Type": "application/json"}
    data = {"body": review_comment}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return True
    else:
        raise Exception(f"Failed to submit review comment: {response.status_code}")

def get_pr_info():
    """Get the PR information from the GitHub API"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{PR_NUMBER}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get PR information: {response.status_code}")

def submit_review():
    """Submit the review to the PR"""
    review_comment = get_review_comment()
    submit_review_comment(review_comment)

def get_review_comment():
    """Get the review comment from the PR"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{PR_NUMBER}/comments"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()[0]["body"]
    else:
        raise Exception(f"Failed to get review comment: {response.status_code}")

def main():
    submit_review()

if __name__ == "__main__":
    main()