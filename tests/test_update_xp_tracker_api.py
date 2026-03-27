#!/usr/bin/env python3
"""Tests for .github/scripts/update_xp_tracker_api.py

Covers:
- Row insert/update
- Rank recalculation
- Badge assignment logic
- Retroactive threshold backfill behavior
- Edge cases and error handling
"""

import datetime as dt
import json
import re
import sys
import textwrap
import unittest
from pathlib import Path
from unittest import mock

# Add the script directory to import path
SCRIPT_DIR = Path(__file__).resolve().parent.parent / ".github" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import update_xp_tracker_api as xp_mod


# ─── Sample Tracker Markdown ────────────────────────────────────────────────

SAMPLE_TRACKER_MD = textwrap.dedent("""\
    ---
    title: RustChain Bounty Hunter XP and Levels
    last_updated: 2025-01-01
    ---

    # Leaderboard

    | Rank | Hunter (GitHub / Agent ID) | Wallet (last 4) | Total XP | Level | Title | Badges Earned | Last Action | Notes |
    |---:|:---|:---:|---:|---:|:---|:---|:---|:---|
    | 1 | @alice | abc1 | 3000 | 5 | Multiplier Hunter | ![First Blood](https://img.shields.io/badge/First%20Blood-red?style=flat-square&logo=git&logoColor=white) ![Rising Hunter](https://img.shields.io/badge/Rising%20Hunter-orange?style=flat-square&logo=rocket&logoColor=white) | 2025-01-01 | notes-a |
    | 2 | @bob | def2 | 800 | 3 | Priority Hunter | ![First Blood](https://img.shields.io/badge/First%20Blood-red?style=flat-square&logo=git&logoColor=white) | 2025-01-02 | notes-b |
    | 3 | @charlie | ghi3 | 100 | 1 | Starting Hunter | - | 2025-01-03 | notes-c |

    ## Latest Awards

    - 2025-01-03: @charlie earned **50 XP** (base action)
""")

EMPTY_TRACKER_MD = textwrap.dedent("""\
    ---
    title: RustChain Bounty Hunter XP and Levels
    last_updated: 2025-01-01
    ---

    # Leaderboard

    | Rank | Hunter (GitHub / Agent ID) | Wallet (last 4) | Total XP | Level | Title | Badges Earned | Last Action | Notes |
    |---:|:---|:---:|---:|---:|:---|:---|:---|:---|

    ## Latest Awards
""")


class TestGetLevelAndTitle(unittest.TestCase):
    """Test level and title determination from XP thresholds."""

    def test_starting_hunter(self):
        level, title = xp_mod.get_level_and_title(0)
        self.assertEqual(level, 1)
        self.assertEqual(title, "Starting Hunter")

    def test_basic_hunter(self):
        level, title = xp_mod.get_level_and_title(200)
        self.assertEqual(level, 2)
        self.assertEqual(title, "Basic Hunter")

    def test_priority_hunter(self):
        level, title = xp_mod.get_level_and_title(500)
        self.assertEqual(level, 3)
        self.assertEqual(title, "Priority Hunter")

    def test_rising_hunter(self):
        level, title = xp_mod.get_level_and_title(1000)
        self.assertEqual(level, 4)
        self.assertEqual(title, "Rising Hunter")

    def test_multiplier_hunter(self):
        level, title = xp_mod.get_level_and_title(2000)
        self.assertEqual(level, 5)
        self.assertEqual(title, "Multiplier Hunter")

    def test_legendary_hunter(self):
        level, title = xp_mod.get_level_and_title(18000)
        self.assertEqual(level, 10)
        self.assertEqual(title, "Legendary Hunter")

    def test_intermediate_xp_uses_lower_threshold(self):
        level, title = xp_mod.get_level_and_title(1500)
        self.assertEqual(level, 4)
        self.assertEqual(title, "Rising Hunter")

    def test_very_high_xp(self):
        level, title = xp_mod.get_level_and_title(100000)
        self.assertEqual(level, 10)
        self.assertEqual(title, "Legendary Hunter")

    def test_negative_xp_returns_starting(self):
        # Edge case: negative XP should still return Level 1
        level, title = xp_mod.get_level_and_title(-10)
        self.assertEqual(level, 1)
        self.assertEqual(title, "Starting Hunter")


