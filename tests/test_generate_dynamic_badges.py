#!/usr/bin/env python3
"""
Tests for .github/scripts/generate_dynamic_badges.py
Covers: empty table, populated table, slug generation, schema correctness, deterministic output
"""

import pytest
import json
import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.github', 'scripts'))

from generate_dynamic_badges import (
    parse_rows,
    parse_int,
    color_for_level,
    slugify_hunter,
    write_badge,
)


# ===== Parse Integer Tests =====

class TestParseInt:
    """Test integer extraction from strings"""

    def test_plain_number(self):
        assert parse_int("42") == 42

    def test_number_with_text(self):
        assert parse_int("Level 5") == 5

    def test_empty_string(self):
        assert parse_int("") == 0

    def test_none_value(self):
        assert parse_int(None) == 0

    def test_no_number(self):
        assert parse_int("no digits here") == 0

    def test_float_string(self):
        """Should extract the first integer part"""
        assert parse_int("3.14") == 3

    def test_negative_style(self):
        """regex r'\\d+' finds first digits, so -5 -> 5"""
        assert parse_int("-5") == 5


# ===== Slug Generation Tests =====

class TestSlugifyHunter:
    """Test hunter name slugification for filenames"""

    def test_simple_name(self):
        assert slugify_hunter("alice") == "alice"

    def test_at_prefix(self):
        """Should strip leading @"""
        assert slugify_hunter("@alice") == "alice"

    def test_spaces(self):
        """Spaces should become hyphens"""
        assert slugify_hunter("john doe") == "john-doe"

    def test_special_characters(self):
        """Special chars should become hyphens"""
        slug = slugify_hunter("test!@#$user")
        assert re.match(r"^[a-z0-9._-]+$", slug), f"Slug contains invalid chars: {slug}"

    def test_uppercase(self):
        """Should be lowercased"""
        assert slugify_hunter("Alice") == "alice"

    def test_empty_string(self):
        assert slugify_hunter("") == "unknown"

    def test_only_special_chars(self):
        assert slugify_hunter("@@@") == "unknown"

    def test_dots_and_hyphens(self):
        """Dots and hyphens should be preserved"""
        assert slugify_hunter("user.name-test") == "user.name-test"

    def test_trailing_special_chars(self):
        """Should not have trailing hyphens"""
        slug = slugify_hunter("test---")
        assert not slug.endswith("-")

    def test_unicode_chars(self):
        """Non-ascii should be replaced"""
        slug = slugify_hunter("用户测试")
        assert re.match(r"^[a-z0-9._-]+$", slug) or slug == "unknown"

    def test_collision_safe_slugs(self):
        """Different inputs should produce different slugs when possible"""
        slug1 = slugify_hunter("alice")
        slug2 = slugify_hunter("bob")
        assert slug1 != slug2


# ===== Color for Level Tests =====

class TestColorForLevel:
    """Test badge color assignment by level"""

    def test_level_1(self):
        assert color_for_level(1) == "blue"

    def test_level_3(self):
        assert color_for_level(3) == "blue"

    def test_level_4(self):
        assert color_for_level(4) == "orange"

    def test_level_5(self):
        assert color_for_level(5) == "yellow"

    def test_level_7(self):
        assert color_for_level(7) == "purple"

    def test_level_10(self):
        assert color_for_level(10) == "gold"

    def test_level_15(self):
        """Levels above 10 should still be gold"""
        assert color_for_level(15) == "gold"

    def test_level_0(self):
        """Level 0 should be blue (fallback)"""
        assert color_for_level(0) == "blue"


# ===== Table Parsing Tests =====

POPULATED_TABLE = """# Bounty Hunter Leaderboard

| Rank | Hunter | Wallet | XP | Level | Title | Badges | Last Action | Notes |
|------|--------|--------|----|-------|-------|--------|-------------|-------|
| 1 | @alice | wallet-a | 1500 | 4 | Rising Hunter | - | 2024-01-15 | top |
| 2 | @bob | wallet-b | 800 | 3 | Priority Hunter | - | 2024-01-14 | |
| 3 | @charlie | wallet-c | 200 | 2 | Basic Hunter | - | 2024-01-13 | new |
"""

EMPTY_TABLE = """# Bounty Hunter Leaderboard

| Rank | Hunter | Wallet | XP | Level | Title | Badges | Last Action | Notes |
|------|--------|--------|----|-------|-------|--------|-------------|-------|
"""

NO_TABLE = """# No leaderboard table here

Just some random text.
"""

TBD_TABLE = """# Bounty Hunter Leaderboard

| Rank | Hunter | Wallet | XP | Level | Title | Badges | Last Action | Notes |
|------|--------|--------|----|-------|-------|--------|-------------|-------|
| 1 | _TBD_ | _TBD_ | 0 | 1 | Starting Hunter | - | bootstrap | tracker initialized |
"""


