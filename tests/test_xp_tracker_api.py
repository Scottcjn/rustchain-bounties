#!/usr/bin/env python3
"""
Tests for .github/scripts/update_xp_tracker_api.py
Covers: row insert/update, rank recalculation, badge assignment, retroactive backfill
"""

import pytest
import sys
import os
import re
from unittest.mock import patch

# Add the scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.github', 'scripts'))

from update_xp_tracker_api import (
    get_level_and_title,
    calculate_xp,
    parse_badges,
    format_badges,
    parse_table_cells,
    parse_hunter_row,
    render_row,
    determine_new_badges,
    update_table_in_md,
    update_frontmatter,
    HunterRow,
    LEVEL_THRESHOLDS,
    BADGE_STYLE,
    is_true,
    parse_labels,
    badge_url,
    badge_md,
)


# ===== Level & Title Tests =====

class TestGetLevelAndTitle:
    """Test level/title assignment from XP thresholds"""

    def test_zero_xp(self):
        level, title = get_level_and_title(0)
        assert level == 1
        assert title == "Starting Hunter"

    def test_exactly_200_xp(self):
        level, title = get_level_and_title(200)
        assert level == 2
        assert title == "Basic Hunter"

    def test_exactly_500_xp(self):
        level, title = get_level_and_title(500)
        assert level == 3
        assert title == "Priority Hunter"

    def test_exactly_1000_xp(self):
        level, title = get_level_and_title(1000)
        assert level == 4
        assert title == "Rising Hunter"

    def test_exactly_2000_xp(self):
        level, title = get_level_and_title(2000)
        assert level == 5
        assert title == "Multiplier Hunter"

    def test_exactly_3500_xp(self):
        level, title = get_level_and_title(3500)
        assert level == 6
        assert title == "Featured Hunter"

    def test_exactly_5500_xp(self):
        level, title = get_level_and_title(5500)
        assert level == 7
        assert title == "Veteran Hunter"

    def test_exactly_8000_xp(self):
        level, title = get_level_and_title(8000)
        assert level == 8
        assert title == "Elite Hunter"

    def test_exactly_12000_xp(self):
        level, title = get_level_and_title(12000)
        assert level == 9
        assert title == "Master Hunter"

    def test_exactly_18000_xp(self):
        level, title = get_level_and_title(18000)
        assert level == 10
        assert title == "Legendary Hunter"

    def test_between_thresholds(self):
        """XP between thresholds should use the lower threshold's level"""
        level, title = get_level_and_title(350)
        assert level == 2
        assert title == "Basic Hunter"

    def test_very_high_xp(self):
        """XP far above max threshold should still be Legendary"""
        level, title = get_level_and_title(100000)
        assert level == 10
        assert title == "Legendary Hunter"

    def test_one_below_threshold(self):
        """199 XP should still be level 1"""
        level, title = get_level_and_title(199)
        assert level == 1
        assert title == "Starting Hunter"

    def test_all_thresholds_covered(self):
        """Verify every threshold in LEVEL_THRESHOLDS is reachable"""
        for threshold, expected_level, expected_title in LEVEL_THRESHOLDS:
            level, title = get_level_and_title(threshold)
            assert level == expected_level, f"Failed for XP={threshold}"
            assert title == expected_title, f"Failed for XP={threshold}"


# ===== XP Calculation Tests =====

