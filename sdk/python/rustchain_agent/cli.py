"""
CLI Tool for RustChain RIP-302 Agent Economy (Tier 1 Bounty).
Allows posting, claiming, delivering, inspecting, and managing jobs directly from the terminal.
"""

import argparse
import json
import os
import sys
from typing import List, Optional

from .client import RustChainAgentClient, compute_deliverable_hash
from .exceptions import AgentEconomyError
from .matching import AutoMatcher
from .models import JobCategory, JobStatus


def format_json(data: dict) -> str:
    return json.dumps(data, indent=2)


def main(args: Optional[List[str]] = None):
    parser = argparse.ArgumentParser(
        prog="rustchain-agent",
        description="RustChain RIP-302 Agent Economy Command-Line Interface",
    )
    parser.add_argument(
        "--node-url",
        default=os.environ.get("RUSTCHAIN_NODE_URL", RustChainAgentClient.DEFAULT_BASE_URL),
        help="RustChain node URL (default: https://rustchain.org or $RUSTCHAIN_NODE_URL)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON response",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # POST
    p_post = subparsers.add_parser("post", help="Post a new job and lock escrow")
    p_post.add_argument("--poster", required=True, help="Poster wallet name or address")
    p_post.add_argument("--title", required=True, help="Job title (min 5 chars)")
    p_post.add_argument("--description", required=True, help="Full job description (min 20 chars)")
    p_post.add_argument(
        "--category",
        choices=JobCategory.values(),
        default="other",
        help="Job category",
    )
    p_post.add_argument("--reward", type=float, required=True, help="RTC reward (e.g. 5.0)")
    p_post.add_argument("--ttl-hours", type=int, default=168, help="TTL in hours (default: 168 = 7 days)")
    p_post.add_argument("--tags", nargs="*", default=[], help="Optional search tags")

    # LIST
    p_list = subparsers.add_parser("list", help="Browse marketplace jobs")
    p_list.add_argument("--category", choices=JobCategory.values(), help="Filter by category")
    p_list.add_argument("--status", default="open", help="Filter by status (default: open)")
    p_list.add_argument("--min-reward", type=float, default=0.0, help="Minimum reward in RTC")
    p_list.add_argument("--limit", type=int, default=20, help="Number of results (max 100)")
    p_list.add_argument("--offset", type=int, default=0, help="Pagination offset")

    # SHOW / GET
    p_show = subparsers.add_parser("show", help="View job details and audit trail")
    p_show.add_argument("job_id", help="Job ID to inspect")

    # CLAIM
    p_claim = subparsers.add_parser("claim", help="Claim an open job")
    p_claim.add_argument("job_id", help="Job ID to claim")
    p_claim.add_argument("--worker", required=True, help="Worker wallet name")

    # DELIVER
    p_deliv = subparsers.add_parser("deliver", help="Submit deliverable for a claimed job")
    p_deliv.add_argument("job_id", help="Job ID")
    p_deliv.add_argument("--worker", required=True, help="Assigned worker wallet")
    p_deliv.add_argument("--url", help="Deliverable URL (PR, repository, article, file)")
    p_deliv.add_argument("--file", help="Local file path (auto-computes SHA-256 deliverable hash)")
    p_deliv.add_argument("--hash", help="Explicit SHA-256 deliverable hash")
    p_deliv.add_argument("--summary", help="Summary of work performed")

    # ACCEPT
    p_acc = subparsers.add_parser("accept", help="Accept delivery and release escrow")
    p_acc.add_argument("job_id", help="Job ID")
    p_acc.add_argument("--poster", required=True, help="Poster wallet name")
    p_acc.add_argument("--rating", type=int, choices=[1, 2, 3, 4, 5], help="Optional rating (1-5 stars)")

    # DISPUTE
    p_disp = subparsers.add_parser("dispute", help="Dispute a delivered job")
    p_disp.add_argument("job_id", help="Job ID")
    p_disp.add_argument("--poster", required=True, help="Poster wallet name")
    p_disp.add_argument("--reason", required=True, help="Rejection rationale")

    # CANCEL
    p_canc = subparsers.add_parser("cancel", help="Cancel open/disputed job and refund escrow")
    p_canc.add_argument("job_id", help="Job ID")
    p_canc.add_argument("--poster", required=True, help="Poster wallet name")

    # REPUTATION
    p_rep = subparsers.add_parser("reputation", help="Query agent trust score and history")
    p_rep.add_argument("wallet_id", help="Agent wallet address or name")

    # STATS
    subparsers.add_parser("stats", help="Show marketplace overview and statistics")

    # MATCH
    p_match = subparsers.add_parser("match", help="Match candidate workers for a job")
    p_match.add_argument("job_id", help="Job ID")
    p_match.add_argument("--candidates", nargs="+", required=True, help="Candidate worker wallet IDs")

    parsed = parser.parse_args(args)

    if not parsed.command:
        parser.print_help()
        sys.exit(1)

    client = RustChainAgentClient(base_url=parsed.node_url)

    try:
        if parsed.command == "post":
            ttl_sec = parsed.ttl_hours * 3600
            res = client.post_job(
                poster_wallet=parsed.poster,
                title=parsed.title,
                description=parsed.description,
                category=parsed.category,
                reward_rtc=parsed.reward,
                ttl_seconds=ttl_sec,
                tags=parsed.tags,
            )
            if parsed.json:
                print(format_json(res))
            else:
                print("✅ Job Successfully Posted!")
                print(f"  Job ID:       {res.get('job_id')}")
                print(f"  Status:       {res.get('status')}")
                print(f"  Reward:       {res.get('reward_rtc')} RTC")
                print(f"  Platform Fee: {res.get('platform_fee_rtc')} RTC")
                print(f"  Total Escrow: {res.get('escrow_total_rtc')} RTC")
                print(f"  Expires In:   {res.get('expires_in_hours')} hours")

        elif parsed.command == "list":
            res = client.list_jobs(
                category=parsed.category,
                status=parsed.status,
                min_reward=parsed.min_reward,
                limit=parsed.limit,
                offset=parsed.offset,
            )
            if parsed.json:
                print(format_json(res))
            else:
                jobs = res.get("jobs", [])
                print(f"=== RustChain Agent Jobs ({len(jobs)} / {res.get('total', 0)}) ===")
                for j in jobs:
                    worker_info = f" | Worker: {j.get('worker_wallet')}" if j.get("worker_wallet") else ""
                    print(f"• [{j.get('job_id')}] ({j.get('category')}) - {j.get('reward_rtc')} RTC [{j.get('status')}]{worker_info}")
                    print(f"  Title: {j.get('title')}")
                    print(f"  Poster: {j.get('poster_wallet')}")
                    print("-" * 60)

        elif parsed.command == "show":
            job = client.get_job(parsed.job_id)
            if parsed.json:
                print(format_json(job.to_dict()))
            else:
                print(f"=== Job Details: {job.job_id} ===")
                print(f"  Title:        {job.title}")
                print(f"  Description:  {job.description}")
                print(f"  Category:     {job.category}")
                print(f"  Reward:       {job.reward_rtc} RTC (Escrow: {job.escrow_total_rtc} RTC)")
                print(f"  Status:       {job.status}")
                print(f"  Poster:       {job.poster_wallet}")
                print(f"  Worker:       {job.worker_wallet or '(unassigned)'}")
                if job.deliverable_url:
                    print(f"  Deliverable:  {job.deliverable_url}")
                if job.deliverable_hash:
                    print(f"  SHA-256 Hash: {job.deliverable_hash}")
                if job.result_summary:
                    print(f"  Summary:      {job.result_summary}")
                if job.rejection_reason:
                    print(f"  Dispute Note: {job.rejection_reason}")
                if job.activity_log:
                    print("\n  Activity Log:")
                    for entry in job.activity_log:
                        print(f"    - [{entry.action}] by {entry.actor_wallet or 'system'}: {entry.details or ''}")

        elif parsed.command == "claim":
            res = client.claim_job(parsed.job_id, parsed.worker)
            if parsed.json:
                print(format_json(res))
            else:
                print(f"✅ Job {parsed.job_id} claimed by {parsed.worker}!")
                print(f"  Reward: {res.get('reward_rtc')} RTC")

        elif parsed.command == "deliver":
            deliv_hash = parsed.hash
            if parsed.file and os.path.exists(parsed.file):
                with open(parsed.file, "rb") as f:
                    deliv_hash = compute_deliverable_hash(f.read())

            res = client.deliver_job(
                job_id=parsed.job_id,
                worker_wallet=parsed.worker,
                deliverable_url=parsed.url,
                deliverable_hash=deliv_hash,
                result_summary=parsed.summary,
            )
            if parsed.json:
                print(format_json(res))
            else:
                print(f"✅ Deliverable submitted for job {parsed.job_id}!")
                if deliv_hash:
                    print(f"  SHA-256 Deliverable Hash: {deliv_hash}")

        elif parsed.command == "accept":
            res = client.accept_delivery(
                job_id=parsed.job_id,
                poster_wallet=parsed.poster,
                rating=parsed.rating,
            )
            if parsed.json:
                print(format_json(res))
            else:
                print(f"✅ Delivery accepted for job {parsed.job_id}!")
                print(f"  Worker {res.get('worker_wallet')} paid {res.get('reward_paid_rtc')} RTC.")
                print(f"  Platform fee: {res.get('platform_fee_rtc')} RTC.")

        elif parsed.command == "dispute":
            res = client.dispute_job(
                job_id=parsed.job_id,
                poster_wallet=parsed.poster,
                reason=parsed.reason,
            )
            if parsed.json:
                print(format_json(res))
            else:
                print(f"⚠️ Job {parsed.job_id} disputed.")
                print(f"  Reason: {parsed.reason}")

        elif parsed.command == "cancel":
            res = client.cancel_job(parsed.job_id, parsed.poster)
            if parsed.json:
                print(format_json(res))
            else:
                print(f"✅ Job {parsed.job_id} cancelled.")
                print(f"  Escrow refunded: {res.get('refunded_rtc')} RTC to {parsed.poster}.")

        elif parsed.command == "reputation":
            rep = client.get_reputation(parsed.wallet_id)
            if parsed.json:
                print(format_json(rep.to_dict()))
            else:
                print(f"=== Agent Reputation: {rep.wallet_id} ===")
                print(f"  Trust Score:   {rep.trust_score}/100 [{rep.trust_level.upper()}]")
                print(f"  Avg Rating:    {rep.avg_rating:.2f}/5.0 ({rep.rating_count} ratings)")
                print(f"  Jobs Posted:   {rep.jobs_posted} (Completed: {rep.jobs_completed_as_poster})")
                print(f"  Jobs Worked:   {rep.jobs_completed_as_worker} (Disputed: {rep.jobs_disputed}, Expired: {rep.jobs_expired})")
                print(f"  Total RTC:     Paid {rep.total_rtc_paid} RTC | Earned {rep.total_rtc_earned} RTC")

        elif parsed.command == "stats":
            stats = client.get_stats()
            if parsed.json:
                print(format_json(stats.to_dict()))
            else:
                print("=== RustChain Agent Economy Stats ===")
                print(f"  Total Jobs:          {stats.total_jobs}")
                print(f"  Open Jobs:           {stats.open_jobs}")
                print(f"  Completed Jobs:      {stats.completed_jobs}")
                print(f"  Total RTC Volume:    {stats.total_rtc_volume} RTC")
                print(f"  Total Fees:          {stats.total_fees_collected} RTC (Fee Rate: {stats.platform_fee_rate})")
                print(f"  Active Agents:       {stats.active_agents}")
                print(f"  Escrow Wallet:       {stats.escrow_wallet} ({stats.escrow_balance_rtc} RTC locked)")
                if stats.categories:
                    print("\n  Top Categories:")
                    for cat in stats.categories:
                        print(f"    • {cat.category}: {cat.jobs} jobs ({cat.total_rtc} RTC)")

        elif parsed.command == "match":
            job = client.get_job(parsed.job_id)
            matcher = AutoMatcher()
            ranked = matcher.rank_candidates_for_job(job, parsed.candidates, client)
            if parsed.json:
                print(format_json([r.to_dict() for r in ranked]))
            else:
                print(f"=== Auto-Match Rankings for Job: {job.job_id} ({job.title}) ===")
                for i, r in enumerate(ranked, 1):
                    print(f"{i}. Worker: {r.worker_wallet} | Match Score: {r.match_score:.1f}/100")
                    print(f"   Trust: {r.trust_score} ({r.trust_level}) | Avg Rating: {r.avg_rating:.1f}")
                    print(f"   Rationale: {r.rationale}")

    except AgentEconomyError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
