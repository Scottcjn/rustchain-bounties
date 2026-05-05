#!/usr/bin/env python3
"""One-off backfill: apply XP from rustchain-bounties issue #104 ledger evidence.

Rules:
- Parse markdown ledger table in issue body under Active Entries.
- Parse payout evidence in issue comments (bullet blocks + table rows).
- Skip rows with status=Voided.
- Convert Amount RTC -> tier label:
  <=10 micro, <=50 standard, <=100 major, >100 critical.
- Apply XP using update_xp_tracker_api.py local mode.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class LedgerEntry:
    user: str
    amount: float
    status: str
    pending_id: str
    tx_hash: str
    source: str = "body"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--issue-json", default="/tmp/issue104.json")
    p.add_argument("--comments-json", default="/tmp/issue104_comments.json")
    p.add_argument("--tracker", default="bounties/XP_TRACKER.md")
    p.add_argument("--comments-only", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def parse_amount(value: str) -> float:
    m = re.search(r"\d+(?:\.\d+)?", value)
    return float(m.group(0)) if m else 0.0


def tier_for_amount(amount: float) -> str:
    if amount <= 10:
        return "micro"
    if amount <= 50:
        return "standard"
    if amount <= 100:
        return "major"
    return "critical"


def clean_user(value: str) -> str:
    value = value.strip().strip("`")
    value = value.lstrip("@")
    return value.strip(" \t*_,.;:()[]{}<>")


def parse_ledger_table(body: str, source: str = "body") -> List[LedgerEntry]:
    """Parse issue body active table rows only."""
    lines = body.splitlines()
    out: List[LedgerEntry] = []

    in_table = False
    for line in lines:
        if line.strip().startswith("| Date (UTC) | Bounty Ref | GitHub User"):
            in_table = True
            continue
        if not in_table:
            continue
        if line.strip().startswith("|---"):
            continue
        if not line.strip().startswith("|"):
            if out:
                break
            continue

        cells = [c.strip() for c in line.strip().split("|")[1:-1]]
        if len(cells) < 9:
            continue

        user_cell = cells[2]
        if not user_cell.startswith("@"):
            continue

        out.append(
            LedgerEntry(
                user=clean_user(user_cell),
                amount=parse_amount(cells[4]),
                status=cells[5].strip().lower(),
                pending_id=cells[6].strip().strip("`"),
                tx_hash=cells[7].strip().strip("`"),
                source=source,
            )
        )

    return out


def parse_table_like_rows(text: str, source: str) -> List[LedgerEntry]:
    """Parse inline markdown table rows in comments."""
    out: List[LedgerEntry] = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().split("|")[1:-1]]
        if len(cells) < 9:
            continue

        status = cells[5].strip().lower()
        if status not in {"pending", "confirmed", "voided"}:
            continue

        user = clean_user(cells[2]) if cells[2].strip().startswith("@") else ""
        amount = parse_amount(cells[4])
        pending_id = cells[6].strip().strip("`")
        tx_hash = cells[7].strip().strip("`")

        if not user or not pending_id or amount <= 0:
            continue

        out.append(
            LedgerEntry(
                user=user,
                amount=amount,
                status=status,
                pending_id=pending_id,
                tx_hash=tx_hash,
                source=source,
            )
        )
    return out


def split_bullet_blocks(text: str) -> List[str]:
    """Collect multiline markdown bullet blocks."""
    blocks: List[str] = []
    cur: List[str] = []

    for raw in text.splitlines():
        s = raw.strip()
        if s.startswith("- "):
            if cur:
                blocks.append("\n".join(cur))
            cur = [s[2:].strip()]
            continue
        if cur:
            cur.append(s)

    if cur:
        blocks.append("\n".join(cur))

    return [b for b in blocks if b.strip()]


def parse_pending_ids(block: str) -> List[str]:
    return re.findall(
        r"\bpending(?:_id|\s+id)?\s*(?:#|:)?\s*`?(\d+)`?\b",
        block,
        flags=re.IGNORECASE,
    )


def parse_bullet_entry(block: str, source: str) -> List[LedgerEntry]:
    """Parse a single bullet block if it contains payout evidence."""
    pending_ids = parse_pending_ids(block)
    if not pending_ids:
        return []

    amount_m = re.search(r"(\d+(?:\.\d+)?)\s*RTC", block, flags=re.IGNORECASE)
    amount = float(amount_m.group(1)) if amount_m else 0.0
    if amount <= 0:
        return []

    user = ""
    m = re.search(r"(?:->|to)\s*`?([A-Za-z0-9_.:@-]+)`?", block, flags=re.IGNORECASE)
    if m:
        user = clean_user(m.group(1))
    if not user:
        mention = re.search(r"@([A-Za-z0-9_.-]+)", block)
        if mention:
            user = clean_user(mention.group(1))
    if not user:
        return []

    tx_m = re.search(
        r"\btx(?:_hash| hash)?\b\s*[: ]\s*`?([a-fA-F0-9]{16,64})`?",
        block,
        flags=re.IGNORECASE,
    )
    tx_hash = tx_m.group(1) if tx_m else ""

    status = "voided" if "voided" in block.lower() else "pending"
    if "confirmed" in block.lower() and status != "voided":
        status = "confirmed"

    out: List[LedgerEntry] = []
    for pending_id in pending_ids:
        out.append(
            LedgerEntry(
                user=user,
                amount=amount,
                status=status,
                pending_id=pending_id,
                tx_hash=tx_hash,
                source=source,
            )
        )
    return out


def parse_comment_entries(comment_body: str, source: str) -> List[LedgerEntry]:
    """Parse entries from a single comment body."""
    entries: List[LedgerEntry] = []

    # First try table-like rows
    entries.extend(parse_table_like_rows(comment_body, source))

    # Then try bullet blocks
    blocks = split_bullet_blocks(comment_body)
    for block in blocks:
        entries.extend(parse_bullet_entry(block, source))

    return entries


def load_data(args) -> tuple[List[LedgerEntry], List[LedgerEntry]]:
    """Load and parse issue body and comments."""
    body_entries: List[LedgerEntry] = []
    comment_entries: List[LedgerEntry] = []

    # Parse issue body
    if not args.comments_only and Path(args.issue_json).exists():
        with open(args.issue_json) as f:
            issue_data = json.load(f)
        body_entries = parse_ledger_table(issue_data["body"], "body")

    # Parse comments
    if Path(args.comments_json).exists():
        with open(args.comments_json) as f:
            comments_data = json.load(f)

        for i, comment in enumerate(comments_data):
            source = f"comment-{i + 1}"
            comment_entries.extend(parse_comment_entries(comment["body"], source))

    return body_entries, comment_entries


def apply_xp_updates(
    entries: List[LedgerEntry], tracker_path: str, dry_run: bool
) -> None:
    """Apply XP updates using the tracker API."""
    for entry in entries:
        if entry.status == "voided":
            continue

        tier = tier_for_amount(entry.amount)
        cmd = [
            "python",
            ".github/scripts/update_xp_tracker_api.py",
            "--local",
            tracker_path,
            "--user",
            entry.user,
            "--tier",
            tier,
            "--source",
            f"backfill-{entry.source}-{entry.pending_id}",
        ]

        if dry_run:
            print(f"DRY RUN: {' '.join(cmd)}")
        else:
            print(
                f"Applying XP: {entry.user} +{tier} from {entry.source} (${entry.amount} RTC)"
            )
            subprocess.run(cmd, check=True)


def main() -> None:
    args = parse_args()
    body_entries, comment_entries = load_data(args)

    all_entries = body_entries + comment_entries
    print(f"Found {len(all_entries)} total entries")
    print(f"  - {len(body_entries)} from issue body")
    print(f"  - {len(comment_entries)} from comments")

    # Group by status
    by_status: Dict[str, List[LedgerEntry]] = {}
    for entry in all_entries:
        by_status.setdefault(entry.status, []).append(entry)

    for status, entries in by_status.items():
        print(f"  - {len(entries)} {status}")

    # Apply XP updates
    valid_entries = [e for e in all_entries if e.status != "voided"]
    if valid_entries:
        apply_xp_updates(valid_entries, args.tracker, args.dry_run)
    else:
        print("No valid entries to process.")


if __name__ == "__main__":
    main()