class TestCalculateXP:
    """Test XP calculation from events and labels"""

    def test_bounty_approved(self):
        xp, reason = calculate_xp("issues", "labeled", {"bounty-approved"}, False)
        assert xp == 200
        assert "bounty approved" in reason

    def test_pr_merged(self):
        xp, reason = calculate_xp("pull_request", "closed", set(), True)
        assert xp == 300
        assert "PR merged" in reason

    def test_issue_closed(self):
        xp, reason = calculate_xp("issues", "closed", set(), False)
        assert xp == 80
        assert "issue closed" in reason

    def test_micro_tier(self):
        xp, reason = calculate_xp("issues", "", {"micro"}, False)
        assert xp >= 50
        assert "micro tier" in reason

    def test_standard_tier(self):
        xp, reason = calculate_xp("issues", "", {"standard"}, False)
        assert xp >= 100
        assert "standard tier" in reason

    def test_major_tier(self):
        xp, reason = calculate_xp("issues", "", {"major"}, False)
        assert xp >= 200
        assert "major tier" in reason

    def test_critical_tier(self):
        xp, reason = calculate_xp("issues", "", {"critical"}, False)
        assert xp >= 300
        assert "critical tier" in reason

    def test_tutorial_docs(self):
        xp, reason = calculate_xp("issues", "", {"tutorial"}, False)
        assert xp >= 150
        assert "tutorial/docs" in reason

    def test_vintage_bonus(self):
        xp, reason = calculate_xp("issues", "", {"vintage"}, False)
        assert xp >= 100
        assert "vintage bonus" in reason

    def test_outreach_bonus(self):
        xp, reason = calculate_xp("issues", "", {"outreach"}, False)
        assert xp >= 30
        assert "outreach bonus" in reason

    def test_combined_labels(self):
        """Multiple labels should stack XP"""
        xp, reason = calculate_xp("pull_request", "closed", {"bounty-approved", "major"}, True)
        assert xp >= 700  # 200 + 300 + 200
        assert "bounty approved" in reason
        assert "PR merged" in reason
        assert "major tier" in reason

    def test_base_action_fallback(self):
        """No matching labels should give base 50 XP"""
        xp, reason = calculate_xp("push", "", set(), False)
        assert xp == 50
        assert "base action" in reason

    def test_seo_marketing_labels(self):
        """SEO and marketing should trigger outreach bonus"""
        xp1, _ = calculate_xp("issues", "", {"seo"}, False)
        xp2, _ = calculate_xp("issues", "", {"marketing"}, False)
        assert xp1 >= 30
        assert xp2 >= 30


# ===== Badge Tests =====

class TestBadges:
    """Test badge parsing, formatting, and assignment"""

    def test_parse_badges_markdown(self):
        """Parse badge names from markdown image syntax"""
        cell = "![First Blood](https://img.shields.io/badge/First%20Blood-red) ![Rising Hunter](https://img.shields.io/badge/Rising%20Hunter-orange)"
        badges = parse_badges(cell)
        assert "First Blood" in badges
        assert "Rising Hunter" in badges

    def test_parse_badges_empty(self):
        badges = parse_badges("-")
        assert len(badges) == 0

    def test_parse_badges_none(self):
        badges = parse_badges(None)
        assert len(badges) == 0

    def test_parse_badges_csv_fallback(self):
        """When no markdown images, parse as comma-separated names"""
        cell = "First Blood, Rising Hunter"
        badges = parse_badges(cell)
        assert "First Blood" in badges
        assert "Rising Hunter" in badges

    def test_format_badges_empty(self):
        result = format_badges(set())
        assert result == "-"

    def test_format_badges_sorted(self):
        """Badge output should be sorted for determinism"""
        badges = {"Rising Hunter", "First Blood"}
        result = format_badges(badges)
        assert result.index("First Blood") < result.index("Rising Hunter")

    def test_format_badges_markdown(self):
        result = format_badges({"First Blood"})
        assert "![First Blood]" in result
        assert "img.shields.io" in result

    def test_badge_url_known_style(self):
        """Known badge should use its defined style"""
        url = badge_url("First Blood")
        assert "red" in url
        assert "git" in url

    def test_badge_url_unknown_style(self):
        """Unknown badge should use default blue/star"""
        url = badge_url("Unknown Badge")
        assert "blue" in url
        assert "star" in url

    def test_badge_md_format(self):
        md = badge_md("First Blood")
        assert md.startswith("![First Blood]")
        assert "(" in md and ")" in md

    def test_all_badge_styles_defined(self):
        """Every badge style should have 3 elements: color, logo, logo_color"""
        for name, style_tuple in BADGE_STYLE.items():
            assert len(style_tuple) == 3, f"Badge '{name}' has {len(style_tuple)} elements, expected 3"


