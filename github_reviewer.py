# complete code
import os
import requests
import json

class GitHubReviewer:
    def __init__(self, github_token):
        self.github_token = github_token
        self.headers = {
            'Authorization': f'token {github_token}',
            'Content-Type': 'application/json'
        }

    def get_open_prs(self, repo_owner, repo_name):
        url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'Failed to get open PRs: {response.status_code}')

    def get_pr_files(self, repo_owner, repo_name, pr_number):
        url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'Failed to get PR files: {response.status_code}')

    def leave_comment(self, repo_owner, repo_name, pr_number, comment):
        url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/comments'
        response = requests.post(url, headers=self.headers, data=json.dumps({'body': comment}))
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f'Failed to leave comment: {response.status_code}')

def main():
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        raise Exception('GITHUB_TOKEN environment variable is required')

    reviewer = GitHubReviewer(github_token)
    repo_owner = 'Scottcjn'
    repo_name = 'rustchain-bounties'
    pr_number = 123  # replace with a valid PR number
    comment = 'This is a substantive review comment with two specific observations.'

    try:
        open_prs = reviewer.get_open_prs(repo_owner, repo_name)
        pr_files = reviewer.get_pr_files(repo_owner, repo_name, pr_number)
        reviewer.leave_comment(repo_owner, repo_name, pr_number, comment)
        print('Comment left successfully!')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    main()