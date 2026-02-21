#!/usr/bin/env python3
"""Tests for .github/scripts/generate_dynamic_badges.py

Covers:
- Empty table handling
- Populated table parsing and badge generation
- Slug generation for hunter names
- Schema correctness of generated badge JSON
- Edge cases and error handling
"""

import json
import re
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

# Add the script directory to import path
SCRIPT_DIR = Path(__file__).resolve().parent.parent / ".github" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import generate_dynamic_badges as badge_mod


# ─── Sample Tracker Markdown ────────────────────────────────────────────────

POPULATED_TRACKER = textwrap.dedent("""\
    ---
    title: RustChain Bounty Hunter XP and Levels
    last_updated: 2025-01-01
    ---

    # Leaderboard

    | Rank | Hunter (GitHub / Agent ID) | Wallet (last 4) | Total XP | Level | Title | Badges Earned | Last Action | Notes |
    |---:|:---|:---:|---:|---:|:---|:---|:---|:---|
    | 1 | @alice | abc1 | 20000 | 10 | Legendary Hunter | ![First Blood](url) | 2025-01-01 | notes-a |
    | 2 | @bob | def2 | 5500 | 7 | Veteran Hunter | ![First Blood](url) | 2025-01-02 | notes-b |
    | 3 | @charlie | ghi3 | 2000 | 5 | Multiplier Hunter | - | 2025-01-03 | notes-c |
    | 4 | @new-agent-01 | jkl4 | 100 | 1 | Starting Hunter | - | 2025-01-04 | notes-d |

    ## Latest Awards
""")

EMPTY_TRACKER = textwrap.dedent("""\
    ---
    title: RustChain Bounty Hunter XP and Levels
    last_updated: 2025-01-01
    ---

    # Leaderboard

    | Rank | Hunter (GitHub / Agent ID) | Wallet (last 4) | Total XP | Level | Title | Badges Earned | Last Action | Notes |
    |---:|:---|:---:|---:|---:|:---|:---|:---|:---|

    ## Latest Awards
""")

TBD_TRACKER = textwrap.dedent("""\
    ---
    title: Test
    last_updated: 2025-01-01
    ---

    | Rank | Hunter (GitHub / Agent ID) | Wallet (last 4) | Total XP | Level | Title | Badges Earned | Last Action | Notes |
    |---:|:---|:---:|---:|---:|:---|:---|:---|:---|
    | 1 | _TBD_ | _TBD_ | 0 | 1 | Starting Hunter | - | bootstrap | tracker initialized |
""")


class TestParseRows(unittest.TestCase):
    """Test table row parsing."""

    def test_parse_populated_table(self):
        rows = badge_mod.parse_rows(POPULATED_TRACKER)
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["hunter"], "@alice")
        self.assertEqual(rows[0]["xp"], 20000)
        self.assertEqual(rows[0]["level"], 10)
        self.assertEqual(rows[0]["title"], "Legendary Hunter")

    def test_parse_empty_table(self):
        rows = badge_mod.parse_rows(EMPTY_TRACKER)
        self.assertEqual(len(rows), 0)

    def test_parse_tbd_rows_excluded(self):
        """_TBD_ placeholder rows should be excluded."""
        rows = badge_mod.parse_rows(TBD_TRACKER)
        self.assertEqual(len(rows), 0)

    def test_parse_ordering(self):
        """Rows should be sorted by XP descending."""
        rows = badge_mod.parse_rows(POPULATED_TRACKER)
        xp_values = [row["xp"] for row in rows]
        self.assertEqual(xp_values, sorted(xp_values, reverse=True))

    def test_parse_rank_assignment(self):
        """Ranks should be re-assigned sequentially."""
        rows = badge_mod.parse_rows(POPULATED_TRACKER)
        ranks = [row["rank"] for row in rows]
        self.assertEqual(ranks, [1, 2, 3, 4])

    def test_parse_no_header(self):
        """Markdown without the expected header should return empty."""
        rows = badge_mod.parse_rows("# No Table Here\n\nJust text.")
        self.assertEqual(len(rows), 0)

    def test_parse_separator_line_skipped(self):
        """Separator lines (|---|---) should be skipped."""
        md = textwrap.dedent("""\
            | Rank | Hunter (GitHub / Agent ID) | Wallet (last 4) | Total XP | Level | Title | Badges Earned | Last Action | Notes |
            |---:|:---|:---:|---:|---:|:---|:---|:---|:---|
            |---|---|---|---|---|---|---|---|---|
            | 1 | @test | w1 | 100 | 1 | Starting Hunter | - | 2025-01-01 | n |
        """)
        rows = badge_mod.parse_rows(md)
        self.assertEqual(len(rows), 1)