class TestDetermineNewBadges:
    """Test badge assignment logic"""

    def test_first_blood(self):
        unlocked = determine_new_badges(set(), 0, 50, set(), "testuser")
        assert "First Blood" in unlocked

    def test_no_duplicate_first_blood(self):
        """Should not award First Blood twice"""
        unlocked = determine_new_badges({"First Blood"}, 0, 50, set(), "testuser")
        assert "First Blood" not in unlocked

    def test_rising_hunter_badge(self):
        unlocked = determine_new_badges(set(), 0, 1000, set(), "testuser")
        assert "Rising Hunter" in unlocked

    def test_multiplier_hunter_badge(self):
        unlocked = determine_new_badges(set(), 0, 2000, set(), "testuser")
        assert "Multiplier Hunter" in unlocked

    def test_veteran_hunter_badge(self):
        unlocked = determine_new_badges(set(), 0, 5500, set(), "testuser")
        assert "Veteran Hunter" in unlocked

    def test_legendary_hunter_badge(self):
        unlocked = determine_new_badges(set(), 0, 18000, set(), "testuser")
        assert "Legendary Hunter" in unlocked

    def test_vintage_veteran_label(self):
        unlocked = determine_new_badges(set(), 0, 100, {"vintage"}, "testuser")
        assert "Vintage Veteran" in unlocked

    def test_tutorial_titan_label(self):
        unlocked = determine_new_badges(set(), 0, 100, {"tutorial"}, "testuser")
        assert "Tutorial Titan" in unlocked

    def test_docs_triggers_tutorial_titan(self):
        unlocked = determine_new_badges(set(), 0, 100, {"docs"}, "testuser")
        assert "Tutorial Titan" in unlocked

    def test_bug_slayer_label(self):
        unlocked = determine_new_badges(set(), 0, 100, {"bug"}, "testuser")
        assert "Bug Slayer" in unlocked

    def test_security_triggers_bug_slayer(self):
        unlocked = determine_new_badges(set(), 0, 100, {"security"}, "testuser")
        assert "Bug Slayer" in unlocked

    def test_outreach_pro_label(self):
        unlocked = determine_new_badges(set(), 0, 100, {"outreach"}, "testuser")
        assert "Outreach Pro" in unlocked

    def test_seo_triggers_outreach_pro(self):
        unlocked = determine_new_badges(set(), 0, 100, {"seo"}, "testuser")
        assert "Outreach Pro" in unlocked

    def test_agent_overlord_badge(self):
        """Agent Overlord requires 'agent' in name + XP >= 500"""
        unlocked = determine_new_badges(set(), 0, 500, set(), "agent-bot")
        assert "Agent Overlord" in unlocked

    def test_agent_overlord_needs_xp(self):
        """Agent Overlord should NOT unlock below 500 XP"""
        unlocked = determine_new_badges(set(), 0, 499, set(), "agent-bot")
        assert "Agent Overlord" not in unlocked

    def test_agent_overlord_needs_agent_name(self):
        """Agent Overlord should NOT unlock for non-agent names"""
        unlocked = determine_new_badges(set(), 0, 500, set(), "humanuser")
        assert "Agent Overlord" not in unlocked

    def test_streak_master(self):
        unlocked = determine_new_badges(set(), 0, 100, {"streak"}, "testuser")
        assert "Streak Master" in unlocked

    def test_retroactive_backfill(self):
        """High XP should retroactively award all threshold badges"""
        unlocked = determine_new_badges(set(), 0, 20000, set(), "agent-test")
        assert "First Blood" in unlocked
        assert "Rising Hunter" in unlocked
        assert "Multiplier Hunter" in unlocked
        assert "Veteran Hunter" in unlocked
        assert "Legendary Hunter" in unlocked
        assert "Agent Overlord" in unlocked


