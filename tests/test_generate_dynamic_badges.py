#!/usr/bin/env python3
"""Tests for generate_dynamic_badges.py"""

import json
import tempfile
from pathlib import Path
import pytest
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / ".github" / "scripts"))

from generate_dynamic_badges import (
    parse_int,
    parse_rows,
    color_for_level,
    slugify_hunter,
    write_badge,
)


class TestParseInt:
    """Test parse_int function"""

    def test_parse_valid_number(self):
        assert parse_int("123") == 123

    def test_parse_number_with_text(self):
        assert parse_int("XP: 456") == 456

    def test_parse_empty_string(self):
        assert parse_int("") == 0

    def test_parse_none(self):
        assert parse_int(None) == 0

    def test_parse_no_digits(self):
        assert parse_int("abc") == 0


class TestColorForLevel:
    """Test color_for_level function"""

    def test_level_10_gold(self):
        assert color_for_level(10) == "gold"

    def test_level_11_gold(self):
        assert color_for_level(11) == "gold"

    def test_level_7_purple(self):
        assert color_for_level(7) == "purple"

    def test_level_9_purple(self):
        assert color_for_level(9) == "purple"

    def test_level_5_yellow(self):
        assert color_for_level(5) == "yellow"

    def test_level_6_yellow(self):
        assert color_for_level(6) == "yellow"

    def test_level_4_orange(self):
        assert color_for_level(4) == "orange"

    def test_level_3_blue(self):
        assert color_for_level(3) == "blue"

    def test_level_1_blue(self):
        assert color_for_level(1) == "blue"


class TestSlugifyHunter:
    """Test slugify_hunter function"""

    def test_simple_username(self):
        assert slugify_hunter("@testuser") == "testuser"

    def test_username_with_at(self):
        assert slugify_hunter("@TestUser") == "testuser"

    def test_username_with_underscores(self):
        assert slugify_hunter("@test_user") == "test_user"

    def test_username_with_dashes(self):
        assert slugify_hunter("@test-user") == "test-user"

    def test_username_with_dots(self):
        assert slugify_hunter("@test.user") == "test.user"

    def test_username_with_special_chars(self):
        assert slugify_hunter("@test user") == "test-user"

    def test_username_strips_leading_at(self):
        assert slugify_hunter("testuser") == "testuser"

    def test_empty_after_strip(self):
        assert slugify_hunter("@@@") == "unknown"


class TestParseRows:
    """Test parse_rows function"""

    def test_parse_valid_table(self):
        md = """# XP Tracker

| Rank | Hunter | Wallet | XP | Level | Title | Badges | Last Action | Notes |
|------|--------|--------|-----|-------|-------|--------|-------------|-------|
| 1 | @hunter1 | wallet1 | 1000 | 4 | Rising Hunter | - | 2024-01-01 | - |
| 2 | @hunter2 | wallet2 | 500 | 3 | Priority Hunter | - | 2024-01-01 | - |
"""
        rows = parse_rows(md)
        assert len(rows) == 2
        assert rows[0]["hunter"] == "@hunter1"
        assert rows[0]["xp"] == 1000
        assert rows[0]["rank"] == 1
        assert rows[1]["hunter"] == "@hunter2"
        assert rows[1]["xp"] == 500

    def test_parse_empty_table(self):
        md = """# XP Tracker

| Rank | Hunter | Wallet | XP | Level | Title | Badges | Last Action | Notes |
|------|--------|--------|-----|-------|-------|--------|-------------|-------|
"""
        rows = parse_rows(md)
        assert len(rows) == 0

    def test_parse_no_table(self):
        md = "# No table here"
        rows = parse_rows(md)
        assert len(rows) == 0

    def test_parse_skips_tbd(self):
        md = """# XP Tracker

| Rank | Hunter | Wallet | XP | Level | Title | Badges | Last Action | Notes |
|------|--------|--------|-----|-------|-------|--------|-------------|-------|
| 1 | _TBD_ | _TBD_ | 0 | 1 | Starting Hunter | - | - | - |
| 2 | @real | wallet | 100 | 2 | Basic Hunter | - | - | - |
"""
        rows = parse_rows(md)
        assert len(rows) == 1
        assert rows[0]["hunter"] == "@real"

    def test_sorts_by_xp_descending(self):
        md = """# XP Tracker

| Rank | Hunter | Wallet | XP | Level | Title | Badges | Last Action | Notes |
|------|--------|--------|-----|-------|-------|--------|-------------|-------|
| 1 | @low | wallet | 100 | 2 | Basic Hunter | - | - | - |
| 2 | @high | wallet | 1000 | 4 | Rising Hunter | - | - | - |
"""
        rows = parse_rows(md)
        assert rows[0]["hunter"] == "@high"
        assert rows[0]["rank"] == 1
        assert rows[1]["hunter"] == "@low"
        assert rows[1]["rank"] == 2


class TestWriteBadge:
    """Test write_badge function"""

    def test_write_badge_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            write_badge(path, "Test", "value", "blue")
            assert path.exists()
            data = json.loads(path.read_text())
            assert data["label"] == "Test"
            assert data["message"] == "value"
            assert data["color"] == "blue"

    def test_write_badge_creates_parent_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "subdir" / "nested" / "test.json"
            write_badge(path, "Test", "value", "red")
            assert path.exists()

    def test_write_badge_with_logo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            write_badge(path, "Test", "value", "green", "github", "white")
            data = json.loads(path.read_text())
            assert data["namedLogo"] == "github"
            assert data["logoColor"] == "white"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
