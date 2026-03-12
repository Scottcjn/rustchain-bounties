#!/usr/bin/env python3
"""Update RustChain bounty XP tracker markdown file.

v1 behavior:
- Award XP based on event and labels
- Update leaderboard table row for actor
- Append latest award note
- Refresh frontmatter last_updated date
"""

import argparse
import datetime as dt
import re
from pathlib import Path


LEVELS = [
    (10, 18000),
    (9, 12000),
    (8, 8000),
    (7, 5500),
    (6, 3500),
    (5, 2000),
    (4, 1000),
    (3, 500),
    (2, 200),
    (1, 0),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-name", required=True)
    parser.add_argument("--event-action", default="")
    parser.add_argument("--actor", required=True)
    parser.add_argument("--issue-number", default="0")
    parser.add_argument("--pr-merged", default="false")
    parser.add_argument("--issue-labels", default="")
    parser.add_argument("--pr-labels", default="")
    parser.add_argument("--tracker-file", default="bounties/XP_TRACKER.md")
    return parser.parse_args()


def is_true(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def award_xp(event_name: str, event_action: str, pr_merged: bool, labels_raw: str):
    labels = {x.strip().lower() for x in labels_raw.split(",") if x.strip()}

    xp = 0
    reasons = []

    if event_name == "pull_request" and pr_merged:
        xp += 300
        reasons.append("PR merged")

    if event_name == "issues" and event_action == "closed":
        xp += 80
        reasons.append("Issue closed")

    if event_action == "labeled":
        xp += 20
        reasons.append("Labeled action")

    if "bounty-approved" in labels:
        xp += 200
        reasons.append("bounty-approved")
    if "micro" in labels:
        xp += 50
        reasons.append("micro tier")
    if "standard" in labels:
        xp += 100
        reasons.append("standard tier")
    if "major" in labels:
        xp += 200
        reasons.append("major tier")
    if "critical" in labels:
        xp += 300
        reasons.append("critical tier")
    if "tutorial" in labels:
        xp += 150
        reasons.append("tutorial bonus")
    if "vintage" in labels:
        xp += 100
        reasons.append("vintage bonus")

    if xp == 0:
        xp = 30
        reasons.append("base activity")

    return xp, ", ".join(reasons)


def level_for_xp(total_xp: int) -> int:
    for level, threshold in LEVELS:
        if total_xp >= threshold:
            return level
    return 1


def update_frontmatter(content: str) -> str:
    today = dt.date.today().isoformat()
    if "last_updated:" in content:
        content = re.sub(r"last_updated:\s*\d{4}-\d{2}-\d{2}", f"last_updated: {today}", content, count=1)
    return content


def parse_table_rows(lines, table_start):
    rows = []
    i = table_start + 2  # skip header + separator
    while i < len(lines) and lines[i].startswith("|"):
        parts = [p.strip() for p in lines[i].strip().split("|")[1:-1]]
        if len(parts) >= 7:
            rows.append({
                "rank": parts[0],
                "hunter": parts[1],
                "wallet": parts[2],
                "xp": parts[3],
                "level": parts[4],
                "last_action": parts[5],
                "notes": parts[6],
            })
        i += 1
    return rows, i


def format_table_rows(rows):
    out = []
    for idx, row in enumerate(rows, start=1):
        out.append(
            "| {rank} | {hunter} | {wallet} | {xp} | {level} | {last_action} | {notes} |".format(
                rank=idx,
                hunter=row["hunter"],
                wallet=row["wallet"],
                xp=row["xp"],
                level=row["level"],
                last_action=row["last_action"],
                notes=row["notes"],
            )
        )
    if not out:
        out.append("| 1 | _TBD_ | _TBD_ | 0 | 1 | bootstrap | tracker initialized |")
    return out


def update_leaderboard(content: str, actor: str, gained_xp: int, action_note: str):
    lines = content.splitlines()

    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("| Rank | Hunter"):
            header_idx = i
            break

    if header_idx is None:
        return content

    rows, end_idx = parse_table_rows(lines, header_idx)

    # Drop placeholder row.
    rows = [r for r in rows if r["hunter"] != "_TBD_"]

    actor_name = f"@{actor}"
    found = None
    for row in rows:
        if row["hunter"].strip() == actor_name:
            found = row
            break

    if found is None:
        found = {
            "rank": "0",
            "hunter": actor_name,
            "wallet": "_TBD_",
            "xp": "0",
            "level": "1",
            "last_action": "first award",
            "notes": "auto-tracked",
        }
        rows.append(found)

    total_xp = int(float(found["xp"])) + int(gained_xp)
    found["xp"] = str(total_xp)
    found["level"] = str(level_for_xp(total_xp))
    found["last_action"] = action_note[:80]

    rows.sort(key=lambda row: int(float(row["xp"])), reverse=True)
    table_lines = format_table_rows(rows)

    new_lines = lines[: header_idx + 2] + table_lines + lines[end_idx:]
    return "\n".join(new_lines)


def append_latest_award(content: str, actor: str, xp: int, reason: str, issue_number: str):
    stamp = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC")
    note = f"- {stamp}: @{actor} +{xp} XP ({reason}) [#{issue_number}]"

    marker = "## Latest Awards"
    idx = content.find(marker)
    if idx == -1:
        return content + "\n\n## Latest Awards\n\n" + note + "\n"

    insert_at = content.find("\n\n", idx)
    if insert_at == -1:
        return content + "\n" + note + "\n"

    head = content[: insert_at + 2]
    tail = content[insert_at + 2 :]
    return head + note + "\n" + tail


def main():
    args = parse_args()
    tracker_path = Path(args.tracker_file)
    if not tracker_path.exists():
        raise SystemExit(f"Tracker file not found: {tracker_path}")

    labels = ",".join(filter(None, [args.issue_labels, args.pr_labels]))
    xp, reason = award_xp(
        event_name=args.event_name,
        event_action=args.event_action,
        pr_merged=is_true(args.pr_merged),
        labels_raw=labels,
    )

    content = tracker_path.read_text(encoding="utf-8")
    content = update_frontmatter(content)
    content = update_leaderboard(
        content,
        actor=args.actor,
        gained_xp=xp,
        action_note=f"{reason} (+{xp} XP)",
    )
    content = append_latest_award(
        content,
        actor=args.actor,
        xp=xp,
        reason=reason,
        issue_number=args.issue_number,
    )

    tracker_path.write_text(content.rstrip() + "\n", encoding="utf-8")
    print(f"Updated {tracker_path} for @{args.actor}: +{xp} XP ({reason})")


if __name__ == "__main__":
    main()
