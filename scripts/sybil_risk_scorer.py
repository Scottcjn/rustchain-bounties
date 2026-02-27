#!/usr/bin/env python3
"""Deterministic Sybil/farming risk scorer for bounty claims."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


@dataclass(frozen=True)
class Policy:
    name: str
    warn_threshold: int
    block_threshold: int


POLICIES = {
    "low": Policy("low", warn_threshold=45, block_threshold=70),
    "medium": Policy("medium", warn_threshold=35, block_threshold=60),
    "high": Policy("high", warn_threshold=25, block_threshold=50),
}


def _days_between(now_iso: str, then_iso: str) -> int:
    now = datetime.fromisoformat(now_iso.replace("Z", "+00:00"))
    then = datetime.fromisoformat(then_iso.replace("Z", "+00:00"))
    return max(0, (now - then).days)


def score_claim(claim: Dict[str, Any], now_iso: str | None = None) -> Dict[str, Any]:
    now_iso = now_iso or datetime.now(timezone.utc).isoformat()
    breakdown: List[Tuple[str, int, str]] = []

    age_days = _days_between(now_iso, claim["account_created_at"])
    if age_days < 7:
        breakdown.append(("account_age", 28, f"new account ({age_days}d)"))
    elif age_days < 30:
        breakdown.append(("account_age", 16, f"young account ({age_days}d)"))
    else:
        breakdown.append(("account_age", 0, f"mature account ({age_days}d)"))

    claims_7d = int(claim.get("claims_last_7d", 0))
    if claims_7d >= 12:
        breakdown.append(("claim_velocity", 24, f"very high velocity ({claims_7d}/7d)"))
    elif claims_7d >= 6:
        breakdown.append(("claim_velocity", 12, f"elevated velocity ({claims_7d}/7d)"))
    else:
        breakdown.append(("claim_velocity", 0, f"normal velocity ({claims_7d}/7d)"))

    overlap = int(claim.get("wallet_overlap_count", 0))
    if overlap >= 3:
        breakdown.append(("wallet_overlap", 22, f"wallet linked to {overlap} accounts"))
    elif overlap >= 1:
        breakdown.append(("wallet_overlap", 10, f"wallet linked to {overlap} account(s)"))
    else:
        breakdown.append(("wallet_overlap", 0, "no overlap"))

    graph_hops = int(claim.get("graph_shared_hops", 0))
    if graph_hops >= 4:
        breakdown.append(("graph_proximity", 14, f"dense graph overlap ({graph_hops})"))
    elif graph_hops >= 2:
        breakdown.append(("graph_proximity", 7, f"moderate graph overlap ({graph_hops})"))
    else:
        breakdown.append(("graph_proximity", 0, "low graph overlap"))

    anomalies = claim.get("behavior_anomalies", [])
    anomaly_points = min(16, 4 * len(anomalies))
    breakdown.append(("behavior_anomalies", anomaly_points, f"{len(anomalies)} anomaly signals"))

    score = min(100, sum(points for _, points, _ in breakdown))
    return {
        "claim_id": claim.get("claim_id"),
        "user": claim.get("user"),
        "score": score,
        "breakdown": [
            {"factor": factor, "points": points, "reason": reason}
            for factor, points, reason in breakdown
        ],
    }


def classify(score: int, policy_name: str = "medium") -> str:
    policy = POLICIES[policy_name]
    if score >= policy.block_threshold:
        return "block"
    if score >= policy.warn_threshold:
        return "review"
    return "allow"


def run(input_path: Path, policy_name: str, now_iso: str | None = None) -> Dict[str, Any]:
    payload = json.loads(input_path.read_text())
    claims = payload.get("claims", [])
    scored = [score_claim(c, now_iso=now_iso) for c in claims]
    for row in scored:
        row["decision"] = classify(row["score"], policy_name=policy_name)
    return {"policy": policy_name, "results": scored}


def main() -> int:
    parser = argparse.ArgumentParser(description="Sybil/farming risk scorer")
    parser.add_argument("--input", required=True, help="JSON input file with claims[]")
    parser.add_argument("--policy", choices=sorted(POLICIES.keys()), default="medium")
    parser.add_argument("--output", help="optional output JSON path")
    args = parser.parse_args()

    report = run(Path(args.input), policy_name=args.policy)
    out = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(out + "\n")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
