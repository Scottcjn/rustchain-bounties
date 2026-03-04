#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Auto-triage claims for Rustchain to 500 stars bounty (Issue #553).
Verifies star claims, account age, and public repo requirements.
"""
import os
import sys
import json
import requests
from datetime import datetime, timedelta

def post_comment(repo, issue_number, token, body):
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    requests.post(url, headers=headers, json={"body": body})

def update_labels(repo, issue_number, token, labels):
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    requests.patch(url, headers=headers, json={"labels": labels})

def main():
    token = os.environ.get("GITHUB_TOKEN")
    event_name = os.environ.get("GITHUB_EVENT_NAME")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token or not event_path or not repo:
        print("Missing required env vars", file=sys.stderr)
        sys.exit(1)
    if event_name != "issue_comment":
        sys.exit(0)
    payload = json.load(open(event_path))
    issue = payload.get("issue", {})
    number = issue.get("number")
    # Only process the 500-stars bounty issue
    if number != 553:
        sys.exit(0)
    commenter = payload.get("comment", {}).get("user", {}).get("login")
    # Verify GitHub account requirements
    user_resp = requests.get(f"https://api.github.com/users/{commenter}",
                              headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}, timeout=10)
    if user_resp.status_code != 200:
        post_comment(repo, number, token, f"Could not fetch user info for @{commenter}.")
        sys.exit(1)
    udata = user_resp.json()
    created = datetime.strptime(udata.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
    if datetime.utcnow() - created < timedelta(days=30) or udata.get("public_repos", 0) < 1:
        post_comment(repo, number, token,
                     f"@{commenter}, account must be ≥30 days old and have ≥1 public repo. Detected created_at={udata.get('created_at')} and public_repos={udata.get('public_repos')}")
        update_labels(repo, number, token, ["claim:invalid"])
        sys.exit(0)
    # Verify star via stargazers list
    owner, reponame = repo.split("/")
    page = 1
    found_star = False
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    while True:
        sg_resp = requests.get(
            f"https://api.github.com/repos/{owner}/Rustchain/stargazers",
            headers=headers, params={"per_page": 100, "page": page}, timeout=10
        )
        if sg_resp.status_code != 200:
            post_comment(repo, number, token, "Error fetching stargazers.")
            sys.exit(1)
        stars = sg_resp.json()
        if not stars:
            break
        logins = [u.get("login") for u in stars]
        if commenter in logins:
            found_star = True
            break
        page += 1
    if not found_star:
        post_comment(repo, number, token,
                     f"@{commenter}, we could not verify your star on Scottcjn/Rustchain. Please star it and comment again.")
        update_labels(repo, number, token, ["claim:invalid"])
        sys.exit(0)
    # All checks passed
    post_comment(repo, number, token,
                 f"✅ @{commenter}, your star and account requirements are verified. Base reward of 2 RTC is pending approval.")
    # Preserve existing labels and add verification label
    existing = [lbl.get("name") for lbl in issue.get("labels", [])]
    new_labels = list(set(existing + ["claim:star-verified", "pending-payment"]))
    update_labels(repo, number, token, new_labels)

if __name__ == "__main__":
    main()
