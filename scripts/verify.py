#!/usr/bin/env python3
"""
Atlas Bounty Verification Bot
Real verification of bounty claims against GitHub API
"""
import argparse
import json
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

GITHUB_API = "https://api.github.com"

def gh_get(path, token):
    """Make authenticated GitHub API GET request"""
    url = f"{GITHUB_API}{path}"
    req = Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
    try:
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read()), resp.status
    except HTTPError as e:
        return None, e.code
    except URLError:
        return None, 0

def verify_stars(user, repos, token):
    """Verify if user starred specific repos"""
    results = []
    for full_name in repos:
        data, code = gh_get(f"/user/starred/{full_name}", token)
        results.append({"repo": full_name, "starred": code == 204, "http_code": code})
    return results

def verify_follow(user_to_follow, token):
    """Verify if authenticated user follows a specific user"""
    data, code = gh_get(f"/user/following/{user_to_follow}", token)
    return {"user": user_to_follow, "following": code == 204, "http_code": code}

def verify_pr(repo, issue_num, token):
    """Verify if there's a merged PR for a bounty issue"""
    query = f"/search/issues?q=repo:{repo}+is:pr+{issue_num}+in:title+is:merged"
    data, code = gh_get(query, token)
    if data:
        items = data.get("items", [])
        return {"issue": issue_num, "merged_prs": len(items), "prs": [{"num": i["number"], "title": i["title"]} for i in items[:3]]}
    return {"issue": issue_num, "error": f"HTTP {code}"}

def verify_emoji_reactions(repo, issue_num, token):
    """Verify emoji reactions on an issue"""
    data, code = gh_get(f"/repos/{repo}/issues/{issue_num}/reactions", token)
    if data:
        reactions = [r for r in data if r.get("content") in ["+1", "heart", "eyes"]]
        return {"issue": issue_num, "reactions": len(reactions), "reaction_types": [r["content"] for r in reactions]}
    return {"issue": issue_num, "reactions": 0}

def verify_readme_badge(repo, user, token):
    """Verify if user's README mentions the repo"""
    data, code = gh_get(f"/repos/{user}/{user}/readme", token)
    if data and isinstance(data, dict):
        import base64
        content = base64.b64decode(data.get("content", "")).decode(errors="ignore").lower()
        keywords = ["rustchain", "bottube", "beacon", "scottcjn"]
        found = [kw for kw in keywords if kw in content]
        return {"user": user, "readme_mentions": found, "total_mentions": len(found)}
    return {"user": user, "readme_mentions": [], "error": f"HTTP {code}"}

def main():
    parser = argparse.ArgumentParser(description="Atlas Bounty Verification Bot")
    parser.add_argument("--token", required=True, help="GitHub token")
    parser.add_argument("--user", required=True, help="Claimant GitHub username")
    parser.add_argument("--bounty", required=True, help="Bounty number")
    parser.add_argument("--type", required=True, choices=["stars", "follow", "pr", "emoji", "readme", "all"], help="Verification type")
    parser.add_argument("--repos", nargs="*", help="Repos to verify stars for")
    parser.add_argument("--follow-user", help="User to verify follow for")
    parser.add_argument("--repo", help="Repo for PR/emoji verification (format: owner/repo)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if args.type == "all" or args.type == "stars":
        if args.repos:
            result = verify_stars(args.user, args.repos, args.token)
            if args.json:
                print(json.dumps({"stars": result}))
            else:
                starred = [r["repo"] for r in result if r["starred"]]
                print(f"Stars: {len(starred)}/{len(result)} verified")
                for r in result:
                    print(f"  {'✅' if r['starred'] else '❌'} {r['repo']}")

    if args.type == "all" or args.type == "follow":
        if args.follow_user:
            result = verify_follow(args.follow_user, args.token)
            if args.json:
                print(json.dumps({"follow": result}))
            else:
                print(f"{'✅' if result['following'] else '❌'} Following {result['user']}")

    if args.type == "all" or args.type == "emoji":
        if args.repo:
            result = verify_emoji_reactions(args.repo, args.bounty, args.token)
            if args.json:
                print(json.dumps({"emoji": result}))
            else:
                print(f"Emoji reactions on #{result['issue']}: {result['reactions']}")
                if result.get("reaction_types"):
                    print(f"  Types: {result['reaction_types']}")

    if args.type == "all" or args.type == "readme":
        result = verify_readme_badge(args.repo or f"Scottcjn/{args.user}", args.user, args.token)
        if args.json:
            print(json.dumps({"readme": result}))
        else:
            print(f"README mentions: {result.get('total_mentions', 0)}")
            if result.get("readme_mentions"):
                print(f"  Found: {result['readme_mentions']}")

if __name__ == "__main__":
    main()
