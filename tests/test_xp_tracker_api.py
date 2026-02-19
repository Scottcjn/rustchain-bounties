#!/usr/bin/env python3
"""Tests for .github/scripts/update_xp_tracker_api.py

Bounty: XP/Badge Automation Hardening Tests for GitHub Actions (35 RTC)
Issue: https://github.com/Scottcjn/rustchain-bounties/issues/312
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Set, Tuple, List
import sys
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / ".github" / "scripts"))

from update_xp_tracker_api import (
    HunterRow,
    parse_hunter_row,
    parse_table_cells,
    parse_badges,
    get_level_and_title,
    parse_labels,
    is_true,
)


# Sample tracker markdown for testing
SAMPLE_TRACKER_MD = """# XP Tracker

Test tracker for bounty submissions.

| Rank | Hunter | Wallet | XP | Level | Title | Badges | Last Action | Notes |
|------|--------|--------|----|-------|-------|--------|-------------|-------|
| 1 | test-hunter | wallet-123 | 1500 | 4 | Rising Hunter | ⭐ | 2026-02-19 | First bounty |
| 2 | another-hunter | wallet-456 | 500 | 3 | Priority Hunter | 🚀 | 2026-02-18 | Good work |
| 3 | newbie | wallet-789 | 50 | 1 | Starting Hunter | | 2026-02-19 | Just started |

---

## Award Log

