# RustChain GitHub Star Growth Tracker Dashboard

**Bounty #1110 - 10 RTC**

A comprehensive dashboard for tracking GitHub star growth across all Scottcjn repositories.

## Features

✨ **Daily Snapshots** - Automatically stores star counts in SQLite database  
📊 **Interactive Charts** - Beautiful visualizations using Chart.js  
📈 **Growth Tracking** - 7-day and 30-day growth statistics  
🏆 **Top Growers** - Identify fastest-growing repositories  
⭐ **Leaderboard** - Top repositories by total stars  
🦀 **RustChain Theme** - Dark gradient UI with Rust orange accents

## Requirements

- Python 3.7+
- requests library

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### 1. Run the Star Tracker

Fetch current GitHub data and save to database:

```bash
python star_tracker.py
```

This will:
- Fetch all repositories for user `Scottcjn`
- Store star counts, forks, and open issues
- Save a daily snapshot to SQLite

### 2. Generate the Dashboard

Create the interactive HTML dashboard:

```bash
python dashboard.py
```

This generates `dashboard.html` with:
- Total repository count
- Total stars across all repos
- 7-day and 30-day growth metrics
- Interactive growth chart
- Top growing repositories table
- Top repositories by stars

### 3. View the Dashboard

Open `dashboard.html` in your web browser:

```bash
# macOS
open dashboard.html

# Linux
xdg-open dashboard.html

# Windows
start dashboard.html
```

## Database Schema

### star_snapshots
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| repo_name | TEXT | Repository name |
| stars | INTEGER | Star count |
| forks | INTEGER | Fork count |
| open_issues | INTEGER | Open issues count |
| snapshot_date | DATE | Date of snapshot |
| created_at | TIMESTAMP | When record was created |

### repos
| Column | Type | Description |
|--------|------|-------------|
| name | TEXT | Repository name (PK) |
| description | TEXT | Repo description |
| language | TEXT | Primary language |
| created_at | TIMESTAMP | Repo creation date |
| first_seen | TIMESTAMP | When first tracked |

## API Rate Limits

The tracker respects GitHub API rate limits:
- Unauthenticated: 60 requests/hour
- Authenticated: 5,000 requests/hour

To use authentication, set the `GITHUB_TOKEN` environment variable:

```bash
export GITHUB_TOKEN=your_token_here
python star_tracker.py
```

## Automation

To run daily updates automatically, add to crontab:

```bash
# Daily at 9 AM
0 9 * * * cd /path/to/bounty-1110 && python star_tracker.py && python dashboard.py
```

## Screenshots

The dashboard includes:
- **Stats Cards**: Total repos, total stars, growth metrics
- **Growth Chart**: 30-day star growth visualization
- **Top Growers**: Fastest-growing repos (7 days)
- **Star Leaderboard**: Top repos by total stars

## Files

| File | Description |
|------|-------------|
| `star_tracker.py` | Core tracking logic and database operations |
| `dashboard.py` | HTML dashboard generator |
| `requirements.txt` | Python dependencies |
| `star_tracker.db` | SQLite database (created on first run) |
| `dashboard.html` | Generated dashboard (created by dashboard.py) |

## Sample Output

```
============================================================
RustChain GitHub Star Tracker
============================================================
Fetching repos for Scottcjn...
  Fetched page 1: 100 repos (total: 100)
  Fetched page 2: 45 repos (total: 145)

Saved snapshot for 145 repos on 2026-03-07

============================================================
GROWTH STATISTICS (Last 7 Days)
============================================================
Total Repositories: 145
Total Stars: 12,847
7-Day Growth: +234 stars

Top 10 Growing Repos:
------------------------------------------------------------
 1. rustchain-bounties                      +45 (128)
 2. rustchain-core                          +32 (2,456)
 3. rustchain-miner                         +28 (892)
 ...
```

## License

MIT License - Created for RustChain Bounty #1110

---

**Wallet for RTC payout:** `sovereign-agent`