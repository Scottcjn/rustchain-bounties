#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Auto-parse and verify star claims on issue #478. Reads comments, extracts wallet and starred repos,
verifies via GitHub API that user has starred each, then appends to a ledger.
"""
import os, re, json, requests, sys

def load_comments(issue_number, token):
    url = f"https://api.github.com/repos/Scottcjn/rustchain-bounties/issues/{issue_number}/comments"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def parse_claim(body):
    wallet = None
    repos = []
    m = re.search(r"Wallet:\s*(\S+)", body)
    if m: wallet = m.group(1).strip()
    for link in re.findall(r"https?://github\.com/([\w\-]+/[\w\-]+)", body):
        repos.append(link)
    return wallet, list(set(repos))

def validate_wallet(name):
    return re.match(r'^[A-Za-z0-9_\-]{3,30}$', name) is not None

def check_star(user, repo, token):
    # List user's starred repos and check for one match
    url = f"https://api.github.com/users/{user}/starred?per_page=100"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3.star+json"}
    stars = requests.get(url, headers=headers).json()
    return any(item.get('repo', item).get('full_name','')==repo or item.get('full_name','')==repo for item in stars)

def calculate_reward(n):
    # n includes main repo
    if n == 1: return 2
    if n >= 6: return 3 * n
    return 2 * n

def main():
    token = os.getenv('GITHUB_TOKEN') or sys.exit("Missing GITHUB_TOKEN")
    issue = os.getenv('STAR_CAMPAIGN_ISSUE') or sys.exit("Missing STAR_CAMPAIGN_ISSUE")
    ledger_file = os.getenv('CLAIM_LEDGER_FILE','stars_claims.json')
    comments = load_comments(issue, token)
    ledger = []
    for c in comments:
        user = c.get('user',{}).get('login')
        body = c.get('body','')
        wallet, repos = parse_claim(body)
        if not user or not wallet or not repos: continue
        if not validate_wallet(wallet): continue
        if 'Scottcjn/Rustchain' not in repos: continue
        valid = True
        for r in repos:
            if not check_star(user, r, token): valid=False
        if not valid: continue
        reward = calculate_reward(len(repos))
        ledger.append({'user':user,'wallet':wallet,'repos':repos,'reward':reward,'status':'verified'})
    os.makedirs(os.path.dirname(ledger_file), exist_ok=True)
    with open(ledger_file,'w') as f: json.dump(ledger,f, indent=2)
    print(f"Processed {len(ledger)} claims to {ledger_file}")

if __name__=='__main__':
    main()
