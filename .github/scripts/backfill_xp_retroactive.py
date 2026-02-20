#!/usr/bin/env python3
"""
Retroactive XP + Badge Backfill Script for RustChain Bounties (#311)

This script:
1. Parses historical payout data from issue #104 ledger
2. Identifies hunters who should have XP but aren't in XP_TRACKER.md
3. Computes XP totals using current tracker rules
4. Applies retroactive badge assignment for threshold badges
5. Generates updated XP_TRACKER.md content

Usage:
    python3 backfill_xp_retroactive.py --dry-run
    python3 backfill_xp_retroactive.py --apply
"""

import argparse
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field

# XP Rules (from XP_TRACKER.md)
XP_RULES = {
    "micro": 50,      # <= 10 RTC
    "standard": 100,  # <= 50 RTC
    "major": 200,     # <= 100 RTC
    "critical": 300,  # > 100 RTC
}

# Level thresholds
LEVEL_THRESHOLDS = [
    (0, 1, "Starting Hunter"),
    (200, 2, "Basic Hunter"),
    (500, 3, "Priority Hunter"),
    (1000, 4, "Rising Hunter"),
    (2000, 5, "Multiplier Hunter"),
    (3500, 6, "Featured Hunter"),
    (5500, 7, "Veteran Hunter"),
    (8000, 8, "Elite Hunter"),
    (12000, 9, "Master Hunter"),
    (18000, 10, "Legendary Hunter"),
]

# Badge definitions
BADGE_THRESHOLDS = {
    "First Blood": 50,  # First claim/activity
    "Rising Hunter": 1000,  # Level 4
    "Multiplier Hunter": 2000,  # Level 5
    "Veteran Hunter": 5500,  # Level 7
    "Legendary Hunter": 18000,  # Level 10
}


@dataclass
class PayoutEntry:
    date: str
    bounty_ref: str
    github_user: str
    wallet: str
    amount: float
    status: str
    pending_id: str
    tx_hash: str
    notes: str = ""


@dataclass
class Hunter:
    github: str
    wallet: str = "_TBD_"
    total_xp: int = 0
    level: int = 1
    title: str = "Starting Hunter"
    badges: Set[str] = field(default_factory=set)
    activities: List[str] = field(default_factory=list)
    payouts: List[PayoutEntry] = field(default_factory=list)


def parse_args():
    parser = argparse.ArgumentParser(description="Retroactive XP Backfill")
    parser.add_argument("--tracker", default="bounties/XP_TRACKER.md")
    parser.add_argument("--ledger", default=".github/scripts/issue104_ledger.json")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--apply", action="store_true", help="Apply changes to tracker file")
    parser.add_argument("--output", default="bounties/XP_TRACKER_BACKFILLED.md", help="Output file")
    return parser.parse_args()


def rtc_to_tier(amount: float) -> str:
    """Convert RTC amount to tier label."""
    if amount <= 10:
        return "micro"
    elif amount <= 50:
        return "standard"
    elif amount <= 100:
        return "major"
    else:
        return "critical"


def tier_to_xp(tier: str) -> int:
    """Get XP for tier."""
    return XP_RULES.get(tier, 50)


def get_level_and_title(xp: int) -> Tuple[int, str]:
    """Get level and title based on XP."""
    for threshold, level, title in reversed(LEVEL_THRESHOLDS):
        if xp >= threshold:
            return level, title
    return 1, "Starting Hunter"


def get_badges_for_xp(xp: int, has_activity: bool = True) -> Set[str]:
    """Get badges based on XP thresholds."""
    badges = set()
    
    if has_activity:
        badges.add("First Blood")
    
    if xp >= 1000:
        badges.add("Rising Hunter")
    if xp >= 2000:
        badges.add("Multiplier Hunter")
    if xp >= 5500:
        badges.add("Veteran Hunter")
    if xp >= 18000:
        badges.add("Legendary Hunter")
    
    return badges


