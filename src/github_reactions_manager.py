import requests

class GitHubReactionsManager:
    def __init__(self, repo_owner, repo_name, token):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.token = token
        self.base_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues'
        self.headers = {'Authorization': f'token {token}'}

    def add_reaction(self, issue_number, emoji):
        url = f'{self.base_url}/{issue_number}/reactions'
        payload = {'content': emoji}
        response = requests.post(url, json=payload, headers=self.headers)
        if response.status_code == 200:
            print(f'Successfully added {emoji} reaction to issue #{issue_number}.')
        else:
            print(f'Failed to add reaction. Status Code: {response.status_code}')

    def react_to_issues(self, issue_numbers, emoji):
        for issue_number in issue_numbers:
            self.add_reaction(issue_number, emoji)

if __name__ == '__main__':
    # Example usage
    repo_owner = 'Scottcjn'
    repo_name = 'rustchain-bounties'
    token = 'your_github_token_here'
    emoji = '👍'
    issue_numbers = [1, 2, 3]  # Example issue numbers
    reactions_manager = GitHubReactionsManager(repo_owner, repo_name, token)
    reactions_manager.react_to_issues(issue_numbers, emoji)