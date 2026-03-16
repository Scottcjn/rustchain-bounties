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
from typing import Dict, List, Optional, Tuple


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
    """Parse markdown table rows that match the known ledger header."""
    lines = body.splitlines()
    out: List[LedgerEntry] = []

    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("| Date (UTC) | Bounty Ref | GitHub User"):
            in_table = True
            continue
        if not in_table:
            continue
        if stripped.startswith("|---"):
            # header separator row
            continue
        if not stripped.startswith("|"):
            # end of table when a non-table line is encountered
            if out:
                break
            continue

        cells = [c.strip() for c in stripped.split("|")[1:-1]]
        # Expected columns: Date | Ref | User | Desc | Amount | Status | Pending | Tx | Note
        if len(cells) < 9:
            continue

        user_cell = cells[2]
        if not user_cell or not user_cell.strip().startswith("@"):
            continue

        entry = LedgerEntry(
            user=clean_user(user_cell),
            amount=parse_amount(cells[4]),
            status=cells[5].strip().lower(),
            pending_id=cells[6].strip().strip("`"),
            tx_hash=cells[7].strip().strip("`"),
            source=source,
        )
        out.append(entry)

    return out


def parse_bullet_block(body: str, source: str = "comments") -> List[LedgerEntry]:
    """Parse loose bullet evidence blocks in comments.

    Tries to extract @user, amount (RTC), status, pending id, tx hash from lines
    that start with '-' or '*'.
    """
    out: List[LedgerEntry] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not (line.startswith("-") or line.startswith("*")):
            continue
        text = line.lstrip("-* ").strip()

        # Find user (first @mention)
        mu = re.search(r"@([A-Za-z0-9][A-Za-z0-9-]+)", text)
        if not mu:
            continue
        user = mu.group(1)

        # Find amount like "12.3 RTC"
        ma = re.search(r"(\d+(?:\.\d+)?)\s*RTC\b", text, re.I)
        if not ma:
            # If there's no amount, skip
            continue
        amount = float(ma.group(1))

        # Find status key=value-ish or words like 'Voided'/'Paid' following 'status'
        ms = re.search(r"status\s*[:=]\s*([A-Za-z]+)", text, re.I)
        status = ms.group(1).lower() if ms else ""

        # Pending ID
        mp = re.search(r"(?:pending[_\s-]*id|pid)\s*[:=]\s*`?([A-Za-z0-9._-]+)`?", text, re.I)
        pending_id = mp.group(1) if mp else ""

        # Tx hash
        mt = (
            re.search(r"(?:tx|transaction)[\s_-]*hash\s*[:=]\s*`?([A-Fa-f0-9x]+)`?", text, re.I)
            or re.search(r"\b0x[a-fA-F0-9]{6,}\b", text)
        )
        tx_hash = mt.group(1) if mt else ""

        out.append(
            LedgerEntry(
                user=clean_user(user),
                amount=amount,
                status=status,
                pending_id=pending_id,
                tx_hash=tx_hash,
                source=source,
            )
        )

    return out


def load_issue_body(issue_json_path: Path) -> str:
    data = json.loads(issue_json_path.read_text(encoding="utf-8"))
    # Support both gh api output (object) and raw body string
    if isinstance(data, dict) and "body" in data:
        return data["body"] or ""
    if isinstance(data, str):
        return data
    return ""


def load_comments_bodies(comments_json_path: Path) -> List[str]:
    data = json.loads(comments_json_path.read_text(encoding="utf-8"))
    bodies: List[str] = []
    if isinstance(data, list):
        for c in data:
            if isinstance(c, dict) and "body" in c and c["body"]:
                bodies.append(c["body"])
            elif isinstance(c, str):
                bodies.append(c)
    elif isinstance(data, dict) and "comments" in data and isinstance(data["comments"], list):
        for c in data["comments"]:
            if isinstance(c, dict) and "body" in c and c["body"]:
                bodies.append(c["body"])
    return bodies


