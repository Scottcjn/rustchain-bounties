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
- badges/hunters/<hunter>-bounties.json
- badges/hunters/<hunter>-rtc.json
- badges/hunters/<hunter>-age.json
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Dict, List, Any
import requests

API_BASE = "https://50.28.86.131"

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracker", default="bounties/XP_TRACKER.md")
    parser.add_argument("--out-dir", default="badges")
    parser.add_argument("--skip-api", action="store_true", help="Skip RustChain API calls")
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
            "notes": cells[8],
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


def parse_tracker_last_updated(md_text: str) -> dt.date | None:
    """Parse front-matter `last_updated` date from XP tracker markdown."""
    match = re.search(r"(?m)^last_updated:\s*(\d{4}-\d{2}-\d{2})\s*$", md_text)
    if not match:
        return None
    try:
        return dt.datetime.strptime(match.group(1), "%Y-%m-%d").date()
    except ValueError:
        return None


def calculate_weekly_growth(rows: List[Dict[str, Any]], reference_date: dt.date | None = None) -> int:
    """Calculate total XP gained in the last 7 calendar days ending on reference_date."""
    total_growth = 0
    anchor_date = reference_date or dt.datetime.now(dt.UTC).date()
    seven_day_start = anchor_date - dt.timedelta(days=6)
    
    for row in rows:
        last_action = str(row.get("last_action", ""))
        # Format: "2026-02-13: +300 XP (rustchain-bounties#62, 150 RTC)"
        match = re.match(r"(\d{4}-\d{2}-\d{2}):\s*\+(\d+)\s*XP", last_action)
        if match:
            date_str, xp_str = match.groups()
            try:
                action_date = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
                if seven_day_start <= action_date <= anchor_date:
                    total_growth += int(xp_str)
            except ValueError:
                continue
    return total_growth


def get_hunter_metrics(hunter_name: str, md_text: str) -> Dict[str, Any]:
    """Calculate per-hunter metrics from the whole XP_TRACKER file."""
    # Count occurrences of @hunter_name in Latest Awards
    # Award line format: "- 2026-02-13 00:00 UTC: @username earned..."
    hunter_handle = hunter_name if hunter_name.startswith("@") else f"@{hunter_name}"
    
    awards_section = md_text.split("## Latest Awards")[-1]
    # Filter for approved/merged/completed bounties
    completed_pattern = re.compile(rf"- .*?: {re.escape(hunter_handle)} earned .*? \((merged|approved|closed|tutorial|docs|bug|vintage|outreach)")
    completed_count = len(completed_pattern.findall(awards_section))
    
    # RTC Earned: sum all "(\d+) RTC" matches in hunter's award lines
    rtc_pattern = re.compile(rf"- .*?: {re.escape(hunter_handle)} earned .*? \((?:.*?,\s*)?(\d+)\s*RTC\)")
    total_rtc = sum(int(amt) for amt in rtc_pattern.findall(awards_section))
    
    return {
        "completed": completed_count,
        "rtc": total_rtc
    }

def fetch_onchain_ages() -> Dict[str, str]:
    """Fetch all miner info once and return a map of miner -> age_string."""
    ages = {}
    try:
        resp = requests.get(f"{API_BASE}/api/miners", verify=False, timeout=10)
        if resp.status_code == 200:
            miners = resp.json()
            now = dt.datetime.now(dt.UTC)
            for m in miners:
                miner_id = m.get("miner")
                first = m.get("first_attest")
                if miner_id and first:
                    first_dt = dt.datetime.fromtimestamp(first, dt.UTC)
                    delta = now - first_dt
                    if delta.days > 365:
                        age_str = f"{delta.days // 365}y { (delta.days % 365) // 30 }m"
                    elif delta.days > 30:
                        age_str = f"{delta.days // 30}m {delta.days % 30}d"
                    else:
                        age_str = f"{delta.days}d"
                    ages[miner_id] = age_str
    except Exception as e:
        print(f"Warning: Failed to fetch on-chain ages: {e}")
    return ages

def main() -> None:
    args = parse_args()
    tracker_path = Path(args.tracker)
    out_dir = Path(args.out_dir)

    if not tracker_path.exists():
        raise SystemExit(f"tracker not found: {tracker_path}")

    md_text = tracker_path.read_text(encoding="utf-8")
    rows = parse_rows(md_text)
    tracker_last_updated = parse_tracker_last_updated(md_text)
    reference_date = tracker_last_updated or dt.datetime.now(dt.UTC).date()

    total_xp = sum(int(row["xp"]) for row in rows)
    active_hunters = len(rows)
    legendary = sum(1 for row in rows if int(row["level"]) >= 10)
    weekly_growth = calculate_weekly_growth(rows, reference_date=reference_date)

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
        message=reference_date.strftime("%Y-%m-%d"),
        color="blue",
        named_logo="clockify",
        logo_color="white",
    )

    # Fetch on-chain ages once if not skipped
    onchain_ages = fetch_onchain_ages() if not args.skip_api else {}

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
        
        # Core XP Badge
        write_badge(
            hunters_dir / f"{slug}.json",
            label=f"{hunter} XP",
            message=f"{xp} (L{level} {title})",
            color=color_for_level(level),
            named_logo="github",
            logo_color="white",
        )
        
        # V2 Richer Metrics
        metrics = get_hunter_metrics(hunter, md_text)
        
        # Bounties Completed
        write_badge(
            hunters_dir / f"{slug}-bounties.json",
            label="Bounties",
            message=str(metrics["completed"]),
            color="brightgreen" if metrics["completed"] > 0 else "blue",
            named_logo="check-circle",
            logo_color="white",
        )
        
        # Total RTC Earned
        write_badge(
            hunters_dir / f"{slug}-rtc.json",
            label="RTC Earned",
            message=f"{metrics['rtc']} RTC",
            color="orange" if metrics["rtc"] > 0 else "blue",
            named_logo="bitcoin", # Shields.io has bitcoin logo, good for RTC
            logo_color="white",
        )
        
        # Account Age (On-chain)
        miner_id = hunter.lstrip("@")
        age = onchain_ages.get(miner_id, "unknown")
        write_badge(
            hunters_dir / f"{slug}-age.json",
            label="Account Age",
            message=age,
            color="blue",
            named_logo="clock",
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