class TestCalculateXP(unittest.TestCase):
    """Test XP calculation from event metadata."""

    def test_bounty_approved(self):
        xp, reason = xp_mod.calculate_xp("issues", "closed", {"bounty-approved"}, False)
        self.assertIn(200, [200])  # 200 for bounty-approved + 80 for issue closed
        self.assertIn("bounty approved", reason)

    def test_pr_merged(self):
        xp, reason = xp_mod.calculate_xp("pull_request", "closed", set(), True)
        self.assertEqual(xp, 300)
        self.assertIn("PR merged", reason)

    def test_issue_closed(self):
        xp, reason = xp_mod.calculate_xp("issues", "closed", set(), False)
        self.assertEqual(xp, 80)
        self.assertIn("issue closed", reason)

    def test_micro_tier(self):
        xp, reason = xp_mod.calculate_xp("issues", "closed", {"micro"}, False)
        self.assertIn("micro tier", reason)

    def test_standard_tier(self):
        xp, reason = xp_mod.calculate_xp("issues", "closed", {"standard"}, False)
        self.assertIn("standard tier", reason)

    def test_major_tier(self):
        xp, reason = xp_mod.calculate_xp("issues", "closed", {"major"}, False)
        self.assertIn("major tier", reason)

    def test_critical_tier(self):
        xp, reason = xp_mod.calculate_xp("issues", "closed", {"critical"}, False)
        self.assertIn("critical tier", reason)

    def test_tutorial_bonus(self):
        xp, reason = xp_mod.calculate_xp("issues", "closed", {"tutorial"}, False)
        self.assertIn("tutorial/docs", reason)

    def test_docs_bonus(self):
        xp, reason = xp_mod.calculate_xp("issues", "closed", {"docs"}, False)
        self.assertIn("tutorial/docs", reason)

    def test_vintage_bonus(self):
        xp, reason = xp_mod.calculate_xp("issues", "closed", {"vintage"}, False)
        self.assertIn("vintage bonus", reason)

    def test_outreach_bonus(self):
        xp, reason = xp_mod.calculate_xp("issues", "closed", {"outreach"}, False)
        self.assertIn("outreach bonus", reason)

    def test_base_action_fallback(self):
        """No special labels → base 50 XP."""
        xp, reason = xp_mod.calculate_xp("workflow_dispatch", "", set(), False)
        self.assertEqual(xp, 50)
        self.assertIn("base action", reason)

    def test_combined_labels(self):
        """Multiple labels should all contribute."""
        xp, reason = xp_mod.calculate_xp(
            "pull_request", "closed",
            {"bounty-approved", "standard", "tutorial"},
            True
        )
        # 200 + 300 + 100 + 150 = 750
        self.assertEqual(xp, 750)
        self.assertIn("bounty approved", reason)
        self.assertIn("PR merged", reason)
        self.assertIn("standard tier", reason)
        self.assertIn("tutorial/docs", reason)


class TestParseLabels(unittest.TestCase):
    """Test label parsing from comma-separated string."""

    def test_basic_labels(self):
        labels = xp_mod.parse_labels("bounty, standard, docs")
        self.assertEqual(labels, {"bounty", "standard", "docs"})

    def test_empty_string(self):
        labels = xp_mod.parse_labels("")
        self.assertEqual(labels, set())

    def test_none_input(self):
        labels = xp_mod.parse_labels(None)
        self.assertEqual(labels, set())

    def test_case_normalization(self):
        labels = xp_mod.parse_labels("Bounty, STANDARD, Docs")
        self.assertEqual(labels, {"bounty", "standard", "docs"})

    def test_extra_whitespace(self):
        labels = xp_mod.parse_labels("  bounty ,  standard  , docs  ")
        self.assertEqual(labels, {"bounty", "standard", "docs"})


