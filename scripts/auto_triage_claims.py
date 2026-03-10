#!/usr/bin/env python3
"""Auto-triage community bounty claims and update ledger issue block.

This script is designed for GitHub Actions. It checks claim comments on
configured bounty issues and marks each recent claim as:
- `eligible`
- `needs-action`

It does not queue payouts directly. It generates an audit-friendly report that
maintainers can use to process payments quickly and consistently.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set


DEFAULT_TARGETS = [
    {
        "owner": "Scottcjn",
        "repo": "rustchain-bounties",
        "issue": 87,
        "min_account_age_days": 30,
        "required_stars": ["Rustchain", "bottube"],
        "require_wallet": True,
        "require_bottube_username": False,
        "require_proof_link": False,
        "name": "Community Support",
    },
    {
        "owner": "Scottcjn",
        "repo": "Rustchain",
        "issue": 47,
        "min_account_age_days": 30,
        "required_stars": ["Rustchain"],
        # Bounty allows either a RustChain wallet name OR a BoTTube username.
        # Treat either as a valid payout target.
        "require_wallet": False,
        "require_bottube_username": False,
        "require_payout_target": True,
        "require_proof_link": False,
        "name": "Rustchain Star",
    },
    {
        "owner": "Scottcjn",
        "repo": "bottube",
        "issue": 74,
        "min_account_age_days": 30,
        "required_stars": ["bottube"],
        "require_wallet": False,
        "require_bottube_username": True,
        "require_proof_link": False,
        "name": "BoTTube Star+Join",
    },
    {
        "owner": "Scottcjn",
        "repo": "rustchain-bounties",
        "issue": 103,
        "min_account_age_days": 30,
        "required_stars": [],
        "require_wallet": True,
        "require_bottube_username": True,
        "require_proof_link": True,
        "name": "X + BoTTube Social",
    },
    {
        "owner": "Scottcjn",
        "repo": "rustchain-bounties",
        "issue": 374,
        "min_account_age_days": 30,
        "required_stars": [],
        "require_wallet": True,
        "require_bottube_username": False,
        "require_proof_link": True,
        "name": "First Attest Bonus",
    },
    {
        "owner": "Scottcjn",
        "repo": "rustchain-bounties",
        "issue": 157,
        "min_account_age_days": 30,
        "required_stars": ["beacon-skill"],
        "require_wallet": True,
        "require_bottube_username": False,
        "require_proof_link": True,
        "name": "Beacon Star + Share",
    },
    {
        "owner": "Scottcjn",
        "repo": "rustchain-bounties",
        "issue": 158,
        "min_account_age_days": 30,
        "required_stars": [],
        "require_wallet": True,
        "require_bottube_username": False,
        "require_proof_link": True,
        "name": "Beacon Integration",
    },
    {
        "owner": "Scottcjn",
        "repo": "bottube",
        "issue": 122,
        "min_account_age_days": 30,
        "required_stars": ["bottube"],
        "require_wallet": True,
        "require_bottube_username": False,
        "require_proof_link": True,
        "name": "BoTTube Star + Share Why",
    },
    {
        "owner": "Scottcjn",
        "repo": "rustchain-bounties",
        "issue": 377,
        "min_account_age_days": 30,
        "required_stars": [],
        "require_wallet": True,
        "require_bottube_username": False,
        "require_proof_link": True,
        "name": "Beacon Mechanism Falsification",
    },
    {
        "owner": "Scottcjn",
        "repo": "rustchain-bounties",
        "issue": 1585,
        "min_account_age_days": 30,
        "required_stars": [],
        "require_wallet": True,
        "require_bottube_username": True,
        "require_proof_link": True,
        "funnel_type": "agent_onboarding",
        "name": "Founding Agent Onboarding Loop",
        # Pool cap: 150 RTC total, first-come first-served.
        "pool_rtc": 150,
        # Milestone C must occur within 7 days of Milestone B.
        "milestone_c_deadline_days": 7,
    },
]

MARKER_START = "<!-- auto-triage-report:start -->"
MARKER_END = "<!-- auto-triage-report:end -->"


def _env(name: str, default: Optional[str] = None) -> str:
    value = os.environ.get(name, default)
    if value is None:
        raise RuntimeError(f"Missing required env: {name}")
    return value


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _gh_request(
    method: str,
    path: str,
    token: str,
    data: Optional[Dict[str, Any]] = None,
) -> Any:
    base = "https://api.github.com"
    url = path if path.startswith("http") else f"{base}{path}"
    payload = None if data is None else json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method=method.upper())
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("User-Agent", "elyan-auto-triage")
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _gh_paginated(path: str, token: str) -> List[Dict[str, Any]]:
    page = 1
    out: List[Dict[str, Any]] = []
    while True:
        sep = "&" if "?" in path else "?"
        p = f"{path}{sep}per_page=100&page={page}"
        chunk = _gh_request("GET", p, token)
        if not isinstance(chunk, list) or not chunk:
            break
        out.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
    return out


def _extract_wallet(body: str) -> Optional[str]:
    # Strip minimal markdown that commonly wraps labels like **RTC Wallet:**,
    # without corrupting valid underscores in wallet names (e.g. abdul_rtc_01).
    body = re.sub(r"[`*]", "", body)

    stop = {"wallet", "address", "miner_id", "please", "thanks", "thankyou"}
    found: Optional[str] = None
    expect_next = False
    for line in body.splitlines():
        s = line.strip()
        if not s:
            continue

        # Handle "Wallet:" on one line and the value on the next.
        if expect_next:
            expect_next = False
            if re.fullmatch(r"[A-Za-z0-9_\-]{4,80}", s) and s.lower() not in stop:
                if re.search(r"[0-9_\-]", s) or s.upper().startswith("RTC") or len(s) >= 6:
                    found = s
                    continue

        # Common non-English label (Chinese): "钱包地址： <wallet>" or value on next line.
        m = re.search(r"钱包(?:地址)?\s*[:：\-]\s*([A-Za-z0-9_\-]{4,80})\b", s)
        if m:
            val = m.group(1).strip()
            if val.lower() not in stop:
                found = val
                continue
        if re.search(r"钱包(?:地址)?\s*[:：\-]\s*$", s):
            expect_next = True
            continue

        # English label with value on next line.
        if re.search(r"(?i)\b(?:rtc\s*)?(?:wallet|miner[_\-\s]?id|address)\b.*[:：\-]\s*$", s):
            expect_next = True
            continue

        # English label + value on same line (also allows "Payout target miner_id: X").
        m = re.search(
            r"(?i)\b(?:payout\s*target\s*)?"
            r"(?:rtc\s*)?"
            r"(wallet|miner[_\-\s]?id|address)\s*"
            r"(?:\((?:miner_?id|id|address)\))?\s*[:：\-]\s*"
            r"([A-Za-z0-9_\-]{4,80})\b",
            s,
        )
        if not m:
            continue
        val = m.group(2).strip()
        if val.lower() in stop:
            continue
        # Heuristic: avoid capturing short plain words after "wallet:".
        if not re.search(r"[0-9_\-]", val) and not val.upper().startswith("RTC") and len(val) < 6:
            continue
        found = val

    return found


def _extract_bottube_user(body: str) -> Optional[str]:
    # Strip minimal markdown without corrupting valid underscores in usernames.
    body = re.sub(r"[`*]", "", body)
    patterns = [
        # Prefer extracting from profile URLs if present.
        r"https?://(?:www\.)?bottube\.ai/@([A-Za-z0-9_-]{2,64})",
        r"https?://(?:www\.)?bottube\.ai/agent/([A-Za-z0-9_-]{2,64})",
        # Explicit label on its own line.
        r"(?im)^\s*bottube(?:\s*(?:username|user|account))?\s*[:：\-]\s*(?!https?\b)([A-Za-z0-9_-]{2,64})\s*$",
    ]
    for pat in patterns:
        matches = list(re.finditer(pat, body))
        if matches:
            return matches[-1].group(1).strip()
    return None


def _has_proof_link(body: str) -> bool:
    return bool(re.search(r"https?://", body))


def _wallet_looks_external(wallet: str) -> bool:
    # Heuristic: very long base58/base62 tokens are usually external chain
    # addresses, not RTC wallet names used in these bounties.
    if re.fullmatch(r"[1-9A-HJ-NP-Za-km-z]{28,64}", wallet):
        return True
    if re.fullmatch(r"[A-Za-z0-9]{30,64}", wallet):
        return True
    return False


def _looks_like_claim(body: str) -> bool:
    text = body.lower()
    tokens = [
        "claim",
        "starred",
        "wallet",
        "proof",
        "bounty",
        "rtc",
        "payout",
        "submission",
        "submit",
        "pr",
        "pull request",
        "demo",
    ]
    return any(t in text for t in tokens)


def _extract_sponsor_ref(body: str) -> Optional[str]:
    """Extract the sponsor GitHub username from 'sponsored by @username'."""
    body = re.sub(r"[`*]", "", body)
    patterns = [
        r"(?i)sponsor(?:ed)?\s+by\s+@([A-Za-z0-9_-]{1,39})",
        r"(?i)referr?(?:ed|er|al)\s*(?:by)?\s*[:：\-]?\s*@([A-Za-z0-9_-]{1,39})",
    ]
    for pat in patterns:
        m = re.search(pat, body)
        if m:
            return m.group(1).strip()
    return None


def _extract_video_url(body: str) -> Optional[str]:
    """Extract a BoTTube video URL from the body text."""
    body = re.sub(r"[`*]", "", body)
    patterns = [
        # BoTTube video URLs.
        r"(https?://(?:www\.)?bottube\.ai/(?:watch|video|v)/[A-Za-z0-9_\-]+)",
        r"(https?://(?:www\.)?bottube\.ai/@[A-Za-z0-9_\-]+/[A-Za-z0-9_\-]+)",
    ]
    for pat in patterns:
        m = re.search(pat, body)
        if m:
            return m.group(1)
    return None


def _has_agent_identity_proof(body: str) -> bool:
    """Check for public proof of agent identity (GitHub repo, project page, etc.)."""
    # Match GitHub repos, Beacon identity, project pages, or BoTTube profiles.
    text = re.sub(r"[`*]", "", body)
    agent_proof_patterns = [
        r"https?://github\.com/[A-Za-z0-9_\-]+/[A-Za-z0-9_\-]+",
        r"https?://(?:www\.)?bottube\.ai/(?:@|agent/)[A-Za-z0-9_\-]+",
        r"(?i)\bbeacon\b.*https?://",
        r"(?i)https?://\S*(?:agent|bot|beacon)",
    ]
    return any(re.search(pat, text) for pat in agent_proof_patterns)


def _looks_like_sponsor_claim(body: str) -> bool:
    """Detect if a comment is a sponsor registering an agent onboarding."""
    text = body.lower()
    sponsor_tokens = ["sponsor", "onboarding", "onboard", "referral", "referring"]
    agent_tokens = ["agent", "bot"]
    has_sponsor = any(t in text for t in sponsor_tokens)
    has_agent = any(t in text for t in agent_tokens)
    return has_sponsor and has_agent


def _looks_like_agent_funnel_claim(body: str) -> bool:
    """Detect if a comment is relevant to the agent onboarding funnel."""
    text = body.lower()
    tokens = [
        "sponsored by",
        "sponsor",
        "agent",
        "milestone",
        "wallet",
        "miner_id",
        "bottube",
        "rtc",
        "claim",
        "onboarding",
        "video",
        "proof",
    ]
    return any(t in text for t in tokens)


def _has_rtc_native_action(body: str) -> bool:
    """Check for proof of RTC-native agent action (Milestone C)."""
    text = body.lower()
    indicators = [
        "rtc earning",
        "rtc tip",
        "rtc transfer",
        "tipped",
        "received rtc",
        "sent rtc",
        "beacon atlas",
        "agent workflow",
    ]
    has_indicator = any(t in text for t in indicators)
    has_link = _has_proof_link(body)
    return has_indicator and has_link


def _distinct_actors(sponsor: str, agent: str) -> bool:
    """Anti-abuse: verify sponsor and agent appear to be distinct actors."""
    if sponsor.lower() == agent.lower():
        return False
    # Flag if one username is a trivial suffix/prefix variant of the other.
    s, a = sponsor.lower(), agent.lower()
    if s.startswith(a) or a.startswith(s):
        if abs(len(s) - len(a)) <= 3:
            return False
    return True


def _status_label(blockers: List[str]) -> str:
    return "eligible" if not blockers else "needs-action"


@dataclass
class AgentFunnelPair:
    """Tracks a sponsor + agent pair through milestones A/B/C."""
    sponsor: str
    agent: str
    sponsor_wallet: Optional[str]
    agent_wallet: Optional[str]
    bottube_user: Optional[str]
    sponsor_comment_url: str
    agent_comment_url: str
    milestone_a_blockers: List[str]
    milestone_b_blockers: List[str]
    milestone_c_blockers: List[str]
    milestone_b_timestamp: Optional[str]

    @property
    def milestone_a_status(self) -> str:
        return _status_label(self.milestone_a_blockers)

    @property
    def milestone_b_status(self) -> str:
        return _status_label(self.milestone_b_blockers)

    @property
    def milestone_c_status(self) -> str:
        return _status_label(self.milestone_c_blockers)

    @property
    def fully_activated(self) -> bool:
        return (
            not self.milestone_a_blockers
            and not self.milestone_b_blockers
            and not self.milestone_c_blockers
        )


@dataclass
class ClaimResult:
    user: str
    issue_ref: str
    comment_url: str
    created_at: str
    account_age_days: Optional[int]
    wallet: Optional[str]
    bottube_user: Optional[str]
    blockers: List[str]

    @property
    def status(self) -> str:
        return _status_label(self.blockers)


def _build_funnel_report_section(
    issue_ref: str,
    pairs: List[AgentFunnelPair],
) -> List[str]:
    """Build the report section for agent onboarding funnel results."""
    lines: List[str] = []
    lines.append(f"#### {issue_ref} (Agent Onboarding Funnel)")
    if not pairs:
        lines.append("_No agent onboarding pairs found._")
        lines.append("")
        return lines

    lines.append(
        "| Sponsor | Agent | Sponsor Wallet | Agent Wallet | BoTTube | "
        "A | B | C | Blockers |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for p in pairs:
        sw = p.sponsor_wallet or ""
        aw = p.agent_wallet or ""
        bt = p.bottube_user or ""
        all_blockers = (
            p.milestone_a_blockers + p.milestone_b_blockers + p.milestone_c_blockers
        )
        blockers_str = ", ".join(all_blockers) if all_blockers else ""
        lines.append(
            f"| @{p.sponsor} | @{p.agent} | `{sw}` | `{aw}` | `{bt}` | "
            f"`{p.milestone_a_status}` | `{p.milestone_b_status}` | "
            f"`{p.milestone_c_status}` | {blockers_str} |"
        )

    # Compounding sponsor bonus summary.
    sponsor_counts: Dict[str, int] = {}
    for p in pairs:
        if p.fully_activated:
            sponsor_counts[p.sponsor] = sponsor_counts.get(p.sponsor, 0) + 1
    if sponsor_counts:
        lines.append("")
        lines.append("**Sponsor Bonus Status:**")
        for sponsor, count in sorted(sponsor_counts.items()):
            bonus_rtc = 0
            if count >= 10:
                bonus_rtc = 18  # 3 + 5 + 10
            elif count >= 5:
                bonus_rtc = 8  # 3 + 5
            elif count >= 3:
                bonus_rtc = 3
            if bonus_rtc > 0:
                lines.append(
                    f"- @{sponsor}: {count} fully activated → +{bonus_rtc} RTC bonus"
                )
    lines.append("")
    return lines


def _build_report_md(
    generated_at: str,
    results_by_issue: Dict[str, List[ClaimResult]],
    since_hours: int,
    funnel_results_by_issue: Optional[Dict[str, List[AgentFunnelPair]]] = None,
) -> str:
    lines: List[str] = []
    lines.append(f"### Auto-Triage Report ({generated_at})")
    lines.append(f"Window: last `{since_hours}`h")
    lines.append("")
    for issue_ref, rows in results_by_issue.items():
        lines.append(f"#### {issue_ref}")
        if not rows:
            lines.append("_No recent claim comments._")
            lines.append("")
            continue
        lines.append(
            "| User | Status | Age(d) | Wallet | BoTTube | Blockers | Comment |"
        )
        lines.append("|---|---|---:|---|---|---|---|")
        for r in rows:
            age = "" if r.account_age_days is None else str(r.account_age_days)
            wallet = r.wallet or ""
            bt = r.bottube_user or ""
            blockers = ", ".join(r.blockers) if r.blockers else ""
            lines.append(
                f"| @{r.user} | `{r.status}` | {age} | `{wallet}` | `{bt}` | {blockers} | [link]({r.comment_url}) |"
            )
        lines.append("")

    if funnel_results_by_issue:
        for issue_ref, pairs in funnel_results_by_issue.items():
            lines.extend(_build_funnel_report_section(issue_ref, pairs))

    return "\n".join(lines).strip()


def _ignored_users() -> Set[str]:
    # Ignore maintainers/bots so their informational comments don't become
    # "claims" (which would pollute triage results).
    ignored = {"scottcjn", "github-actions[bot]", "sophiaeagent-beep"}
    extra = os.environ.get("TRIAGE_IGNORE_USERS", "").strip()
    if extra:
        for u in extra.split(","):
            u = u.strip().lower()
            if u:
                ignored.add(u)
    return ignored


def _triage_agent_funnel(
    comments: List[Dict[str, Any]],
    issue_ref: str,
    min_age: int,
    milestone_c_deadline_days: int,
    cutoff: datetime,
    ignored_users: Set[str],
    user_cache: Dict[str, Dict[str, Any]],
    token: str,
) -> List[AgentFunnelPair]:
    """Triage comments on an agent onboarding funnel issue into pairs.

    Builds sponsor+agent pairs and validates milestones A, B, C per pair.

    Claim flow (from the issue):
    - Step 1: Sponsor comments with wallet + note about onboarding an agent.
    - Step 2: Agent comments with "sponsored by @SPONSOR", wallet, BoTTube
      profile, and proof of agent identity.
    - Step 3: Either side comments with milestone B (video) / C (RTC action).
    """
    # Collect all relevant comments per user (no cutoff for funnel — we need
    # full history to build pairs and track milestones across time).
    per_user: Dict[str, Dict[str, Any]] = {}
    for c in comments:
        user = (c.get("user") or {}).get("login")
        if not user:
            continue
        if user.lower() in ignored_users:
            continue
        created = c.get("created_at")
        if not created:
            continue

        body = c.get("body") or ""
        if not _looks_like_agent_funnel_claim(body):
            continue

        if user not in per_user:
            per_user[user] = {
                "bodies": [],
                "timestamps": [],
                "latest_url": c.get("html_url") or "",
            }
        per_user[user]["bodies"].append(body)
        per_user[user]["timestamps"].append(created)
        per_user[user]["latest_url"] = c.get("html_url") or ""

    # Identify sponsors: users whose comments indicate they are onboarding
    # an agent, and who have a wallet.
    sponsors: Dict[str, Dict[str, Any]] = {}
    for user, info in per_user.items():
        merged = "\n\n".join(info["bodies"])
        if _looks_like_sponsor_claim(merged):
            wallet = _extract_wallet(merged)
            sponsors[user] = {
                "wallet": wallet,
                "url": info["latest_url"],
            }

    # Identify agents: users who reference a sponsor via "sponsored by @X".
    # An agent may also be posted by the sponsor on behalf of the agent.
    agent_claims: Dict[str, Dict[str, Any]] = {}
    for user, info in per_user.items():
        merged = "\n\n".join(info["bodies"])
        sponsor_ref = _extract_sponsor_ref(merged)
        if sponsor_ref:
            wallet = _extract_wallet(merged)
            bottube_user = _extract_bottube_user(merged)
            agent_claims[user] = {
                "sponsor": sponsor_ref,
                "wallet": wallet,
                "bottube_user": bottube_user,
                "merged_body": merged,
                "timestamps": info["timestamps"],
                "url": info["latest_url"],
            }

    # Build pairs.  One sponsor per agent (anti-abuse).
    seen_agents: Set[str] = set()
    pairs: List[AgentFunnelPair] = []
    for agent_user, claim in agent_claims.items():
        if agent_user.lower() in seen_agents:
            continue
        seen_agents.add(agent_user.lower())

        sponsor_user = claim["sponsor"]
        sponsor_info = sponsors.get(sponsor_user, {})
        sponsor_wallet = sponsor_info.get("wallet")
        sponsor_url = sponsor_info.get("url", "")

        merged_body = claim["merged_body"]
        agent_wallet = claim["wallet"]
        bottube_user = claim["bottube_user"]

        # --- Resolve user ages ---
        for u in (sponsor_user, agent_user):
            if u not in user_cache:
                try:
                    udata = _gh_request("GET", f"/users/{u}", token)
                    created_at = udata.get("created_at")
                    age_days = None
                    if created_at:
                        age_days = (_now_utc() - _parse_iso(created_at)).days
                    user_cache[u] = {"age_days": age_days}
                except urllib.error.HTTPError:
                    user_cache[u] = {"age_days": None}

        # --- Milestone A: Agent Identity + Profile ---
        a_blockers: List[str] = []
        agent_age = user_cache.get(agent_user, {}).get("age_days")
        sponsor_age = user_cache.get(sponsor_user, {}).get("age_days")

        if sponsor_age is not None and sponsor_age < min_age:
            a_blockers.append(f"sponsor_account_age<{min_age}")
        if sponsor_user not in sponsors:
            a_blockers.append("sponsor_not_registered")
        if not sponsor_wallet:
            a_blockers.append("sponsor_missing_wallet")
        if not agent_wallet:
            a_blockers.append("agent_missing_wallet")
        if agent_wallet and _wallet_looks_external(agent_wallet):
            a_blockers.append("agent_wallet_external_format")
        if sponsor_wallet and _wallet_looks_external(sponsor_wallet):
            a_blockers.append("sponsor_wallet_external_format")
        if not bottube_user:
            a_blockers.append("agent_missing_bottube_profile")
        if not _has_agent_identity_proof(merged_body):
            a_blockers.append("agent_missing_identity_proof")
        if not _distinct_actors(sponsor_user, agent_user):
            a_blockers.append("sponsor_agent_not_distinct")

        # --- Milestone B: First Agent Content (video) ---
        # Check all comments from both sponsor and agent for video evidence.
        all_bodies = list(claim.get("merged_body", "").splitlines())
        sponsor_bodies = sponsors.get(sponsor_user, {})
        combined_for_video = merged_body
        if sponsor_user in per_user:
            combined_for_video += "\n\n" + "\n\n".join(
                per_user[sponsor_user]["bodies"]
            )

        b_blockers: List[str] = []
        video_url = _extract_video_url(combined_for_video)
        if not video_url:
            b_blockers.append("missing_agent_video")

        # Track when milestone B evidence appeared for deadline calculation.
        milestone_b_ts: Optional[str] = None
        if video_url:
            # Use the latest timestamp from agent comments as milestone B date.
            if claim["timestamps"]:
                milestone_b_ts = max(claim["timestamps"])

        # --- Milestone C: First RTC-Native Agent Action ---
        c_blockers: List[str] = []
        if not _has_rtc_native_action(combined_for_video):
            c_blockers.append("missing_rtc_native_action")

        # Check 7-day deadline from milestone B.
        if not c_blockers and milestone_b_ts and claim["timestamps"]:
            b_dt = _parse_iso(milestone_b_ts)
            latest_ts = max(claim["timestamps"])
            latest_dt = _parse_iso(latest_ts)
            deadline = b_dt + timedelta(days=milestone_c_deadline_days)
            if latest_dt > deadline:
                c_blockers.append(
                    f"milestone_c_after_deadline({milestone_c_deadline_days}d)"
                )

        # Milestone B must pass before C can be eligible.
        if b_blockers:
            if not c_blockers:
                c_blockers.append("milestone_b_incomplete")

        # Milestone A must pass before B can be eligible.
        if a_blockers:
            if not b_blockers:
                b_blockers.append("milestone_a_incomplete")
            if not c_blockers:
                c_blockers.append("milestone_a_incomplete")

        pairs.append(
            AgentFunnelPair(
                sponsor=sponsor_user,
                agent=agent_user,
                sponsor_wallet=sponsor_wallet,
                agent_wallet=agent_wallet,
                bottube_user=bottube_user,
                sponsor_comment_url=sponsor_url,
                agent_comment_url=claim["url"],
                milestone_a_blockers=a_blockers,
                milestone_b_blockers=b_blockers,
                milestone_c_blockers=c_blockers,
                milestone_b_timestamp=milestone_b_ts,
            )
        )

    # Deterministic ordering: eligible pairs first, then by agent username.
    pairs.sort(
        key=lambda p: (not p.fully_activated, p.agent.lower()),
    )
    return pairs


def main() -> int:
    token = _env("GITHUB_TOKEN")
    since_hours = int(_env("SINCE_HOURS", "72"))
    ignored_users = _ignored_users()
    targets_json = os.environ.get("TRIAGE_TARGETS_JSON", "").strip()
    if targets_json:
        targets = json.loads(targets_json)
    else:
        targets = DEFAULT_TARGETS

    # Build star cache only for repos we need.
    required_star_repos: Set[str] = set()
    for t in targets:
        for repo in t.get("required_stars", []):
            required_star_repos.add(repo)

    star_cache: Dict[str, Set[str]] = {}
    for repo in sorted(required_star_repos):
        users = _gh_paginated(f"/repos/Scottcjn/{repo}/stargazers", token)
        star_cache[repo] = {u.get("login") for u in users if u.get("login")}

    user_cache: Dict[str, Dict[str, Any]] = {}
    cutoff = _now_utc() - timedelta(hours=since_hours)

    results_by_issue: Dict[str, List[ClaimResult]] = {}
    funnel_results_by_issue: Dict[str, List[AgentFunnelPair]] = {}

    for target in targets:
        owner = target["owner"]
        repo = target["repo"]
        issue = int(target["issue"])
        min_age = int(target.get("min_account_age_days", 0))
        funnel_type = target.get("funnel_type")

        issue_ref = f"{owner}/{repo}#{issue}"
        issue_obj = _gh_request("GET", f"/repos/{owner}/{repo}/issues/{issue}", token)
        comments_url = issue_obj["comments_url"]
        comments = _gh_paginated(comments_url, token)

        if funnel_type == "agent_onboarding":
            pairs = _triage_agent_funnel(
                comments=comments,
                issue_ref=issue_ref,
                min_age=min_age,
                milestone_c_deadline_days=int(
                    target.get("milestone_c_deadline_days", 7)
                ),
                cutoff=cutoff,
                ignored_users=ignored_users,
                user_cache=user_cache,
                token=token,
            )
            funnel_results_by_issue[issue_ref] = pairs
            continue

        req_wallet = bool(target.get("require_wallet", True))
        req_bt = bool(target.get("require_bottube_username", False))
        req_payout_target = bool(target.get("require_payout_target", False))
        req_proof = bool(target.get("require_proof_link", False))
        req_stars = list(target.get("required_stars", []))

        # Merge multi-comment claims per user (users often add follow-ups).
        per_user: Dict[str, Dict[str, Any]] = {}
        for c in comments:
            user = (c.get("user") or {}).get("login")
            if not user:
                continue
            # Ignore maintainer/system messages
            if user.lower() in ignored_users:
                continue
            created = c.get("created_at")
            if not created:
                continue
            created_dt = _parse_iso(created)
            if created_dt < cutoff:
                continue

            body = c.get("body") or ""
            if not _looks_like_claim(body):
                continue

            if user not in per_user:
                per_user[user] = {
                    "bodies": [],
                    "latest_created": created,
                    "latest_url": c.get("html_url") or "",
                }
            per_user[user]["bodies"].append(body)
            if _parse_iso(per_user[user]["latest_created"]) <= created_dt:
                per_user[user]["latest_created"] = created
                per_user[user]["latest_url"] = c.get("html_url") or ""

        rows: List[ClaimResult] = []
        for user, info in per_user.items():
            if user not in user_cache:
                try:
                    u = _gh_request("GET", f"/users/{user}", token)
                    created_at = u.get("created_at")
                    age_days = None
                    if created_at:
                        age_days = (_now_utc() - _parse_iso(created_at)).days
                    user_cache[user] = {"age_days": age_days}
                except urllib.error.HTTPError:
                    user_cache[user] = {"age_days": None}

            age_days = user_cache[user]["age_days"]
            merged_body = "\n\n".join(info["bodies"])
            wallet = _extract_wallet(merged_body)
            bottube_user = _extract_bottube_user(merged_body)
            blockers: List[str] = []

            if age_days is not None and age_days < min_age:
                blockers.append(f"account_age<{min_age}")
            if req_payout_target:
                if not wallet and not bottube_user:
                    blockers.append("missing_payout_target")
            else:
                if req_wallet and not wallet:
                    blockers.append("missing_wallet")
            if wallet and _wallet_looks_external(wallet):
                blockers.append("wallet_external_format")
            if req_bt and not bottube_user:
                blockers.append("missing_bottube_username")
            if req_proof and not _has_proof_link(merged_body):
                blockers.append("missing_proof_link")

            for star_repo in req_stars:
                if user not in star_cache.get(star_repo, set()):
                    blockers.append(f"missing_star:{star_repo}")

            rows.append(
                ClaimResult(
                    user=user,
                    issue_ref=issue_ref,
                    comment_url=info["latest_url"],
                    created_at=info["latest_created"],
                    account_age_days=age_days,
                    wallet=wallet,
                    bottube_user=bottube_user,
                    blockers=blockers,
                )
            )

        # Deterministic ordering
        rows.sort(key=lambda r: (r.status != "eligible", r.user.lower()))
        results_by_issue[issue_ref] = rows

    generated_at = _now_utc().isoformat().replace("+00:00", "Z")
    report = _build_report_md(
        generated_at, results_by_issue, since_hours, funnel_results_by_issue
    )
    print(report)

    ledger_repo = os.environ.get("LEDGER_REPO", "").strip()
    ledger_issue = os.environ.get("LEDGER_ISSUE", "").strip()
    if ledger_repo and ledger_issue:
        issue_path = f"/repos/Scottcjn/{ledger_repo}/issues/{int(ledger_issue)}"
        ledger = _gh_request("GET", issue_path, token)
        body = ledger.get("body") or ""
        new_block = f"{MARKER_START}\n{report}\n{MARKER_END}"
        if MARKER_START in body and MARKER_END in body:
            start = body.index(MARKER_START)
            end = body.index(MARKER_END) + len(MARKER_END)
            updated = f"{body[:start]}{new_block}{body[end:]}"
        else:
            updated = f"{body}\n\n{new_block}\n"
        _gh_request("PATCH", issue_path, token, data={"body": updated})
        print(f"\nUpdated ledger issue: Scottcjn/{ledger_repo}#{ledger_issue}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - runtime safety for actions logs
        print(f"auto-triage failed: {exc}", file=sys.stderr)
        raise
