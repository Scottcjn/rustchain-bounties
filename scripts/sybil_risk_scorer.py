#!/usr/bin/env python3
"""Explainable risk scoring for bounty claim triage."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable, List, Mapping, Optional, Sequence, Tuple
from urllib.parse import urlsplit, urlunsplit

URL_RE = re.compile(r"https?://[^\s<>()\]]+")
TOKEN_RE = re.compile(r"[a-z0-9_]{3,}")
CLAIM_LINE_RE = re.compile(
    r"(?im)^\s*(?:wallet|miner[_\-\s]?id|eta|timezone|github|proof|claimant|applicant)\s*[:：\-].*$"
)
STOP_TOKENS = {
    "claim",
    "claiming",
    "bounty",
    "wallet",
    "miner",
    "issue",
    "github",
    "timezone",
    "proof",
    "ready",
    "start",
    "immediately",
    "implementation",
    "plan",
    "approach",
    "eta",
    "rtc",
}


@dataclass(frozen=True)
class RiskPolicy:
    name: str
    medium_threshold: int
    high_threshold: int
    new_account_days: int = 7
    young_account_days: int = 30
    medium_velocity_claims: int = 2
    high_velocity_claims: int = 4
    medium_repo_spread: int = 2
    high_repo_spread: int = 3
    medium_similarity: float = 0.78
    high_similarity: float = 0.88


POLICIES = {
    "relaxed": RiskPolicy("relaxed", medium_threshold=38, high_threshold=68),
    "balanced": RiskPolicy("balanced", medium_threshold=32, high_threshold=60),
    "strict": RiskPolicy("strict", medium_threshold=25, high_threshold=50),
}


@dataclass(frozen=True)
class ClaimInput:
    claim_id: str
    user: str
    issue_ref: str
    created_at: str
    body: str = ""
    account_age_days: Optional[int] = None
    wallet: Optional[str] = None
    proof_links: Tuple[str, ...] = ()


@dataclass(frozen=True)
class RiskSignal:
    code: str
    points: int
    detail: str


@dataclass(frozen=True)
class RiskResult:
    claim_id: str
    user: str
    issue_ref: str
    score: int
    level: str
    reasons: Tuple[str, ...] = field(default_factory=tuple)
    details: Tuple[RiskSignal, ...] = field(default_factory=tuple)

    def to_dict(self) -> Mapping[str, object]:
        payload = asdict(self)
        payload["reasons"] = list(self.reasons)
        payload["details"] = [asdict(item) for item in self.details]
        return payload


def extract_links(text: str) -> Tuple[str, ...]:
    links = []
    for raw in URL_RE.findall(text or ""):
        url = raw.rstrip(").,;!?")
        parts = urlsplit(url)
        path = parts.path.rstrip("/") or "/"
        cleaned = urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, parts.query, ""))
        links.append(cleaned)
    return tuple(sorted(set(links)))


def _normalize_text(text: str) -> str:
    text = (text or "").lower()
    # We want to detect "template reuse" in claim comments, not similarity in the
    # user-specific fields. Strip URLs/mentions/structured claim lines so two
    # otherwise-identical templates remain comparable.
    text = URL_RE.sub(" ", text)
    text = re.sub(r"@[a-z0-9_-]+", " user ", text)
    text = CLAIM_LINE_RE.sub(" ", text)
    text = re.sub(r"`[^`]*`", " token ", text)
    text = re.sub(r"[^a-z0-9_\s]", " ", text)
    tokens = [tok for tok in TOKEN_RE.findall(text) if tok not in STOP_TOKENS]
    return " ".join(tokens)


def _text_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    # Use two similarity measures:
    # 1) SequenceMatcher ratio: catches near-identical templates.
    # 2) Jaccard overlap: catches re-ordered templates / small edits.
    # Taking max biases toward flagging "same template" even if order changes.
    seq_ratio = SequenceMatcher(None, a, b).ratio()
    a_tokens = set(a.split())
    b_tokens = set(b.split())
    if not a_tokens or not b_tokens:
        token_ratio = 0.0
    else:
        token_ratio = len(a_tokens & b_tokens) / len(a_tokens | b_tokens)
    return max(seq_ratio, token_ratio)


def _repo_from_issue_ref(issue_ref: str) -> str:
    owner_repo, _, _issue = issue_ref.partition("#")
    _owner, _sep, repo = owner_repo.partition("/")
    return repo or owner_repo


def _bucket(score: int, policy: RiskPolicy) -> str:
    if score >= policy.high_threshold:
        return "high"
    if score >= policy.medium_threshold:
        return "medium"
    return "low"


def _coerce_claim(claim: Mapping[str, object]) -> ClaimInput:
    proof_links = claim.get("proof_links") or ()
    if isinstance(proof_links, list):
        proof_tuple = tuple(str(link) for link in proof_links)
    elif isinstance(proof_links, tuple):
        proof_tuple = tuple(str(link) for link in proof_links)
    else:
        proof_tuple = ()
    age_days = claim.get("account_age_days")
    if age_days is not None:
        try:
            age_days = int(age_days)
        except (TypeError, ValueError):
            age_days = None
    wallet = claim.get("wallet")
    return ClaimInput(
        claim_id=str(claim.get("claim_id") or ""),
        user=str(claim.get("user") or ""),
        issue_ref=str(claim.get("issue_ref") or ""),
        created_at=str(claim.get("created_at") or ""),
        body=str(claim.get("body") or ""),
        account_age_days=age_days,
        wallet=(str(wallet).strip() or None) if wallet is not None else None,
        proof_links=proof_tuple,
    )


def score_claims(
    claims: Sequence[ClaimInput | Mapping[str, object]],
    policy_name: str = "balanced",
) -> List[RiskResult]:
    policy = POLICIES[policy_name]
    normalized_claims = [
        claim if isinstance(claim, ClaimInput) else _coerce_claim(claim)
        for claim in claims
    ]

    # Precompute per-user / per-wallet aggregates so a single claim can be scored
    # against the surrounding "claim window" without extra API calls.
    user_claim_counts = {}
    user_repo_counts = {}
    wallet_users = {}
    proof_users = {}
    normalized_text = {}

    for claim in normalized_claims:
        user_claim_counts[claim.user] = user_claim_counts.get(claim.user, 0) + 1
        repos = user_repo_counts.setdefault(claim.user, set())
        repos.add(_repo_from_issue_ref(claim.issue_ref))
        if claim.wallet:
            wallet_users.setdefault(claim.wallet, set()).add(claim.user)
        for link in claim.proof_links:
            proof_users.setdefault(link, set()).add(claim.user)
        normalized_text[claim.claim_id] = _normalize_text(claim.body)

    results: List[RiskResult] = []
    for claim in normalized_claims:
        signals: List[RiskSignal] = []

        age_days = claim.account_age_days
        if age_days is not None:
            if age_days < policy.new_account_days:
                signals.append(RiskSignal("ACCOUNT_AGE", 24, f"account age {age_days}d"))
            elif age_days < policy.young_account_days:
                signals.append(RiskSignal("ACCOUNT_AGE", 12, f"account age {age_days}d"))

        claim_count = user_claim_counts.get(claim.user, 0)
        # Fast claim velocity is a common indicator of "bounty farming" (claiming
        # many issues quickly without doing the work).
        if claim_count >= policy.high_velocity_claims:
            signals.append(RiskSignal("CLAIM_VELOCITY", 18, f"{claim_count} claims in window"))
        elif claim_count >= policy.medium_velocity_claims:
            signals.append(RiskSignal("CLAIM_VELOCITY", 8, f"{claim_count} claims in window"))

        repo_count = len(user_repo_counts.get(claim.user, set()))
        # Spreading claims across many repos is suspicious mainly when combined
        # with high velocity (spray-and-pray pattern).
        if repo_count >= policy.high_repo_spread:
            signals.append(RiskSignal("REPO_SPREAD", 10, f"claims span {repo_count} repos"))
        elif repo_count >= policy.medium_repo_spread and claim_count >= policy.medium_velocity_claims:
            signals.append(RiskSignal("REPO_SPREAD", 5, f"claims span {repo_count} repos"))

        if claim.wallet:
            overlap = len(wallet_users.get(claim.wallet, set()))
            # Multiple accounts claiming with the same payout wallet is a strong
            # sybil / multi-account signal.
            if overlap >= 3:
                signals.append(RiskSignal("WALLET_REUSE", 24, f"wallet reused by {overlap} accounts"))
            elif overlap >= 2:
                signals.append(RiskSignal("WALLET_REUSE", 14, f"wallet reused by {overlap} accounts"))

        duplicate_links = []
        for link in claim.proof_links:
            overlap = len(proof_users.get(link, set()))
            if overlap >= 2:
                duplicate_links.append((link, overlap))
        if duplicate_links:
            # Reused "proof" (same tweet / same starred page / same screenshot link)
            # is a high-signal indicator of low-effort or copied submissions.
            strongest_overlap = max(overlap for _link, overlap in duplicate_links)
            points = 20 if strongest_overlap >= 3 else 12
            signals.append(
                RiskSignal(
                    "PROOF_DUPLICATE",
                    points,
                    f"{len(duplicate_links)} proof link(s) reused across claims",
                )
            )

        best_similarity = 0.0
        best_users: List[str] = []
        same_user_best_similarity = 0.0
        same_user_issue_refs: List[str] = []
        current_text = normalized_text.get(claim.claim_id, "")
        if current_text:
            for other in normalized_claims:
                if other.claim_id == claim.claim_id:
                    continue
                # Compare against other claims to detect shared templates across
                # distinct accounts, and repeated boilerplate by the same user.
                sim = _text_similarity(current_text, normalized_text.get(other.claim_id, ""))
                if other.user == claim.user:
                    if other.issue_ref == claim.issue_ref:
                        continue
                    if sim > same_user_best_similarity + 1e-9:
                        same_user_best_similarity = sim
                        same_user_issue_refs = [other.issue_ref]
                    elif abs(sim - same_user_best_similarity) <= 1e-9 and sim > 0:
                        if other.issue_ref not in same_user_issue_refs:
                            same_user_issue_refs.append(other.issue_ref)
                    continue
                if sim > best_similarity + 1e-9:
                    best_similarity = sim
                    best_users = [other.user]
                elif abs(sim - best_similarity) <= 1e-9 and sim > 0:
                    if other.user not in best_users:
                        best_users.append(other.user)
        if same_user_best_similarity >= policy.high_similarity:
            issue_refs = ", ".join(sorted(same_user_issue_refs)[:2])
            signals.append(
                RiskSignal(
                    "SELF_TEMPLATE_REUSE",
                    12,
                    f"same-user template reuse {same_user_best_similarity:.2f} across {issue_refs}",
                )
            )
        elif same_user_best_similarity >= policy.medium_similarity:
            issue_refs = ", ".join(sorted(same_user_issue_refs)[:2])
            signals.append(
                RiskSignal(
                    "SELF_TEMPLATE_REUSE",
                    6,
                    f"same-user similar claims {same_user_best_similarity:.2f} across {issue_refs}",
                )
            )
        if best_similarity >= policy.high_similarity:
            peers = ", ".join(sorted(best_users)[:2])
            signals.append(
                RiskSignal(
                    "TEXT_SIMILARITY",
                    20,
                    f"template-level similarity {best_similarity:.2f} with {peers}",
                )
            )
        elif best_similarity >= policy.medium_similarity:
            peers = ", ".join(sorted(best_users)[:2])
            signals.append(
                RiskSignal(
                    "TEXT_SIMILARITY",
                    10,
                    f"similar claim text {best_similarity:.2f} with {peers}",
                )
            )

        score = min(100, sum(signal.points for signal in signals))
        level = _bucket(score, policy)
        results.append(
            RiskResult(
                claim_id=claim.claim_id,
                user=claim.user,
                issue_ref=claim.issue_ref,
                score=score,
                level=level,
                reasons=tuple(signal.code for signal in signals),
                details=tuple(signals),
            )
        )

    results.sort(key=lambda item: (-item.score, item.user.lower(), item.issue_ref.lower()))
    return results


def run(input_path: Path, policy_name: str = "balanced") -> Mapping[str, object]:
    payload = json.loads(input_path.read_text())
    claims = payload.get("claims", [])
    results = score_claims(claims, policy_name=policy_name)
    return {
        "policy": policy_name,
        "results": [item.to_dict() for item in results],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Sybil/farming risk scorer")
    parser.add_argument("--input", required=True, help="JSON input file with claims[]")
    parser.add_argument("--policy", choices=sorted(POLICIES.keys()), default="balanced")
    parser.add_argument("--output", help="optional output JSON path")
    args = parser.parse_args()

    report = run(Path(args.input), policy_name=args.policy)
    output = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(output + "\n")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