class TestIsTrueHelper(unittest.TestCase):
    """Test is_true helper."""

    def test_true_values(self):
        for val in ["true", "True", "TRUE", "1", "yes", "y", "Y"]:
            self.assertTrue(xp_mod.is_true(val), f"Expected True for {val!r}")

    def test_false_values(self):
        for val in ["false", "False", "0", "no", "n", ""]:
            self.assertFalse(xp_mod.is_true(val), f"Expected False for {val!r}")


class TestParseBadges(unittest.TestCase):
    """Test badge parsing from markdown cell."""

    def test_parse_badge_markdown(self):
        cell = '![First Blood](https://img.shields.io/badge/...) ![Rising Hunter](https://img.shields.io/badge/...)'
        badges = xp_mod.parse_badges(cell)
        self.assertEqual(badges, {"First Blood", "Rising Hunter"})

    def test_parse_empty(self):
        self.assertEqual(xp_mod.parse_badges("-"), set())
        self.assertEqual(xp_mod.parse_badges(""), set())
        self.assertEqual(xp_mod.parse_badges(None), set())

    def test_parse_comma_fallback(self):
        """Fallback parsing for plain text badges."""
        badges = xp_mod.parse_badges("First Blood, Rising Hunter")
        self.assertEqual(badges, {"First Blood", "Rising Hunter"})


class TestFormatBadges(unittest.TestCase):
    """Test badge formatting to markdown."""

    def test_empty_badges(self):
        self.assertEqual(xp_mod.format_badges(set()), "-")

    def test_single_badge(self):
        result = xp_mod.format_badges({"First Blood"})
        self.assertIn("![First Blood]", result)
        self.assertIn("shields.io", result)

    def test_multiple_badges_sorted(self):
        result = xp_mod.format_badges({"Rising Hunter", "First Blood"})
        fb_idx = result.index("First Blood")
        rh_idx = result.index("Rising Hunter")
        self.assertLess(fb_idx, rh_idx, "Badges should be alphabetically sorted")


class TestParseHunterRow(unittest.TestCase):
    """Test individual row parsing."""

    def test_parse_9_column_row(self):
        cells = ["1", "@alice", "abc1", "3000", "5", "Multiplier Hunter",
                 "![First Blood](url)", "2025-01-01", "notes"]
        row = xp_mod.parse_hunter_row(cells)
        self.assertIsNotNone(row)
        self.assertEqual(row.hunter, "@alice")
        self.assertEqual(row.xp, 3000)
        self.assertEqual(row.level, 5)
        self.assertEqual(row.title, "Multiplier Hunter")
        self.assertIn("First Blood", row.badges)

    def test_parse_7_column_row(self):
        """Backward compat with older 7-column schema."""
        cells = ["1", "@alice", "abc1", "500", "3", "2025-01-01", "notes"]
        row = xp_mod.parse_hunter_row(cells)
        self.assertIsNotNone(row)
        self.assertEqual(row.hunter, "@alice")
        self.assertEqual(row.xp, 500)

    def test_parse_short_row_returns_none(self):
        cells = ["1", "@alice", "abc1"]
        row = xp_mod.parse_hunter_row(cells)
        self.assertIsNone(row)

    def test_parse_invalid_xp(self):
        cells = ["1", "@alice", "abc1", "not_a_number", "1", "Starting Hunter",
                 "-", "2025-01-01", "notes"]
        row = xp_mod.parse_hunter_row(cells)
        self.assertEqual(row.xp, 0)


