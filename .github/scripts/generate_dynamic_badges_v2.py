#!/usr/bin/env python3
"""Generate shields.io endpoint JSON badges from XP_TRACKER.md.

V2 Enhancements:
- Weekly growth badge
- Top 3 hunters summary badge
- Category badges (docs/outreach/bug) if data exists
- Collision-safe slug mapping
- JSON schema validation
- Deterministic output

Outputs:
- badges/hunter-stats.json
- badges/top-hunter.json
- badges/top-3-hunters.json (NEW)
- badges/active-hunters.json
- badges/legendary-hunters.json
- badges/weekly-growth.json (NEW)
- badges/category-docs.json (NEW, if data exists)
- badges/category-outreach.json (NEW, if data exists)
- badges/category-bug.json (NEW, if data exists)
- badges/updated-at.json
- badges/hunters/<hunter>.json (per hunter)
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracker", default="bounties/XP_TRACKER.md")
    parser.add_argument("--out-dir", default="badges")
    parser.add_argument("--history", default="bounties/XP_HISTORY.md",
                        help="Optional XP history file for growth calculation")
    parser.add_argument("--ledger", default="bounties/LEDGER.md",
                        help="Optional ledger file for category badges")
    return parser.parse_args()


def parse_int(value: str) -> int:
    """Extract integer from string."""
    match = re.search(r"\d+", value or "")
    return int(match.group(0)) if match else 0


def parse_rows(md_text: str) -> List[Dict[str, object]]:
    """Parse hunter rows from XP tracker markdown table."""
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
            "notes": cells[8] if len(cells) > 8 else "",
        }
        rows.append(row)
        i += 1

    # Sort by XP descending, then by name for tie-breaking
    rows.sort(key=lambda item: (-int(item["xp"]), str(item["hunter"]).lower()))
    # Reassign ranks after sorting
    for idx, row in enumerate(rows, start=1):
        row["rank"] = idx
    return rows


def color_for_level(level: int) -> str:
    """Get badge color based on hunter level."""
    if level >= 10:
        return "gold"
    if level >= 7:
        return "purple"
    if level >= 5:
        return "yellow"
    if level >= 4:
        return "orange"
    return "blue"


def slugify_hunter(hunter: str, existing_slugs: Optional[Set[str]] = None) -> str:
    """
    Convert hunter name to URL-safe slug with collision detection.
    
    Args:
        hunter: Hunter name (may include @ prefix)
        existing_slugs: Set of already-used slugs to avoid collisions
    
    Returns:
        Unique slug string
    """
    value = hunter.lstrip("@").strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = value.strip("-")
    base_slug = value or "unknown"
    
    if existing_slugs is None:
        return base_slug
    
    # Handle collisions by appending number
    slug = base_slug
    counter = 1
    while slug in existing_slugs:
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug


def calculate_weekly_growth(rows: List[Dict], history_path: Optional[Path] = None) -> int:
    """
    Calculate XP growth over the past week.
    
    Args:
        rows: Current hunter rows
        history_path: Path to XP history file (optional)
    
    Returns:
        Total XP gained this week
    """
    current_total = sum(int(row["xp"]) for row in rows)
    
    if not history_path or not history_path.exists():
        # No history, assume all XP is "growth" for first run
        return current_total
    
    try:
        history_text = history_path.read_text(encoding="utf-8")
        # Look for last week's total
        # Format: "## Week of YYYY-MM-DD\n\nTotal XP: 12345"
        week_pattern = r"## Week of \d{4}-\d{2}-\d{2}\s*\n\s*Total XP:\s*(\d+)"
        matches = re.findall(week_pattern, history_text)
        
        if matches:
            last_week_total = int(matches[-1])
            return max(0, current_total - last_week_total)
    except Exception:
        pass
    
    return current_total


def parse_category_stats(ledger_path: Optional[Path]) -> Dict[str, int]:
    """
    Parse category statistics from ledger file.
    
    Args:
        ledger_path: Path to LEDGER.md file
    
    Returns:
        Dictionary mapping category names to counts
    """
    stats = {"docs": 0, "outreach": 0, "bug": 0}
    
    if not ledger_path or not ledger_path.exists():
        return stats
    
    try:
        ledger_text = ledger_path.read_text(encoding="utf-8")
        
        # Count by labels in ledger entries
        # Look for patterns like "label: docs" or "[docs]" or "category: outreach"
        docs_patterns = [
            r"label:\s*docs",
            r"\[docs\]",
            r"category:\s*docs",
            r"documentation",
        ]
        outreach_patterns = [
            r"label:\s*outreach",
            r"\[outreach\]",
            r"category:\s*outreach",
            r"social",
            r"marketing",
        ]
        bug_patterns = [
            r"label:\s*bug",
            r"\[bug\]",
            r"category:\s*bug",
            r"bug.?bounty",
            r"security",
        ]
        
        for pattern in docs_patterns:
            stats["docs"] += len(re.findall(pattern, ledger_text, re.IGNORECASE))
        
        for pattern in outreach_patterns:
            stats["outreach"] += len(re.findall(pattern, ledger_text, re.IGNORECASE))
        
        for pattern in bug_patterns:
            stats["bug"] += len(re.findall(pattern, ledger_text, re.IGNORECASE))
            
    except Exception:
        pass
    
    return stats


def validate_badge_json(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate badge JSON against shields.io schema.
    
    Args:
        data: Badge JSON data
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    if "schemaVersion" not in data:
        errors.append("Missing schemaVersion")
    elif data["schemaVersion"] != 1:
        errors.append(f"Invalid schemaVersion: {data['schemaVersion']}")
    
    if "label" not in data:
        errors.append("Missing label")
    elif not isinstance(data["label"], str):
        errors.append("label must be a string")
    
    if "message" not in data:
        errors.append("Missing message")
    elif not isinstance(data["message"], str):
        errors.append("message must be a string")
    
    if "color" not in data:
        errors.append("Missing color")
    elif not isinstance(data["color"], str):
        errors.append("color must be a string")
    
    # Optional fields type checking
    if "namedLogo" in data and not isinstance(data["namedLogo"], str):
        errors.append("namedLogo must be a string")
    
    if "logoColor" in data and not isinstance(data["logoColor"], str):
        errors.append("logoColor must be a string")
    
    return len(errors) == 0, errors


def write_badge(path: Path, label: str, message: str, color: str,
                named_logo: str = "github", logo_color: str = "white",
                validate: bool = True) -> None:
    """
    Write a shields.io badge JSON file.
    
    Args:
        path: Output file path
        label: Badge label
        message: Badge message
        color: Badge color
        named_logo: Logo name
        logo_color: Logo color
        validate: Whether to validate JSON schema
    """
    payload = {
        "schemaVersion": 1,
        "label": label,
        "message": message,
        "color": color,
        "namedLogo": named_logo,
        "logoColor": logo_color,
    }
    
    if validate:
        is_valid, errors = validate_badge_json(payload)
        if not is_valid:
            raise ValueError(f"Invalid badge JSON for {path}: {', '.join(errors)}")
    
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Deterministic output: sort keys and consistent formatting
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8"
    )


def generate_top_3_badge(rows: List[Dict]) -> Tuple[str, str, str]:
    """
    Generate badge data for top 3 hunters.
    
    Returns:
        Tuple of (label, message, color)
    """
    if not rows:
        return "Top 3", "No hunters yet", "lightgrey"
    
    top_3 = rows[:3]
    names = [str(r["hunter"]).lstrip("@") for r in top_3]
    
    if len(names) == 1:
        message = names[0]
    elif len(names) == 2:
        message = f"{names[0]}, {names[1]}"
    else:
        message = f"{names[0]}, {names[1]}, {names[2]}"
    
    # Color based on top hunter's level
    top_level = int(top_3[0]["level"]) if top_3 else 1
    color = color_for_level(top_level)
    
    return "Top 3 Hunters", message, color


def generate_weekly_growth_badge(growth: int) -> Tuple[str, str, str]:
    """
    Generate badge data for weekly XP growth.
    
    Returns:
        Tuple of (label, message, color)
    """
    if growth == 0:
        return "Weekly Growth", "No change", "lightgrey"
    elif growth < 100:
        color = "blue"
    elif growth < 500:
        color = "green"
    elif growth < 1000:
        color = "yellow"
    else:
        color = "brightgreen"
    
    return "Weekly Growth", f"+{growth} XP", color


def generate_category_badge(category: str, count: int) -> Tuple[str, str, str]:
    """
    Generate badge data for a category.
    
    Returns:
        Tuple of (label, message, color)
    """
    colors = {
        "docs": "blue",
        "outreach": "teal",
        "bug": "red",
    }
    color = colors.get(category, "blue")
    
    return f"{category.title()} Bounties", str(count), color


def main() -> None:
    args = parse_args()
    tracker_path = Path(args.tracker)
    out_dir = Path(args.out_dir)
    history_path = Path(args.history) if args.history else None
    ledger_path = Path(args.ledger) if args.ledger else None

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

    # Track existing files for cleanup
    existing_files = set(out_dir.glob("*.json"))
    existing_hunter_files = set((out_dir / "hunters").glob("*.json")) if (out_dir / "hunters").exists() else set()
    
    generated_files: List[Path] = []

    # Core badges (existing functionality)
    badge_configs = [
        (out_dir / "hunter-stats.json", "Bounty Hunter XP", f"{total_xp} total",
         "orange" if total_xp > 0 else "blue", "rust", "white"),
        (out_dir / "top-hunter.json", "Top Hunter", top_msg,
         "gold" if rows else "lightgrey", "crown", "black" if rows else "white"),
        (out_dir / "active-hunters.json", "Active Hunters", str(active_hunters),
         "teal", "users", "white"),
        (out_dir / "legendary-hunters.json", "Legendary Hunters", str(legendary),
         "gold" if legendary > 0 else "lightgrey", "crown", "black" if legendary > 0 else "white"),
    ]
    
    for path, label, message, color, logo, logo_color in badge_configs:
        write_badge(path, label, message, color, logo, logo_color)
        generated_files.append(path)

    # NEW: Top 3 hunters badge
    top3_label, top3_msg, top3_color = generate_top_3_badge(rows)
    top3_path = out_dir / "top-3-hunters.json"
    write_badge(top3_path, top3_label, top3_msg, top3_color, "trophy", "gold")
    generated_files.append(top3_path)

    # NEW: Weekly growth badge
    weekly_growth = calculate_weekly_growth(rows, history_path)
    growth_label, growth_msg, growth_color = generate_weekly_growth_badge(weekly_growth)
    growth_path = out_dir / "weekly-growth.json"
    write_badge(growth_path, growth_label, growth_msg, growth_color, "chart-line", "white")
    generated_files.append(growth_path)

    # NEW: Category badges (only if data exists)
    category_stats = parse_category_stats(ledger_path)
    for category, count in category_stats.items():
        if count > 0:
            cat_label, cat_msg, cat_color = generate_category_badge(category, count)
            cat_path = out_dir / f"category-{category}.json"
            write_badge(cat_path, cat_label, cat_msg, cat_color, "tag", "white")
            generated_files.append(cat_path)

    # Updated timestamp
    updated_path = out_dir / "updated-at.json"
    write_badge(
        updated_path,
        label="XP Updated",
        message=dt.datetime.now(dt.UTC).strftime("%Y-%m-%d"),
        color="blue",
        named_logo="clockify",
        logo_color="white",
    )
    generated_files.append(updated_path)

    # Per-hunter badges with collision-safe slugs
    hunters_dir = out_dir / "hunters"
    hunters_dir.mkdir(parents=True, exist_ok=True)
    
    # Clean old hunter files
    for old_file in hunters_dir.glob("*.json"):
        old_file.unlink()
    
    used_slugs: Set[str] = set()
    for row in rows:
        hunter = str(row["hunter"])
        xp = int(row["xp"])
        level = int(row["level"])
        title = str(row["title"])
        
        # Use collision-safe slug
        slug = slugify_hunter(hunter, used_slugs)
        used_slugs.add(slug)
        
        hunter_path = hunters_dir / f"{slug}.json"
        write_badge(
            hunter_path,
            label=f"{hunter} XP",
            message=f"{xp} (L{level} {title})",
            color=color_for_level(level),
            named_logo="github",
            logo_color="white",
        )
        generated_files.append(hunter_path)

    # Output summary
    output = {
        "total_xp": total_xp,
        "active_hunters": active_hunters,
        "legendary_hunters": legendary,
        "top_hunter": top_msg,
        "weekly_growth": weekly_growth,
        "category_stats": category_stats,
        "generated_files": len(generated_files),
        "collision_free_slugs": len(used_slugs),
    }
    
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
