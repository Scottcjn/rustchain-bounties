#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Tests for scripts/retention_metrics.py.

The correctness risks worth pinning:
  - farm accounts must be excluded from human figures, never blended in
    (blending is what made the first hand-run report 2% instead of 0%)
  - a cohort younger than 30 days must read "immature", not 0% retention,
    or a healthy new cohort looks like total churn
  - maintainers post bounties rather than claim them and must not count
"""
import datetime
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "retention_metrics.py"
spec = importlib.util.spec_from_file_location("retention_under_test", SCRIPT)
rm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rm)

TODAY = datetime.date(2026, 8, 7)


def rows(*pairs):
    return sorted(pairs)


class FarmExclusionTests(unittest.TestCase):
    def test_farm_excluded_from_human_counts(self):
        data = rows(*[("2026-05-01", "farm")] * 30, ("2026-05-01", "alice"))
        r = rm.analyse(data, farm_threshold=21, today=TODAY)
        self.assertEqual(r["farm_accounts"], 1)
        self.assertEqual(r["farm_claims"], 30)
        self.assertEqual(r["human_accounts"], 1)
        self.assertEqual(r["human_claims"], 1)

    def test_farm_absent_from_weekly_people(self):
        data = rows(*[("2026-05-04", "farm")] * 25, ("2026-05-04", "alice"))
        r = rm.analyse(data, farm_threshold=21, today=TODAY)
        wk = [w for w in r["weekly"] if w["week"] == "2026-05-04"][0]
        self.assertEqual(wk["people"], 1)

    def test_farm_absent_from_cohorts(self):
        data = rows(*[("2026-05-01", "farm")] * 25, ("2026-05-01", "alice"))
        r = rm.analyse(data, farm_threshold=21, today=TODAY)
        c = [c for c in r["cohorts"] if c["cohort"] == "2026-05"][0]
        self.assertEqual(c["people"], 1)


class CohortMaturityTests(unittest.TestCase):
    def test_young_cohort_is_immature_not_zero(self):
        """A cohort with no 30-day runway must not read as 0% churn."""
        recent = (TODAY - datetime.timedelta(days=5)).isoformat()
        r = rm.analyse(rows((recent, "newbie")), 21, TODAY)
        c = [c for c in r["cohorts"] if c["cohort"] == recent[:7]][0]
        self.assertEqual(c["mature"], 0)
        self.assertIsNone(c["retention_pct"])

    def test_retained_requires_more_than_30_days_span(self):
        data = rows(("2026-05-01", "stayer"), ("2026-06-20", "stayer"),
                    ("2026-05-01", "leaver"))
        r = rm.analyse(data, 21, TODAY)
        c = [c for c in r["cohorts"] if c["cohort"] == "2026-05"][0]
        self.assertEqual(c["mature"], 2)
        self.assertEqual(c["retained_30d"], 1)
        self.assertEqual(c["retention_pct"], 50.0)

    def test_one_and_done_counted(self):
        data = rows(("2026-05-01", "once"), ("2026-05-02", "twice"),
                    ("2026-05-09", "twice"))
        r = rm.analyse(data, 21, TODAY)
        c = [c for c in r["cohorts"] if c["cohort"] == "2026-05"][0]
        self.assertEqual(c["one_and_done"], 1)


class WeeklyTests(unittest.TestCase):
    def test_new_vs_returning(self):
        data = rows(("2026-05-04", "alice"), ("2026-05-11", "alice"),
                    ("2026-05-11", "bob"))
        r = rm.analyse(data, 21, TODAY)
        w2 = [w for w in r["weekly"] if w["week"] == "2026-05-11"][0]
        self.assertEqual(w2["new"], 1)        # bob
        self.assertEqual(w2["returning"], 1)  # alice

    def test_week_of_snaps_to_monday(self):
        self.assertEqual(rm.week_of("2026-08-07"), "2026-08-03")  # Fri -> Mon
        self.assertEqual(rm.week_of("2026-08-03"), "2026-08-03")


class MaintainerTests(unittest.TestCase):
    def test_maintainers_are_filtered_by_fetch(self):
        self.assertIn("scottcjn", rm.MAINTAINERS)
        self.assertIn("sophiaeagent-beep", rm.MAINTAINERS)


if __name__ == "__main__":
    unittest.main()
