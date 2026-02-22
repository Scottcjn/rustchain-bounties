#!/usr/bin/env python3
"""Generate shields.io endpoint JSON badges from XP_TRACKER.md.

Outputs:
- badges/hunter-stats.json
- badges/top-hunter.json
- badges/active-hunters.json
- badges/legendary-hunters.json
- badges/updated-at.json
- badges/top-3-hunters.json
- badges/weekly-growth.json
- badges/hunters/<hunter>.json (per hunter)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Dict, List, Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracker", default="bounties/XP_TRACKER.md")
    parser.add_argument("--out-dir", default="badges")
    return parser.parse_args()


def parse_int(value: str) -> int:
    match = re.search(r"\d+", value or "")
    return int(match.group(0)) if match else 0


def parse_rows(md_text: str) -> List[Dict[str, Any]]:
    lines = md_text.splitlines()
    header_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("| Rank | Hunter"):
            header_idx = i
            break

    if header_idx < 0:
        return []

    rows: List[Dict[str, Any]] = []
    i = header_idx + 2
    while i < len(lines) and lines[i].strip().startswith("|"):
        line = lines[i].strip()
        if line.startswith("|---"):
            i += 1
            continue

        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) < 9:
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
            "badges": cells[6],
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


def slugify_hunter(hunter: str) -> str:
    value = hunter.lstrip("@").strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = value.strip("-")
    return value or "unknown"


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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def calculate_weekly_growth(rows: List[Dict[str, Any]]) -> int:
    """Calculate total XP gained in the last 7 days based on Last Action column."""
    total_growth = 0
    now = dt.datetime.now()
    seven_days_ago = now - dt.timedelta(days=7)
    
    for row in rows:
        last_action = str(row.get("last_action", ""))
        # Format: "2026-02-13: +300 XP (rustchain-bounties#62, 150 RTC)"
        match = re.match(r"(\d{4}-\d{2}-\d{2}):\s*\+(\d+)\s*XP", last_action)
        if match:
            date_str, xp_str = match.groups()
            try:
                action_date = dt.datetime.strptime(date_str, "%Y-%m-%d")
                if action_date >= seven_days_ago:
                    total_growth += int(xp_str)
            except ValueError:
                continue
    return total_growth


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
    weekly_growth = calculate_weekly_growth(rows)

    if rows:
        top = rows[0]
        top_name = str(top["hunter"]).lstrip("@")
        top_msg = f"{top_name} ({top['xp']} XP)"
        
        # Top 3 summary
        top_3 = rows[:3]
        top_3_names = [str(r["hunter"]).lstrip("@") for r in top_3]
        top_3_msg = ", ".join(top_3_names)
    else:
        top_msg = "none yet"
        top_3_msg = "none yet"

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
        label="Leaders",
        message=top_3_msg,
        color="gold" if rows else "lightgrey",
        named_logo="crown",
        logo_color="white",
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
        message=f"+{weekly_growth}",
        color="brightgreen" if weekly_growth > 0 else "blue",
        named_logo="trending-up" if weekly_growth > 0 else "dash",
        logo_color="white",
    )
    write_badge(
        out_dir / "updated-at.json",
        label="XP Updated",
        message=dt.datetime.now(dt.UTC).strftime("%Y-%m-%d"),
        color="blue",
        named_logo="clockify",
        logo_color="white",
    )

    # Reset per-hunter directory before writing fresh files.
    hunters_dir = out_dir / "hunters"
    hunters_dir.mkdir(parents=True, exist_ok=True)
    for old_file in hunters_dir.glob("*.json"):
        old_file.unlink()

    for row in rows:
        hunter = str(row["hunter"])
        xp = int(row["xp"])
        level = int(row["level"])
        title = str(row["title"])
        slug = slugify_hunter(hunter)
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
        "weekly_growth": weekly_growth,
        "generated_files": len(list(out_dir.glob("*.json"))) + len(list((out_dir / "hunters").glob("*.json"))),
    }))


if __name__ == "__main__":
    main()