def parse_ledger_from_issue104() -> List[PayoutEntry]:
    """Parse ledger entries from issue #104 content."""
    # Hardcoded from the issue #104 snapshot we fetched
    # In production, this would fetch from GitHub API
    
    entries = []
    
    # Active Entries from issue #104 (as of 2026-02-20)
    raw_entries = [
        ("2026-02-10", "Rustchain#47", "BuilderFred", "BuilderFred", 2, "Confirmed", "19", "26a8383f7e18754d32b17f088f6363ec", "Stars verified"),
        ("2026-02-10", "Rustchain#47", "EugeneJarvis88", "EugeneJarvis88", 2, "Confirmed", "20", "507e0a81cae59497a07b32d058ed6a5e", "Stars verified"),
        ("2026-02-10", "bottube#74", "BuilderFred", "fred-the-builder", 2, "Confirmed", "21", "692fa63a5cc7a8c048d367160bb90b40", "Stars verified (BoTTube wallet)"),
        ("2026-02-10", "bottube#74", "EugeneJarvis88", "jarvis-ai-bot", 2, "Confirmed", "22", "000862031480c060fd38ed184205371b", "Stars verified (BoTTube wallet)"),
        ("2026-02-10", "rustchain-bounties#87", "mgrigajtis", "agentgubbins", 4, "Confirmed", "23", "dafe9cf255a35dbf35395f36477738b9", "Stars verified"),
        ("2026-02-10", "rustchain-bounties#87", "Abdul-nazeer", "abdul_rtc_01", 4, "Confirmed", "24", "4bcb8e89c1b1415bb5f6c3faa269aa6d", "Stars verified"),
        ("2026-02-10", "rustchain-bounties#87", "Best-creator", "xiaojie-rtc-wallet", 7, "Confirmed", "25", "526525f7f45251b2fe9e950f3ef055f5", "Stars + Discord"),
        ("2026-02-12", "rustchain-bounties#87", "dlin38", "dlin38", 4, "Confirmed", "26", "3049b19a21eed34d728e35a607dfd2b2", "Stars verified"),
        ("2026-02-12", "bottube#74", "BoozeLee", "BoozeLee", 2, "Voided", "27", "016f7a70cd6c767524a13d0c8357e1da", "Voided (wrong casing)"),
        ("2026-02-12", "bottube#74", "BoozeLee", "boozelee", 2, "Confirmed", "29", "78e6e75ce6f43bdb7d2b6532373baa64", "Stars verified"),
        ("2026-02-12", "bottube#74", "juzigu40-ui", "juzigu40-ui", 2, "Confirmed", "28", "f3de2e31f0c0f2bbbbc4d24ee736be62", "Stars verified"),
        ("2026-02-13", "rustchain-bounties#37", "liu971227-sys", "liu971227-sys", 25, "Confirmed", "59", "44bc2006a8d14ad9e6cd1aa71fe0b263", "PR#147 merged"),
        ("2026-02-13", "rustchain-bounties#123", "David-code-tang", "davidtang-codex", 40, "Confirmed", "60", "97b54984930cf1e336b67cb9f7fdd60b", "PR#115 merged"),
        ("2026-02-13", "rustchain-bounties#29", "liu971227-sys", "liu971227-sys", 100, "Confirmed", "61", "5391f1c57c1ffc178692bfa32e7042b5", "PR#148 merged (Phase 1)"),
        ("2026-02-13", "rustchain-bounties#62", "liu971227-sys", "liu971227-sys", 150, "Confirmed", "62", "b6e843b54d542afbe59bc814af40752d", "PR#155 merged"),
        # Additional entries from comments
        ("2026-02-13", "rustchain-bounties#255", "energypantry", "energypantry", 10, "Confirmed", "232", "ffd02fe08d47bf1cece33fbd16e3e2d0", "Parser/triage fixes"),
        ("2026-02-19", "rustchain-bounties#178", "zhanglinqian", "zhanglinqian", 35, "Confirmed", "233", "cd887b8bfd0fa112473f793fea3cad16", "Dashboard widget"),
        ("2026-02-20", "rustchain-bounties#255", "createkr", "createker", 10, "Confirmed", "254", "a8483103ec3e21b326507e430ed6ed06", "False-positive matcher fix"),
    ]
    
    for entry in raw_entries:
        if entry[5].lower() != "voided":  # Skip voided entries
            entries.append(PayoutEntry(*entry))
    
    return entries