# ===== Row Parsing/Rendering Tests =====

class TestRowParsing:
    """Test table cell parsing and row rendering"""

    def test_parse_table_cells(self):
        line = "| 1 | @alice | wallet-1 | 500 | 3 | Priority Hunter | - | 2024-01-01 | notes |"
        cells = parse_table_cells(line)
        assert cells[0] == "1"
        assert cells[1] == "@alice"
        assert cells[3] == "500"

    def test_parse_hunter_row_9_columns(self):
        cells = ["1", "@alice", "wallet-1", "500", "3", "Priority Hunter", "-", "2024-01-01", "notes"]
        row = parse_hunter_row(cells)
        assert row is not None
        assert row.hunter == "@alice"
        assert row.wallet == "wallet-1"
        assert row.xp == 500
        assert row.level == 3
        assert row.title == "Priority Hunter"

    def test_parse_hunter_row_7_columns(self):
        """Backward-compatible 7-column parsing"""
        cells = ["1", "@bob", "wallet-2", "200", "2", "2024-01-01", "note"]
        row = parse_hunter_row(cells)
        assert row is not None
        assert row.hunter == "@bob"
        assert row.xp == 200

    def test_parse_hunter_row_too_few_columns(self):
        cells = ["1", "@bad", "wallet"]
        row = parse_hunter_row(cells)
        assert row is None

    def test_parse_hunter_row_bad_xp(self):
        """Non-numeric XP should default to 0"""
        cells = ["1", "@alice", "w", "invalid", "1", "Starting Hunter", "-", "today", ""]
        row = parse_hunter_row(cells)
        assert row is not None
        assert row.xp == 0

    def test_render_row(self):
        row = HunterRow(
            hunter="@alice",
            wallet="wallet-1",
            xp=500,
            level=3,
            title="Priority Hunter",
            badges=set(),
            last_action="2024-01-01",
            notes="test"
        )
        rendered = render_row(1, row)
        assert "| 1 |" in rendered
        assert "@alice" in rendered
        assert "500" in rendered
        assert "Priority Hunter" in rendered

    def test_render_row_with_badges(self):
        row = HunterRow(
            hunter="@alice",
            wallet="wallet-1",
            xp=1000,
            level=4,
            title="Rising Hunter",
            badges={"First Blood", "Rising Hunter"},
            last_action="today",
            notes=""
        )
        rendered = render_row(1, row)
        assert "![First Blood]" in rendered
        assert "![Rising Hunter]" in rendered


# ===== Table Update & Rank Recalculation Tests =====

SAMPLE_MD = """---
title: XP Tracker
last_updated: 2024-01-01
---

# Bounty Hunter Leaderboard

| Rank | Hunter | Wallet | XP | Level | Title | Badges | Last Action | Notes |
|------|--------|--------|----|-------|-------|--------|-------------|-------|
| 1 | @alice | wallet-a | 500 | 3 | Priority Hunter | - | 2024-01-01 | |
| 2 | @bob | wallet-b | 300 | 2 | Basic Hunter | - | 2024-01-01 | |
| 3 | @charlie | wallet-c | 100 | 1 | Starting Hunter | - | 2024-01-01 | |

## Latest Awards

"""


