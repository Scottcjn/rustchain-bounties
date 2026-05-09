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
    """Parse comment for both bullet blocks and table rows."""
    out: List[LedgerEntry] = []

    # Parse table-like rows
    out.extend(parse_table_like_rows(comment_body, source))

    # Parse bullet blocks
    bullet_blocks = split_bullet_blocks(comment_body)
    for block in bullet_blocks:
        out.extend(parse_bullet_entry(block, source))

    return out


def load_entries(args: argparse.Namespace) -> List[LedgerEntry]:
    """Load all ledger entries from issue and comments."""
    all_entries: List[LedgerEntry] = []

    if not args.comments_only:
        # Parse issue body
        issue_path = Path(args.issue_json)
        if issue_path.exists():
            with open(issue_path) as f:
                issue_data = json.load(f)
            body = issue_data.get("body", "")
            all_entries.extend(parse_ledger_table(body, "issue-body"))

    # Parse comments
    comments_path = Path(args.comments_json)
    if comments_path.exists():
        with open(comments_path) as f:
            comments_data = json.load(f)

        for i, comment in enumerate(comments_data):
            comment_body = comment.get("body", "")
            source = f"comment-{i + 1}"
            all_entries.extend(parse_comment_entries(comment_body, source))

    return all_entries


def dedupe_entries(entries: List[LedgerEntry]) -> List[LedgerEntry]:
    """Remove duplicates, preferring comments over issue body."""
    seen: Dict[str, LedgerEntry] = {}

    for entry in entries:
        key = f"{entry.user}:{entry.pending_id}"
        if key not in seen or entry.source.startswith("comment"):
            seen[key] = entry

    return list(seen.values())


def apply_xp_updates(entries: List[LedgerEntry], args: argparse.Namespace) -> None:
    """Apply XP updates using the tracker API."""
    script_path = Path(".github/scripts/update_xp_tracker_api.py")
    if not script_path.exists():
        print(f"ERROR: {script_path} not found")
        return

    for entry in entries:
        if entry.status == "voided":
            print(
                f"SKIP voided: {entry.user} {entry.amount} RTC (pending #{entry.pending_id})"
            )
            continue

        tier = tier_for_amount(entry.amount)
        cmd = [
            "python3",
            str(script_path),
            "--mode=local",
            f"--tracker={args.tracker}",
            f"--user={entry.user}",
            f"--tier={tier}",
            f"--reason=Backfill from issue #104 ledger (pending #{entry.pending_id})",
        ]

        if args.dry_run:
            print(f"DRY-RUN: {' '.join(cmd)}")
        else:
            print(
                f"APPLY: {entry.user} +{tier} XP (from {entry.amount} RTC, pending #{entry.pending_id})"
            )
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                print(f"ERROR applying XP for {entry.user}: {e}")
                print(f"STDERR: {e.stderr}")


def main() -> None:
    args = parse_args()

    print(f"Loading entries from {args.issue_json} and {args.comments_json}...")
    entries = load_entries(args)
    print(f"Found {len(entries)} raw entries")

    entries = dedupe_entries(entries)
    print(f"After deduplication: {len(entries)} entries")

    # Filter out voided entries for summary
    active_entries = [e for e in entries if e.status != "voided"]
    print(f"Active entries (non-voided): {len(active_entries)}")

    if not entries:
        print("No entries found to process")
        return

    print("\nEntries to process:")
    for entry in entries:
        tier = tier_for_amount(entry.amount)
        status_marker = "[VOIDED]" if entry.status == "voided" else ""
        print(
            f"  {entry.user}: {entry.amount} RTC -> {tier} XP (#{entry.pending_id}) {status_marker}"
        )

    if args.dry_run:
        print("\nDRY RUN - no changes will be made")

    apply_xp_updates(entries, args)
    print("\nBackfill complete!")


if __name__ == "__main__":
    main()
