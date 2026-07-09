# complete code
import os
import requests

# GitHub API credentials
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME")

def track_review_comments():
    """Track the review comments on the PR"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{PR_NUMBER}/comments"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to track review comments: {response.status_code}")

def get_review_comments():
    """Get the review comments from the PR"""
    review_comments = track_review_comments()
    return review_comments

def main():
    review_comments = get_review_comments()
    print(review_comments)

if __name__ == "__main__":
    main()