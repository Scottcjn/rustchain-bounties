#!/usr/bin/env python3
"""
Autonomous Bounty Hunter Agent for RustChain.

Workflow: scan → evaluate → implement → submit PR
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from evaluator import BountyEvaluator
from implementer import CodeImplementer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("bounty-hunter")


class GitHubClient:
    """Thin wrapper around the GitHub REST API."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.session = requests.Session()
        if self.token:
            self.session.headers["Authorization"] = f"token {self.token}"
        self.session.headers["Accept"] = "application/vnd.github+json"
        self.session.headers["User-Agent"] = "rustchain-bounty-hunter"

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{path}"
        resp = self.session.request(method, url, **kwargs)
        if resp.status_code == 403:
            logger.warning("Rate limited – sleeping 60 s")
            time.sleep(60)
            resp = self.session.request(method, url, **kwargs)
        resp.raise_for_status()
        return resp.json()

    # ── Issues ───────────────────────────────────────────────────────────
    def list_issues(self, owner: str, repo: str, labels: Optional[List[str]] = None,
                    state: str = "open", per_page: int = 30) -> List[Dict]:
        params = {"state": state, "per_page": per_page}
        if labels:
            params["labels"] = ",".join(labels)
        return self._request("GET", f"/repos/{owner}/{repo}/issues", params=params)

    def get_issue(self, owner: str, repo: str, number: int) -> Dict:
        return self._request("GET", f"/repos/{owner}/{repo}/issues/{number}")

    def comment_issue(self, owner: str, repo: str, number: int, body: str) -> Dict:
        return self._request("POST", f"/repos/{owner}/{repo}/issues/{number}/comments",
                             json={"body": body})

    # ── Repos / Forks ────────────────────────────────────────────────────
    def fork(self, owner: str, repo: str) -> Dict:
        return self._request("POST", f"/repos/{owner}/{repo}/forks")

    def get_branch(self, owner: str, repo: str, branch: str) -> Optional[Dict]:
        try:
            return self._request("GET", f"/repos/{owner}/{repo}/branches/{branch}")
        except requests.exceptions.HTTPError:
            return None

    def create_branch(self, owner: str, repo: str, ref: str, branch: str) -> Dict:
        return self._request("POST", f"/repos/{owner}/{repo}/git/refs",
                             json={"ref": f"refs/heads/{branch}", "sha": ref})

    # ── Pull Requests ────────────────────────────────────────────────────
    def create_pr(self, owner: str, repo: str, title: str, body: str,
                  head: str, base: str = "main") -> Dict:
        return self._request("POST", f"/repos/{owner}/{repo}/pulls",
                             json={"title": title, "body": body,
                                   "head": head, "base": base})

    def list_prs(self, owner: str, repo: str, state: str = "open") -> List[Dict]:
        return self._request("GET", f"/repos/{owner}/{repo}/pulls",
                             params={"state": state})

    # ── Files (via Contents API) ─────────────────────────────────────────
    def get_file(self, owner: str, repo: str, path: str,
                 ref: Optional[str] = None) -> Optional[Dict]:
        params = {}
        if ref:
            params["ref"] = ref
        try:
            return self._request("GET", f"/repos/{owner}/{repo}/contents/{path}",
                                 params=params)
        except requests.exceptions.HTTPError:
            return None


