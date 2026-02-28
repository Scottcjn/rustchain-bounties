from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import Dict, List, Optional, Sequence, Set


@dataclass(frozen=True)
class RiskConfig:
    # Buckets
    low_max: int = 24
    medium_max: int = 59

    # Account age heuristic
    age_very_new_days: int = 7
    age_new_days: int = 30
    age_very_new_weight: int = 35
    age_new_weight: int = 20

    # Claim velocity heuristic
    velocity_burst_count: int = 3
    velocity_burst_hours: int = 24
    velocity_burst_weight: int = 15
    multi_repo_count: int = 3
    multi_repo_weight: int = 10

    # Text similarity/template reuse
    text_similarity_threshold: float = 0.92
    text_similarity_weight: int = 20

    # Wallet / cross-pattern
    shared_wallet_weight: int = 25
    shared_bottube_weight: int = 20

    # Duplicate proof links
    duplicate_proof_weight: int = 25

    # Optional cadence signal
    cadence_window_minutes: int = 10
    cadence_count: int = 3
    cadence_weight: int = 10


DEFAULT_RISK_CONFIG = RiskConfig()


@dataclass
class ClaimRiskInput:
    user: str
    issue_ref: str
    repo: str
    created_at: str
    body_text: str
    account_age_days: Optional[int]
    wallet: Optional[str]
    bottube_user: Optional[str]
    proof_links: List[str] = field(default_factory=list)
    comment_timestamps: List[str] = field(default_factory=list)


@dataclass
class ClaimRiskResult:
    score: int
    bucket: str
    reasons: List[str]


def _parse_iso(ts: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def _normalize_text(text: str) -> Set[str]:
    text = text.lower()
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = [t for t in text.split() if len(t) > 2]
    return set(tokens)


def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    u = len(a | b)
    if u == 0:
        return 0.0
    return len(a & b) / u


def bucket_for_score(score: int, cfg: RiskConfig = DEFAULT_RISK_CONFIG) -> str:
    if score <= cfg.low_max:
        return "low"
    if score <= cfg.medium_max:
        return "medium"
    return "high"


def score_claims(claims: Sequence[ClaimRiskInput], cfg: RiskConfig = DEFAULT_RISK_CONFIG) -> Dict[str, ClaimRiskResult]:
    # Indexes for cross-claim signals.
    claims_by_user: Dict[str, List[ClaimRiskInput]] = defaultdict(list)
    wallet_to_users: Dict[str, Set[str]] = defaultdict(set)
    bt_to_users: Dict[str, Set[str]] = defaultdict(set)
    proof_to_users: Dict[str, Set[str]] = defaultdict(set)

    token_sets: Dict[str, Set[str]] = {}
    for c in claims:
        key = f"{c.issue_ref}:{c.user}"
        token_sets[key] = _normalize_text(c.body_text or "")
        claims_by_user[c.user].append(c)
        if c.wallet:
            wallet_to_users[c.wallet.lower()].add(c.user)
        if c.bottube_user:
            bt_to_users[c.bottube_user.lower()].add(c.user)
        for link in c.proof_links:
            proof_to_users[link.strip().lower()].add(c.user)

    out: Dict[str, ClaimRiskResult] = {}

    for c in claims:
        score = 0
        reasons: List[str] = []
        key = f"{c.issue_ref}:{c.user}"

        # 1) Account age heuristic
        if c.account_age_days is not None:
            if c.account_age_days < cfg.age_very_new_days:
                score += cfg.age_very_new_weight
                reasons.append(f"ACCOUNT_AGE_VERY_NEW<{cfg.age_very_new_days}d")
            elif c.account_age_days < cfg.age_new_days:
                score += cfg.age_new_weight
                reasons.append(f"ACCOUNT_AGE_NEW<{cfg.age_new_days}d")

        # 2) Claim velocity heuristic
        user_claims = claims_by_user.get(c.user, [])
        if len(user_claims) >= cfg.velocity_burst_count:
            parsed = sorted([p for p in (_parse_iso(x.created_at) for x in user_claims) if p is not None])
            if parsed:
                span_hours = (parsed[-1] - parsed[0]).total_seconds() / 3600.0
                if span_hours <= cfg.velocity_burst_hours:
                    score += cfg.velocity_burst_weight
                    reasons.append(
                        f"CLAIM_BURST_{len(user_claims)}IN{cfg.velocity_burst_hours}H"
                    )

        repo_count = len({x.repo for x in user_claims})
        if repo_count >= cfg.multi_repo_count:
            score += cfg.multi_repo_weight
            reasons.append(f"MULTI_REPO_BURST>={cfg.multi_repo_count}")

        # 3) Text similarity/template reuse heuristic
        my_tokens = token_sets.get(key, set())
        similar_users: Set[str] = set()
        if my_tokens:
            for other in claims:
                if other.user == c.user:
                    continue
                other_key = f"{other.issue_ref}:{other.user}"
                sim = _jaccard(my_tokens, token_sets.get(other_key, set()))
                if sim >= cfg.text_similarity_threshold:
                    similar_users.add(other.user)
            if similar_users:
                score += cfg.text_similarity_weight
                reasons.append(
                    f"TEMPLATE_REUSE_SIM>={cfg.text_similarity_threshold:.2f}:users={len(similar_users)}"
                )

        # 4) Wallet/repo cross-pattern heuristic
        if c.wallet and len(wallet_to_users.get(c.wallet.lower(), set())) > 1:
            score += cfg.shared_wallet_weight
            reasons.append("SHARED_WALLET_ACCOUNTS")
        if c.bottube_user and len(bt_to_users.get(c.bottube_user.lower(), set())) > 1:
            score += cfg.shared_bottube_weight
            reasons.append("SHARED_BOTTUBE_ACCOUNT")

        # 5) Duplicate proof-link heuristic
        duplicate_links = [
            link for link in c.proof_links if len(proof_to_users.get(link.strip().lower(), set())) > 1
        ]
        if duplicate_links:
            score += cfg.duplicate_proof_weight
            reasons.append(f"DUPLICATE_PROOF_LINKS:{len(set(duplicate_links))}")

        # 6) Optional timezone/posting cadence anomaly signal
        # A simple, explainable signal: many comments from same user packed into
        # a very tight time window.
        comment_times = sorted([p for p in (_parse_iso(ts) for ts in c.comment_timestamps) if p is not None])
        if len(comment_times) >= cfg.cadence_count:
            window_secs = cfg.cadence_window_minutes * 60
            hit = False
            for i in range(0, len(comment_times) - cfg.cadence_count + 1):
                if (comment_times[i + cfg.cadence_count - 1] - comment_times[i]).total_seconds() <= window_secs:
                    hit = True
                    break
            if hit:
                score += cfg.cadence_weight
                reasons.append(
                    f"CADENCE_TIGHT_WINDOW_{cfg.cadence_count}IN{cfg.cadence_window_minutes}M"
                )

        out[key] = ClaimRiskResult(score=score, bucket=bucket_for_score(score, cfg), reasons=reasons)

    return out


def top_suspicious(claims: Sequence[ClaimRiskInput], scored: Dict[str, ClaimRiskResult], n: int = 10) -> List[tuple[ClaimRiskInput, ClaimRiskResult]]:
    rows: List[tuple[ClaimRiskInput, ClaimRiskResult]] = []
    for c in claims:
        key = f"{c.issue_ref}:{c.user}"
        rr = scored.get(key)
        if rr is None:
            continue
        rows.append((c, rr))
    rows.sort(key=lambda row: (-row[1].score, row[0].user.lower()))
    return rows[: max(0, n)]
