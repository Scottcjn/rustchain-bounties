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
        self.found_tasks = []
        self._seen_ids = set()

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
                last_err = f"status={resp.status_code}"
                time.sleep(self._retry_delay_seconds(resp, attempt))
                continue

            return resp, f"status={resp.status_code}"

        return None, last_err

    def _parse_reward_number(self, num_raw: str, unit_suffix: str) -> Optional[int]:
        normalized = (
            num_raw.replace(",", "")
            .replace("，", "")
            .replace("_", "")
            .strip()
        )
        try:
            base = float(normalized)
        except ValueError:
            return None

        suffix = (unit_suffix or "").lower()
        if suffix == "k":
            base *= 1000
        elif suffix == "m":
            base *= 1_000_000

        return int(base)

    def _extract_rtc_reward(self, text: str) -> int:
        """Best-effort RTC reward extraction from title/body for payout-first ranking.

        Supports forms like: 500 RTC, ~500 RTC, 500+ RTC, 1,200 RTC, 1，200 RTC, 1k RTC, 2.5k RTC, 1.2M RTC, RTC 500, and RTC~2k.
        """
        rewards: List[int] = []
        patterns = [
            re.compile(r"[~≈]?\s*(\d{1,3}(?:[，,]\d{3})+|\d+(?:\.\d+)?)\s*([kKmM])?\+?\s*RTC", re.IGNORECASE),
            re.compile(r"RTC\s*[:：\-~≈]?\s*(\d{1,3}(?:[，,]\d{3})+|\d+(?:\.\d+)?)\s*([kKmM])?\+?", re.IGNORECASE),
        ]
        for pattern in patterns:
            for num_raw, k_suffix in pattern.findall(text):
                parsed = self._parse_reward_number(num_raw, k_suffix)
                if parsed is not None:
                    rewards.append(parsed)
        if not rewards:
            return 0
        return max(rewards)

    def _max_report_results(self) -> int:
        raw = os.getenv("MEAT_MAX_RESULTS", "30")
        try:
            return max(1, int(raw))
        except ValueError:
            return 30

    def _min_reward_rtc(self) -> int:
        """Optional payout floor to suppress low/no-value matches in report output."""
        raw = os.getenv("MEAT_MIN_RTC", "0")
        try:
            return max(0, int(raw))
        except ValueError:
            return 0

    def _github_repos(self) -> List[str]:
        """Optional repo override for faster, payout-first scanning.

        Env format: MEAT_GITHUB_REPOS="owner/repo,owner/repo2"
        """
        raw = os.getenv("MEAT_GITHUB_REPOS", "").strip()
        if not raw:
            return list(DEFAULT_GITHUB_REPOS)

        repos: List[str] = []
        for candidate in (part.strip() for part in raw.split(",")):
            if not candidate:
                continue
            if "/" not in candidate:
                continue
            repos.append(candidate)

        return repos or list(DEFAULT_GITHUB_REPOS)

    def _keywords(self) -> List[str]:
        """Optional keyword override for tuning bounty matching.

        Env format: MEAT_KEYWORDS="python,automation,agent"
        Empty/invalid values gracefully fall back to defaults.
        """
        raw = os.getenv("MEAT_KEYWORDS", "").strip()
        if not raw:
            return list(KEYWORDS)

        parsed = [part.strip().lower() for part in raw.split(",") if part.strip()]
        return parsed or list(KEYWORDS)

    def scan_github_elyan(self):
        """Scans Scottcjn's repos for open bounties."""
        repos = self._github_repos()
        keywords = self._keywords()
        for repo in repos:
            url = f"https://api.github.com/repos/{repo}/issues?state=open&labels=bounty&per_page=100"
            while url:
                try:
                    resp, err = self._github_get_with_retry(url)
                    if resp is None:
                        print(f"GitHub scan warning for {repo}: request failed ({err})")
                        break
                    if err:
                        print(f"GitHub scan warning for {repo}: {err}")
                        break
                    issues = resp.json()
                    if not isinstance(issues, list):
                        message = issues.get("message") if isinstance(issues, dict) else str(issues)
                        print(f"GitHub scan warning for {repo}: unexpected payload ({message})")
                        break
                    if not issues:
                        break

                    for issue in issues:
                        # GitHub issues API returns PRs too; skip them explicitly.
                        if issue.get("pull_request"):
                            continue

                        title = issue.get("title", "").lower()
                        body = issue.get("body", "").lower()
                        if any(k in title or k in body for k in keywords):
                            task_id = f"{repo}#{issue['number']}"
                            if task_id in self._seen_ids:
                                continue
                            self._seen_ids.add(task_id)
                            reward_rtc = self._extract_rtc_reward(
                                f"{issue.get('title', '')}\n{issue.get('body', '')}"
                            )
                            self.found_tasks.append({
                                "platform": "GitHub",
                                "id": task_id,
                                "title": issue["title"],
                                "url": issue["html_url"],
                                "tags": [l["name"] for l in issue.get("labels", [])],
                                "reward_rtc": reward_rtc,
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
        ordered_tasks = sorted(
            self.found_tasks,
            key=lambda t: (-int(t.get("reward_rtc", 0)), t.get("id", "")),
        )

        min_reward = self._min_reward_rtc()
        if min_reward > 0:
            ordered_tasks = [
                t for t in ordered_tasks if int(t.get("reward_rtc", 0)) >= min_reward
            ]

        if not ordered_tasks:
            return "No new 'meat' found in this cycle."

        limit = self._max_report_results()
        visible_tasks = ordered_tasks[:limit]
        for task in visible_tasks:
            reward = int(task.get("reward_rtc", 0))
            reward_suffix = f" [~{reward} RTC]" if reward > 0 else ""
            line = f"- [{task['platform']}] {task['title']}{reward_suffix} ({task['url']})"
            report_lines.append(line)

        hidden_count = len(ordered_tasks) - len(visible_tasks)
        if hidden_count > 0:
            report_lines.append(f"…and {hidden_count} more matches (set MEAT_MAX_RESULTS to adjust output size).")

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
