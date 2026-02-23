#!/usr/bin/env python3
import json
import unittest
from pathlib import Path
import sys
import datetime as dt

# Load badge script module from .github/scripts
SCRIPT_DIR = Path(__file__).resolve().parent.parent / ".github" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
import generate_dynamic_badges

class TestBadgeGenerator(unittest.TestCase):
    def test_parse_int(self):
        self.assertEqual(generate_dynamic_badges.parse_int("+300"), 300)
        self.assertEqual(generate_dynamic_badges.parse_int("100"), 100)
        self.assertEqual(generate_dynamic_badges.parse_int("None"), 0)

    def test_slugify_hunter(self):
        self.assertEqual(generate_dynamic_badges.slugify_hunter("@AdnanMehr8"), "adnanmehr8")
        self.assertEqual(generate_dynamic_badges.slugify_hunter("Agent 007"), "agent-007")

    def test_calculate_weekly_growth(self):
        rows = [
            {"last_action": "2026-02-22: +100 XP"},
            {"last_action": "2026-01-01: +500 XP"}, # Old
            {"last_action": "Invalid date"},
        ]
        growth = generate_dynamic_badges.calculate_weekly_growth(
            rows,
            reference_date=dt.date(2026, 2, 23),
        )
        self.assertEqual(growth, 100)

    def test_color_for_level(self):
        self.assertEqual(generate_dynamic_badges.color_for_level(1), "blue")
        self.assertEqual(generate_dynamic_badges.color_for_level(10), "gold")

if __name__ == "__main__":
    unittest.main()