def parse_existing_tracker(tracker_path: str) -> Dict[str, Hunter]:
    """Parse existing XP_TRACKER.md to get current hunters."""
    hunters = {}
    path = Path(tracker_path)
    
    if not path.exists():
        return hunters
    
    content = path.read_text(encoding="utf-8")
    
    # Parse hunter table
    in_table = False
    for line in content.split("\n"):
        if "| Rank | Hunter (GitHub / Agent ID)" in line:
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("|") and "@" in line:
            cells = [c.strip() for c in line.split("|")]
            if len(cells) >= 8:
                hunter_name = cells[2].strip()
                wallet = cells[3].strip() if len(cells) > 3 else "_TBD_"
                
                # Extract XP
                xp_match = re.search(r'(\d+)\s*XP', cells[4]) if len(cells) > 4 else None
                xp = int(xp_match.group(1)) if xp_match else 0
                
                # Extract level
                level_match = re.search(r'Level\s*(\d+)', cells[5]) if len(cells) > 5 else None
                level = int(level_match.group(1)) if level_match else 1
                
                # Extract title
                title = cells[6].strip() if len(cells) > 6 else "Starting Hunter"
                
                # Extract badges from markdown
                badges = set()
                if len(cells) > 7:
                    badge_text = cells[7]
                    for badge in ["First Blood", "Rising Hunter", "Multiplier Hunter", 
                                  "Veteran Hunter", "Legendary Hunter", "Tutorial Titan", 
                                  "Bug Slayer", "Vintage Veteran", "Agent Overlord", "Streak Master", "Outreach Pro"]:
                        if badge in badge_text:
                            badges.add(badge)
                
                # Clean hunter name
                hunter_clean = hunter_name.lstrip("@").strip()
                if hunter_clean and hunter_clean != "Hunter (GitHub / Agent ID)":
                    hunters[hunter_clean] = Hunter(
                        github=hunter_clean,
                        wallet=wallet,
                        total_xp=xp,
                        level=level,
                        title=title,
                        badges=badges
                    )
        
        if in_table and not line.startswith("|") and hunters:
            break
    
    return hunters


def compute_xp_from_payouts(payouts: List[PayoutEntry]) -> int:
    """Compute XP from payout entries."""
    total_xp = 0
    
    for payout in payouts:
        tier = rtc_to_tier(payout.amount)
        xp = tier_to_xp(tier)
        total_xp += xp
    
    return total_xp


def backfill_hunters(entries: List[PayoutEntry], existing_hunters: Dict[str, Hunter]) -> Dict[str, Hunter]:
    """Backfill hunters from payout entries."""
    hunters = dict(existing_hunters)
    
    for entry in entries:
        github = entry.github_user
        
        if github not in hunters:
            hunters[github] = Hunter(
                github=github,
                wallet=entry.wallet if entry.wallet != github else "_TBD_"
            )
        
        hunters[github].payouts.append(entry)
        hunters[github].activities.append(
            f"{entry.date}: +{tier_to_xp(rtc_to_tier(entry.amount))} XP ({entry.bounty_ref}, {entry.amount} RTC)"
        )
    
    # Recompute XP and badges for all hunters
    for github, hunter in hunters.items():
        hunter.total_xp = compute_xp_from_payouts(hunter.payouts)
        hunter.level, hunter.title = get_level_and_title(hunter.total_xp)
        hunter.badges = get_badges_for_xp(hunter.total_xp, len(hunter.payouts) > 0)
    
    return hunters


