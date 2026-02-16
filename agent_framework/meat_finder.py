#!/usr/bin/env python3
import json
import time
import requests
import os
from typing import List, Dict

# Configuration
MEAT_LOG = "/Users/xr/clawd/meat_finder.log"
KEYWORDS = ["python", "scraping", "crawler", "bot", "automation", "script", "data"]
MIN_BOUNTY_USD = 10.0

class MeatFinder:
    """
    Scans multiple platforms for 'meat' (profitable tasks).
    Currently supports: GitHub RustChain/BoTTube, and placeholders for Bountycaster/Apify.
    """

    def __init__(self):
        self.found_tasks = []

    def scan_github_elyan(self):
        """Scans Scottcjn's repos for open bounties."""
        repos = ["Scottcjn/Rustchain", "Scottcjn/bottube", "Scottcjn/rustchain-bounties"]
        for repo in repos:
            url = f"https://api.github.com/repos/{repo}/issues?state=open&labels=bounty"
            try:
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    issues = resp.json()
                    for issue in issues:
                        title = issue.get("title", "").lower()
                        body = issue.get("body", "").lower()
                        if any(k in title or k in body for k in KEYWORDS):
                            self.found_tasks.append({
                                "platform": "GitHub",
                                "id": f"{repo}#{issue['number']}",
                                "title": issue["title"],
                                "url": issue["html_url"],
                                "tags": [l["name"] for l in issue.get("labels", [])]
                            })
            except Exception as e:
                print(f"GitHub scan error for {repo}: {e}")

    def scan_bountycaster_proxy(self):
        """
        Since direct scrape is blocked, we use search results or public feeds.
        Placeholder for logic that uses public hubs or searchcaster mirrors.
        """
        # Note: In a real run, this would query nemes.farcaster.xyz if reachable
        pass

    def scan_apify_ideas(self):
        """Placeholder for Apify Ideas scraping."""
        pass

    def report(self):
        """Returns a summary of newly found tasks."""
        if not self.found_tasks:
            return "No new 'meat' found in this cycle."
        
        report_lines = ["🥩 **Found New Meat!**"]
        for task in self.found_tasks:
            line = f"- [{task['platform']}] {task['title']} ({task['url']})"
            report_lines.append(line)
        
        return "\n".join(report_lines)

    def save_log(self):
        with open(MEAT_LOG, "a") as f:
            f.write(f"--- Scan at {time.ctime()} ---\n")
            f.write(json.dumps(self.found_tasks, indent=2))
            f.write("\n")

if __name__ == "__main__":
    finder = MeatFinder()
    finder.scan_github_elyan()
    print(finder.report())
    finder.save_log()
