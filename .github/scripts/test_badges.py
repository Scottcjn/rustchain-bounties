#!/usr/bin/env python3
"""Test suite for generate_dynamic_badges.py"""

import unittest
import json
import tempfile
from pathlib import Path
from generate_dynamic_badges import parse_rows, slugify_hunter, validate_badge, parse_xp_from_action, parse_date_from_action

class TestBadgeGenerator(unittest.TestCase):
    def test_slugify(self):
        used = set()
        self.assertEqual(slugify_hunter("@Alice", used), "alice")
        used.add("alice")
        self.assertEqual(slugify_hunter("@Alice", used), "alice-2")
        self.assertEqual(slugify_hunter("Bob!@#", set()), "bob")

    def test_parse_xp(self):
        self.assertEqual(parse_xp_from_action("2026-02-20: +50 XP (note)"), 50)
        self.assertEqual(parse_xp_from_action("no xp here"), 0)

    def test_parse_date(self):
        dt_val = parse_date_from_action("2026-02-20: +50 XP")
        self.assertIsNotNone(dt_val)
        self.assertEqual(dt_val.year, 2026)
        self.assertEqual(dt_val.month, 2)
        self.assertEqual(dt_val.day, 20)

    def test_validate_badge(self):
        valid = {
            "schemaVersion": 1,
            "label": "test",
            "message": "msg",
            "color": "blue"
        }
        self.assertTrue(validate_badge(valid))
        self.assertFalse(validate_badge({"schemaVersion": 2}))
        self.assertFalse(validate_badge({}))

    def test_parse_rows(self):
        md = """
| Rank | Hunter | Wallet | Total XP | Level | Title | Badges Earned | Last Action | Notes |
|---:|:---|:---:|---:|---:|:---|:---|:---|:---|
| 1 | @Hunter1 | 0x123 | 500 | 3 | Title | ![First Blood](url) | 2026-02-20: +100 XP | auto |
"""
        rows = parse_rows(md)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["hunter"], "@Hunter1")
        self.assertEqual(rows[0]["xp"], 500)
        self.assertIn("First Blood", rows[0]["badges"])

if __name__ == "__main__":
    unittest.main()