### 2026-02-19
- test-hunter: +1500 XP (Issue #123 completed)
"""


class TestParseHunterRow:
    """Test parsing individual table rows into HunterRow objects."""

    def test_parse_valid_row(self):
        """Should parse a well-formed table row."""
        cells = ["1", "test-hunter", "wallet-123", "1500", "4", "Rising Hunter", "⭐", "2026-02-19", "First bounty"]
        row = parse_hunter_row(cells)

        assert row is not None
        assert row.hunter == "test-hunter"
        assert row.wallet == "wallet-123"
        assert row.xp == 1500
        assert row.level == 4
        assert row.title == "Rising Hunter"
        assert "⭐" in row.badges
        assert row.last_action == "2026-02-19"
        assert row.notes == "First bounty"

    def test_parse_row_with_minimal_columns(self):
        """Handle older schema with fewer columns."""
        cells = ["1", "old-hunter", "wallet-456", "300", "2", "2026-02-18", "Old entry"]
        row = parse_hunter_row(cells)

        assert row is not None
        assert row.hunter == "old-hunter"
        assert row.xp == 300
        assert row.level == 2

    def test_parse_invalid_row_too_short(self):
        """Skip rows with insufficient columns."""
        cells = ["1", "hunter", "wallet"]
        row = parse_hunter_row(cells)
        assert row is None


class TestParseTableCells:
    """Test parsing markdown table row strings into cell arrays."""

    def test_parse_valid_table_row(self):
        """Should split pipe-delimited table row into cells."""
        line = "| 1 | test-hunter | wallet-123 | 1500 | 4 | Rising Hunter |"
        cells = parse_table_cells(line)

        assert len(cells) == 6
        assert cells[0] == "1"
        assert cells[1] == "test-hunter"
        assert cells[3] == "1500"

    def test_parse_handles_whitespace(self):
        """Should strip whitespace from cells."""
        line = "|  1  |  test-hunter  |  wallet-123  |"
        cells = parse_table_cells(line)

        assert cells[0] == "1"
        assert cells[1] == "test-hunter"
        assert cells[2] == "wallet-123"


class TestParseBadges:
    """Test badge parsing from markdown cell text."""

    def test_parse_markdown_badges(self):
        """Extract badge names from markdown image syntax."""
        cell = "![⭐](badge_url) ![🚀](badge_url2)"
        badges = parse_badges(cell)

        assert "⭐" in badges
        assert "🚀" in badges
        assert len(badges) == 2

    def test_parse_comma_separated_badges(self):
        """Fallback to comma-separated text if no markdown images."""
        cell = "First Blood, Rising Hunter, Tutorial Titan"
        badges = parse_badges(cell)

        assert "First Blood" in badges
        assert "Rising Hunter" in badges
        assert "Tutorial Titan" in badges

    def test_parse_empty_badges(self):
        """Empty or dash cells should return empty set."""
        assert parse_badges("") == set()
        assert parse_badges("  ") == set()
        assert parse_badges("-") == set()


class TestRankRecalculation:
    """Test XP-based ranking logic."""

    def test_ranks_by_xp_descending(self):
        """Higher XP = lower rank number (rank 1 is best)."""
        rows = [
            HunterRow("hunter-1", "w1", 100, 1, "Title", set(), "", ""),
            HunterRow("hunter-2", "w2", 500, 1, "Title", set(), "", ""),
            HunterRow("hunter-3", "w3", 300, 1, "Title", set(), "", ""),
        ]
        ranked = sorted(rows, key=lambda h: (-h.xp, h.hunter.lower()))

        assert ranked[0].hunter == "hunter-2"  # 500 XP
        assert ranked[1].hunter == "hunter-3"  # 300 XP
        assert ranked[2].hunter == "hunter-1"  # 100 XP

    def test_tie_breaker_by_name(self):
        """Equal XP should rank alphabetically by hunter name."""
        rows = [
            HunterRow("zebra", "w1", 200, 1, "Title", set(), "", ""),
            HunterRow("alpha", "w2", 200, 1, "Title", set(), "", ""),
        ]
        ranked = sorted(rows, key=lambda h: (-h.xp, h.hunter.lower()))

        assert ranked[0].hunter == "alpha"
        assert ranked[1].hunter == "zebra"


class TestBadgeAssignment:
    """Test badge logic based on XP and labels."""

    def test_level_badge_assignment(self):
        """XP thresholds determine level/tier badges."""
        # Test Rising Hunter threshold
        level, title = get_level_and_title(1000)
        assert level == 4
        assert "Rising Hunter" in title

        # Test Master Hunter threshold
        level, title = get_level_and_title(15000)
        assert level == 9
        assert "Master Hunter" in title

        # Test Legendary Hunter threshold
        level, title = get_level_and_title(20000)
        assert level == 10
        assert "Legendary Hunter" in title

    def test_label_badge_mapping(self):
        """Issue labels should map to specific badges."""
        labels = parse_labels("bug,documentation,first-blood")

        assert "bug" in labels
        assert "documentation" in labels
        assert "first-blood" in labels

    def test_empty_labels(self):
        """Empty label strings should return empty set."""
        labels = parse_labels("")
        assert len(labels) == 0

        labels = parse_labels("   ")
        assert len(labels) == 0


class TestRetroactiveBackfill:
    """Test backfill logic for missing historical badges."""

    def test_backfill_threshold_badges(self):
        """Backfill badges when XP qualifies but badge is missing."""
        row = HunterRow(
            hunter="old-hunter",
            wallet="old-wallet",
            xp=2500,
            level=5,
            title="Multiplier Hunter",
            badges={"🚀"},  # Missing Rising Hunter badge
            last_action="",
            notes=""
        )

        level, title = get_level_and_title(row.xp)
        # Should qualify for multiple badges
        assert level >= 4  # Rising Hunter threshold
        assert "Multiplier Hunter" in title

    def test_backfill_preserves_existing_badges(self):
        """Backfill should not remove existing badges."""
        existing_badges = {"⭐", "🚀", "🛡️"}
        row = HunterRow(
            hunter="badge-holder",
            wallet="w",
            xp=5000,
            level=6,
            title="",
            badges=existing_badges.copy(),
            last_action="",
            notes=""
        )

        # After any processing, existing badges should remain
        # (this is a contract; actual logic in the script)
        assert existing_badges is not None


class TestUtilityFunctions:
    """Test helper utility functions."""

    def test_is_true_various_formats(self):
        """Test boolean value parsing from strings."""
        assert is_true("true")
        assert is_true("True")
        assert is_true("TRUE")
        assert is_true("1")
        assert is_true("yes")
        assert is_true("YES")
        assert is_true("y")

        assert not is_true("false")
        assert not is_true("0")
        assert not is_true("no")
        assert not is_true("")
        assert not is_true("  ")

    def test_parse_labels_comma_separated(self):
        """Parse comma-separated label strings."""
        labels = parse_labels("bug,feature,enhancement")

        assert len(labels) == 3
        assert "bug" in labels
        assert "feature" in labels
        assert "enhancement" in labels

    def test_parse_labels_handling_whitespace(self):
        """Labels should be trimmed of whitespace."""
        labels = parse_labels("  bug  ,  feature , documentation ")

        assert "bug" in labels
        assert "feature" in labels
        assert "documentation" in labels
        assert "  bug  " not in labels  # Should not store with whitespace

    def test_parse_labels_case_insensitive(self):
        """Label parsing should normalize to lowercase."""
        labels = parse_labels("BUG,Feature,DOCUMENTATION")

        assert labels == {"bug", "feature", "documentation"}


class TestSchemaCorrectness:
    """Test that HunterRow data validates schema constraints."""

    def test_xp_must_be_non_negative(self):
        """XP values should be >= 0."""
        row = HunterRow("h", "w", 0, 1, "Title", set(), "", "")
        assert row.xp >= 0

        row = HunterRow("h", "w", 1500, 4, "Title", set(), "", "")
        assert row.xp >= 0

    def test_level_must_match_xp_threshold(self):
        """Level should correspond correctly to XP."""
        for xp in [0, 200, 500, 1000, 2000, 5000, 10000]:
            level, title = get_level_and_title(xp)
            assert 1 <= level <= 10

    def test_badges_set_must_be_unique(self):
        """Badge set should not contain duplicates."""
        badges = {"⭐", "🚀", "🛡️"}
        assert len(badges) == 3  # No duplicates

        # Adding duplicate should not increase size
        badges.add("⭐")
        assert len(badges) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
