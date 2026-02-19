#!/usr/bin/env python3
"""Tests for update_xp_tracker_api.py"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / ".github" / "scripts"))

from update_xp_tracker_api import (
    is_true,
    parse_labels,
    get_level_and_title,
    calculate_xp,
    badge_url,
    badge_md,
    parse_badges,
    format_badges,
    parse_table_cells,
    parse_hunter_row,
    determine_new_badges,
    HunterRow,
)


class TestIsTrue:
    """Test is_true function"""

    def test_true_strings(self):
        assert is_true("true")
        assert is_true("True")
        assert is_true("TRUE")
        assert is_true("1")
        assert is_true("yes")
        assert is_true("Yes")
        assert is_true("y")

    def test_false_strings(self):
        assert not is_true("false")
        assert not is_true("no")
        assert not is_true("0")
        assert not is_true("")


class TestParseLabels:
    """Test parse_labels function"""

    def test_single_label(self):
        labels = parse_labels("bounty")
        assert "bounty" in labels

    def test_multiple_labels(self):
        labels = parse_labels("bounty, standard, help wanted")
        assert "bounty" in labels
        assert "standard" in labels
        assert "help wanted" in labels

    def test_empty_string(self):
        labels = parse_labels("")
        assert len(labels) == 0

    def test_normalizes_to_lowercase(self):
        labels = parse_labels("Bounty, Standard")
        assert "bounty" in labels
        assert "standard" in labels


class TestGetLevelAndTitle:
    """Test get_level_and_title function"""

    def test_level_1(self):
        level, title = get_level_and_title(0)
        assert level == 1
        assert title == "Starting Hunter"

    def test_level_2(self):
        level, title = get_level_and_title(200)
        assert level == 2
        assert title == "Basic Hunter"

    def test_level_5(self):
        level, title = get_level_and_title(2000)
        assert level == 5
        assert title == "Multiplier Hunter"

    def test_level_10(self):
        level, title = get_level_and_title(18000)
        assert level == 10
        assert title == "Legendary Hunter"

    def test_between_levels(self):
        level, title = get_level_and_title(500)
        assert level == 3
        assert title == "Priority Hunter"


class TestCalculateXP:
    """Test calculate_xp function"""

    def test_bounty_approved(self):
        xp, reason = calculate_xp("pull_request", "closed", {"bounty-approved"}, True)
        assert xp == 500  # 200 + 300

    def test_micro_tier(self):
        xp, reason = calculate_xp("issues", "opened", {"micro"}, False)
        assert xp == 50

    def test_standard_tier(self):
        xp, reason = calculate_xp("issues", "opened", {"standard"}, False)
        assert xp == 100

    def test_major_tier(self):
        xp, reason = calculate_xp("issues", "opened", {"major"}, False)
        assert xp == 200

    def test_critical_tier(self):
        xp, reason = calculate_xp("issues", "opened", {"critical"}, False)
        assert xp == 300

    def test_tutorial_docs(self):
        xp, reason = calculate_xp("issues", "opened", {"tutorial"}, False)
        assert xp == 150

    def test_vintage_bonus(self):
        xp, reason = calculate_xp("issues", "opened", {"vintage"}, False)
        assert xp == 100

    def test_outreach(self):
        xp, reason = calculate_xp("issues", "opened", {"outreach"}, False)
        assert xp == 30

    def test_base_action(self):
        xp, reason = calculate_xp("issues", "opened", set(), False)
        assert xp == 50
        assert "base action" in reason


class TestBadgeUrl:
    """Test badge_url function"""

    def test_known_badge(self):
        url = badge_url("First Blood")
        assert "First-Blood" in url
        assert "red" in url

    def test_unknown_badge(self):
        url = badge_url("Unknown Badge")
        assert "Unknown-Badge" in url
        assert "blue" in url  # default


class TestParseBadges:
    """Test parse_badges function"""

    def test_markdown_badges(self):
        badges = parse_badges("![First Blood](url1) ![Rising Hunter](url2)")
        assert "First Blood" in badges
        assert "Rising Hunter" in badges

    def test_comma_separated(self):
        badges = parse_badges("badge1, badge2, badge3")
        assert "badge1" in badges
        assert "badge2" in badges

    def test_dash_returns_empty(self):
        badges = parse_badges("-")
        assert len(badges) == 0


class TestFormatBadges:
    """Test format_badges function"""

    def test_empty_returns_dash(self):
        assert format_badges(set()) == "-"

    def test_single_badge(self):
        result = format_badges({"First Blood"})
        assert "First Blood" in result

    def test_multiple_badges_sorted(self):
        result = format_badges({"zebra", "apple", "banana"})
        # Should be sorted alphabetically
        assert "apple" in result
        assert "banana" in result
        assert "zebra" in result


class TestParseHunterRow:
    """Test parse_hunter_row function"""

    def test_new_schema_9_columns(self):
        cells = ["1", "@hunter", "wallet", "1000", "4", "Rising Hunter", "-", "2024-01-01", "notes"]
        row = parse_hunter_row(cells)
        assert row is not None
        assert row.hunter == "@hunter"
        assert row.wallet == "wallet"
        assert row.xp == 1000
        assert row.level == 4
        assert row.title == "Rising Hunter"

    def test_older_schema_7_columns(self):
        cells = ["1", "@hunter", "wallet", "500", "3", "Priority Hunter", "notes"]
        row = parse_hunter_row(cells)
        assert row is not None
        assert row.hunter == "@hunter"
        assert row.xp == 500

    def test_invalid_xp_returns_zero(self):
        cells = ["1", "@hunter", "wallet", "invalid", "1", "Starting Hunter", "-", "-", "-"]
        row = parse_hunter_row(cells)
        assert row is not None
        assert row.xp == 0

    def test_too_few_columns_returns_none(self):
        cells = ["1", "@hunter"]
        row = parse_hunter_row(cells)
        assert row is None


class TestDetermineNewBadges:
    """Test determine_new_badges function"""

    def test_first_blood_new_hunter(self):
        unlocked = determine_new_badges(set(), 0, 100, set(), "test")
        assert "First Blood" in unlocked

    def test_rising_hunter_at_1000(self):
        unlocked = determine_new_badges(set(), 900, 1100, set(), "test")
        assert "Rising Hunter" in unlocked

    def test_legendary_at_18000(self):
        unlocked = determine_new_badges(set(), 17000, 19000, set(), "test")
        assert "Legendary Hunter" in unlocked

    def test_tutorial_badge(self):
        unlocked = determine_new_badges(set(), 0, 100, {"tutorial"}, "test")
        assert "Tutorial Titan" in unlocked

    def test_vintage_badge(self):
        unlocked = determine_new_badges(set(), 0, 100, {"vintage"}, "test")
        assert "Vintage Veteran" in unlocked

    def test_agent_overlord(self):
        unlocked = determine_new_badges(set(), 400, 600, set(), "agent-test")
        assert "Agent Overlord" in unlocked

    def test_existing_badge_not_reawarded(self):
        existing = {"First Blood"}
        unlocked = determine_new_badges(existing, 0, 100, set(), "test")
        assert "First Blood" not in unlocked


class TestHunterRow:
    """Test HunterRow dataclass"""

    def test_create_hunter_row(self):
        row = HunterRow(
            hunter="@test",
            wallet="wallet1",
            xp=1000,
            level=4,
            title="Rising Hunter",
            badges={"First Blood"},
            last_action="test action",
            notes="test notes"
        )
        assert row.hunter == "@test"
        assert row.xp == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
