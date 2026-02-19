# This script would automate the process of claiming the bounty by
# sending a comment on the GitHub issue with the required proof.

import requests

GITHUB_API_URL = "https://api.github.com"
REPO = "Scottcjn/beacon-skill"
ISSUE_NUMBER = 157
YOUR_WALLET_ID = "your_wallet_id"  # Replace with your wallet ID

def claim_bounty():
    headers = {
        "Authorization": f"token YOUR_GITHUB_TOKEN",  # Replace with your token
        "Accept": "application/vnd.github.v3+json",
    }
    
    comment = f"I'd like to claim the bounty for this issue. My wallet ID is {YOUR_WALLET_ID}."
    
    response = requests.post(
        f"{GITHUB_API_URL}/repos/{REPO}/issues/{ISSUE_NUMBER}/comments",
        json={"body": comment},
        headers=headers,
    )
    
    if response.status_code == 201:
        print("Bounty claimed successfully!")
    else:
        print("Failed to claim bounty:", response.content)

if __name__ == "__main__":
    claim_bounty()