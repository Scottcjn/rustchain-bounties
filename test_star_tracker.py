import sqlite3
import pytest
from unittest.mock import patch, MagicMock
from star_tracker import init_db, get_stats, save_repos

@pytest.fixture
def mock_db():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
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
    conn.commit()
    yield conn
    conn.close()

def test_save_repos_and_get_stats(mock_db):
    repos = [
        {
            "id": 1,
            "name": "Rustchain",
            "full_name": "Scottcjn/Rustchain",
            "stargazers_count": 150,
            "forks_count": 10,
            "description": "A blockchain",
            "updated_at": "2026-04-03"
        },
        {
            "id": 2,
            "name": "Another-Repo",
            "full_name": "Scottcjn/Another-Repo",
            "stargazers_count": 50,
            "forks_count": 2,
            "description": "Some tool",
            "updated_at": "2026-04-03"
        }
    ]
    
    save_repos(mock_db, repos)
    
    # Add fake snapshots to make get_stats work
    cursor = mock_db.cursor()
    cursor.execute("INSERT INTO snapshots (repo_name, stars, recorded_at) VALUES ('Rustchain', 150, '2026-04-03')")
    cursor.execute("INSERT INTO snapshots (repo_name, stars, recorded_at) VALUES ('Another-Repo', 50, '2026-04-03')")
    mock_db.commit()

    stats = get_stats(mock_db)
    
    assert stats["total_stars"] == 200
    assert stats["total_repos"] == 2
    assert stats["main_stars"] == 150
    assert len(stats["top_repos"]) == 2