def generate_badge_markdown(badges: Set[str]) -> str:
    """Generate shields.io badge markdown."""
    badge_urls = {
        "First Blood": "https://img.shields.io/badge/First%20Blood-red?style=flat-square&logo=git&logoColor=white",
        "Rising Hunter": "https://img.shields.io/badge/Rising%20Hunter-orange?style=flat-square&logo=rocket&logoColor=white",
        "Multiplier Hunter": "https://img.shields.io/badge/Multiplier%20Hunter-yellow?style=flat-square&logo=star&logoColor=black",
        "Veteran Hunter": "https://img.shields.io/badge/Veteran%20Hunter-purple?style=flat-square&logo=shield&logoColor=white",
        "Legendary Hunter": "https://img.shields.io/badge/Legendary%20Hunter-gold?style=flat-square&logo=crown&logoColor=black",
        "Tutorial Titan": "https://img.shields.io/badge/Tutorial%20Titan-blue?style=flat-square&logo=book&logoColor=white",
        "Bug Slayer": "https://img.shields.io/badge/Bug%20Slayer-darkred?style=flat-square&logo=bug&logoColor=white",
        "Vintage Veteran": "https://img.shields.io/badge/Vintage%20Veteran-purple?style=flat-square&logo=apple&logoColor=white",
        "Agent Overlord": "https://img.shields.io/badge/Agent%20Overlord-cyan?style=flat-square&logo=robot&logoColor=white",
        "Streak Master": "https://img.shields.io/badge/Streak%20Master-green?style=flat-square&logo=fire&logoColor=white",
        "Outreach Pro": "https://img.shields.io/badge/Outreach%20Pro-teal?style=flat-square&logo=twitter&logoColor=white",
    }
    
    result = []
    for badge in sorted(badges):
        if badge in badge_urls:
            result.append(f"![{badge}]({badge_urls[badge]})")
    
    return " ".join(result) if result else ""