class TestParseRows:
    """Test leaderboard table parsing"""

    def test_populated_table(self):
        rows = parse_rows(POPULATED_TABLE)
        assert len(rows) == 3
        assert rows[0]["hunter"] == "@alice"
        assert rows[0]["xp"] == 1500

    def test_empty_table(self):
        rows = parse_rows(EMPTY_TABLE)
        assert len(rows) == 0

    def test_no_table(self):
        rows = parse_rows(NO_TABLE)
        assert len(rows) == 0

    def test_tbd_rows_excluded(self):
        rows = parse_rows(TBD_TABLE)
        assert len(rows) == 0

    def test_sort_by_xp_descending(self):
        rows = parse_rows(POPULATED_TABLE)
        for i in range(len(rows) - 1):
            assert rows[i]["xp"] >= rows[i + 1]["xp"]

    def test_rank_recalculated(self):
        """Ranks should be sequential starting from 1"""
        rows = parse_rows(POPULATED_TABLE)
        for i, row in enumerate(rows):
            assert row["rank"] == i + 1

    def test_mixed_content_robustness(self):
        """Should handle rows with varying content"""
        md = """| Rank | Hunter | Wallet | XP | Level | Title | Badges | Last Action | Notes |
|------|--------|--------|----|-------|-------|--------|-------------|-------|
| 1 | @user1 | w1 | 100 | 1 | Starting Hunter | ![First Blood](url) | today | |
| 2 | @user2 | w2 | 50 | 1 | Starting Hunter | - | yesterday | test note |
"""
        rows = parse_rows(md)
        assert len(rows) == 2
        assert rows[0]["xp"] == 100
        assert rows[1]["xp"] == 50


# ===== Write Badge Tests =====

class TestWriteBadge:
    """Test badge JSON file writing"""

    def test_write_badge_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test-badge.json"
            write_badge(path, "Test Label", "Test Message", "blue")
            assert path.exists()

    def test_write_badge_valid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test-badge.json"
            write_badge(path, "Test Label", "Test Message", "green")
            data = json.loads(path.read_text())
            assert data["schemaVersion"] == 1
            assert data["label"] == "Test Label"
            assert data["message"] == "Test Message"
            assert data["color"] == "green"

    def test_write_badge_schema_correctness(self):
        """Badge JSON should have all required shields.io fields"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "schema-test.json"
            write_badge(path, "L", "M", "red", "github", "white")
            data = json.loads(path.read_text())
            required_keys = {"schemaVersion", "label", "message", "color", "namedLogo", "logoColor"}
            assert required_keys.issubset(set(data.keys()))

    def test_write_badge_creates_parent_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sub" / "dir" / "badge.json"
            write_badge(path, "L", "M", "blue")
            assert path.exists()

    def test_write_badge_deterministic_output(self):
        """Same inputs should produce identical output"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path1 = Path(tmpdir) / "badge1.json"
            path2 = Path(tmpdir) / "badge2.json"
            write_badge(path1, "Same", "Data", "blue")
            write_badge(path2, "Same", "Data", "blue")
            assert path1.read_text() == path2.read_text()


# ===== Integration Tests =====

class TestBadgeGenIntegration:
    """Integration tests combining parsing and badge generation"""

    def test_populated_table_generates_correct_stats(self):
        rows = parse_rows(POPULATED_TABLE)
        total_xp = sum(int(r["xp"]) for r in rows)
        active_hunters = len(rows)
        legendary = sum(1 for r in rows if int(r["level"]) >= 10)

        assert total_xp == 2500  # 1500 + 800 + 200
        assert active_hunters == 3
        assert legendary == 0

    def test_empty_table_stats(self):
        rows = parse_rows(EMPTY_TABLE)
        total_xp = sum(int(r["xp"]) for r in rows)
        assert total_xp == 0
        assert len(rows) == 0

    def test_per_hunter_badge_generation(self):
        """Each hunter should get a correctly slugified badge file"""
        rows = parse_rows(POPULATED_TABLE)
        with tempfile.TemporaryDirectory() as tmpdir:
            hunters_dir = Path(tmpdir) / "hunters"
            hunters_dir.mkdir()

            for row in rows:
                hunter = str(row["hunter"])
                xp = int(row["xp"])
                level = int(row["level"])
                title = str(row["title"])
                slug = slugify_hunter(hunter)
                write_badge(
                    hunters_dir / f"{slug}.json",
                    label=f"{hunter} XP",
                    message=f"{xp} (L{level} {title})",
                    color=color_for_level(level),
                )

            # Verify files were created
            json_files = list(hunters_dir.glob("*.json"))
            assert len(json_files) == 3

            # Verify each file is valid JSON with correct schema
            for jf in json_files:
                data = json.loads(jf.read_text())
                assert data["schemaVersion"] == 1
                assert "XP" in data["label"]


# Need the import for regex
import re


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