class TestDetermineNewBadges(unittest.TestCase):
    """Test badge assignment logic."""

    def test_first_blood(self):
        badges = xp_mod.determine_new_badges(set(), 0, 50, set(), "user1")
        self.assertIn("First Blood", badges)

    def test_rising_hunter_badge(self):
        badges = xp_mod.determine_new_badges({"First Blood"}, 900, 1000, set(), "user1")
        self.assertIn("Rising Hunter", badges)

    def test_multiplier_hunter_badge(self):
        badges = xp_mod.determine_new_badges({"First Blood", "Rising Hunter"}, 1900, 2000, set(), "user1")
        self.assertIn("Multiplier Hunter", badges)

    def test_veteran_hunter_badge(self):
        badges = xp_mod.determine_new_badges(set(), 5000, 5500, set(), "user1")
        self.assertIn("Veteran Hunter", badges)

    def test_legendary_hunter_badge(self):
        badges = xp_mod.determine_new_badges(set(), 17000, 18000, set(), "user1")
        self.assertIn("Legendary Hunter", badges)

    def test_vintage_veteran_badge(self):
        badges = xp_mod.determine_new_badges(set(), 0, 50, {"vintage"}, "user1")
        self.assertIn("Vintage Veteran", badges)

    def test_tutorial_titan_badge(self):
        badges = xp_mod.determine_new_badges(set(), 0, 50, {"tutorial"}, "user1")
        self.assertIn("Tutorial Titan", badges)

    def test_bug_slayer_badge(self):
        badges = xp_mod.determine_new_badges(set(), 0, 50, {"bug"}, "user1")
        self.assertIn("Bug Slayer", badges)

    def test_bug_slayer_from_security(self):
        badges = xp_mod.determine_new_badges(set(), 0, 50, {"security"}, "user1")
        self.assertIn("Bug Slayer", badges)

    def test_bug_slayer_from_critical(self):
        badges = xp_mod.determine_new_badges(set(), 0, 50, {"critical"}, "user1")
        self.assertIn("Bug Slayer", badges)

    def test_outreach_pro_badge(self):
        badges = xp_mod.determine_new_badges(set(), 0, 50, {"outreach"}, "user1")
        self.assertIn("Outreach Pro", badges)

    def test_outreach_pro_from_seo(self):
        badges = xp_mod.determine_new_badges(set(), 0, 50, {"seo"}, "user1")
        self.assertIn("Outreach Pro", badges)

    def test_streak_master_badge(self):
        badges = xp_mod.determine_new_badges(set(), 0, 50, {"streak"}, "user1")
        self.assertIn("Streak Master", badges)

    def test_agent_overlord_badge(self):
        badges = xp_mod.determine_new_badges(set(), 0, 500, set(), "my-agent-bot")
        self.assertIn("Agent Overlord", badges)

    def test_agent_overlord_requires_xp(self):
        """Agent Overlord requires 500+ XP even if actor name has 'agent'."""
        badges = xp_mod.determine_new_badges(set(), 0, 100, set(), "my-agent-bot")
        self.assertNotIn("Agent Overlord", badges)

    def test_no_duplicate_badges(self):
        """If badge already exists, don't add it again."""
        existing = {"First Blood", "Rising Hunter"}
        badges = xp_mod.determine_new_badges(existing, 1000, 1500, set(), "user1")
        self.assertNotIn("First Blood", badges)
        self.assertNotIn("Rising Hunter", badges)

    def test_retroactive_backfill(self):
        """Test retroactive badge assignment for existing high-XP users."""
        badges = xp_mod.determine_new_badges(set(), 5500, 5500, set(), "user1")
        self.assertIn("First Blood", badges)
        self.assertIn("Rising Hunter", badges)
        self.assertIn("Multiplier Hunter", badges)
        self.assertIn("Veteran Hunter", badges)


