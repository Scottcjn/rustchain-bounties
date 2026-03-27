import os
import json
import time
import subprocess
import re
from dotenv import load_dotenv
from reporting import log_event

load_dotenv()

# Config
TARGET_REPO = "Scottcjn/rustchain-bounties"
VERIFIED_LOG = "verified_claims.json"
RTC_WALLET = os.getenv("RTC_WALLET", "RTCfe4525ac631c325867a65d1b52b793779731d0d7")

def get_json_set(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f: return set(json.load(f))
        except: pass
    return set()

def save_json_set(filepath, data_set):
    with open(filepath, "w", encoding="utf-8") as f: json.dump(list(data_set), f, indent=4)

def check_star(username, repo_full):
    """Checks if username has starred repo_full."""
    # gh api user/starred/{repo} only works for @me. 
    # For others, we need gh api users/{username}/starred
    try:
        res = subprocess.run(["gh", "api", f"users/{username}/starred", "--paginate", "--jq", ".[].full_name"], capture_output=True, text=True, encoding="utf-8")
        if res.returncode == 0:
            starred_repos = res.stdout.splitlines()
            return repo_full in starred_repos
    except: pass
    return False

def check_follow(username, target_user):
    """Checks if username follows target_user."""
    try:
        res = subprocess.run(["gh", "api", f"users/{username}/following/{target_user}", "--silent"], capture_output=True)
        return res.returncode == 204
    except: pass
    return False

def verify_claim(issue_num, username, comment_body, issue_data):
    """Verifies a specific claim based on issue content and comment."""
    log_event("VERIFIER", f"Verifying claim for {username} on #{issue_num}")
    
    reasons = []
    is_valid = True
    
    title_upper = issue_data["title"].upper()
    body_upper = issue_data["body"].upper()
    
    # 1. Star Verification
    if "STAR" in title_upper or "STAR" in body_upper:
        # Extract repo name from issue body if possible
        # Example: "Star Scottcjn/bottube"
        match = re.search(r"star\s+([A-Za-z0-9_-]+/[A-Za-z0-9_-]+)", issue_data["body"], re.IGNORECASE)
        repo_to_star = match.group(1) if match else "Scottcjn/rustchain-bounties"
        
        if check_star(username, repo_to_star):
            reasons.append(f"✅ Star verified for {repo_to_star}")
        else:
            reasons.append(f"❌ Pull/Star NOT found for {repo_to_star}")
            is_valid = False

    # 2. Follow Verification
    if "FOLLOW" in title_upper or "FOLLOW" in body_upper:
        target = "Scottcjn"
        if check_follow(username, target):
            reasons.append(f"✅ Follow verified for {target}")
        else:
            reasons.append(f"❌ Follow NOT found for {target}")
            is_valid = False

    # 3. Wallet Verification
    if "RTC" in comment_body.upper() and ("RTC" in title_upper or "RTC" in body_upper):
        if re.search(r"RTC[a-f0-9]{40}", comment_body, re.IGNORECASE):
            reasons.append("✅ RTC Wallet format valid")
        else:
            reasons.append("❌ RTC Wallet NOT found or invalid format in comment")
            is_valid = False

    # 4. Result
    status_msg = "✅ **VERIFIED**" if is_valid else "❌ **INCOMPLETE**"
    response = f"{status_msg}\n\n" + "\n".join(reasons) + "\n\n*Action taken by Autonomous Bounty Verification Bot v1.0*"
    
    return is_valid, response

def run_bot_cycle():
    verified = get_json_set(VERIFIED_LOG)
    
    # 1. Fetch recent issues with /claim comments
    # Actually, we'll fetch all open issues in the last 24h
    log_event("VERIFIER", "Scanning GitHub for new claims...")
    res = subprocess.run(["gh", "issue", "list", "--repo", TARGET_REPO, "--limit", "20", "--json", "number,title,body"], capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0: return
    
    issues = json.loads(res.stdout)
    
    for issue in issues:
        num = str(issue["number"])
        
        # 2. Fetch comments for this issue
        comm_res = subprocess.run(["gh", "issue", "view", num, "--repo", TARGET_REPO, "--json", "comments"], capture_output=True, text=True, encoding="utf-8")
        if comm_res.returncode != 0: continue
        
        comments = json.loads(comm_res.stdout).get("comments", [])
        
        for c in comments:
            comment_id = str(c["id"])
            if comment_id in verified: continue
            
            body = c["body"]
            if "/claim" in body.lower():
                username = c["author"]["login"]
                
                # Skip self-claims or known bots if needed
                if username == "rbxict" or username == "ghost": continue
                
                success, response = verify_claim(num, username, body, issue)
                
                # 3. Post verification result
                subprocess.run(["gh", "issue", "comment", num, "--repo", TARGET_REPO, "--body", response], capture_output=True)
                
                verified.add(comment_id)
                save_json_set(VERIFIED_LOG, verified)
                time.sleep(2)

    log_event("SUCCESS", "Bounty Verification Bot cycle complete.")

if __name__ == "__main__":
    run_bot_cycle()
