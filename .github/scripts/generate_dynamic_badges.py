#!/usr/bin/env python3
"""Generate shields.io endpoint JSON badges from XP_TRACKER.md.

Outputs:
- badges/hunter-stats.json
- badges/top-hunter.json
- badges/active-hunters.json
- badges/legendary-hunters.json
- badges/updated-at.json
- badges/hunters/<hunter>.json (per hunter)
- badges/weekly-growth.json (new)
- badges/top-3-hunters.json (new)
- badges/docs-champions.json (new - if data exists)
- badges/bug-slayers.json (new - if data exists)
- badges/outreach-stars.json (new - if data exists)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Optional


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracker", default="bounties/XP_TRACKER.md")
    parser.add_argument("--out-dir", default="badges")
    return parser.parse_args()


def parse_int(value: str) -> int:
    match = re.search(r"\d+", value or "")
    return int(match.group(0)) if match else 0


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
            "badges": cells[6] if len(cells) > 6 else "",
            "last_action": cells[7] if len(cells) > 7 else "",
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
    validate_badge_schema(payload, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


# Schema for shields.io badge validation
BADGE_SCHEMA = {
    "required": ["schemaVersion", "label", "message", "color"],
    "properties": {
        "schemaVersion": {"type": "integer", "minimum": 1},
        "label": {"type": "string"},
        "message": {"type": "string"},
        "color": {"type": "string"},
        "namedLogo": {"type": "string"},
        "logoColor": {"type": "string"},
    },
}


def validate_badge_schema(payload: Dict, path: Path) -> None:
    """Validate badge JSON conforms to shields.io schema."""
    errors: List[str] = []
    
    # Check required fields
    for field in BADGE_SCHEMA["required"]:
        if field not in payload:
            errors.append(f"Missing required field: {field}")
    
    # Check schemaVersion is integer
    if "schemaVersion" in payload and not isinstance(payload["schemaVersion"], int):
        errors.append("schemaVersion must be an integer")
    
    if errors:
        raise ValueError(f"Invalid badge schema for {path}: {', '.join(errors)}")


# Category badge mappings - maps badge names to categories
CATEGORY_BADGES = {
    "docs": {"Tutorial Titan", "Doc Wizard", "Documentation Pro"},
    "bug": {"Bug Slayer", "Bug Hunter", "Security Researcher"},
    "outreach": {"Outreach Star", "Social Champion", "Evangelist"},
}


def get_category_hunters(rows: List[Dict[str, object]]) -> Dict[str, List[Dict[str, object]]]:
    """Extract hunters that have category-specific badges."""
    category_hunters: Dict[str, List[Dict[str, object]]] = {
        "docs": [],
        "bug": [],
        "outreach": [],
    }
    
    for row in rows:
        # Parse badges from the row - badges are in the Badges column (index 6)
        badges_cell = str(row.get("badges", ""))
        
        for category, category_badge_set in CATEGORY_BADGES.items():
            for badge in category_badge_set:
                if badge.lower() in badges_cell.lower():
                    category_hunters[category].append(row)
                    break
    
    return category_hunters


def slugify_hunter_collision_safe(hunter: str, used_slugs: Set[str]) -> str:
    """Generate collision-safe slug for hunter name.
    
    If the base slug already exists, append a counter suffix.
    """
    base_slug = slugify_hunter(hunter)
    if base_slug not in used_slugs:
        used_slugs.add(base_slug)
        return base_slug
    
    # Handle collision - try numbered variants
    counter = 1
    while f"{base_slug}-{counter}" in used_slugs:
        counter += 1
    
    slug = f"{base_slug}-{counter}"
    used_slugs.add(slug)
    return slug


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

    if rows:
        top = rows[0]
        top_name = str(top["hunter"]).lstrip("@")
        top_msg = f"{top_name} ({top['xp']} XP)"
    else:
        top_msg = "none yet"

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
        out_dir / "updated-at.json",
        label="XP Updated",
        message=dt.datetime.now(dt.UTC).strftime("%Y-%m-%d"),
        color="blue",
        named_logo="clockify",
        logo_color="white",
    )

    # === NEW: Top 3 Hunters Summary Badge ===
    if len(rows) >= 3:
        top3_names = [str(r["hunter"]).lstrip("@") for r in rows[:3]]
        top3_msg = ", ".join(top3_names[:2]) + (f" +{len(top3_names)-2}" if len(top3_names) > 2 else "")
        write_badge(
            out_dir / "top-3-hunters.json",
            label="Top 3 Hunters",
            message=top3_msg,
            color="gold",
            named_logo="trophy",
            logo_color="black",
        )
    elif len(rows) > 0:
        # Only 1-2 hunters
        top_names = ", ".join(str(r["hunter"]).lstrip("@") for r in rows)
        write_badge(
            out_dir / "top-3-hunters.json",
            label="Top Hunters",
            message=top_names,
            color="gold",
            named_logo="trophy",
            logo_color="black",
        )

    # === NEW: Weekly Growth Badge (estimated from recent activity) ===
    # Parse last_action dates to estimate weekly growth
    recent_xp = 0
    now = dt.datetime.now(dt.UTC)
    week_ago = now - dt.timedelta(days=7)
    
    for row in rows:
        last_action = str(row.get("last_action", ""))
        # Extract date from last_action (format: "YYYY-MM-DD (+N XP)" or similar)
        date_match = re.search(r"(\d{4})-(\d{2})-(\d{2})", last_action)
        if date_match:
            try:
                action_date = dt.datetime(int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3)), tzinfo=dt.UTC)
                if action_date >= week_ago:
                    # Extract XP gain from last action
                    xp_match = re.search(r"\+(\d+)\s*XP", last_action)
                    if xp_match:
                        recent_xp += int(xp_match.group(1))
            except ValueError:
                pass  # Invalid date, skip
    
    growth_color = "green" if recent_xp > 0 else "grey"
    write_badge(
        out_dir / "weekly-growth.json",
        label="This Week",
        message=f"+{recent_xp} XP" if recent_xp > 0 else "no new XP",
        color=growth_color,
        named_logo="trending-up" if recent_xp > 0 else "minus",
        logo_color="white",
    )

    # === NEW: Category Badges (docs, bug, outreach) ===
    category_hunters = get_category_hunters(rows)
    
    # Docs champions
    docs_count = len(category_hunters["docs"])
    if docs_count > 0:
        write_badge(
            out_dir / "docs-champions.json",
            label="Docs Champions",
            message=str(docs_count),
            color="blue",
            named_logo="book",
            logo_color="white",
        )
    
    # Bug slayers
    bug_count = len(category_hunters["bug"])
    if bug_count > 0:
        write_badge(
            out_dir / "bug-slayers.json",
            label="Bug Slayers",
            message=str(bug_count),
            color="darkred",
            named_logo="bug",
            logo_color="white",
        )
    
    # Outreach stars
    outreach_count = len(category_hunters["outreach"])
    if outreach_count > 0:
        write_badge(
            out_dir / "outreach-stars.json",
            label="Outreach Stars",
            message=str(outreach_count),
            color="pink",
            named_logo="megaphone",
            logo_color="white",
        )

    # Reset per-hunter directory before writing fresh files.
    hunters_dir = out_dir / "hunters"
    hunters_dir.mkdir(parents=True, exist_ok=True)
    for old_file in hunters_dir.glob("*.json"):
        old_file.unlink()

    # === Use collision-safe slug mapping ===
    used_slugs: Set[str] = set()
    for row in rows:
        hunter = str(row["hunter"])
        xp = int(row["xp"])
        level = int(row["level"])
        title = str(row["title"])
        slug = slugify_hunter_collision_safe(hunter, used_slugs)
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
        "generated_files": len(list(out_dir.glob("*.json"))) + len(list((out_dir / "hunters").glob("*.json"))),
    }))


if __name__ == "__main__":
    main()