class TestParseInt(unittest.TestCase):
    """Test integer extraction from strings."""

    def test_simple_number(self):
        self.assertEqual(badge_mod.parse_int("123"), 123)

    def test_number_with_text(self):
        self.assertEqual(badge_mod.parse_int("Level 5"), 5)

    def test_empty_string(self):
        self.assertEqual(badge_mod.parse_int(""), 0)

    def test_no_number(self):
        self.assertEqual(badge_mod.parse_int("abc"), 0)

    def test_none_input(self):
        self.assertEqual(badge_mod.parse_int(None), 0)


class TestSlugifyHunter(unittest.TestCase):
    """Test slug generation for hunter names."""

    def test_basic_slug(self):
        self.assertEqual(badge_mod.slugify_hunter("@alice"), "alice")

    def test_hyphenated_name(self):
        self.assertEqual(badge_mod.slugify_hunter("@new-agent-01"), "new-agent-01")

    def test_uppercase_normalized(self):
        self.assertEqual(badge_mod.slugify_hunter("@Alice"), "alice")

    def test_at_sign_stripped(self):
        self.assertEqual(badge_mod.slugify_hunter("@bob"), "bob")
        self.assertEqual(badge_mod.slugify_hunter("bob"), "bob")

    def test_special_chars_replaced(self):
        slug = badge_mod.slugify_hunter("@user with spaces!")
        self.assertNotIn(" ", slug)
        self.assertNotIn("!", slug)
        self.assertTrue(re.match(r'^[a-z0-9._-]+$', slug))

    def test_empty_input(self):
        self.assertEqual(badge_mod.slugify_hunter(""), "unknown")
        self.assertEqual(badge_mod.slugify_hunter("@"), "unknown")

    def test_dots_preserved(self):
        self.assertEqual(badge_mod.slugify_hunter("@user.name"), "user.name")

    def test_underscores_preserved(self):
        self.assertEqual(badge_mod.slugify_hunter("@user_name"), "user_name")


class TestColorForLevel(unittest.TestCase):
    """Test color assignment by level."""

    def test_level_1(self):
        self.assertEqual(badge_mod.color_for_level(1), "blue")

    def test_level_3(self):
        self.assertEqual(badge_mod.color_for_level(3), "blue")

    def test_level_4(self):
        self.assertEqual(badge_mod.color_for_level(4), "orange")

    def test_level_5(self):
        self.assertEqual(badge_mod.color_for_level(5), "yellow")

    def test_level_7(self):
        self.assertEqual(badge_mod.color_for_level(7), "purple")

    def test_level_10(self):
        self.assertEqual(badge_mod.color_for_level(10), "gold")

    def test_level_above_10(self):
        self.assertEqual(badge_mod.color_for_level(15), "gold")


