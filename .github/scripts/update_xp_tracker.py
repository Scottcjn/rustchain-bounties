# complete code
import os
import json
import requests

def update_xp_tracker(repo_owner, repo_name, issue_number):
    """
    Update the XP tracker API to reflect the newly filed bug report.

    Args:
        repo_owner (str): The owner of the repository.
        repo_name (str): The name of the repository.
        issue_number (int): The number of the newly filed bug report.
    """
    # Set up the GitHub API credentials
    github_token = os.environ.get('GITHUB_TOKEN')
    github_api_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/bounty-{issue_number}/metadata.json'

    # Update the XP tracker API
    headers = {'Authorization': f'token {github_token}'}
    data = {
        'message': 'Update XP tracker API',
        'content': f'{{"issue_number": {issue_number}, "title": "Bug Report", "description": "Bug report filed on GitHub"}}'
    }
    response = requests.patch(github_api_url, headers=headers, data=json.dumps(data))

    # Check if the XP tracker API was updated successfully
    if response.status_code == 200:
        return True
    else:
        raise Exception(f'Failed to update XP tracker API: {response.text}')

if __name__ == '__main__':
    repo_owner = 'Scottcjn'
    repo_name = 'Rustchain-bounties'
    issue_number = 1
    update_xp_tracker(repo_owner, repo_name, issue_number)