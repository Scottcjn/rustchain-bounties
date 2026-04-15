import os
import json
import time
import subprocess
from github import Github
from anthropic import Anthropic

# Constants
REPO_NAME = "Scottcjn/rustchain-bounties"
WALLET_ADDRESS = os.environ.get("RTC_WALLET", "Chronolapse411")

class RustChainBountyHunter:
    def __init__(self, github_token, anthropic_api_key):
        self.gh = Github(github_token)
        self.anthropic = Anthropic(api_key=anthropic_api_key)
        self.repo = self.gh.get_repo(REPO_NAME)
        self.local_repo_path = "/tmp/rustchain-bounties"

    def scan_open_bounties(self):
        """Browse open RustChain bounties on GitHub"""
        print("Scanning for open bounties...")
        issues = self.repo.get_issues(state="open", labels=["bounty"])
        bounties = []
        for issue in issues:
            if issue.pull_request:
                continue
            if issue.assignees:
                continue
            bounties.append({
                "number": issue.number,
                "title": issue.title,
                "body": issue.body,
                "url": issue.html_url
            })
        print(f"Found {len(bounties)} unassigned bounties.")
        return bounties

    def evaluate_and_pick(self, bounties):
        """Evaluate which bounties the agent can complete and pick the best one."""
        if not bounties:
            return None
        
        prompt = "Evaluate the following GitHub issues and select the ONE that is easiest for an AI code agent to solve (like typos, simple bug fixes, or script creation). Reply ONLY with the issue number.\n\n"
        for i, b in enumerate(bounties[:10]):  # evaluate top 10
            prompt += f"Issue {b['number']}: {b['title']}\n"
            prompt += f"Description: {b['body'][:1000]}...\n\n"
            
        print("Asking Claude to evaluate the easiest bounty...")
        message = self.anthropic.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=20,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            # Extract number
            selection = message.content[0].text.strip()
            issue_number = int(''.join(filter(str.isdigit, selection)))
            return next(b for b in bounties if b['number'] == issue_number)
        except Exception as e:
            print(f"Error evaluating bounties: {e}. Defaulting to first bounty.")
            return bounties[0]
            
    def prepare_environment(self):
        """Fork and clone the repository"""
        print("Ensuring repository is available locally...")
        if not os.path.exists(self.local_repo_path):
            subprocess.run(["gh", "repo", "fork", REPO_NAME, "--clone", self.local_repo_path], check=True)
            
    def implement_fix(self, issue):
        """Use Anthropic to generate a fix and apply it locally."""
        print(f"Implementing fix for Issue #{issue['number']}: {issue['title']}")
        
        # Get repository file tree context
        tree = subprocess.run(["git", "ls-tree", "-r", "main", "--name-only"], cwd=self.local_repo_path, capture_output=True, text=True).stdout
        
        prompt = f"""You are an autonomous AI agent working on a repository. 
The current task is to solve this GitHub issue:
TITLE: {issue['title']}
BODY: {issue['body']}

Files in repo:
{tree}

Generate a clear python snippet that will create or modify the necessary files to fix this issue.
Your response MUST be wrapped in a python code block that I can execute to apply the changes to the disk.
Assume the current working directory is the root of the repository.
"""
        message = self.anthropic.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4000,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        print("Executing AI-generated fix snippet...")
        
        # Extract python code
        try:
            start_idx = response_text.index("```python") + 9
            end_idx = response_text.index("```", start_idx)
            code = response_text[start_idx:end_idx].strip()
            
            # Execute the code to apply the changes
            temp_script = "/tmp/apply_fix.py"
            with open(temp_script, "w") as f:
                f.write(code)
                
            subprocess.run(["python3", temp_script], cwd=self.local_repo_path, check=True)
            return True
        except Exception as e:
            print(f"Failed to apply fix: {e}")
            return False

    def submit_pull_request(self, issue):
        """Submit a clean PR with bounty claim."""
        print("Committing and submitting pull request...")
        branch_name = f"fix-bounty-{issue['number']}"
        
        subprocess.run(["git", "checkout", "-b", branch_name], cwd=self.local_repo_path)
        subprocess.run(["git", "add", "."], cwd=self.local_repo_path)
        try:
            subprocess.run(["git", "commit", "-m", f"Fix #{issue['number']}: {issue['title']}"], cwd=self.local_repo_path, check=True)
        except subprocess.CalledProcessError:
            print("No changes to commit. Aborting.")
            return False
            
        subprocess.run(["git", "push", "-u", "origin", branch_name], cwd=self.local_repo_path)
        
        pr_body = (
            f"Resolves #{issue['number']}\n\n"
            f"### Autonomous Bounty Claim\n"
            f"This PR was autonomously generated by the RustChain Auto-Hunter Agent.\n\n"
            f"**Wallet Address for RTC Payout:** `{WALLET_ADDRESS}`\n"
        )
        
        print("Creating PR via GH CLI...")
        subprocess.run([
            "gh", "pr", "create", 
            "--title", f"Fix: {issue['title']}",
            "--body", pr_body,
            "--base", "main",
            "--head", f"{self.gh.get_user().login}:{branch_name}"
        ], cwd=self.local_repo_path)
        
        print("Pull request submitted successfully!")
        return True

def main():
    gh_token = os.environ.get("GITHUB_TOKEN")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not gh_token or not anthropic_key:
        print("Error: GITHUB_TOKEN and ANTHROPIC_API_KEY environment variables are required.")
        return
        
    hunter = RustChainBountyHunter(gh_token, anthropic_key)
    
    bounties = hunter.scan_open_bounties()
    target_issue = hunter.evaluate_and_pick(bounties)
    
    if target_issue:
        print(f"Target selected: #{target_issue['number']}")
        hunter.prepare_environment()
        success = hunter.implement_fix(target_issue)
        
        if success:
            hunter.submit_pull_request(target_issue)
    else:
        print("No open bounties found.")

if __name__ == "__main__":
    main()
