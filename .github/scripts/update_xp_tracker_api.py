#!/usr/bin/env python3
"""GitHub API-driven XP tracker updater for RustChain bounties.

Flow:
1) GET tracker markdown from repo contents API
2) Parse leaderboard table
3) Update/add hunter row with XP, level/title, badges
4) Re-rank by total XP
5) Append award log line
6) PUT updated file back to GitHub

Also supports local dry-run mode for testing (`--local-file`).
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import quote

import requests


LEVEL_THRESHOLDS: List[Tuple[int, int, str]] = [
    (0, 1, "Starting Hunter"),
    (200, 2, "Basic Hunter"),
    (500, 3, "Priority Hunter"),
    (1000, 4, "Rising Hunter"),
    (2000, 5, "Multiplier Hunter"),
    (3500, 6, "Featured Hunter"),
    (5500, 7, "Veteran Hunter"),
    (8000, 8, "Elite Hunter"),
    (12000, 9, "Master Hunter"),
    (18000, 10, "Legendary Hunter"),
]

BADGE_STYLE: Dict[str, Tuple[str, str, str]] = {
    "First Blood": ("red", "git", "white"),
    "Rising Hunter": ("orange", "rocket", "white"),
    "Multiplier Hunter": ("yellow", "star", "black"),
    "Veteran Hunter": ("purple", "shield", "white"),
    "Legendary Hunter": ("gold", "crown", "black"),
    "Vintage Veteran": ("purple", "apple", "white"),
    "Agent Overlord": ("cyan", "robot", "white"),
    "Tutorial Titan": ("blue", "book", "white"),
    "Bug Slayer": ("darkred", "bug", "white"),
    "Outreach Pro": ("teal", "twitter", "white"),
    "Streak Master": ("green", "fire", "white"),
}


@dataclass
class HunterRow:
    hunter: str
    wallet: str
    xp: int
    level: int
    title: str
    badges: Set[str]
    last_action: str
    notes: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", default="")
    parser.add_argument("--repo", default="")
    parser.add_argument("--actor", required=True)
    parser.add_argument("--event-type", default="workflow_dispatch")
    parser.add_argument("--event-action", default="")
    parser.add_argument("--issue-number", type=int, default=0)
    parser.add_argument("--labels", default="")
    parser.add_argument("--pr-merged", default="false")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--tracker-path", default="bounties/XP_TRACKER.md")
    parser.add_argument("--local-file", default="")
    return parser.parse_args()


def is_true(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def parse_labels(raw: str) -> Set[str]:
    labels: Set[str] = set()
    for token in (raw or "").split(","):
        token = token.strip().lower()
        if token:
            labels.add(token)
    return labels


def get_level_and_title(total_xp: int) -> Tuple[int, str]:
    for threshold, level, title in reversed(LEVEL_THRESHOLDS):
        if total_xp >= threshold:
            return level, title
    return 1, "Starting Hunter"


def calculate_xp(event_type: str, event_action: str, labels: Set[str], pr_merged: bool) -> Tuple[int, str]:
    xp = 0
    reasons: List[str] = []

    if "bounty-approved" in labels:
        xp += 200
        reasons.append("bounty approved")

    if pr_merged:
        xp += 300
        reasons.append("PR merged")

    if event_type == "issues" and event_action == "closed":
        xp += 80
        reasons.append("issue closed")

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
    if "tutorial" in labels or "docs" in labels:
        xp += 150
        reasons.append("tutorial/docs")
    if "vintage" in labels:
        xp += 100
        reasons.append("vintage bonus")

    # RTC extraction from labels or comments would go here.
    # For now, we rely on the award reason containing "X RTC" for the badge script.
    rtc_match = re.search(r"(\d+)\s*rtc", (",".join(labels)).lower())
    if rtc_match:
        reasons.append(f"{rtc_match.group(1)} RTC")
    if "outreach" in labels or "seo" in labels or "marketing" in labels:
        xp += 30
        reasons.append("outreach bonus")

    if xp == 0:
        xp = 50
        reasons.append("base action")

    return xp, ", ".join(reasons)


def badge_url(name: str) -> str:
    color, logo, logo_color = BADGE_STYLE.get(name, ("blue", "star", "white"))
    encoded = quote(name)
    return (
        f"https://img.shields.io/badge/{encoded}-{color}"
        f"?style=flat-square&logo={logo}&logoColor={logo_color}"
    )


def badge_md(name: str) -> str:
    return f"![{name}]({badge_url(name)})"


def parse_badges(cell: str) -> Set[str]:
    names = set(re.findall(r"!\[([^\]]+)\]", cell or ""))
    if names:
        return names

    fallback = set()
    for token in (cell or "").split(","):
        token = token.strip()
        if token and token != "-":
            fallback.add(token)
    return fallback


def format_badges(names: Set[str]) -> str:
    if not names:
        return "-"
    ordered = sorted(names)
    return " ".join(badge_md(name) for name in ordered)


def parse_table_cells(line: str) -> List[str]:
    return [part.strip() for part in line.strip().split("|")[1:-1]]


def render_row(rank: int, row: HunterRow) -> str:
    return (
        f"| {rank} | {row.hunter} | {row.wallet} | {row.xp} | {row.level} | {row.title} | "
        f"{format_badges(row.badges)} | {row.last_action} | {row.notes} |"
    )


def parse_hunter_row(cells: List[str]) -> Optional[HunterRow]:
    if len(cells) < 7:
        return None

    # New schema: 9 columns after splitting
    if len(cells) >= 9:
        try:
            xp_val = int(float(cells[3]))
        except Exception:
            xp_val = 0
        try:
            level_val = int(float(cells[4]))
        except Exception:
            level_val = get_level_and_title(xp_val)[0]

        title_val = cells[5].strip() or get_level_and_title(xp_val)[1]
        return HunterRow(
            hunter=cells[1].strip(),
            wallet=cells[2].strip() or "_TBD_",
            xp=xp_val,
            level=level_val,
            title=title_val,
            badges=parse_badges(cells[6]),
            last_action=cells[7].strip(),
            notes=cells[8].strip(),
        )

    # Backward compatibility with older schema (7 columns)
    try:
        xp_val = int(float(cells[3]))
    except Exception:
        xp_val = 0
    try:
        level_val = int(float(cells[4]))
    except Exception:
        level_val = get_level_and_title(xp_val)[0]

    _, title = get_level_and_title(xp_val)
    return HunterRow(
        hunter=cells[1].strip(),
        wallet=cells[2].strip() or "_TBD_",
        xp=xp_val,
        level=level_val,
        title=title,
        badges=set(),
        last_action=cells[5].strip() if len(cells) > 5 else "",
        notes=cells[6].strip() if len(cells) > 6 else "",
    )


def determine_new_badges(existing: Set[str], old_xp: int, new_xp: int,
                         labels: Set[str], actor: str) -> List[str]:
    unlocked: List[str] = []

    def maybe(name: str, cond: bool):
        if cond and name not in existing and name not in unlocked:
            unlocked.append(name)

    maybe("First Blood", new_xp > 0)
    maybe("Rising Hunter", new_xp >= 1000)
    maybe("Multiplier Hunter", new_xp >= 2000)
    maybe("Veteran Hunter", new_xp >= 5500)
    maybe("Legendary Hunter", new_xp >= 18000)
    maybe("Vintage Veteran", "vintage" in labels)
    maybe("Tutorial Titan", "tutorial" in labels or "docs" in labels)
    maybe("Bug Slayer", "bug" in labels or "security" in labels or "critical" in labels)
    maybe("Outreach Pro", "outreach" in labels or "seo" in labels or "marketing" in labels)
    maybe("Streak Master", "streak" in labels)
    maybe("Agent Overlord", "agent" in actor.lower() and new_xp >= 500)

    return unlocked


def update_frontmatter(md: str) -> str:
    today = dt.date.today().isoformat()
    return re.sub(r"last_updated:\s*\d{4}-\d{2}-\d{2}", f"last_updated: {today}", md, count=1)


def update_table_in_md(md: str, actor: str, gained_xp: int, reason: str,
                       labels: Set[str]) -> Tuple[str, int, int, str, List[str]]:
    lines = md.splitlines()

    header_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("| Rank | Hunter"):
            header_idx = i
            break
    if header_idx < 0:
        raise RuntimeError("Leaderboard table header not found")

    start = header_idx + 2
    end = start
    while end < len(lines) and lines[end].strip().startswith("|"):
        end += 1

    rows: List[HunterRow] = []
    for line in lines[start:end]:
        cells = parse_table_cells(line)
        row = parse_hunter_row(cells)
        if not row:
            continue
        if row.hunter == "_TBD_":
            continue
        rows.append(row)

    # Backfill threshold-based badges for existing hunters each run.
    for row in rows:
        retro = determine_new_badges(
            existing=row.badges,
            old_xp=row.xp,
            new_xp=row.xp,
            labels=set(),
            actor=row.hunter,
        )
        row.badges.update(retro)

    actor_key = f"@{actor}"
    target: Optional[HunterRow] = None
    for row in rows:
        if row.hunter.strip() == actor_key:
            target = row
            break

    if target is None:
        target = HunterRow(
            hunter=actor_key,
            wallet="_TBD_",
            xp=0,
            level=1,
            title="Starting Hunter",
            badges=set(),
            last_action="first award",
            notes="auto-tracked",
        )
        rows.append(target)

    old_xp = int(target.xp)
    new_total = old_xp + int(gained_xp)
    level, title = get_level_and_title(new_total)

    unlocked = determine_new_badges(
        existing=target.badges,
        old_xp=old_xp,
        new_xp=new_total,
        labels=labels,
        actor=actor,
    )
    target.badges.update(unlocked)

    stamp = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC")
    target.xp = new_total
    target.level = level
    target.title = title
    target.last_action = f"{stamp} (+{gained_xp} XP: {reason})"

    rows.sort(key=lambda row: (-row.xp, row.hunter.lower()))
    new_table_lines = [render_row(idx, row) for idx, row in enumerate(rows, start=1)]
    if not new_table_lines:
        new_table_lines = [
            "| 1 | _TBD_ | _TBD_ | 0 | 1 | Starting Hunter | - | bootstrap | tracker initialized |"
        ]

    rebuilt = lines[:start] + new_table_lines + lines[end:]
    md_new = "\n".join(rebuilt)

    award_line = (
        f"- {stamp}: @{actor} earned **{gained_xp} XP** ({reason}) -> "
        f"Total: {new_total} XP (Level {level} - {title})"
    )
    if unlocked:
        award_line += f" | New badges: {', '.join(unlocked)}"

    marker = "## Latest Awards"
    idx = md_new.find(marker)
    if idx >= 0:
        insert = md_new.find("\n\n", idx)
        if insert >= 0:
            md_new = md_new[: insert + 2] + award_line + "\n" + md_new[insert + 2 :]
        else:
            md_new += "\n\n" + award_line + "\n"
    else:
        md_new += "\n\n## Latest Awards\n\n" + award_line + "\n"

    return md_new.rstrip() + "\n", new_total, level, title, unlocked


def api_headers(token: str) -> Dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def get_file_contents(token: str, repo: str, path: str, branch: str) -> Tuple[str, str]:
    url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={quote(branch)}"
    resp = requests.get(url, headers=api_headers(token), timeout=30)
    resp.raise_for_status()
    data = resp.json()
    content = base64.b64decode(data["content"]).decode("utf-8")
    sha = data["sha"]
    return content, sha


def put_file_contents(token: str, repo: str, path: str, branch: str,
                      sha: str, content: str, message: str) -> str:
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    payload = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "sha": sha,
        "branch": branch,
    }
    resp = requests.put(url, headers=api_headers(token), json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["commit"]["html_url"]


def main() -> None:
    args = parse_args()

    labels = parse_labels(args.labels)
    pr_merged = is_true(args.pr_merged)
    gained_xp, reason = calculate_xp(
        event_type=args.event_type,
        event_action=args.event_action,
        labels=labels,
        pr_merged=pr_merged,
    )

    if args.local_file:
        with open(args.local_file, "r", encoding="utf-8") as fh:
            md = fh.read()
        md = update_frontmatter(md)
        updated_md, total_xp, level, title, unlocked = update_table_in_md(
            md=md,
            actor=args.actor,
            gained_xp=gained_xp,
            reason=reason,
            labels=labels,
        )
        with open(args.local_file, "w", encoding="utf-8") as fh:
            fh.write(updated_md)
        result = {
            "mode": "local",
            "actor": args.actor,
            "awarded_xp": gained_xp,
            "total_xp": total_xp,
            "level": level,
            "title": title,
            "reason": reason,
            "new_badges": unlocked,
            "commit_url": "",
        }
        print(json.dumps(result))
        return

    if not args.token or not args.repo:
        raise SystemExit("--token and --repo are required in API mode")

    max_attempts = 4
    commit_url = ""
    total_xp = 0
    level = 1
    title = "Starting Hunter"
    unlocked: List[str] = []
    conflict_exhausted = False

    message = f"chore(xp): update tracker for @{args.actor} (+{gained_xp} XP)"

    for attempt in range(1, max_attempts + 1):
        content, sha = get_file_contents(
            token=args.token,
            repo=args.repo,
            path=args.tracker_path,
            branch=args.branch,
        )
        content = update_frontmatter(content)
        updated_md, total_xp, level, title, unlocked = update_table_in_md(
            md=content,
            actor=args.actor,
            gained_xp=gained_xp,
            reason=reason,
            labels=labels,
        )

        try:
            commit_url = put_file_contents(
                token=args.token,
                repo=args.repo,
                path=args.tracker_path,
                branch=args.branch,
                sha=sha,
                content=updated_md,
                message=message,
            )
            break
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else None
            if status == 409:
                if attempt < max_attempts:
                    continue
                conflict_exhausted = True
                break
            raise

    result_reason = reason
    if conflict_exhausted:
        result_reason = f"{reason}; commit_conflict_skipped"

    result = {
        "mode": "api",
        "actor": args.actor,
        "awarded_xp": gained_xp,
        "total_xp": total_xp,
        "level": level,
        "title": title,
        "reason": result_reason,
        "new_badges": unlocked,
        "commit_url": commit_url,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
