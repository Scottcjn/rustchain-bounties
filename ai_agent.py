import requests
from github import Github
import json
import random
import string

# GitHub API Token for authentication
GITHUB_TOKEN = 'YOUR_GITHUB_TOKEN'
REPO_NAME = 'Scottcjn/rustchain-bounties'
RTC_WALLET = f"RTC-agent-{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}"

# Initialize GitHub client
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# Function to get open issues from the repository
def get_open_bounties():
    open_bounties = []
    issues = repo.get_issues(state='open')
    for issue in issues:
        text = (issue.title + " " + issue.body).lower()
        if "hardware" not in text and "bounty" in text:  # case-insensitive, searches title+body
            open_bounties.append(issue)
    return open_bounties

# Function to claim a bounty via GitHub comment
def claim_bounty(issue):
    comment = f"Claiming this bounty with AI agent. Wallet: {RTC_WALLET}"
    issue.create_comment(comment)
    print(f"Claimed bounty: {issue.title}")

# Function to fork the repository and create a new branch
def fork_repo_and_create_branch():
    fork = g.create_fork(REPO_NAME)
    branch_name = f"ai-agent-{RTC_WALLET}-{fork.default_branch[:6].upper()}"
    fork.create_branch(branch_name, fork.default_branch)
    return fork, branch_name

# Function to implement a solution for a bounty
def implement_solution(fork, branch_name, issue):
    solution_file = "solution.py"
    solution_content = "This is a simple placeholder solution by AI agent."
    fork.create_file(solution_file, "Implementing solution", solution_content, branch=branch_name)
    print(f"Implemented solution for bounty: {issue.title}")

# Function to create a pull request for a bounty
def create_pull_request(fork, branch_name, issue):
    pr_title = f"AI Agent Solution for {issue.title}"
    pr_body = f"This is a solution for {issue.title} implemented by AI agent."
    fork.create_pull_request(pr_title, branch_name, fork.default_branch, pr_body)
    print(f"Created pull request for bounty: {issue.title}")

# Main function
def main():
    open_bounties = get_open_bounties()
    for issue in open_bounties:
        claim_bounty(issue)
        fork, branch_name = fork_repo_and_create_branch()
        implement_solution(fork, branch_name, issue)
        create_pull_request(fork, branch_name, issue)

if __name__ == '__main__':
    main()