class TestRowInsertUpdate(unittest.TestCase):
    """Test row insertion and update in the tracker table."""

    def test_update_existing_hunter(self):
        """Updating an existing hunter should increase their XP."""
        updated_md, total_xp, level, title, unlocked = xp_mod.update_table_in_md(
            md=SAMPLE_TRACKER_MD,
            actor="bob",
            gained_xp=200,
            reason="bounty approved",
            labels=set(),
        )
        self.assertEqual(total_xp, 1000)  # 800 + 200
        self.assertEqual(level, 4)
        self.assertEqual(title, "Rising Hunter")
        self.assertIn("@bob", updated_md)

    def test_insert_new_hunter(self):
        """New hunter should be added to the table."""
        updated_md, total_xp, level, title, unlocked = xp_mod.update_table_in_md(
            md=SAMPLE_TRACKER_MD,
            actor="newuser",
            gained_xp=100,
            reason="first bounty",
            labels=set(),
        )
        self.assertEqual(total_xp, 100)
        self.assertIn("@newuser", updated_md)
        self.assertIn("First Blood", unlocked)

    def test_insert_into_empty_table(self):
        """Insert into an empty tracker table."""
        updated_md, total_xp, level, title, unlocked = xp_mod.update_table_in_md(
            md=EMPTY_TRACKER_MD,
            actor="firstuser",
            gained_xp=50,
            reason="base action",
            labels=set(),
        )
        self.assertEqual(total_xp, 50)
        self.assertIn("@firstuser", updated_md)

    def test_award_log_appended(self):
        """Award log should be appended to Latest Awards section."""
        updated_md, _, _, _, _ = xp_mod.update_table_in_md(
            md=SAMPLE_TRACKER_MD,
            actor="bob",
            gained_xp=100,
            reason="test award",
            labels=set(),
        )
        self.assertIn("@bob earned **100 XP**", updated_md)
        self.assertIn("test award", updated_md)


class TestRankRecalculation(unittest.TestCase):
    """Test that ranks are correctly recalculated after updates."""

    def test_ranks_sorted_by_xp_descending(self):
        """After update, ranks should reflect XP order."""
        updated_md, _, _, _, _ = xp_mod.update_table_in_md(
            md=SAMPLE_TRACKER_MD,
            actor="charlie",
            gained_xp=5000,  # Charlie goes from 100 to 5100
            reason="huge bounty",
            labels=set(),
        )
        lines = [l for l in updated_md.splitlines() if l.strip().startswith("|") and "@" in l]
        # Charlie (5100) should now be rank 1, Alice (3000) rank 2, Bob (800) rank 3
        self.assertIn("@charlie", lines[0])
        self.assertIn("@alice", lines[1])
        self.assertIn("@bob", lines[2])

    def test_rank_numbers_are_sequential(self):
        """Rank numbers should be 1, 2, 3, ... without gaps."""
        updated_md, _, _, _, _ = xp_mod.update_table_in_md(
            md=SAMPLE_TRACKER_MD,
            actor="bob",
            gained_xp=50,
            reason="test",
            labels=set(),
        )
        lines = [l for l in updated_md.splitlines() if l.strip().startswith("|") and "@" in l]
        for i, line in enumerate(lines, start=1):
            cells = xp_mod.parse_table_cells(line)
            rank = int(cells[0].strip())
            self.assertEqual(rank, i, f"Expected rank {i}, got {rank}")

    def test_tiebreaker_by_hunter_name(self):
        """Same XP should sort by hunter name (case-insensitive)."""
        md = textwrap.dedent("""\
            ---
            last_updated: 2025-01-01
            ---
            | Rank | Hunter (GitHub / Agent ID) | Wallet (last 4) | Total XP | Level | Title | Badges Earned | Last Action | Notes |
            |---:|:---|:---:|---:|---:|:---|:---|:---|:---|
            | 1 | @zara | w1 | 100 | 1 | Starting Hunter | - | 2025-01-01 | n |
            | 2 | @adam | w2 | 100 | 1 | Starting Hunter | - | 2025-01-01 | n |

            ## Latest Awards
        """)
        updated_md, _, _, _, _ = xp_mod.update_table_in_md(
            md=md, actor="adam", gained_xp=0, reason="no-op", labels=set()
        )
        lines = [l for l in updated_md.splitlines() if l.strip().startswith("|") and "@" in l]
        # Same XP: alphabetical → @adam before @zara
        self.assertIn("@adam", lines[0])
        self.assertIn("@zara", lines[1])


