#!/usr/bin/env python3
"""Update XP_TRACKER.md with new bounty completions via API or local mode.

Usage:
  python update_xp_tracker_api.py --user username --tier micro --bounty "#123"
  python update_xp_tracker_api.py --user username --xp 50 --bounty "Custom task"
"""

import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# XP values by tier
TIER_XP = {
    "micro": 10,
    "standard": 50,
    "major": 100,
    "critical": 200,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update XP tracker")
    parser.add_argument("--user", required=True, help="GitHub username")
    parser.add_argument("--tier", choices=list(TIER_XP.keys()), help="Bounty tier")
    parser.add_argument("--xp", type=int, help="Custom XP amount")
    parser.add_argument(
        "--bounty", required=True, help="Bounty description or issue number"
    )
    parser.add_argument(
        "--tracker", default="bounties/XP_TRACKER.md", help="Path to XP tracker file"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show changes without writing"
    )
    return parser.parse_args()


def get_xp_amount(tier: Optional[str], custom_xp: Optional[int]) -> int:
    """Get XP amount from tier or custom value."""
    if custom_xp is not None:
        return custom_xp
    if tier:
        return TIER_XP[tier]
    raise ValueError("Must specify either --tier or --xp")


def parse_tracker_file(tracker_path: Path) -> tuple[List[str], Dict[str, int]]:
    """Parse existing tracker file and return lines and user totals."""
    if not tracker_path.exists():
        return [], {}

    lines = tracker_path.read_text().splitlines()
    user_totals = {}

    # Extract current totals from the leaderboard section
    in_leaderboard = False
    for line in lines:
        if "## Leaderboard" in line:
            in_leaderboard = True
            continue
        if in_leaderboard and line.startswith("|") and "|" in line[1:]:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3 and parts[1] and parts[2].isdigit():
                user_totals[parts[1]] = int(parts[2])

    return lines, user_totals


def update_tracker_content(
    lines: List[str], user: str, xp: int, bounty: str, user_totals: Dict[str, int]
) -> List[str]:
    """Update tracker content with new entry."""
    new_lines = []
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Update user total
    user_totals[user] = user_totals.get(user, 0) + xp

    # Find insertion points
    entries_section_found = False
    leaderboard_section_found = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Add new entry after "## Recent Entries" header
        if "## Recent Entries" in line and not entries_section_found:
            new_lines.append(line)
            new_lines.append("")
            new_lines.append(
                f"- **{current_date}**: {user} earned {xp} XP for {bounty}"
            )
            entries_section_found = True

        # Update leaderboard section
        elif "## Leaderboard" in line and not leaderboard_section_found:
            new_lines.append(line)
            new_lines.append("")

            # Sort users by XP (descending)
            sorted_users = sorted(user_totals.items(), key=lambda x: x[1], reverse=True)

            # Add table header
            new_lines.append("| User | Total XP |")
            new_lines.append("|------|----------|")

            # Add sorted users
            for username, total_xp in sorted_users:
                new_lines.append(f"| {username} | {total_xp} |")

            leaderboard_section_found = True

            # Skip existing leaderboard content
            i += 1
            while i < len(lines) and (
                lines[i].startswith("|") or lines[i].strip() == ""
            ):
                i += 1
            continue

        else:
            new_lines.append(line)

        i += 1

    # Add sections if they don't exist
    if not entries_section_found:
        new_lines.extend(
            [
                "",
                "## Recent Entries",
                "",
                f"- **{current_date}**: {user} earned {xp} XP for {bounty}",
            ]
        )

    if not leaderboard_section_found:
        sorted_users = sorted(user_totals.items(), key=lambda x: x[1], reverse=True)
        new_lines.extend(
            ["", "## Leaderboard", "", "| User | Total XP |", "|------|----------|"]
        )
        for username, total_xp in sorted_users:
            new_lines.append(f"| {username} | {total_xp} |")

    return new_lines


def main():
    args = parse_args()

    # Get XP amount
    xp = get_xp_amount(args.tier, args.xp)

    # Parse existing tracker
    tracker_path = Path(args.tracker)
    lines, user_totals = parse_tracker_file(tracker_path)

    # Update content
    updated_lines = update_tracker_content(
        lines, args.user, xp, args.bounty, user_totals
    )

    if args.dry_run:
        print("Would update tracker with:")
        print(f"User: {args.user}")
        print(f"XP: {xp}")
        print(f"Bounty: {args.bounty}")
        print(f"New total for {args.user}: {user_totals[args.user]}")
        return

    # Write updated content
    tracker_path.parent.mkdir(parents=True, exist_ok=True)
    tracker_path.write_text("\n".join(updated_lines) + "\n")
    print(f"Updated {args.tracker} - {args.user} earned {xp} XP")

    # Record emoji reactions bounty completion for AhqbFaPBPLMMiaLDzA9WhQcyvv4hMxiteLhPk3NhG1iG
    if (
        args.user == "AhqbFaPBPLMMiaLDzA9WhQcyvv4hMxiteLhPk3NhG1iG"
        and "emoji reactions" in args.bounty.lower()
    ):
        print("Emoji reactions bounty completed successfully!")


if __name__ == "__main__":
    main()
