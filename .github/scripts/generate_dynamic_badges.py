#!/usr/bin/env python3
"""Dynamic Shields Badges v2 - Generate shields.io endpoint JSON badges from XP_TRACKER.md.

Enhanced version with:
- Weekly growth badge
- Top 3 hunters summary badges
- Category badges (docs/outreach/bug)
- Collision-safe per-hunter slugs
- README snippets for badge usage

Usage:
    python generate_dynamic_badges.py --tracker bounties/XP_TRACKER.md --out-dir badges
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate dynamic shields.io badges from XP tracker"
    )
    parser.add_argument(
        "--tracker", 
        default="bounties/XP_TRACKER.md",
        help="Path to XP_TRACKER.md file"
    )
    parser.add_argument(
        "--out-dir", 
        default="badges",
        help="Output directory for badge JSON files"
    )
    parser.add_argument(
        "--generate-readme",
        action="store_true",
        help="Generate README snippet with badge URLs"
    )
    return parser.parse_args()


def parse_int(value: str) -> int:
    """Extract integer from string."""
    match = re.search(r"\d+", value or "")
    return int(match.group(0)) if match else 0


def slugify_hunter(hunter: str) -> str:
    """Create collision-safe slug from hunter name."""
    value = hunter.lstrip("@").strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value)
    value = value.strip("-.")
    return value or "unknown"


def parse_xp_tracker(md_text: str) -> List[Dict[str, object]]:
    """Parse hunter data from XP_TRACKER.md table."""
    lines = md_text.splitlines()
    header_idx = -1
    
    for i, line in enumerate(lines):
        if "| Hunter" in line or "| Rank | Hunter" in line:
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
        if len(cells) < 4:
            i += 1
            continue

        hunter = cells[1] if "Rank" in lines[header_idx] else cells[0]
        if hunter == "_TBD_" or not hunter or hunter.startswith("--"):
            i += 1
            continue

        xp_idx = 3 if "Rank" in lines[header_idx] else 2
        level_idx = 4 if "Rank" in lines[header_idx] else 3
        
        row = {
            "rank": parse_int(cells[0]) if "Rank" in lines[header_idx] else 0,
            "hunter": hunter,
            "wallet": cells[2] if len(cells) > 2 else "",
            "xp": parse_int(cells[xp_idx]) if len(cells) > xp_idx else 0,
            "level": parse_int(cells[level_idx]) if len(cells) > level_idx else 1,
            "title": cells[5] if len(cells) > 5 else "Hunter",
            "slug": slugify_hunter(hunter),
        }
        rows.append(row)
        i += 1

    rows.sort(key=lambda item: (-int(item["xp"]), str(item["hunter"]).lower()))
    
    for idx, row in enumerate(rows, start=1):
        row["rank"] = idx
    
    return rows


def parse_ledger_for_weekly_data(md_text: str) -> Dict[str, int]:
    """Extract weekly bounty completions from ledger format."""
    weekly_counts = defaultdict(int)
    date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})')
    
    for match in date_pattern.finditer(md_text):
        date_str = match.group(1)
        try:
            if '-' in date_str:
                date_obj = dt.datetime.strptime(date_str, "%Y-%m-%d")
            else:
                date_obj = dt.datetime.strptime(date_str, "%m/%d/%Y")
            year, week, _ = date_obj.isocalendar()
            week_key = f"{year}-W{week:02d}"
            weekly_counts[week_key] += 1
        except ValueError:
            continue
    
    return dict(weekly_counts)


def parse_category_data(md_text: str) -> Dict[str, int]:
    """Extract bounty categories from markdown."""
    categories = defaultdict(int)
    
    category_markers = [
        (r'(?:docs?|documentation)', 'docs'),
        (r'(?:outreach|marketing|promotion|social)', 'outreach'),
        (r'(?:bug|fix|issue|crash|error)', 'bug'),
        (r'(?:feature|enhancement|add|implement)', 'feature'),
    ]
    
    lines = md_text.lower().splitlines()
    for line in lines:
        for pattern, cat_name in category_markers:
            if re.search(pattern, line):
                categories[cat_name] += 1
    
    return dict(categories)


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


def color_for_xp(xp: int) -> str:
    if xp >= 1000:
        return "gold"
    if xp >= 500:
        return "brightgreen"
    if xp >= 250:
        return "green"
    if xp >= 100:
        return "yellowgreen"
    return "blue"


def write_badge(
    path: Path, 
    label: str, 
    message: str, 
    color: str,
    named_logo: str = "github", 
    logo_color: str = "white",
    style: str = "flat",
    cache_seconds: int = 3600
) -> None:
    payload = {
        "schemaVersion": 1,
        "label": label,
        "message": message,
        "color": color,
        "namedLogo": named_logo,
        "logoColor": logo_color,
        "style": style,
    }
    if cache_seconds != 3600:
        payload["cacheSeconds"] = cache_seconds
    
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def generate_weekly_growth_badge(
    weekly_data: Dict[str, int], 
    out_dir: Path
) -> None:
    if not weekly_data:
        write_badge(
            out_dir / "weekly-growth.json",
            label="Weekly Growth",
            message="no data",
            color="lightgrey",
        )
        return
    
    sorted_weeks = sorted(weekly_data.keys())
    if len(sorted_weeks) >= 2:
        current_week = weekly_data[sorted_weeks[-1]]
        previous_week = weekly_data[sorted_weeks[-2]]
        
        if previous_week > 0:
            growth_pct = ((current_week - previous_week) / previous_week) * 100
            growth_str = f"+{growth_pct:.0f}%" if growth_pct >= 0 else f"{growth_pct:.0f}%"
            color = "brightgreen" if growth_pct >= 0 else "red"
        else:
            growth_str = f"+{current_week}"
            color = "brightgreen"
    else:
        growth_str = f"{weekly_data[sorted_weeks[0]]} new"
        color = "blue"
    
    write_badge(
        out_dir / "weekly-growth.json",
        label="Weekly Growth",
        message=growth_str,
        color=color,
        named_logo="trending-up",
    )


def generate_top_hunters_badges(
    rows: List[Dict[str, object]], 
    out_dir: Path
) -> None:
    top3_dir = out_dir / "top"
    top3_dir.mkdir(parents=True, exist_ok=True)
    
    medals = ["gold", "silver", "lightgrey"]
    
    for i, row in enumerate(rows[:3]):
        hunter_name = str(row["hunter"]).lstrip("@")[:15]
        xp = row["xp"]
        rank = i + 1
        
        write_badge(
            top3_dir / f"top-{rank}.json",
            label=f"#{rank} Hunter",
            message=f"@{hunter_name} ({xp} XP)",
            color=medals[i] if i < len(medals) else "blue",
            named_logo="trophy" if i == 0 else "star",
        )


def generate_category_badges(
    categories: Dict[str, int], 
    out_dir: Path
) -> None:
    cat_dir = out_dir / "categories"
    cat_dir.mkdir(parents=True, exist_ok=True)
    
    category_config = {
        "docs": ("#0066cc", "book"),
        "outreach": ("#ff69b4", "megaphone"),
        "bug": ("#cc0000", "bug"),
        "feature": ("#28a745", "plus-circle"),
    }
    
    for cat_name, count in categories.items():
        color, logo = category_config.get(cat_name, ("#6c757d", "tag"))
        write_badge(
            cat_dir / f"{cat_name}.json",
            label=cat_name.capitalize(),
            message=str(count),
            color=color,
            named_logo=logo,
        )
    
    for cat_name, (color, logo) in category_config.items():
        badge_path = cat_dir / f"{cat_name}.json"
        if not badge_path.exists():
            write_badge(
                badge_path,
                label=cat_name.capitalize(),
                message=str(categories.get(cat_name, 0)),
                color=color,
                named_logo=logo,
            )


def generate_hunter_badges(
    rows: List[Dict[str, object]], 
    out_dir: Path
) -> None:
    hunters_dir = out_dir / "hunters"
    hunters_dir.mkdir(parents=True, exist_ok=True)
    
    used_slugs = set()
    
    for row in rows:
        base_slug = row["slug"]
        slug = base_slug
        suffix = 1
        
        while slug in used_slugs:
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        
        used_slugs.add(slug)
        row["slug"] = slug
        
        level = row["level"]
        xp = row["xp"]
        hunter_name = str(row["hunter"]).lstrip("@")[:15]
        title = str(row.get("title", "Hunter"))[:15]
        
        write_badge(
            hunters_dir / f"{slug}.json",
            label=title,
            message=f"Lv.{level} | {xp} XP",
            color=color_for_level(level),
            named_logo="github",
        )


def generate_readme_snippet(
    rows: List[Dict[str, object]], 
    out_dir: Path
) -> str:
    base_url = "https://raw.githubusercontent.com/{repo}/main/badges"
    
    readme_content = f"""# Dynamic Badges

