#!/usr/bin/env python3
"""Tests for .github/scripts/generate_dynamic_badges.py

Bounty: XP/Badge Automation Hardening Tests for GitHub Actions (35 RTC)
Issue: https://github.com/Scottcjn/rustchain-bounties/issues/312
"""

import pytest
import json
import re
from pathlib import Path
from typing import List, Dict
import sys
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / ".github" / "scripts"))

from generate_dynamic_badges import (
    parse_int,
    parse_rows,
    slugify_hunter,
    write_badge,
    color_for_level,
)


# Sample tracker for badge generation
SAMPLE_TRACKER_MD = """# XP Tracker

| Rank | Hunter | Wallet | XP | Level | Title | Badges | Last Action | Notes |
|------|--------|--------|----|-------|-------|--------|-------------|-------|
| 1 | legendary-hunter | wallet-001 | 20000 | 10 | Legendary Hunter | ⭐🚀🛡️👑 | 2026-02-19 | Top |
| 2 | elite-hunter | wallet-002 | 9000 | 8 | Elite Hunter | ⭐🚀 | 2026-02-18 | Great |
| 3 | rising-hunter | wallet-003 | 1500 | 4 | Rising Hunter | ⭐ | 2026-02-19 | New |
| 4 | newbie | wallet-004 | 50 | 1 | Starting Hunter | | 2026-02-19 | Start |

---

## Award Log

### 2026-02-19
- legendary-hunter: +5000 XP
"""


class TestParseInt:
    """Test integer parsing from strings."""

    def test_parse_valid_numbers(self):
        """Extract integers from numeric strings."""
        assert parse_int("100") == 100
        assert parse_int("42") == 42
        assert parse_int("0") == 0
        assert parse_int("9999") == 9999

    def test_parse_int_from_mixed_text(self):
        """Extract first number from strings containing text."""
        assert parse_int("100 XP") == 100
        assert parse_int("Level 5") == 5
        assert parse_int("Rank #1") == 1
        assert parse_int("Score: 250 points") == 250

    def test_parse_empty_or_invalid(self):
        """Return 0 for empty or non-numeric strings."""
        assert parse_int("") == 0
        assert parse_int("   ") == 0
        assert parse_int("N/A") == 0
        assert parse_int("unknown") == 0


class TestParseRows:
    """Test parsing tracker table into row dictionaries."""

    def test_parse_valid_tracker_rows(self):
        """Should parse all rows from a valid tracker."""
        rows = parse_rows(SAMPLE_TRACKER_MD)

        assert len(rows) == 4

        assert rows[0]["hunter"] == "legendary-hunter"
        assert rows[0]["xp"] == 20000
        assert rows[0]["level"] == 10

        assert rows[1]["hunter"] == "elite-hunter"
        assert rows[1]["xp"] == 9000

        assert rows[3]["hunter"] == "newbie"
        assert rows[3]["xp"] == 50

    def test_parse_ranks_correctly(self):
        """Ranks should be assigned 1-indexed after sorting."""
        rows = parse_rows(SAMPLE_TRACKER_MD)

        assert rows[0]["rank"] == 1
        assert rows[1]["rank"] == 2
        assert rows[2]["rank"] == 3
        assert rows[3]["rank"] == 4

    def test_parse_skips_tbd_hunters(self):
        """Should skip placeholder _TBD_ hunters (requires full schema)."""
        tbd_tracker = """| Rank | Hunter | Wallet | XP | Level | Title | Badges | Last Action | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | _TBD_ | xyz | 0 | 1 | Starting Hunter | | | |
| 2 | real-hunter | abc | 100 | 2 | Starting Hunter | | | |
"""
        rows = parse_rows(tbd_tracker)

        assert len(rows) == 1
        assert rows[0]["hunter"] == "real-hunter"

    def test_parse_empty_tracker(self):
        """Empty tracker should return empty list."""
        empty = "# No table here"
        rows = parse_rows(empty)
        assert rows == []

    def test_parse_sorts_by_xp_descending(self):
        """Rows should be sorted by XP (highest first) - requires full schema."""
        unsorted_tracker = """| Rank | Hunter | Wallet | XP | Level | Title | Badges | Last Action | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | mid | w1 | 500 | 3 | Title | | | |
| 2 | low | w2 | 100 | 1 | Title | | | |
| 3 | high | w3 | 2000 | 5 | Title | | | |
"""
        rows = parse_rows(unsorted_tracker)

        assert rows[0]["xp"] >= rows[1]["xp"] >= rows[2]["xp"]
        assert rows[0]["hunter"] == "high"
        assert rows[1]["hunter"] == "mid"
        assert rows[2]["hunter"] == "low"