class TestWriteBadge(unittest.TestCase):
    """Test badge JSON file writing."""

    def test_badge_schema(self):
        """Generated badge should have correct shields.io endpoint schema."""
        with tempfile.TemporaryDirectory() as tmpdir:
            badge_path = Path(tmpdir) / "test-badge.json"
            badge_mod.write_badge(
                badge_path,
                label="Test Label",
                message="Test Message",
                color="blue",
                named_logo="github",
                logo_color="white",
            )

            self.assertTrue(badge_path.exists())
            data = json.loads(badge_path.read_text())

            # Verify schema
            self.assertEqual(data["schemaVersion"], 1)
            self.assertEqual(data["label"], "Test Label")
            self.assertEqual(data["message"], "Test Message")
            self.assertEqual(data["color"], "blue")
            self.assertEqual(data["namedLogo"], "github")
            self.assertEqual(data["logoColor"], "white")

    def test_badge_creates_parent_dirs(self):
        """write_badge should create parent directories if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            badge_path = Path(tmpdir) / "nested" / "dir" / "badge.json"
            badge_mod.write_badge(badge_path, "L", "M", "blue")
            self.assertTrue(badge_path.exists())

    def test_badge_file_is_valid_json(self):
        """All generated badge files should be valid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            badge_path = Path(tmpdir) / "badge.json"
            badge_mod.write_badge(badge_path, "Label", "Message", "red")

            content = badge_path.read_text()
            data = json.loads(content)
            self.assertIsInstance(data, dict)

    def test_badge_file_ends_with_newline(self):
        """Badge files should end with a newline for POSIX compliance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            badge_path = Path(tmpdir) / "badge.json"
            badge_mod.write_badge(badge_path, "L", "M", "blue")
            content = badge_path.read_text()
            self.assertTrue(content.endswith("\n"))


class TestEndToEndBadgeGeneration(unittest.TestCase):
    """End-to-end tests for badge generation."""

    def test_populated_table_generates_all_badges(self):
        """Populated table should generate summary + per-hunter badges."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = Path(tmpdir) / "XP_TRACKER.md"
            tracker.write_text(POPULATED_TRACKER)
            out_dir = Path(tmpdir) / "badges"

            # Monkey-patch sys.argv for the script
            sys.argv = ["generate_dynamic_badges.py",
                        "--tracker", str(tracker),
                        "--out-dir", str(out_dir)]
            badge_mod.main()

            # Check summary badges exist
            self.assertTrue((out_dir / "hunter-stats.json").exists())
            self.assertTrue((out_dir / "top-hunter.json").exists())
            self.assertTrue((out_dir / "active-hunters.json").exists())
            self.assertTrue((out_dir / "legendary-hunters.json").exists())
            self.assertTrue((out_dir / "updated-at.json").exists())

            # Check per-hunter badges
            hunters_dir = out_dir / "hunters"
            self.assertTrue(hunters_dir.exists())
            self.assertTrue((hunters_dir / "alice.json").exists())
            self.assertTrue((hunters_dir / "bob.json").exists())
            self.assertTrue((hunters_dir / "charlie.json").exists())
            self.assertTrue((hunters_dir / "new-agent-01.json").exists())

    def test_populated_table_badge_content(self):
        """Verify content of generated badges."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = Path(tmpdir) / "XP_TRACKER.md"
            tracker.write_text(POPULATED_TRACKER)
            out_dir = Path(tmpdir) / "badges"

            sys.argv = ["generate_dynamic_badges.py",
                        "--tracker", str(tracker),
                        "--out-dir", str(out_dir)]
            badge_mod.main()

            # Check hunter-stats
            stats = json.loads((out_dir / "hunter-stats.json").read_text())
            self.assertEqual(stats["schemaVersion"], 1)
            self.assertEqual(stats["label"], "Bounty Hunter XP")
            self.assertIn("total", stats["message"])
            self.assertEqual(stats["color"], "orange")  # total_xp > 0

            # Check top-hunter
            top = json.loads((out_dir / "top-hunter.json").read_text())
            self.assertIn("alice", top["message"])
            self.assertIn("20000", top["message"])
            self.assertEqual(top["color"], "gold")

            # Check active-hunters
            active = json.loads((out_dir / "active-hunters.json").read_text())
            self.assertEqual(active["message"], "4")

            # Check legendary-hunters
            legendary = json.loads((out_dir / "legendary-hunters.json").read_text())
            self.assertEqual(legendary["message"], "1")  # Only alice is level 10+
            self.assertEqual(legendary["color"], "gold")

    def test_empty_table_generates_badges(self):
        """Empty table should still generate summary badges with defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = Path(tmpdir) / "XP_TRACKER.md"
            tracker.write_text(EMPTY_TRACKER)
            out_dir = Path(tmpdir) / "badges"

            sys.argv = ["generate_dynamic_badges.py",
                        "--tracker", str(tracker),
                        "--out-dir", str(out_dir)]
            badge_mod.main()

            # Summary badges should exist
            self.assertTrue((out_dir / "hunter-stats.json").exists())
            self.assertTrue((out_dir / "top-hunter.json").exists())
            self.assertTrue((out_dir / "active-hunters.json").exists())

            # Check empty-state values
            stats = json.loads((out_dir / "hunter-stats.json").read_text())
            self.assertIn("0", stats["message"])
            self.assertEqual(stats["color"], "blue")  # total_xp == 0

            top = json.loads((out_dir / "top-hunter.json").read_text())
            self.assertEqual(top["message"], "none yet")
            self.assertEqual(top["color"], "lightgrey")

            active = json.loads((out_dir / "active-hunters.json").read_text())
            self.assertEqual(active["message"], "0")

            # No per-hunter badges should exist
            hunters_dir = out_dir / "hunters"
            if hunters_dir.exists():
                self.assertEqual(len(list(hunters_dir.glob("*.json"))), 0)

    def test_per_hunter_badge_content(self):
        """Per-hunter badge should contain correct XP and level info."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = Path(tmpdir) / "XP_TRACKER.md"
            tracker.write_text(POPULATED_TRACKER)
            out_dir = Path(tmpdir) / "badges"

            sys.argv = ["generate_dynamic_badges.py",
                        "--tracker", str(tracker),
                        "--out-dir", str(out_dir)]
            badge_mod.main()

            alice = json.loads((out_dir / "hunters" / "alice.json").read_text())
            self.assertIn("20000", alice["message"])
            self.assertIn("L10", alice["message"])
            self.assertIn("Legendary", alice["message"])
            self.assertEqual(alice["color"], "gold")

            charlie = json.loads((out_dir / "hunters" / "charlie.json").read_text())
            self.assertIn("2000", charlie["message"])
            self.assertIn("L5", charlie["message"])
            self.assertEqual(charlie["color"], "yellow")

    def test_stale_hunter_files_removed(self):
        """Old per-hunter badge files should be cleaned up."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = Path(tmpdir) / "XP_TRACKER.md"
            tracker.write_text(POPULATED_TRACKER)
            out_dir = Path(tmpdir) / "badges"
            hunters_dir = out_dir / "hunters"
            hunters_dir.mkdir(parents=True, exist_ok=True)

            # Create a stale badge file
            stale_file = hunters_dir / "old-hunter.json"
            stale_file.write_text('{"stale": true}')
            self.assertTrue(stale_file.exists())

            sys.argv = ["generate_dynamic_badges.py",
                        "--tracker", str(tracker),
                        "--out-dir", str(out_dir)]
            badge_mod.main()

            # Stale file should be removed
            self.assertFalse(stale_file.exists())
            # Active hunters should exist
            self.assertTrue((hunters_dir / "alice.json").exists())