def generate_tracker_content(hunters: Dict[str, Hunter]) -> str:
    """Generate updated XP_TRACKER.md content."""
    # Sort hunters by XP descending
    sorted_hunters = sorted(hunters.values(), key=lambda h: h.total_xp, reverse=True)
    
    content = """---
title: RustChain Bounty Hunter XP and Levels
description: Track XP, levels, badges, and progression for all bounty hunters (humans + agents)
version: 1.4
last_updated: {}
maintainer: Scottcjn
---

# RustChain Bounty Hunter XP System

Welcome to the Hall of Hunters. Contributors earn XP for meaningful work and unlock levels, badges, and status.

## XP Rules (v2)

| Action | XP Awarded | Notes |
|---|---:|:---|
| Claim a bounty (valid wallet comment) | +20 | First claim per bounty |
| Submit linked PR | +50 to +300 | Micro 50 / Standard 100 / Major 200 / Critical 300 |
| PR merged or bounty approved | +100 to +500 | Tier-based bonus |
| Tutorial or long-form guide accepted | +150 | Must be linked in issue/PR |
| Bug report accepted | +80 | Reproducible + validated |
| Outreach proof accepted | +30 | Star/fork/share evidence |
| Vintage hardware proof | +100 | Screenshot or node proof |
| First completion bonus | +100 | One-time |

## Level Requirements and Perks

| Level | XP Required | Title | Perk |
|---:|---:|:---|:---|
| 1 | 0 | Starting Hunter | Starting status |
| 2 | 200 | Basic Hunter | Public recognition |
| 3 | 500 | Priority Hunter | Priority triage label |
| 4 | 1000 | Rising Hunter | Rising Hunter badge |
| 5 | 2000 | Multiplier Hunter | 1.1x payout multiplier (manual) |
| 6 | 3500 | Featured Hunter | Weekly shoutout eligibility |
| 7 | 5500 | Veteran Hunter | Veteran badge |
| 8 | 8000 | Elite Hunter | Early access to critical bounties |
| 9 | 12000 | Master Hunter | Extended vintage bonus eligibility |
| 10 | 18000+ | Legendary Hunter | Hall of Hunters |

## Current Hunters Leaderboard

| Rank | Hunter (GitHub / Agent ID) | Wallet (last 4) | Total XP | Level | Title | Badges Earned | Last Action | Notes |
|---:|:---|:---:|---:|---:|:---|:---|:---|:---|
""".format(datetime.now().strftime("%Y-%m-%d"))
    
    # Add hunter rows
    for rank, hunter in enumerate(sorted_hunters, 1):
        wallet_display = hunter.wallet if len(hunter.wallet) <= 20 else hunter.wallet[-16:]
        badges_md = generate_badge_markdown(hunter.badges)
        last_action = hunter.activities[-1] if hunter.activities else "Backfilled"
        
        content += f"| {rank} | @{hunter.github} | {wallet_display} | {hunter.total_xp} | {hunter.level} | {hunter.title} | {badges_md} | {last_action} | auto-tracked |\n"
    
    # Add badge gallery
    content += """
## Badge Gallery (Integrated shields.io URLs)

| Badge | URL | Markdown |
|:---|:---|:---|
| First Blood | `https://img.shields.io/badge/First%20Blood-red?style=flat-square&logo=git&logoColor=white` | ![First Blood](https://img.shields.io/badge/First%20Blood-red?style=flat-square&logo=git&logoColor=white) |
| Rising Hunter | `https://img.shields.io/badge/Rising%20Hunter-orange?style=flat-square&logo=rocket&logoColor=white` | ![Rising Hunter](https://img.shields.io/badge/Rising%20Hunter-orange?style=flat-square&logo=rocket&logoColor=white) |
| Multiplier Hunter | `https://img.shields.io/badge/Multiplier%20Hunter-yellow?style=flat-square&logo=star&logoColor=black` | ![Multiplier Hunter](https://img.shields.io/badge/Multiplier%20Hunter-yellow?style=flat-square&logo=star&logoColor=black) |
| Veteran Hunter | `https://img.shields.io/badge/Veteran%20Hunter-purple?style=flat-square&logo=shield&logoColor=white` | ![Veteran Hunter](https://img.shields.io/badge/Veteran%20Hunter-purple?style=flat-square&logo=shield&logoColor=white) |
| Legendary Hunter | `https://img.shields.io/badge/Legendary%20Hunter-gold?style=flat-square&logo=crown&logoColor=black` | ![Legendary Hunter](https://img.shields.io/badge/Legendary%20Hunter-gold?style=flat-square&logo=crown&logoColor=black) |
| Tutorial Titan | `https://img.shields.io/badge/Tutorial%20Titan-blue?style=flat-square&logo=book&logoColor=white` | ![Tutorial Titan](https://img.shields.io/badge/Tutorial%20Titan-blue?style=flat-square&logo=book&logoColor=white) |
| Bug Slayer | `https://img.shields.io/badge/Bug%20Slayer-darkred?style=flat-square&logo=bug&logoColor=white` | ![Bug Slayer](https://img.shields.io/badge/Bug%20Slayer-darkred?style=flat-square&logo=bug&logoColor=white) |
| Vintage Veteran | `https://img.shields.io/badge/Vintage%20Veteran-purple?style=flat-square&logo=apple&logoColor=white` | ![Vintage Veteran](https://img.shields.io/badge/Vintage%20Veteran-purple?style=flat-square&logo=apple&logoColor=white) |
| Agent Overlord | `https://img.shields.io/badge/Agent%20Overlord-cyan?style=flat-square&logo=robot&logoColor=white` | ![Agent Overlord](https://img.shields.io/badge/Agent%20Overlord-cyan?style=flat-square&logo=robot&logoColor=white) |
| Streak Master | `https://img.shields.io/badge/Streak%20Master-green?style=flat-square&logo=fire&logoColor=white` | ![Streak Master](https://img.shields.io/badge/Streak%20Master-green?style=flat-square&logo=fire&logoColor=white) |
| Outreach Pro | `https://img.shields.io/badge/Outreach%20Pro-teal?style=flat-square&logo=twitter&logoColor=white` | ![Outreach Pro](https://img.shields.io/badge/Outreach%20Pro-teal?style=flat-square&logo=twitter&logoColor=white) |

## Dynamic Badge Endpoints

- Total XP: `https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/hunter-stats.json`
- Top Hunter: `https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/top-hunter.json`
- Active Hunters: `https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/active-hunters.json`

Per-hunter dynamic badge pattern:
`https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/hunters/<hunter-slug>.json`

## Backfill Notes

- This tracker was backfilled from historical payout data in issue #104
- XP computed using current tier rules: micro (≤10 RTC) = 50 XP, standard (≤50 RTC) = 100 XP, major (≤100 RTC) = 200 XP, critical (>100 RTC) = 300 XP
- Badges assigned based on XP thresholds
- {} hunters in leaderboard

## Notes

- Automation source: `.github/workflows/bounty-xp-tracker.yml` + `.github/scripts/update_xp_tracker_api.py`.
- Dynamic badge source: `.github/workflows/update-dynamic-badges.yml` + `.github/scripts/generate_dynamic_badges.py`.
- Badge backfill is automatic: if a hunter already meets a threshold, missing threshold badges are added on the next XP update run.
- The updater recalculates rank by XP descending on each award.
""".format(len(sorted_hunters))
    
    return content