class TestUpdateTableInMd:
    """Test full table update + rank recalculation"""

    def test_update_existing_hunter(self):
        updated_md, total_xp, level, title, unlocked = update_table_in_md(
            md=SAMPLE_MD,
            actor="bob",
            gained_xp=300,
            reason="test",
            labels=set(),
        )
        assert total_xp == 600  # 300 + 300
        assert "@bob" in updated_md

    def test_add_new_hunter(self):
        updated_md, total_xp, level, title, unlocked = update_table_in_md(
            md=SAMPLE_MD,
            actor="newuser",
            gained_xp=100,
            reason="new entry",
            labels=set(),
        )
        assert total_xp == 100
        assert "@newuser" in updated_md

    def test_rank_recalculation_after_update(self):
        """After giving bob +500 XP, bob should be rank 1 (800 > 500)"""
        updated_md, total_xp, level, title, unlocked = update_table_in_md(
            md=SAMPLE_MD,
            actor="bob",
            gained_xp=500,
            reason="big award",
            labels=set(),
        )
        lines = updated_md.splitlines()
        for line in lines:
            if "@bob" in line:
                cells = parse_table_cells(line)
                assert cells[0] == "1", f"Expected bob at rank 1, got rank {cells[0]}"
                break

    def test_award_log_appended(self):
        updated_md, _, _, _, _ = update_table_in_md(
            md=SAMPLE_MD,
            actor="alice",
            gained_xp=100,
            reason="test award",
            labels=set(),
        )
        assert "earned **100 XP**" in updated_md
        assert "test award" in updated_md

    def test_badge_unlocked_on_threshold(self):
        """Giving enough XP to cross a badge threshold should unlock badge"""
        updated_md, total_xp, _, _, unlocked = update_table_in_md(
            md=SAMPLE_MD,
            actor="charlie",
            gained_xp=900,
            reason="big boost",
            labels=set(),
        )
        assert total_xp == 1000
        assert "Rising Hunter" in unlocked

    def test_tbd_rows_skipped(self):
        """_TBD_ placeholder rows should be ignored"""
        md_with_tbd = SAMPLE_MD.replace(
            "| 3 | @charlie", "| 3 | _TBD_"
        )
        updated_md, _, _, _, _ = update_table_in_md(
            md=md_with_tbd,
            actor="alice",
            gained_xp=50,
            reason="test",
            labels=set(),
        )
        assert "_TBD_" not in updated_md.split("## Latest Awards")[0] or \
               updated_md.count("_TBD_") <= 1  # At most one placeholder

    def test_no_header_raises(self):
        """Missing leaderboard header should raise RuntimeError"""
        with pytest.raises(RuntimeError, match="Leaderboard table header not found"):
            update_table_in_md(
                md="# No table here\n\nJust text.",
                actor="test",
                gained_xp=100,
                reason="test",
                labels=set(),
            )


# ===== Frontmatter Tests =====

class TestUpdateFrontmatter:
    """Test YAML frontmatter date update"""

    def test_updates_date(self):
        md = "---\ntitle: test\nlast_updated: 2024-01-01\n---\n"
        updated = update_frontmatter(md)
        assert "2024-01-01" not in updated or "last_updated:" in updated
        # The date should be today's date
        import datetime
        today = datetime.date.today().isoformat()
        assert today in updated

    def test_no_frontmatter_unchanged(self):
        md = "# No frontmatter\n\nJust markdown."
        updated = update_frontmatter(md)
        assert updated == md


# ===== Utility Tests =====

class TestUtilities:
    """Test utility functions"""

    def test_is_true_positive(self):
        assert is_true("true") is True
        assert is_true("True") is True
        assert is_true("TRUE") is True
        assert is_true("1") is True
        assert is_true("yes") is True
        assert is_true("y") is True

    def test_is_true_negative(self):
        assert is_true("false") is False
        assert is_true("0") is False
        assert is_true("no") is False
        assert is_true("") is False

    def test_parse_labels(self):
        labels = parse_labels("bounty, micro, open")
        assert "bounty" in labels
        assert "micro" in labels
        assert "open" in labels

    def test_parse_labels_empty(self):
        labels = parse_labels("")
        assert len(labels) == 0

    def test_parse_labels_none(self):
        labels = parse_labels(None)
        assert len(labels) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