class LLMClient:
    """Simple OpenAI-compatible LLM client (works with OpenAI, local models, etc.)."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None,
                 model: str = "gpt-4"):
        self.base_url = (base_url or os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", model)

    def complete(self, system: str, prompt: str, max_tokens: int = 2048,
                 temperature: float = 0.4) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        resp = requests.post(f"{self.base_url}/chat/completions",
                             headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


class BountyHunterAgent:
    """Top-level orchestrator: scan → evaluate → implement → submit PR."""

    def __init__(self, github_token: Optional[str] = None,
                 llm_base_url: Optional[str] = None,
                 llm_api_key: Optional[str] = None,
                 llm_model: str = "gpt-4",
                 target_owner: str = "Scottcjn",
                 target_repo: str = "rustchain-bounties",
                 github_username: Optional[str] = None,
                 work_dir: Optional[str] = None):
        self.gh = GitHubClient(github_token)
        self.llm = LLMClient(llm_base_url, llm_api_key, llm_model)
        self.evaluator = BountyEvaluator(self.llm)
        self.implementer = CodeImplementer(self.llm)
        self.target_owner = target_owner
        self.target_repo = target_repo
        self.github_username = github_username or os.getenv("GITHUB_USERNAME", "")
        self.work_dir = Path(work_dir or os.getenv("WORK_DIR", "/tmp/bounty-hunter-work"))
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.work_dir / "state.json"

    # ── State persistence ────────────────────────────────────────────────
    def _load_state(self) -> Dict:
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return {"claimed": [], "completed": [], "skipped": []}

    def _save_state(self, state: Dict) -> None:
        self.state_file.write_text(json.dumps(state, indent=2))

    # ── Scan ─────────────────────────────────────────────────────────────
    def scan_bounties(self, labels: Optional[List[str]] = None,
                      min_reward: float = 0) -> List[Dict]:
        """Scan for open bounty issues."""
        logger.info("Scanning %s/%s for bounties…", self.target_owner, self.target_repo)
        issues = self.gh.list_issues(self.target_owner, self.target_repo, labels=labels)
        bounties = []
        for issue in issues:
            # Skip pull requests (GitHub returns PRs in the issues endpoint)
            if "pull_request" in issue:
                continue
            reward = self._extract_reward(issue)
            if reward >= min_reward:
                bounties.append({
                    "number": issue["number"],
                    "title": issue["title"],
                    "body": issue.get("body", "") or "",
                    "labels": [l["name"] for l in issue.get("labels", [])],
                    "reward": reward,
                    "url": issue["html_url"],
                    "assignee": issue.get("assignee"),
                })
        logger.info("Found %d bounties (≥%.0f RTC)", len(bounties), min_reward)
        return sorted(bounties, key=lambda b: b["reward"], reverse=True)

    @staticmethod
    def _extract_reward(issue: Dict) -> float:
        """Try to extract RTC reward from issue title/body."""
        import re
        text = f"{issue.get('title', '')} {issue.get('body', '')}"
        m = re.search(r"(\d+)\s*RTC", text, re.IGNORECASE)
        return float(m.group(1)) if m else 0

    # ── Evaluate ─────────────────────────────────────────────────────────
    def evaluate_bounty(self, bounty: Dict) -> Dict:
        """Evaluate a bounty and return assessment."""
        logger.info("Evaluating bounty #%d: %s", bounty["number"], bounty["title"])
        assessment = self.evaluator.evaluate(bounty)
        return assessment

    # ── Claim & Implement ────────────────────────────────────────────────
    def claim_bounty(self, bounty: Dict, assessment: Dict) -> Optional[str]:
        """Claim a bounty: comment, fork, implement, PR."""
        state = self._load_state()
        num = bounty["number"]
        if num in state["claimed"]:
            logger.info("Bounty #%d already claimed", num)
            return None

        # Comment to claim
        logger.info("Claiming bounty #%d", num)
        self.gh.comment_issue(
            self.target_owner, self.target_repo, num,
            f"🤖 **Bounty Hunter Agent** — claiming this bounty. Starting work now."
        )
        state["claimed"].append(num)
        self._save_state(state)

        # Fork the repo
        logger.info("Forking %s/%s…", self.target_owner, self.target_repo)
        fork_data = self.gh.fork(self.target_owner, self.target_repo)
        fork_full_name = fork_data["full_name"]
        logger.info("Forked to %s", fork_full_name)

        # Create feature branch
        branch_name = f"bounty-{num}-{int(time.time())}"
        default_branch = fork_data.get("default_branch", "main")
        ref_data = self.gh.get_branch(self.github_username or fork_data["owner"]["login"],
                                      self.target_repo, default_branch)
        if ref_data:
            sha = ref_data["commit"]["sha"]
            self.gh.create_branch(
                self.github_username or fork_data["owner"]["login"],
                self.target_repo, sha, branch_name
            )
            logger.info("Created branch %s", branch_name)

        # Implement
        logger.info("Implementing solution for bounty #%d…", num)
        implementation = self.implementer.implement(bounty, assessment)

        # In a real agent, we would push files via the GitHub API here.
        # For now, save locally.
        bounty_dir = self.work_dir / f"bounty-{num}"
        bounty_dir.mkdir(exist_ok=True)
        for filepath, content in implementation.get("files", {}).items():
            fpath = bounty_dir / filepath
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text(content)
            logger.info("  Wrote %s", filepath)

        # Create PR
        pr_title = f"feat: {bounty['title']} (Bounty #{num})"
        pr_body = (
            f"Closes #{num}\n\n"
            f"## Bounty #{num} — {bounty['reward']} RTC\n\n"
            f"### Changes\n{implementation.get('summary', 'See files.')}\n\n"
            f"---\n_Automated by Bounty Hunter Agent_"
        )
        head = f"{self.github_username}:{branch_name}"
        try:
            pr = self.gh.create_pr(
                self.target_owner, self.target_repo,
                pr_title, pr_body, head
            )
            logger.info("PR created: %s", pr.get("html_url", "N/A"))
            state["completed"].append(num)
            self._save_state(state)
            return pr.get("html_url")
        except Exception as exc:
            logger.error("PR creation failed: %s", exc)
            return None

    # ── Main loop ────────────────────────────────────────────────────────
    def run(self, labels: Optional[List[str]] = None,
            min_reward: float = 10, max_bounties: int = 5,
            auto: bool = False) -> List[Dict]:
        """Main entry point: scan, evaluate, optionally claim."""
        bounties = self.scan_bounties(labels=labels, min_reward=min_reward)
        results = []

        for bounty in bounties[:max_bounties]:
            assessment = self.evaluate_bounty(bounty)
            result = {
                "bounty": bounty,
                "assessment": assessment,
            }

            if auto and assessment.get("feasible", False):
                pr_url = self.claim_bounty(bounty, assessment)
                result["pr_url"] = pr_url

            results.append(result)

        return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="RustChain Bounty Hunter Agent")
    parser.add_argument("--scan", action="store_true", help="Scan for bounties only")
    parser.add_argument("--auto", action="store_true", help="Fully autonomous mode")
    parser.add_argument("--min-reward", type=float, default=10, help="Min RTC reward")
    parser.add_argument("--max-bounties", type=int, default=5, help="Max bounties to process")
    parser.add_argument("--labels", nargs="*", help="Filter by labels")
    parser.add_argument("--work-dir", default="/tmp/bounty-hunter-work")
    args = parser.parse_args()

    agent = BountyHunterAgent(work_dir=args.work_dir)

    if args.scan:
        bounties = agent.scan_bounties(labels=args.labels, min_reward=args.min_reward)
        for b in bounties:
            print(f"  #{b['number']:>5}  [{b['reward']:>5.0f} RTC]  {b['title']}")
        return

    results = agent.run(
        labels=args.labels,
        min_reward=args.min_reward,
        max_bounties=args.max_bounties,
        auto=args.auto,
    )

    for r in results:
        b = r["bounty"]
        a = r["assessment"]
        print(f"\n{'='*60}")
        print(f"Bounty #{b['number']}: {b['title']} ({b['reward']} RTC)")
        print(f"  Difficulty: {a.get('difficulty', 'N/A')}")
        print(f"  Time estimate: {a.get('time_estimate', 'N/A')}")
        print(f"  Feasible: {a.get('feasible', False)}")
        if "pr_url" in r:
            print(f"  PR: {r['pr_url']}")


if __name__ == "__main__":
    main()