def main():
    args = parse_args()
    
    print("=" * 60)
    print("Retroactive XP + Badge Backfill Script (#311)")
    print("=" * 60)
    
    # Parse existing tracker
    print(f"\n📖 Parsing existing tracker: {args.tracker}")
    existing_hunters = parse_existing_tracker(args.tracker)
    print(f"   Found {len(existing_hunters)} existing hunters")
    
    # Parse ledger entries
    print("\n📊 Parsing historical payout data from issue #104...")
    entries = parse_ledger_from_issue104()
    print(f"   Found {len(entries)} valid payout entries (excluding voided)")
    
    # Backfill hunters
    print("\n🔍 Backfilling hunters...")
    hunters = backfill_hunters(entries, existing_hunters)
    print(f"   Total hunters after backfill: {len(hunters)}")
    
    # Show new hunters
    new_hunters = set(hunters.keys()) - set(existing_hunters.keys())
    if new_hunters:
        print(f"\n✨ New hunters added ({len(new_hunters)}):")
        for h in sorted(new_hunters):
            hunter = hunters[h]
            print(f"   - @{h}: {hunter.total_xp} XP, Level {hunter.level} ({hunter.title})")
    
    # Generate updated tracker
    print("\n📝 Generating updated tracker content...")
    content = generate_tracker_content(hunters)
    
    # Write output
    if args.apply:
        output_path = args.tracker
    else:
        output_path = args.output
    
    Path(output_path).write_text(content, encoding="utf-8")
    print(f"   Written to: {output_path}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total hunters: {len(hunters)}")
    print(f"New hunters added: {len(new_hunters)}")
    print(f"Existing hunters updated: {len(set(hunters.keys()) & set(existing_hunters.keys()))}")
    
    # Show top 10
    print("\n🏆 Top 10 Hunters:")
    sorted_hunters = sorted(hunters.values(), key=lambda h: h.total_xp, reverse=True)
    for i, h in enumerate(sorted_hunters[:10], 1):
        print(f"   {i}. @{h.github}: {h.total_xp} XP (Level {h.level})")
    
    if args.dry_run:
        print("\n⚠️  DRY RUN - No changes applied to original file")
        print(f"   Output written to: {args.output}")
    elif args.apply:
        print(f"\n✅ Changes applied to: {args.tracker}")
    else:
        print(f"\n💾 Output written to: {args.output}")
        print("   Use --apply to update the original tracker file")


if __name__ == "__main__":
    main()
