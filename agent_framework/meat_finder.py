#!/usr/bin/env python3
import json
import time
import requests
import os
import re
from typing import List, Dict, Optional, Tuple

# Configuration
DEFAULT_LOG_PATH = os.path.join(os.path.dirname(__file__), "meat_finder.log")
MEAT_LOG = os.getenv("MEAT_LOG", DEFAULT_LOG_PATH)
KEYWORDS = ["python", "scraping", "crawler", "bot", "automation", "script", "data"]
MIN_BOUNTY_USD = 10.0
DEFAULT_GITHUB_REPOS = ["Scottcjn/Rustchain", "Scottcjn/bottube", "Scottcjn/rustchain-bounties"]
# GH token is resolved dynamically per request so runtime env updates are honored.

class MeatFinder:
    """
    Scans multiple platforms for 'meat' (profitable tasks).
    Currently supports: GitHub RustChain/BoTTube, and placeholders for Bountycaster/Apify.
    """

    def __init__(self):
        self.found_tasks: List[Dict] = []
        self._seen_ids = set()

    def _log(self, msg: str) -> None:
        try:
            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            line = f"[{ts}] {msg}\n"
            with open(MEAT_LOG, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:
            # Best-effort logging; never raise from logger.
            pass

    def _github_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "raybot-meat-finder"
        }
        github_token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
        if github_token:
            headers["Authorization"] = f"Bearer {github_token}"
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

    def _retry_delay_seconds(self, resp: requests.Response, attempt: int) -> float:
        retry_after = resp.headers.get("Retry-After")
        if retry_after:
            try:
                return max(0.0, float(retry_after))
            except ValueError:
                pass
        # Small bounded backoff: 1s, 2s, 4s
        return float(min(4, 2 ** max(0, attempt - 1)))

    def _github_get_with_retry(self, url: str, max_attempts: int = 3, timeout: int = 15) -> Tuple[Optional[requests.Response], Optional[str]]:
        last_err: Optional[str] = None
        for attempt in range(1, max_attempts + 1):
            try:
                resp = requests.get(url, headers=self._github_headers(), timeout=timeout)
            except Exception as e:
                last_err = str(e)
                if attempt < max_attempts:
                    time.sleep(min(4, 2 ** (attempt - 1)))
                    continue
                return None, last_err

            if resp.status_code == 200:
                return resp, None

            # Retry transient/rate-limit style statuses.
            if resp.status_code in (403, 429, 500, 502, 503, 504) and attempt < max_attempts:
                last_err = f"status={resp.status_code} attempt={attempt} url={url}"
                time.sleep(self._retry_delay_seconds(resp, attempt))
                continue

            # Non-retriable or exhausted attempts
            try:
                body = resp.json()
                snippet = json.dumps(body)[:200]
            except Exception:
                snippet = (resp.text or "")[:200]
            last_err = f"status={resp.status_code} url={url} body={snippet}"
            return None, last_err

        return None, last_err

    def _extract_bounty_usd(self, text: str) -> Optional[float]:
        if not text:
            return None
        t = text.lower()

        # Normalize numbers like $1,500.50 or 1 500 usd
        patterns = [
            r"\$?\s*([0-9]{1,3}(?:[, ]?[0-9]{3})*(?:\.[0-9]{1,2})?)\s*(?:usd|us\$|\$)?",
            r"(?:usd|us\$)\s*([0-9]{1,3}(?:[, ]?[0-9]{3})*(?:\.[0-9]{1,2})?)",
            r"bounty:\s*\$?\s*([0-9]{1,3}(?:[, ]?[0-9]{3})*(?:\.[0-9]{1,2})?)",
        ]
        for pat in patterns:
            for m in re.finditer(pat, t, flags=re.IGNORECASE):
                amt_s = m.group(1)
                if not amt_s:
                    continue
                try:
                    amt = float(amt_s.replace(",", "").replace(" ", ""))
                    if amt > 0:
                        return amt
                except Exception:
                    continue
        return None

    def _matches_keywords(self, title: str, body: str) -> bool:
        hay = f"{title or ''}\n{body or ''}".lower()
        return any(k.lower() in hay for k in KEYWORDS)

    def _issue_is_pull_request(self, issue: Dict) -> bool:
        # GitHub issues API includes PRs if 'pull_request' key present
        return "pull_request" in issue

    def _fetch_repo_issues(self, repo: str) -> Tuple[List[Dict], Optional[str]]:
        issues: List[Dict] = []
        url = f"https://api.github.com/repos/{repo}/issues?state=open&per_page=100&sort=created&direction=desc"
        while url:
            resp, err = self._github_get_with_retry(url)
            if err:
                return issues, err
            try:
                page_items = resp.json()
                if isinstance(page_items, list):
                    issues.extend(page_items)
                else:
                    return issues, f"unexpected response shape for {repo}"
            except Exception as e:
                return issues, f"json decode error for {repo}: {e}"
            url = self._next_link(resp.headers.get("Link"))
        return issues, None

    def _task_from_issue(self, repo: str, issue: Dict) -> Optional[Dict]:
        if self._issue_is_pull_request(issue):
            return None
        title = issue.get("title") or ""
        body = issue.get("body") or ""
        if not self._matches_keywords(title, body):
            return None
        bounty = self._extract_bounty_usd(f"{title}\n{body}")
        if bounty is None or bounty < MIN_BOUNTY_USD:
            return None

        task_id = f"github:{repo}#{issue.get('number')}"
        if task_id in self._seen_ids:
            return None
        self._seen_ids.add(task_id)

        return {
            "id": task_id,
            "platform": "github",
            "repo": repo,
            "number": issue.get("number"),
            "title": title,
            "url": issue.get("html_url"),
            "bounty_usd": bounty,
            "labels": [l.get("name") for l in issue.get("labels", []) if isinstance(l, dict)],
            "created_at": issue.get("created_at"),
            "updated_at": issue.get("updated_at"),
        }

    def scan_github(self, repos: Optional[List[str]] = None) -> List[Dict]:
        repos = repos or self._default_repos()
        results: List[Dict] = []

        for repo in repos:
            issues, err = self._fetch_repo_issues(repo)
            if err:
                self._log(f"ERR fetch issues {repo}: {err}")
                continue
            for it in issues:
                task = self._task_from_issue(repo, it)
                if task:
                    results.append(task)
        return results

    def _default_repos(self) -> List[str]:
        # Allow override via env: GH_REPOS="owner1/repo1,owner2/repo2"
        env_val = os.getenv("GH_REPOS")
        if env_val:
            parts = [p.strip() for p in env_val.split(",") if p.strip()]
            if parts:
                return parts
        return list(DEFAULT_GITHUB_REPOS)

    def find_meat(self) -> List[Dict]:
        found = []
        try:
            gh = self.scan_github()
            found.extend(gh)
        except Exception as e:
            self._log(f"ERR scan_github: {e}")

        # Extend here with other platforms (Bountycaster/Apify) as needed.
        self.found_tasks = found
        return found


if __name__ == "__main__":
    mf = MeatFinder()
    tasks = mf.find_meat()
    print(json.dumps({"count": len(tasks), "tasks": tasks}, indent=2))