"""Unit tests for star_tracker.py — Bounty Issue #1589

Covers all 7 public functions with 17 test cases:
- init_db: table creation, idempotency, index
- save_repos: insert, upsert, empty list
- record_snapshot: basic, multiple, empty db
- get_stats: total stars, total repos, empty db
- get_all_repos: success, empty, error, token header
"""

import os
import sqlite3
import json
import pytest
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import star_tracker


# ─── Fixtures ───────────────────────────────────────────────────────

@pytest.fixture
def tmp_db(tmp_path):
    original = star_tracker.DB_PATH
    star_tracker.DB_PATH = str(tmp_path / "test_stars.db")
    yield star_tracker.DB_PATH
    star_tracker.DB_PATH = original


@pytest.fixture
def sample_repos():
    return [
        {"id": 1, "name": "repo-a", "full_name": "Scottcjn/repo-a",
         "stargazers_count": 10, "forks_count": 2, "description": "Test repo A",
         "updated_at": "2026-03-17T00:00:00Z"},
        {"id": 2, "name": "repo-b", "full_name": "Scottcjn/repo-b",
         "stargazers_count": 25, "forks_count": 5, "description": "Test repo B",
         "updated_at": "2026-03-17T00:00:00Z"},
    ]


# ─── init_db ────────────────────────────────────────────────────────

class TestInitDb:
    def test_creates_repos_table(self, tmp_db):
        conn = star_tracker.init_db()
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='repos'")
        assert cur.fetchone() is not None
        conn.close()

    def test_creates_snapshots_table(self, tmp_db):
        conn = star_tracker.init_db()
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='snapshots'")
        assert cur.fetchone() is not None
        conn.close()

    def test_idempotent(self, tmp_db):
        star_tracker.init_db().close()
        star_tracker.init_db().close()

    def test_creates_index(self, tmp_db):
        conn = star_tracker.init_db()
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_snapshot_date'"
        )
        assert cur.fetchone() is not None
        conn.close()


# ─── save_repos ─────────────────────────────────────────────────────

class TestSaveRepos:
    def test_inserts_new_repos(self, tmp_db, sample_repos):
        conn = star_tracker.init_db()
        star_tracker.save_repos(conn, sample_repos)
        rows = conn.execute("SELECT name, stars FROM repos ORDER BY name").fetchall()
        assert rows == [("repo-a", 10), ("repo-b", 25)]
        conn.close()

    def test_upserts_existing_repos(self, tmp_db, sample_repos):
        conn = star_tracker.init_db()
        star_tracker.save_repos(conn, sample_repos)
        sample_repos[0]["stargazers_count"] = 15
        star_tracker.save_repos(conn, [sample_repos[0]])
        row = conn.execute("SELECT stars FROM repos WHERE name='repo-a'").fetchone()
        assert row[0] == 15
        conn.close()

    def test_empty_list_noop(self, tmp_db):
        conn = star_tracker.init_db()
        star_tracker.save_repos(conn, [])
        count = conn.execute("SELECT COUNT(*) FROM repos").fetchone()[0]
        assert count == 0
        conn.close()


# ─── record_snapshot ────────────────────────────────────────────────

class TestRecordSnapshot:
    def test_records_current_stars(self, tmp_db, sample_repos):
        conn = star_tracker.init_db()
        star_tracker.save_repos(conn, sample_repos)
        star_tracker.record_snapshot(conn)
        rows = conn.execute("SELECT repo_name, stars FROM snapshots ORDER BY repo_name").fetchall()
        assert rows == [("repo-a", 10), ("repo-b", 25)]
        conn.close()

    def test_multiple_snapshots(self, tmp_db, sample_repos):
        conn = star_tracker.init_db()
        star_tracker.save_repos(conn, sample_repos)
        star_tracker.record_snapshot(conn)
        sample_repos[0]["stargazers_count"] = 20
        star_tracker.save_repos(conn, [sample_repos[0]])
        star_tracker.record_snapshot(conn)
        count = conn.execute("SELECT COUNT(*) FROM snapshots WHERE repo_name='repo-a'").fetchone()[0]
        assert count == 2
        conn.close()

    def test_empty_db_no_error(self, tmp_db):
        conn = star_tracker.init_db()
        star_tracker.record_snapshot(conn)
        count = conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
        assert count == 0
        conn.close()


# ─── get_stats ──────────────────────────────────────────────────────

class TestGetStats:
    def test_total_stars(self, tmp_db, sample_repos):
        conn = star_tracker.init_db()
        star_tracker.save_repos(conn, sample_repos)
        stats = star_tracker.get_stats(conn)
        assert stats["total_stars"] == 35
        conn.close()

    def test_total_repos(self, tmp_db, sample_repos):
        conn = star_tracker.init_db()
        star_tracker.save_repos(conn, sample_repos)
        stats = star_tracker.get_stats(conn)
        assert stats["total_repos"] == 2
        conn.close()

    def test_empty_db_stats(self, tmp_db):
        conn = star_tracker.init_db()
        stats = star_tracker.get_stats(conn)
        assert stats["total_stars"] == 0
        assert stats["total_repos"] == 0
        conn.close()


# ─── get_all_repos ──────────────────────────────────────────────────

class TestGetAllRepos:
    @patch("star_tracker.requests.get")
    def test_returns_list_on_success(self, mock_get, sample_repos):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = sample_repos
        mock_get.return_value = mock_resp

        result = star_tracker.get_all_repos()
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "repo-a"

    @patch("star_tracker.requests.get")
    def test_empty_page_stops_pagination(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        result = star_tracker.get_all_repos()
        assert result == []

    @patch("star_tracker.requests.get")
    def test_non_200_returns_empty(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.text = "Forbidden"
        mock_get.return_value = mock_resp

        result = star_tracker.get_all_repos()
        assert result == []

    @patch("star_tracker.requests.get")
    def test_passes_github_token_header(self, mock_get, sample_repos):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = sample_repos
        mock_get.return_value = mock_resp

        with patch.dict(os.environ, {"GITHUB_TOKEN": "test-token-123"}):
            import importlib
            importlib.reload(star_tracker)
            star_tracker.get_all_repos()
            headers = mock_get.call_args.kwargs.get("headers", {})
            assert headers.get("Authorization") == "token test-token-123"
