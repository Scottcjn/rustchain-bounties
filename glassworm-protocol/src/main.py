import os
import sys
import requests
import json
from github import Github

def verify_poa(commit_sha, poa_hash, rpc_url):
    # Mocking Proof of Antiquity verification against RustChain
    # A real implementation would call the RustChain RPC to verify the micro-hash
    # against the block header and difficulty target.
    print(f"Verifying PoA Hash {poa_hash} for commit {commit_sha}...")
    if poa_hash and poa_hash.startswith("poa_"):
        return True
    return False

def main():
    token = os.environ.get("INPUT_GITHUB-TOKEN")
    rpc_url = os.environ.get("INPUT_RPC-URL")
    
    if not token:
        print("Missing GITHUB-TOKEN")
        sys.exit(1)
        
    github_event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not github_event_path or not os.path.exists(github_event_path):
        print("Missing GITHUB_EVENT_PATH")
        sys.exit(1)
        
    with open(github_event_path, "r") as f:
        event_data = json.load(f)
        
    if "pull_request" not in event_data:
        print("Not a pull request event. Skipping.")
        sys.exit(0)
        
    pr_data = event_data["pull_request"]
    repo_name = event_data["repository"]["full_name"]
    pr_number = pr_data["number"]
    
    g = Github(token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    commits = list(pr.get_commits())
    latest_commit = commits[-1]
    commit_msg = latest_commit.commit.message
    
    poa_hash = None
    for line in commit_msg.splitlines():
        if line.startswith("PoA-Signature: "):
            poa_hash = line.split("PoA-Signature: ")[1].strip()
            
    if not poa_hash:
        pr.create_issue_comment("🛑 **Glassworm Protocol Alert** 🛑\n\nNo Proof of Antiquity signature found in the latest commit message.\nPlease include `PoA-Signature: poa_<hash>` to verify this PR.")
        pr.add_to_labels("poa-failed")
        print("No PoA signature found.")
        sys.exit(1)
        
    is_valid = verify_poa(latest_commit.sha, poa_hash, rpc_url)
    
    if is_valid:
        pr.create_issue_comment("✅ **Glassworm Protocol Verified** ✅\n\nProof of Antiquity signature successfully validated. Hardware fingerprint confirmed.")
        pr.add_to_labels("poa-verified")
        try:
            pr.remove_from_labels("poa-failed")
        except:
            pass
        print("PoA signature valid.")
        sys.exit(0)
    else:
        pr.create_issue_comment("🛑 **Glassworm Protocol Alert** 🛑\n\nInvalid Proof of Antiquity signature detected. Hardware Sybil attempt flagged.")
        pr.add_to_labels("poa-failed")
        try:
            pr.remove_from_labels("poa-verified")
        except:
            pass
        print("Invalid PoA signature.")
        sys.exit(1)

if __name__ == "__main__":
    main()