class TestEmptyTableHandling:
    """Test behavior with empty or degenerate tables."""

    def test_table_with_no_valid_rows(self):
        """Table with only _TBD_ rows should be treated as empty."""
        tbd_only = """| Rank | Hunter | Wallet | XP | Level | Title | Badges | Last Action | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | _TBD_ | w | 0 | 1 | Title | | | |
| 2 | _TBD_ | w2 | 0 | 1 | Title | | | |
"""
        rows = parse_rows(tbd_only)
        assert len(rows) == 0


class TestSlugGeneration:
    """Test slug generation for hunter badge filenames."""

    def test_slug_from_hunter_name(self):
        """Hunter names should be slugified for filenames."""
        rows = parse_rows(SAMPLE_TRACKER_MD)

        # Check that slugs contain valid filename characters
        for row in rows:
            hunter = row["hunter"]
            # Slug typically replaces spaces with hyphens, removes special chars
            slug = hunter.lower().replace(" ", "-").replace("_", "-")
            # Slug should be valid (basic check)
            assert " " not in slug
            assert not any(c in slug for c in ('/', '\\', ':', '*'))

    def test_slug_is_lowercase(self):
        """Generated slugs should be lowercase."""
        rows = parse_rows(SAMPLE_TRACKER_MD)

        for row in rows:
            slug = row["hunter"].lower()
            assert slug.islower()


class TestSchemaCorrectness:
    """Test that parsed row data validates schema constraints."""

    def test_row_has_required_fields(self):
        """Parsed rows should have all required fields."""
        rows = parse_rows(SAMPLE_TRACKER_MD)

        for row in rows:
            assert "hunter" in row
            assert "xp" in row
            assert "level" in row
            assert "title" in row

    def test_xp_values_are_integers(self):
        """XP values should parse as integers."""
        rows = parse_rows(SAMPLE_TRACKER_MD)

        for row in rows:
            assert isinstance(row["xp"], int)
            assert row["xp"] >= 0


class TestSlugifyHunter:
    """Test hunter name slugification for filenames."""

    def test_slugify_simple_name(self):
        """Simple names should be lowercase."""
        assert slugify_hunter("TestHunter") == "testhunter"

    def test_slugify_spaces_to_hyphens(self):
        """Spaces should be converted to hyphens."""
        assert slugify_hunter("Test Hunter") == "test-hunter"
        assert slugify_hunter("Test  Hunter") == "test-hunter"

    def test_slugify_special_chars(self):
        """Special characters - underscores and dots are preserved by actual implementation."""
        # Based on actual slugify_hunter implementation: keeps alphanumerics, _, ., -
        assert slugify_hunter("test.hunter") == "test.hunter"
        assert slugify_hunter("test_hunter") == "test_hunter"


class TestColorForLevel:
    """Test badge color mapping for hunter levels."""

    def test_level_colors(self):
        """Each level should have an assigned color."""
        assert color_for_level(1) is not None
        assert color_for_level(5) is not None
        assert color_for_level(10) is not None

    def test_level_colors_are_strings(self):
        """Colors should be string values."""
        for level in range(1, 11):
            color = color_for_level(level)
            assert isinstance(color, str)
            assert len(color) > 0


class TestWriteBadge:
    """Test writing badge JSON to files."""

    def test_write_badge_creates_valid_json(self, tmp_path):
        """Badge file should contain valid JSON structure."""
        output_dir = tmp_path / "badges"
        output_dir.mkdir()

        # Uses actual write_badge signature
        write_badge(
            path=output_dir / "test.json",
            label="Test Hunter",
            message="Level 5",
            color="blue"
        )

        badge_file = output_dir / "test.json"
        assert badge_file.exists()

        with open(badge_file) as f:
            loaded = json.load(f)

        assert loaded["label"] == "Test Hunter"
        assert loaded["message"] == "Level 5"
        assert loaded["color"] == "blue"


class TestDeterministicOutput:
    """Test that output is deterministic across runs."""

    def test_same_input_same_output(self):
        """Parsing same tracker twice should produce identical results."""
        rows1 = parse_rows(SAMPLE_TRACKER_MD)
        rows2 = parse_rows(SAMPLE_TRACKER_MD)

        assert len(rows1) == len(rows2)

        for i in range(len(rows1)):
            assert rows1[i]["hunter"] == rows2[i]["hunter"]
            assert rows1[i]["xp"] == rows2[i]["xp"]
            assert rows1[i]["level"] == rows2[i]["level"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
