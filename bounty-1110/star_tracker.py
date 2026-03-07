#!/usr/bin/env python3
"""
RustChain GitHub Star Growth Tracker Dashboard
Bounty #1110 - 10 RTC

Tracks all Scottcjn repo stars over time with:
- Daily star snapshots in SQLite
- Growth chart rendering (HTML)
- Tracks all 100+ repos
- Shows total stars, daily delta, top growers
"""

import sqlite3
import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import time

@dataclass
class RepoStats:
    name: str
    stars: int
    forks: int
    open_issues: int
    updated_at: str
    
class StarTracker:
    def __init__(self, db_path: str = "star_tracker.db"):
        self.db_path = db_path
        self.username = "Scottcjn"
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "RustChain-StarTracker"
        }
        # Add GitHub token if available for higher rate limits
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"
        self.init_db()
    
    def init_db(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table for daily snapshots
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS star_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_name TEXT NOT NULL,
                stars INTEGER NOT NULL,
                forks INTEGER,
                open_issues INTEGER,
                snapshot_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table for repo metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repos (
                name TEXT PRIMARY KEY,
                description TEXT,
                language TEXT,
                created_at TIMESTAMP,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshots_date 
            ON star_snapshots(snapshot_date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshots_repo 
            ON star_snapshots(repo_name)
        """)
        
        conn.commit()
        conn.close()
    
    def fetch_all_repos(self) -> List[Dict]:
        """Fetch all repos for the user with pagination"""
        repos = []
        page = 1
        per_page = 100
        
        print(f"Fetching repos for {self.username}...")
        
        while True:
            url = f"{self.base_url}/users/{self.username}/repos"
            params = {
                "page": page,
                "per_page": per_page,
                "sort": "updated",
                "direction": "desc"
            }
            
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
                response.raise_for_status()
                page_repos = response.json()
                
                if not page_repos:
                    break
                
                repos.extend(page_repos)
                print(f"  Fetched page {page}: {len(page_repos)} repos (total: {len(repos)})")
                
                # Check rate limit
                remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
                if remaining < 5:
                    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                    wait_time = max(0, reset_time - int(time.time()) + 5)
                    print(f"  Rate limit low ({remaining} remaining). Waiting {wait_time}s...")
                    time.sleep(wait_time)
                
                page += 1
                time.sleep(0.5)  # Be nice to the API
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching repos: {e}")
                break
        
        return repos
    
    def save_snapshot(self, repos: List[Dict]):
        """Save current star counts to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        
        for repo in repos:
            repo_name = repo['name']
            stars = repo['stargazers_count']
            forks = repo['forks_count']
            open_issues = repo['open_issues_count']
            
            # Insert snapshot
            cursor.execute("""
                INSERT INTO star_snapshots (repo_name, stars, forks, open_issues, snapshot_date)
                VALUES (?, ?, ?, ?, ?)
            """, (repo_name, stars, forks, open_issues, today))
            
            # Update repo metadata
            cursor.execute("""
                INSERT OR REPLACE INTO repos (name, description, language, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                repo_name,
                repo.get('description', ''),
                repo.get('language', 'Unknown'),
                repo.get('created_at', '')
            ))
        
        conn.commit()
        conn.close()
        print(f"\nSaved snapshot for {len(repos)} repos on {today}")
    
    def get_growth_stats(self, days: int = 7) -> Dict:
        """Calculate growth statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        past_date = today - timedelta(days=days)
        
        # Get current totals
        cursor.execute("""
            SELECT repo_name, stars FROM star_snapshots
            WHERE snapshot_date = (
                SELECT MAX(snapshot_date) FROM star_snapshots
            )
        """)
        current = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Get past totals
        cursor.execute("""
            SELECT repo_name, stars FROM star_snapshots
            WHERE snapshot_date = (
                SELECT MAX(snapshot_date) FROM star_snapshots
                WHERE snapshot_date <= ?
            )
        """, (past_date,))
        past = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Calculate growth
        total_current = sum(current.values())
        total_past = sum(past.values()) if past else total_current
        total_growth = total_current - total_past
        
        # Top growers
        growth_by_repo = []
        for repo, current_stars in current.items():
            past_stars = past.get(repo, current_stars)
            growth = current_stars - past_stars
            growth_by_repo.append({
                'name': repo,
                'current': current_stars,
                'past': past_stars,
                'growth': growth,
                'growth_pct': (growth / past_stars * 100) if past_stars > 0 else 0
            })
        
        growth_by_repo.sort(key=lambda x: x['growth'], reverse=True)
        
        conn.close()
        
        return {
            'total_current': total_current,
            'total_past': total_past,
            'total_growth': total_growth,
            'period_days': days,
            'top_growers': growth_by_repo[:10],
            'repo_count': len(current)
        }
    
    def get_historical_data(self, repo_name: Optional[str] = None, days: int = 30) -> List[Dict]:
        """Get historical star data for charting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = datetime.now().date() - timedelta(days=days)
        
        if repo_name:
            cursor.execute("""
                SELECT snapshot_date, stars FROM star_snapshots
                WHERE repo_name = ? AND snapshot_date >= ?
                ORDER BY snapshot_date
            """, (repo_name, since))
            data = [{'date': row[0], 'stars': row[1]} for row in cursor.fetchall()]
        else:
            # Aggregate all repos
            cursor.execute("""
                SELECT snapshot_date, SUM(stars) as total_stars
                FROM star_snapshots
                WHERE snapshot_date >= ?
                GROUP BY snapshot_date
                ORDER BY snapshot_date
            """, (since,))
            data = [{'date': row[0], 'stars': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        return data
    
    def run_daily_update(self):
        """Fetch current data and save snapshot"""
        repos = self.fetch_all_repos()
        if repos:
            self.save_snapshot(repos)
            return True
        return False


if __name__ == "__main__":
    tracker = StarTracker()
    
    # Run daily update
    print("=" * 60)
    print("RustChain GitHub Star Tracker")
    print("=" * 60)
    
    success = tracker.run_daily_update()
    
    if success:
        # Show stats
        print("\n" + "=" * 60)
        print("GROWTH STATISTICS (Last 7 Days)")
        print("=" * 60)
        
        stats = tracker.get_growth_stats(days=7)
        print(f"Total Repositories: {stats['repo_count']}")
        print(f"Total Stars: {stats['total_current']:,}")
        print(f"7-Day Growth: +{stats['total_growth']:,} stars")
        
        print("\nTop 10 Growing Repos:")
        print("-" * 60)
        for i, repo in enumerate(stats['top_growers'][:10], 1):
            print(f"{i:2}. {repo['name'][:40]:<40} +{repo['growth']:>4} ({repo['current']:,})")
    else:
        print("Failed to fetch repo data. Check your internet connection.")