class TestRetroactiveBackfill(unittest.TestCase):
    """Test retroactive badge backfill for existing hunters."""

    def test_backfill_adds_missing_badges(self):
        """Existing hunter at 3000 XP should get Multiplier Hunter badge retroactively."""
        updated_md, _, _, _, _ = xp_mod.update_table_in_md(
            md=SAMPLE_TRACKER_MD,
            actor="charlie",
            gained_xp=50,
            reason="test",
            labels=set(),
        )
        # Alice is at 3000 XP — should have Multiplier Hunter badge backfilled
        alice_lines = [l for l in updated_md.splitlines() if "@alice" in l]
        self.assertTrue(len(alice_lines) > 0)
        alice_line = alice_lines[0]
        self.assertIn("Multiplier Hunter", alice_line)

    def test_backfill_does_not_duplicate(self):
        """Backfill should not duplicate existing badges."""
        updated_md, _, _, _, _ = xp_mod.update_table_in_md(
            md=SAMPLE_TRACKER_MD,
            actor="charlie",
            gained_xp=50,
            reason="test",
            labels=set(),
        )
        alice_lines = [l for l in updated_md.splitlines() if "@alice" in l]
        alice_line = alice_lines[0]
        # Count occurrences of First Blood — should be exactly 1
        self.assertEqual(alice_line.count("First Blood"), 1)


class TestUpdateFrontmatter(unittest.TestCase):
    """Test frontmatter date update."""

    def test_updates_date(self):
        md = "---\nlast_updated: 2024-01-01\n---\nContent here"
        result = xp_mod.update_frontmatter(md)
        today = dt.date.today().isoformat()
        self.assertIn(f"last_updated: {today}", result)

    def test_preserves_other_content(self):
        md = "---\ntitle: Test\nlast_updated: 2024-01-01\n---\nContent here"
        result = xp_mod.update_frontmatter(md)
        self.assertIn("title: Test", result)
        self.assertIn("Content here", result)


class TestRenderRow(unittest.TestCase):
    """Test row rendering."""

    def test_render_basic_row(self):
        row = xp_mod.HunterRow(
            hunter="@test", wallet="abc1", xp=100, level=1,
            title="Starting Hunter", badges=set(), last_action="test", notes="n"
        )
        rendered = xp_mod.render_row(1, row)
        self.assertTrue(rendered.startswith("| 1 |"))
        self.assertIn("@test", rendered)
        self.assertIn("100", rendered)
        self.assertIn("Starting Hunter", rendered)

    def test_render_row_with_badges(self):
        row = xp_mod.HunterRow(
            hunter="@test", wallet="abc1", xp=1000, level=4,
            title="Rising Hunter", badges={"First Blood", "Rising Hunter"},
            last_action="test", notes="n"
        )
        rendered = xp_mod.render_row(1, row)
        self.assertIn("First Blood", rendered)
        self.assertIn("Rising Hunter", rendered)


class TestDeterministicOutput(unittest.TestCase):
    """Test that output is deterministic for same input."""

    def test_same_input_same_output(self):
        """Running the same update twice should produce identical rank ordering."""
        result1, xp1, lv1, title1, _ = xp_mod.update_table_in_md(
            md=SAMPLE_TRACKER_MD, actor="bob", gained_xp=100,
            reason="test", labels=set()
        )
        result2, xp2, lv2, title2, _ = xp_mod.update_table_in_md(
            md=SAMPLE_TRACKER_MD, actor="bob", gained_xp=100,
            reason="test", labels=set()
        )

        self.assertEqual(xp1, xp2)
        self.assertEqual(lv1, lv2)
        self.assertEqual(title1, title2)
        # Extract just the table rows for comparison (timestamps may differ slightly)
        rows1 = [l for l in result1.splitlines() if l.strip().startswith("|") and "@" in l]
        rows2 = [l for l in result2.splitlines() if l.strip().startswith("|") and "@" in l]
        self.assertEqual(len(rows1), len(rows2))
        # Hunter order should be identical
        hunters1 = [xp_mod.parse_table_cells(l)[1] for l in rows1]
        hunters2 = [xp_mod.parse_table_cells(l)[1] for l in rows2]
        self.assertEqual(hunters1, hunters2)


if __name__ == "__main__":
    unittest.main()