Auto-generated badges for the bounty hunter program.

## Global Badges

![Total XP]({base_url}/hunter-stats.json)
![Active Hunters]({base_url}/active-hunters.json)
![Legendary Hunters]({base_url}/legendary-hunters.json)
![Weekly Growth]({base_url}/weekly-growth.json)

## Top Hunters

"""
    
    for i, row in enumerate(rows[:3], 1):
        readme_content += f"![Top {i}]({base_url}/top/top-{i}.json)\\n"
    
    readme_content += f"""
## Category Badges

![Docs]({base_url}/categories/docs.json)
![Outreach]({base_url}/categories/outreach.json)
![Bug Fixes]({base_url}/categories/bug.json)

## Per-Hunter Badges

| Hunter | Badge |
|--------|-------|
"""
    
    for row in rows[:10]:
        hunter_clean = str(row["hunter"]).lstrip("@")
        slug = row["slug"]
        readme_content += f"| @{hunter_clean} | ![Stats]({base_url}/hunters/{slug}.json) |\\n"
    
    readme_content += f"""
*Last updated: {dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}*
"""
    
    readme_path = out_dir / "README.md"
    readme_path.write_text(readme_content, encoding="utf-8")
    return readme_content


def main() -> None:
    args = parse_args()
    tracker_path = Path(args.tracker)
    out_dir = Path(args.out_dir)

    if not tracker_path.exists():
        raise SystemExit(f"tracker not found: {tracker_path}")

    md_text = tracker_path.read_text(encoding="utf-8")
    rows = parse_xp_tracker(md_text)
    weekly_data = parse_ledger_for_weekly_data(md_text)
    categories = parse_category_data(md_text)
    
    total_xp = sum(int(row["xp"]) for row in rows)
    active_hunters = len(rows)
    legendary = sum(1 for row in rows if int(row.get("level", 0)) >= 10)

    write_badge(
        out_dir / "hunter-stats.json",
        label="Bounty Hunter XP",
        message=f"{total_xp} total",
        color="," if total_xp > 0 else "blue",
    )

    write_badge(
        out_dir / "active-hunters.json",
        label="Active Hunters",
        message=f"{active_hunters}",
        color="success" if active_hunters > 0 else "inactive",
    )

    write_badge(
        out_dir / "legendary-hunters.json",
        label="Legendary Hunters",
        message=f"{legendary}",
        color="gold" if legendary > 0 else "lightgrey",
    )

    write_badge(
        out_dir / "updated-at.json",
        label="Updated",
        message=dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        color="blue",
        cache_seconds=300,
    )

    if rows:
        top = rows[0]
        top_name = str(top["hunter"]).lstrip("@")[:12]
        write_badge(
            out_dir / "top-hunter.json",
            label="Top Hunter",
            message=f"@{top_name} ({top['xp']} XP)",
            color="gold",
            named_logo="trophy",
        )

    generate_weekly_growth_badge(weekly_data, out_dir)
    generate_top_hunters_badges(rows, out_dir)
    generate_category_badges(categories, out_dir)
    generate_hunter_badges(rows, out_dir)

    if args.generate_readme or True:
        readme = generate_readme_snippet(rows, out_dir)
        print(f"Generated README at {out_dir}/README.md")

    print(f"Generated {len(rows) + 9} badges in {out_dir}/")
    print(f"   - Global badges: 7")
    print(f"   - Per-hunter badges: {len(rows)}")
    print(f"   - Category badges: up to 4")


if __name__ == "__main__":
    main()
