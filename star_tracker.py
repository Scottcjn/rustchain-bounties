#!/usr/bin/env python3
"""
GitHub Star Tracker - Track Scottcjn repo stars over time
Bounty: https://github.com/Scottcjn/rustchain-bounties/issues/1110
"""

import sqlite3
import requests
import json
from datetime import datetime, date
import os

# Configuration
DB_PATH = "star_tracker.db"
OWNER = "Scottcjn"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# API Endpoints
GITHUB_API = "https://api.github.com"


def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS repos (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            full_name TEXT,
            stars INTEGER,
            forks INTEGER,
            description TEXT,
            updated_at TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_name TEXT NOT NULL,
            stars INTEGER NOT NULL,
            recorded_at TEXT NOT NULL,
            FOREIGN KEY (repo_name) REFERENCES repos (name)
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_snapshot_date 
        ON snapshots (recorded_at)
    """)
    
    conn.commit()
    return conn


def get_all_repos():
    """Fetch all repos for the owner"""
    repos = []
    page = 1
    per_page = 100
    
    while True:
        url = f"{GITHUB_API}/users/{OWNER}/repos"
        params = {"per_page": per_page, "page": page, "type": "all"}
        headers = {"Accept": "application/vnd.github.v3+json"}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
        
        resp = requests.get(url, params=params, headers=headers)
        
        if resp.status_code != 200:
            print(f"Error fetching repos: {resp.status_code} - {resp.text}")
            break
        
        data = resp.json()
        if not data:
            break
            
        repos.extend(data)
        
        if len(data) < per_page:
            break
        page += 1
    
    return repos


def save_repos(conn, repos):
    """Save repo info to database"""
    cursor = conn.cursor()
    
    for repo in repos:
        cursor.execute("""
            INSERT OR REPLACE INTO repos 
            (id, name, full_name, stars, forks, description, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            repo["id"],
            repo["name"],
            repo["full_name"],
            repo["stargazers_count"],
            repo["forks_count"],
            repo["description"],
            repo["updated_at"]
        ))
    
    conn.commit()
    print(f"Saved {len(repos)} repos")


def record_snapshot(conn, repos, when=None):
    """Record a daily snapshot of stars for each repo.
    
    If a snapshot already exists for the same repo on the same date, update it.
    """
    cursor = conn.cursor()

    # Normalize date to YYYY-MM-DD string (daily granularity)
    if when is None:
        day = date.today().isoformat()
    else:
        if isinstance(when, datetime):
            day = when.date().isoformat()
        elif isinstance(when, date):
            day = when.isoformat()
        else:
            # Accept string-like; use only the date portion if present
            day = str(when)[:10]

    count = 0
    for repo in repos:
        name = repo.get("name")
        stars = repo.get("stargazers_count")

        if name is None or stars is None:
            continue

        # Check if a snapshot already exists for this repo on this date
        cursor.execute(
            "SELECT id FROM snapshots WHERE repo_name = ? AND recorded_at = ?",
            (name, day)
        )
        row = cursor.fetchone()
        if row:
            cursor.execute(
                "UPDATE snapshots SET stars = ? WHERE id = ?",
                (stars, row[0])
            )
        else:
            cursor.execute(
                "INSERT INTO snapshots (repo_name, stars, recorded_at) VALUES (?, ?, ?)",
                (name, stars, day)
            )
        count += 1

    conn.commit()
    print(f"Recorded snapshot for {count} repos on {day}")


def main():
    conn = init_db()
    repos = get_all_repos()
    if not repos:
        print("No repositories fetched. Exiting.")
        return
    save_repos(conn, repos)
    record_snapshot(conn, repos)
    conn.close()


if __name__ == "__main__":
    main()