def unique_key(entry: LedgerEntry) -> Tuple[str, str, str, float]:
    """Build a key to deduplicate entries from multiple sources."""
    # Prefer pending_id or tx_hash when present, otherwise fall back to user+amount+status
    pid = entry.pending_id or ""
    tx = entry.tx_hash or ""
    return (entry.user.lower(), pid or tx, entry.status.lower(), float(entry.amount))


def collect_entries(
    issue_body: Optional[str], comment_bodies: List[str], include_body: bool
) -> List[LedgerEntry]:
    entries: List[LedgerEntry] = []

    if include_body and issue_body:
        entries.extend(parse_ledger_table(issue_body, source="body"))

    for i, body in enumerate(comment_bodies):
        # Parse any tables in comment
        entries.extend(parse_ledger_table(body, source=f"comment#{i+1}"))
        # Parse bullet blocks
        entries.extend(parse_bullet_block(body, source=f"comment#{i+1}"))

    # Deduplicate
    uniq: Dict[Tuple[str, str, str, float], LedgerEntry] = {}
    for e in entries:
        uniq[unique_key(e)] = e

    return list(uniq.values())


def filter_non_void(entries: List[LedgerEntry]) -> List[LedgerEntry]:
    out: List[LedgerEntry] = []
    for e in entries:
        st = (e.status or "").strip().lower()
        if st == "voided" or st == "void":
            continue
        out.append(e)
    return out


def apply_xp(entries: List[LedgerEntry], tracker: Path, dry_run: bool = False) -> None:
    """Apply XP awards using update_xp_tracker_api.py in local mode.

    Falls back to printing the plan if the updater script is missing.
    """
    script_path = (Path(__file__).parent / "update_xp_tracker_api.py").resolve()
    has_updater = script_path.exists()

    for e in entries:
        tier = tier_for_amount(e.amount)
        note = f"rustchain-bounties#104:{e.source}"
        if e.pending_id:
            note += f":{e.pending_id}"
        elif e.tx_hash:
            note += f":{e.tx_hash}"

        cmd = [
            "python3",
            str(script_path),
            "--local",
            "--tracker",
            str(tracker),
            "award",
            "--user",
            e.user,
            "--tier",
            tier,
            "--note",
            note,
        ]

        if dry_run or not has_updater:
            print(f"[DRY-RUN]" if dry_run else "[NO-UPDATER]", "Would run:", " ".join(cmd))
            continue

        try:
            subprocess.run(cmd, check=True)
        except FileNotFoundError:
            print("[WARN] update_xp_tracker_api.py not found; printing plan instead.")
            print("[PLAN]", " ".join(cmd))
        except subprocess.CalledProcessError as ex:
            print(f"[ERROR] Failed to apply XP for {e.user} ({tier}) from {e.source}: {ex}")


def main() -> None:
    args = parse_args()
    issue_path = Path(args.issue_json)
    comments_path = Path(args.comments_json)
    tracker_path = Path(args.tracker)

    issue_body = ""
    if not args.comments_only and issue_path.exists():
        issue_body = load_issue_body(issue_path)

    comment_bodies: List[str] = []
    if comments_path.exists():
        comment_bodies = load_comments_bodies(comments_path)

    entries = collect_entries(issue_body, comment_bodies, include_body=not args.comments_only)
    entries = filter_non_void(entries)

    # Display summary
    print(f"Collected {len(entries)} non-voided entries.")
    by_user: Dict[str, List[LedgerEntry]] = {}
    for e in entries:
        by_user.setdefault(e.user, []).append(e)
    for user, items in sorted(by_user.items()):
        total = sum(i.amount for i in items)
        tiers = [tier_for_amount(i.amount) for i in items]
        print(f" - {user}: {len(items)} entries, total {total:.2f} RTC, tiers={','.join(tiers)}")

    apply_xp(entries, tracker=tracker_path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()