class TestBadgeSchemaCorrectness(unittest.TestCase):
    """Test that all generated badges follow the shields.io endpoint schema."""

    REQUIRED_KEYS = {"schemaVersion", "label", "message", "color"}

    def test_all_badges_have_required_keys(self):
        """Every badge file should contain all required keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = Path(tmpdir) / "XP_TRACKER.md"
            tracker.write_text(POPULATED_TRACKER)
            out_dir = Path(tmpdir) / "badges"

            sys.argv = ["generate_dynamic_badges.py",
                        "--tracker", str(tracker),
                        "--out-dir", str(out_dir)]
            badge_mod.main()

            for badge_file in out_dir.rglob("*.json"):
                data = json.loads(badge_file.read_text())
                for key in self.REQUIRED_KEYS:
                    self.assertIn(key, data, f"Missing {key} in {badge_file.name}")
                self.assertEqual(data["schemaVersion"], 1)

    def test_all_badges_are_valid_json(self):
        """Every badge file should be valid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = Path(tmpdir) / "XP_TRACKER.md"
            tracker.write_text(POPULATED_TRACKER)
            out_dir = Path(tmpdir) / "badges"

            sys.argv = ["generate_dynamic_badges.py",
                        "--tracker", str(tracker),
                        "--out-dir", str(out_dir)]
            badge_mod.main()

            for badge_file in out_dir.rglob("*.json"):
                try:
                    data = json.loads(badge_file.read_text())
                    self.assertIsInstance(data, dict)
                except json.JSONDecodeError:
                    self.fail(f"Invalid JSON in {badge_file}")


if __name__ == "__main__":
    unittest.main()
