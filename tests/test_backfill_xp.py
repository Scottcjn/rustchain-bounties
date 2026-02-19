#!/usr/bin/env python3
"""Tests for backfill_xp_from_merged_prs.py"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / ".github" / "scripts"))

from backfill_xp_from_merged_prs import (
    parse_existing_tracker,
    get_level_and_title,
    format_badges,
    generate_hunter_row,
    HistoricalContributor,
)


class TestGetLevelAndTitle:
    """Test level and title calculation from XP"""

    def test_level_1_starting_hunter(self):
        level, title = get_level_and_title(0)
        assert level == 1
        assert title == "Starting Hunter"

    def test_level_2_basic_hunter(self):
        level, title = get_level_and_title(200)
        assert level == 2
        assert title == "Basic Hunter"

    def test_level_3_priority_hunter(self):
        level, title = get_level_and_title(500)
        assert level == 3
        assert title == "Priority Hunter"

    def test_level_4_rising_hunter(self):
        level, title = get_level_and_title(1000)
        assert level == 4
        assert title == "Rising Hunter"

    def test_level_5_multiplier_hunter(self):
        level, title = get_level_and_title(2000)
        assert level == 5
        assert title == "Multiplier Hunter"

    def test_level_10_legendary_hunter(self):
        level, title = get_level_and_title(18000)
        assert level == 10
        assert title == "Legendary Hunter"

    def test_between_levels(self):
        level, title = get_level_and_title(750)
        assert level == 3
        assert title == "Priority Hunter"


class TestFormatBadges:
    """Test badge formatting"""

    def test_empty_returns_dash(self):
        result = format_badges(set())
        assert result == "-"

    def test_single_badge(self):
        result = format_badges({"First Blood"})
        assert "First Blood" in result

    def test_multiple_badges_sorted(self):
        badges = {"Rising Hunter", "First Blood", "Multiplier Hunter"}
        result = format_badges(badges)
        # Should contain all badges
        assert "First Blood" in result
        assert "Rising Hunter" in result
        assert "Multiplier Hunter" in result


class TestGenerateHunterRow:
    """Test table row generation"""

    def test_basic_row_generation(self):
        contributor = HistoricalContributor(
            username="testuser",
            xp=100,
            badges={"First Blood"},
            last_action="2025-01 historical",
            source_issue=1
        )
        row = generate_hunter_row(contributor, 1)
        assert "@testuser" in row
        assert "100" in row
        assert "1" in row  # level
        assert "Starting Hunter" in row

    def test_rising_hunter_level(self):
        contributor = HistoricalContributor(
            username="risingstar",
            xp=1500,
            badges={"First Blood", "Rising Hunter"},
            last_action="2025-02 historical",
            source_issue=2
        )
        row = generate_hunter_row(contributor, 5)
        assert "1500" in row
        assert "4" in row  # level for 1500 XP
        assert "Rising Hunter" in row


class TestParseExistingTracker:
    """Test parsing existing tracker for known hunters"""

    def test_parses_existing_hunters(self, tmp_path):
        # Create a test tracker file
        tracker_content = """# XP Tracker

| Rank | Hunter | Wallet | XP | Level | Title | Badges | Last Action | Notes |
|------|--------|--------|-----|-------|-------|--------|-------------|-------|
| 1 | @existing1 | _TBD_ | 1000 | 4 | Rising Hunter | First Blood | 2026-01-01 | - |
| 2 | @existing2 | _TBD_ | 500 | 3 | Priority Hunter | - | 2026-01-01 | - |
"""
        tracker_file = tmp_path / "test_tracker.md"
        tracker_file.write_text(tracker_content)

        result = parse_existing_tracker(tracker_file)
        
        assert "existing1" in result
        assert "existing2" in result

    def test_ignores_tbd(self, tmp_path):
        tracker_content = """# XP Tracker

| Rank | Hunter | Wallet | XP | Level | Title | Badges | Last Action | Notes |
|------|--------|--------|-----|-------|-------|--------|-------------|-------|
| 1 | _TBD_ | _TBD_ | 0 | 1 | Starting Hunter | - | - | - |
| 2 | @real | _TBD_ | 100 | 1 | Starting Hunter | - | 2026-01-01 | - |
"""
        tracker_file = tmp_path / "test_tracker.md"
        tracker_file.write_text(tracker_content)

        result = parse_existing_tracker(tracker_file)
        
        assert "real" in result
        assert len(result) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
