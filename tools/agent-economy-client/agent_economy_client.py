"""RIP-302 Agent Economy job marketplace client.

Wraps the RustChain node's agent-to-agent job marketplace API: post jobs,
browse open jobs, claim work, deliver results, and check reputation. Jobs
are paid out in RTC via trustless on-chain escrow.
"""

import argparse
import json
import os
import sys
from typing import Optional

import requests

DEFAULT_TIMEOUT = 15


def normalize_base_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    if "://" not in url:
        url = f"https://{url}"
    scheme, _, rest = url.partition("://")
    host = rest.split("/", 1)[0]
    return f"{scheme}://{host}"


class AgentEconomyClient:
    def __init__(self, node_url: str, admin_key: Optional[str] = None, agent_id: Optional[str] = None):
        self.base_url = normalize_base_url(node_url)
        if not self.base_url:
            raise ValueError("node_url is required")
        self.admin_key = admin_key
        self.agent_id = agent_id

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.admin_key:
            headers["Authorization"] = f"Bearer {self.admin_key}"
        return headers

    def post_job(self, title: str, description: str, budget_rtc: float, deadline_minutes: int = 60) -> dict:
        payload = {
            "title": title,
            "description": description,
            "budget_rtc": budget_rtc,
            "deadline_minutes": deadline_minutes,
        }
        resp = requests.post(f"{self.base_url}/api/jobs", headers=self._headers(), json=payload, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        return resp.json()

    def browse_jobs(self, status: str = "open") -> list:
        resp = requests.get(
            f"{self.base_url}/api/jobs", headers=self._headers(), params={"status": status}, timeout=DEFAULT_TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("jobs", data if isinstance(data, list) else [])

    def claim_job(self, job_id: str) -> dict:
        if not self.agent_id:
            raise ValueError("agent_id is required to claim a job")
        payload = {"agent_id": self.agent_id}
        resp = requests.post(
            f"{self.base_url}/api/jobs/{job_id}/claim", headers=self._headers(), json=payload, timeout=DEFAULT_TIMEOUT
        )
        resp.raise_for_status()
        return resp.json()

    def deliver_job(self, job_id: str, result: str) -> dict:
        if not self.agent_id:
            raise ValueError("agent_id is required to deliver a job")
        payload = {"agent_id": self.agent_id, "result": result}
        resp = requests.post(
            f"{self.base_url}/api/jobs/{job_id}/deliver", headers=self._headers(), json=payload, timeout=DEFAULT_TIMEOUT
        )
        resp.raise_for_status()
        return resp.json()

    def get_job(self, job_id: str) -> dict:
        resp = requests.get(f"{self.base_url}/api/jobs/{job_id}", headers=self._headers(), timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        return resp.json()

    def get_reputation(self, agent_id: Optional[str] = None) -> dict:
        target = agent_id or self.agent_id
        if not target:
            raise ValueError("agent_id is required to fetch reputation")
        resp = requests.get(
            f"{self.base_url}/api/agents/{target}/reputation", headers=self._headers(), timeout=DEFAULT_TIMEOUT
        )
        resp.raise_for_status()
        return resp.json()


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RIP-302 Agent Economy job marketplace client")
    parser.add_argument("--node-url", default=os.environ.get("RTC_NODE_URL", ""), help="RustChain node base URL")
    parser.add_argument("--admin-key", default=os.environ.get("RTC_ADMIN_KEY"), help="Admin/API key")
    parser.add_argument("--agent-id", default=os.environ.get("RTC_AGENT_ID"), help="Acting agent id")

    sub = parser.add_subparsers(dest="command", required=True)

    post = sub.add_parser("post-job", help="Post a new job")
    post.add_argument("--title", required=True)
    post.add_argument("--description", required=True)
    post.add_argument("--budget-rtc", type=float, required=True)
    post.add_argument("--deadline-minutes", type=int, default=60)

    sub.add_parser("browse-jobs", help="List open jobs")

    claim = sub.add_parser("claim-job", help="Claim a job")
    claim.add_argument("job_id")

    deliver = sub.add_parser("deliver-job", help="Deliver results for a claimed job")
    deliver.add_argument("job_id")
    deliver.add_argument("--result", required=True)

    reputation = sub.add_parser("reputation", help="Get an agent's reputation")
    reputation.add_argument("--agent-id", dest="target_agent_id", default=None)

    return parser


def main(argv=None) -> int:
    args = _build_arg_parser().parse_args(argv)
    client = AgentEconomyClient(args.node_url, admin_key=args.admin_key, agent_id=args.agent_id)

    if args.command == "post-job":
        result = client.post_job(args.title, args.description, args.budget_rtc, args.deadline_minutes)
    elif args.command == "browse-jobs":
        result = client.browse_jobs()
    elif args.command == "claim-job":
        result = client.claim_job(args.job_id)
    elif args.command == "deliver-job":
        result = client.deliver_job(args.job_id, args.result)
    elif args.command == "reputation":
        result = client.get_reputation(args.target_agent_id)
    else:
        raise ValueError(f"Unknown command: {args.command}")

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
