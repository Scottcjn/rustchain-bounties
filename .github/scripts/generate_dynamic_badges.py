#!/usr/bin/env python3
"""Generate shields.io endpoint JSON badges from XP_TRACKER.md.

Outputs:
- badges/hunter-stats.json
- badges/top-hunter.json
- badges/active-hunters.json
- badges/legendary-hunters.json
- badges/updated-at.json
- badges/weekly-growth.json (NEW)
- badges/top-3-hunters.json (NEW)
- badges/category-bug-slayers.json (NEW)
- badges/category-tutorial-titans.json (NEW)
- badges/category-outreach-pros.json (NEW)
- badges/hunters/<hunter>.json (per hunter)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Dict, List, Set


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracker", default="bounties/XP_TRACKER.md")
    parser.add_argument("--out-dir", default="badges")
    return parser.parse_args()


def parse_int(value: str) -> int:
    match = re.search(r"(\d+)", value or "")
    return int(match.group(1)) if match else 0


def parse_xp_from_action(action_text: str) -> int:
    # Example: "2026-02-20 13:44 UTC (+50 XP: tutorial bonus)"
    match = re.search(r"\+(\d+)\s*XP", action_text)
    return int(match.group(1)) if match else 0


def parse_date_from_action(action_text: str) -> dt.datetime | None:
    # Example: "2026-02-20" or "2026-02-20 13:44 UTC"
    match = re.search(r"(\d{4}-\d{2}-\d{2})", action_text)
    if match:
        try:
            return dt.datetime.strptime(match.group(1), "%Y-%m-%d").replace(tzinfo=dt.UTC)
        except ValueError:
            return None
    return None


def parse_badges(cell: str) -> Set[str]:
    # Extract names from ![Name](url)
    return set(re.findall(r"!\[([^\]]+)\]", cell or ""))


def parse_rows(md_text: str) -> List[Dict[str, object]]:
    lines = md_text.splitlines()
    header_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("| Rank | Hunter"):
            header_idx = i
            break

    if header_idx < 0:
        return []

    rows: List[Dict[str, object]] = []
    i = header_idx + 2
    while i < len(lines) and lines[i].strip().startswith("|"):
        line = lines[i].strip()
        if line.startswith("|---"):
            i += 1
            continue

        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) < 8:
            i += 1
            continue

        hunter = cells[1]
        if hunter == "_TBD_":
            i += 1
            continue

        row = {
            "rank": parse_int(cells[0]),
            "hunter": hunter,
            "wallet": cells[2],
            "xp": parse_int(cells[3]),
            "level": parse_int(cells[4]),
            "title": cells[5],
            "badges": parse_badges(cells[6]),
            "last_action": cells[7],
        }
        rows.append(row)
        i += 1

    rows.sort(key=lambda item: (-int(item["xp"]), str(item["hunter"]).lower()))
    for idx, row in enumerate(rows, start=1):
        row["rank"] = idx
    return rows


def color_for_level(level: int) -> str:
    if level >= 10:
        return "gold"
    if level >= 7:
        return "purple"
    if level >= 5:
        return "yellow"
    if level >= 4:
        return "orange"
    return "blue"


def slugify_hunter(hunter: str, existing_slugs: Set[str]) -> str:
    value = hunter.lstrip("@").strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = value.strip("-")
    base_slug = value or "unknown"
    
    slug = base_slug
    counter = 2
    while slug in existing_slugs:
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


def validate_badge(payload: Dict[str, object]) -> bool:
    required = {"schemaVersion", "label", "message", "color"}
    return all(k in payload for k in required) and payload["schemaVersion"] == 1


def write_badge(path: Path, label: str, message: str, color: str,
                named_logo: str = "github", logo_color: str = "white") -> None:
    payload = {
        "schemaVersion": 1,
        "label": label,
        "message": message,
        "color": color,
        "namedLogo": named_logo,
        "logoColor": logo_color,
    }
    
    if not validate_badge(payload):
        print(f"Warning: Invalid badge payload for {path}")
        
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    tracker_path = Path(args.tracker)
    out_dir = Path(args.out_dir)

    if not tracker_path.exists():
        raise SystemExit(f"tracker not found: {tracker_path}")

    md_text = tracker_path.read_text(encoding="utf-8")
    rows = parse_rows(md_text)

    total_xp = sum(int(row["xp"]) for row in rows)
    active_hunters = len(rows)
    legendary = sum(1 for row in rows if int(row["level"]) >= 10)

    # Weekly Growth Calculation
    now = dt.datetime.now(dt.UTC)
    seven_days_ago = now - dt.timedelta(days=7)
    weekly_xp_gain = 0
    for row in rows:
        action_date = parse_date_from_action(str(row["last_action"]))
        if action_date and action_date >= seven_days_ago:
            weekly_xp_gain += parse_xp_from_action(str(row["last_action"]))

    # Top 3 Hunters
    if rows:
        top_3 = rows[:3]
        top_3_names = ", ".join(str(r["hunter"]).lstrip("@") for r in top_3)
        top_msg = f"{str(rows[0]['hunter']).lstrip('@')} ({rows[0]['xp']} XP)"
    else:
        top_3_names = "none"
        top_msg = "none yet"

    # Category Badges
    bug_slayers = sum(1 for row in rows if "Bug Slayer" in row["badges"])
    tutorial_titans = sum(1 for row in rows if "Tutorial Titan" in row["badges"])
    outreach_pros = sum(1 for row in rows if "Outreach Pro" in row["badges"])

    # Write Standard Badges
    write_badge(
        out_dir / "hunter-stats.json",
        label="Bounty Hunter XP",
        message=f"{total_xp} total",
        color="orange" if total_xp > 0 else "blue",
        named_logo="rust",
        logo_color="white",
    )
    write_badge(
        out_dir / "top-hunter.json",
        label="Top Hunter",
        message=top_msg,
        color="gold" if rows else "lightgrey",
        named_logo="crown",
        logo_color="black" if rows else "white",
    )
    write_badge(
        out_dir / "top-3-hunters.json",
        label="Top 3 Hunters",
        message=top_3_names,
        color="gold" if rows else "lightgrey",
        named_logo="crown",
        logo_color="black" if rows else "white",
    )
    write_badge(
        out_dir / "active-hunters.json",
        label="Active Hunters",
        message=str(active_hunters),
        color="teal",
        named_logo="users",
        logo_color="white",
    )
    write_badge(
        out_dir / "legendary-hunters.json",
        label="Legendary Hunters",
        message=str(legendary),
        color="gold" if legendary > 0 else "lightgrey",
        named_logo="crown",
        logo_color="black" if legendary > 0 else "white",
    )
    write_badge(
        out_dir / "weekly-growth.json",
        label="Weekly XP",
        message=f"+{weekly_xp_gain}",
        color="brightgreen" if weekly_xp_gain > 0 else "blue",
        named_logo="trending-up",
        logo_color="white",
    )
    write_badge(
        out_dir / "updated-at.json",
        label="XP Updated",
        message=now.strftime("%Y-%m-%d"),
        color="blue",
        named_logo="clockify",
        logo_color="white",
    )

    # Category Badges
    write_badge(
        out_dir / "category-bug-slayers.json",
        label="Bug Slayers",
        message=str(bug_slayers),
        color="darkred",
        named_logo="bug",
    )
    write_badge(
        out_dir / "category-tutorial-titans.json",
        label="Tutorial Titans",
        message=str(tutorial_titans),
        color="blue",
        named_logo="book",
    )
    write_badge(
        out_dir / "category-outreach-pros.json",
        label="Outreach Pros",
        message=str(outreach_pros),
        color="teal",
        named_logo="twitter",
    )

    # Reset per-hunter directory before writing fresh files.
    hunters_dir = out_dir / "hunters"
    hunters_dir.mkdir(parents=True, exist_ok=True)
    for old_file in hunters_dir.glob("*.json"):
        old_file.unlink()

    used_slugs: Set[str] = set()
    for row in rows:
        hunter = str(row["hunter"])
        xp = int(row["xp"])
        level = int(row["level"])
        title = str(row["title"])
        slug = slugify_hunter(hunter, used_slugs)
        used_slugs.add(slug)
        
        write_badge(
            hunters_dir / f"{slug}.json",
            label=f"{hunter} XP",
            message=f"{xp} (L{level} {title})",
            color=color_for_level(level),
            named_logo="github",
            logo_color="white",
        )

    print(json.dumps({
        "total_xp": total_xp,
        "active_hunters": active_hunters,
        "legendary_hunters": legendary,
        "top_hunter": top_msg,
        "weekly_growth": weekly_xp_gain,
        "bug_slayers": bug_slayers,
        "generated_files": len(list(out_dir.glob("*.json"))) + len(list((out_dir / "hunters").glob("*.json"))),
    }))


if __name__ == "__main__":
    main()
