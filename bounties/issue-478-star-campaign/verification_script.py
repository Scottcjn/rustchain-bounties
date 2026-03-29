"""Star campaign verification and payout tracking for RustChain bounties."""

import os
import json
import logging
from dataclasses import dataclass, asdict
from typing import Optional

import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"

MAIN_REPO = "Scottcjn/RustChain"

TIER_REPOS = [
    "Scottcjn/RustChain",
    "Scottcjn/rustchain-bounties",
    "Scottcjn/rustchain-node",
    "Scottcjn/rustchain-wallet",
    "Scottcjn/rustchain-explorer",
    "Scottcjn/rustchain-sdk",
]

# All 86 repos — extend this list as needed
ALL_REPOS = TIER_REPOS + [
    # Additional repos would be listed here
]

# Reward tiers
# Tier 1: main repo only              -> 2 RTC total
# Tier 2: main + 5 extra repos        -> 3 RTC per repo (18 RTC total)
# Tier 3: all 86 repos                -> 5 RTC per repo
TIER1_REPOS = {MAIN_REPO}
TIER2_REPOS = set(TIER_REPOS)
TIER3_REPOS = set(ALL_REPOS)

TIER1_REWARD = 2
TIER2_REWARD_PER_REPO = 3
TIER3_REWARD_PER_REPO = 5


@dataclass
class PayoutRecord:
    username: str
    wallet: str
    starred_repos: list
    tier: int
    reward_rtc: float
    verified: bool


def _github_headers(token: Optional[str] = None) -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def get_starred_repos(username: str, token: Optional[str] = None) -> set:
    """Return the set of repos (owner/name) starred by username."""
    starred = set()
    page = 1
    headers = _github_headers(token)
    while True:
        url = f"{GITHUB_API}/users/{username}/starred"
        resp = requests.get(
            url,
            headers=headers,
            params={"per_page": 100, "page": page},
            timeout=15,
        )
        if resp.status_code == 404:
            logger.warning("User not found: %s", username)
            return starred
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        for repo in data:
            starred.add(repo["full_name"])
        if len(data) < 100:
            break
        page += 1
    return starred


def calculate_reward(starred: set) -> tuple[int, float]:
    """Return (tier, reward_rtc) based on starred repos."""
    if TIER3_REPOS and TIER3_REPOS.issubset(starred):
        return 3, len(TIER3_REPOS) * TIER3_REWARD_PER_REPO
    if TIER2_REPOS.issubset(starred):
        return 2, len(TIER2_REPOS) * TIER2_REWARD_PER_REPO
    if MAIN_REPO in starred:
        return 1, TIER1_REWARD
    return 0, 0.0


def verify_claim(username: str, wallet: str, token: Optional[str] = None) -> PayoutRecord:
    """Verify a star campaign claim and return a PayoutRecord."""
    logger.info("Verifying claim for %s", username)
    starred = get_starred_repos(username, token)

    relevant = sorted(
        starred & (TIER3_REPOS if TIER3_REPOS else TIER2_REPOS)
    )
    tier, reward = calculate_reward(starred)
    verified = tier > 0

    record = PayoutRecord(
        username=username,
        wallet=wallet,
        starred_repos=relevant,
        tier=tier,
        reward_rtc=reward,
        verified=verified,
    )
    logger.info(
        "%s -> tier=%d reward=%.1f RTC verified=%s",
        username, tier, reward, verified,
    )
    return record


def process_claims(claims: list[dict], token: Optional[str] = None) -> list[PayoutRecord]:
    """Process a list of {username, wallet} claim dicts."""
    records = []
    for claim in claims:
        try:
            record = verify_claim(claim["username"], claim["wallet"], token)
            records.append(record)
        except requests.HTTPError as exc:
            logger.error("HTTP error for %s: %s", claim.get("username"), exc)
        except KeyError as exc:
            logger.error("Malformed claim entry, missing key: %s", exc)
    return records


def save_payout_records(records: list[PayoutRecord], path: str = "payouts.json") -> None:
    """Persist payout records to a JSON file."""
    data = [asdict(r) for r in records]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    logger.info("Saved %d payout records to %s", len(records), path)


def summary(records: list[PayoutRecord]) -> dict:
    """Return aggregate statistics over all records."""
    verified = [r for r in records if r.verified]
    total_rtc = sum(r.reward_rtc for r in verified)
    tier_counts = {1: 0, 2: 0, 3: 0}
    for r in verified:
        tier_counts[r.tier] = tier_counts.get(r.tier, 0) + 1
    return {
        "total_claims": len(records),
        "verified": len(verified),
        "total_rtc": total_rtc,
        "tier_counts": tier_counts,
    }


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN")
    claims_path = os.environ.get("CLAIMS_FILE", "claims.json")
    output_path = os.environ.get("OUTPUT_FILE", "payouts.json")

    try:
        with open(claims_path, encoding="utf-8") as fh:
            claims = json.load(fh)
    except FileNotFoundError:
        logger.error("Claims file not found: %s", claims_path)
        return
    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON in claims file: %s", exc)
        return

    records = process_claims(claims, token)
    save_payout_records(records, output_path)

    stats = summary(records)
    logger.info(
        "Summary: %d/%d verified, %.1f RTC total, tiers=%s",
        stats["verified"],
        stats["total_claims"],
        stats["total_rtc"],
        stats["tier_counts"],
    )


if __name__ == "__main__":
    main()
