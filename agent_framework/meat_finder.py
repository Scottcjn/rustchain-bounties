#!/usr/bin/env python3
import json
import time
import requests
import os
from typing import List, Dict, Optional

# Configuration
DEFAULT_LOG_PATH = os.path.join(os.path.dirname(__file__), "meat_finder.log")
MEAT_LOG = os.getenv("MEAT_LOG", DEFAULT_LOG_PATH)
KEYWORDS = ["python", "scraping", "crawler", "bot", "automation", "script", "data"]
MIN_BOUNTY_USD = 10.0
GITHUB_TOKEN = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")

class MeatFinder:
    """
    Scans multiple platforms for 'meat' (profitable tasks).
    Currently supports: GitHub RustChain/BoTTube, and placeholders for Bountycaster/Apify.
    """

    def __init__(self):
        self.found_tasks = []

    def _github_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "raybot-meat-finder"
        }
        if GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
        return headers

    def _next_link(self, link_header: Optional[str]) -> Optional[str]:
        if not link_header:
            return None
        for part in link_header.split(","):
            if 'rel="next"' in part:
                seg = part.split(";")[0].strip()
                if seg.startswith("<") and seg.endswith(">"):
                    return seg[1:-1]
        return None

    def scan_github_elyan(self):
        """Scans Scottcjn's repos for open bounties."""
        repos = ["Scottcjn/Rustchain", "Scottcjn/bottube", "Scottcjn/rustchain-bounties"]
        for repo in repos:
            url = f"https://api.github.com/repos/{repo}/issues?state=open&labels=bounty&per_page=100"
            while url:
                try:
                    resp = requests.get(url, headers=self._github_headers(), timeout=15)
                    if resp.status_code != 200:
                        print(f"GitHub scan warning for {repo}: status={resp.status_code}")
                        break
                    issues = resp.json()
                    if not isinstance(issues, list) or not issues:
                        break

                    for issue in issues:
                        # GitHub issues API returns PRs too; skip them explicitly.
                        if issue.get("pull_request"):
                            continue

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

                    # Follow GitHub Link headers for robust pagination.
                    url = self._next_link(resp.headers.get("Link"))
                except Exception as e:
                    print(f"GitHub scan error for {repo}: {e}")
                    break

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
        log_dir = os.path.dirname(MEAT_LOG)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        with open(MEAT_LOG, "a") as f:
            f.write(f"--- Scan at {time.ctime()} ---\n")
            f.write(json.dumps(self.found_tasks, indent=2))
            f.write("\n")

if __name__ == "__main__":
    finder = MeatFinder()
    finder.scan_github_elyan()
    print(finder.report())
    finder.save_log()
