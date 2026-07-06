"""
star_tracker_security_fix.py — Security improvements for GitHub Star Tracker
- Added proper User-Agent header
- Request timeout
- HTTPS enforcement
- Input validation on star counts
- Error handling for network failures
"""

import sqlite3
import requests
import json
from datetime import datetime
import os
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), "star_tracker.db")
OWNER = "Scottcjn"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_API = "https://api.github.com"
REQUEST_TIMEOUT = 30

REPOS = [
    "Scottcjn/rustchain-bounties",
    "Scottcjn/Rustchain",
    "Scottcjn/bottube",
    "Scottcjn/beacon-skill",
    "Scottcjn/rustchain-miner",
]


class StarTrackerError(Exception):
    """Star tracker error"""
    pass


def get_github_headers() -> dict:
    """Get secure headers for GitHub API requests"""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": f"RustChain-StarTracker/1.0 (python-requests/{requests.__version__})",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def validate_star_count(stars: int, forks: int) -> bool:
    """Validate star/fork counts are reasonable"""
    if not isinstance(stars, int) or stars < 0:
        return False
    if not isinstance(forks, int) or forks < 0:
        return False
    if stars > 10_000_000:  # Sanity cap
        return False
    return True


def fetch_repo_stats(repo_name: str) -> dict:
    """
    Fetch repository statistics from GitHub API

    Security improvements:
    - Enforces HTTPS
    - Sets proper User-Agent
    - Validates response data
    - Handles rate limiting
    """
    url = f"{GITHUB_API}/repos/{repo_name}"

    try:
        response = requests.get(
            url,
            headers=get_github_headers(),
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 403:
            raise StarTrackerError("GitHub API rate limit exceeded")

        if response.status_code == 404:
            raise StarTrackerError(f"Repository not found: {repo_name}")

        response.raise_for_status()
        data = response.json()

        stars = data.get("stargazers_count", 0)
        forks = data.get("forks_count", 0)

        if not validate_star_count(stars, forks):
            raise StarTrackerError(f"Invalid star/fork count for {repo_name}")

        return {
            "name": repo_name,
            "full_name": data.get("full_name", repo_name),
            "stars": stars,
            "forks": forks,
            "description": str(data.get("description", ""))[:500],
            "updated_at": data.get("updated_at", ""),
            "fetched_at": datetime.utcnow().isoformat(),
        }

    except requests.exceptions.Timeout:
        raise StarTrackerError(f"Timeout fetching {repo_name}")
    except requests.exceptions.ConnectionError:
        raise StarTrackerError(f"Connection error fetching {repo_name}")
    except ValueError as e:
        raise StarTrackerError(f"Invalid JSON response: {e}")


def init_db():
    """Initialize SQLite database with proper schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS repos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            full_name TEXT,
            stars INTEGER CHECK(stars >= 0),
            forks INTEGER CHECK(forks >= 0),
            description TEXT,
            updated_at TEXT,
            fetched_at TEXT DEFAULT (datetime('now'))
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_repos_name ON repos(name)
    """)

    conn.commit()
    return conn


def record_stats(conn, stats: dict):
    """Record repository stats in database"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO repos
            (name, full_name, stars, forks, description, updated_at, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        stats["name"],
        stats["full_name"],
        stats["stars"],
        stats["forks"],
        stats["description"],
        stats["updated_at"],
        stats["fetched_at"],
    ))
    conn.commit()


def generate_html_report(stats_list: list) -> str:
    """Generate HTML report from stats"""
    rows = "".join(
        f"<tr>"
        f"<td>{s['name']}</td>"
        f"<td>{s['stars']} ⭐</td>"
        f"<td>{s['forks']} 🍴</td>"
        f"<td>{s.get('fetched_at', 'N/A')}</td>"
        f"</tr>\n"
        for s in stats_list
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>RustChain Star Tracker</title>
<style>body{{font-family:sans-serif;max-width:800px;margin:auto;padding:2em}}
table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #ddd;padding:8px;text-align:left}}
th{{background:#4a90d9;color:white}}
tr:nth-child(even){{background:#f2f2f2}}</style></head>
<body>
<h1>🦀 RustChain Star Tracker</h1>
<p>Last updated: {datetime.utcnow().isoformat()}</p>
<table>
<tr><th>Repository</th><th>Stars</th><th>Forks</th><th>Checked</th></tr>
{rows}
</table>
</body></html>"""


def main():
    conn = init_db()
    all_stats = []

    for repo in REPOS:
        try:
            stats = fetch_repo_stats(repo)
            record_stats(conn, stats)
            all_stats.append(stats)
            print(f"✅ {repo}: {stats['stars']} ⭐, {stats['forks']} 🍴")
        except StarTrackerError as e:
            print(f"❌ {repo}: {e}")
            continue

    # Generate HTML report
    html = generate_html_report(all_stats)
    report_path = os.path.join(os.path.dirname(__file__), "star_tracker.html")
    with open(report_path, "w") as f:
        f.write(html)
    print(f"\n📊 Report saved to: {report_path}")

    conn.close()


if __name__ == "__main__":
    main()
