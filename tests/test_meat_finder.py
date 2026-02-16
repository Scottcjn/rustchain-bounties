import os
import unittest

from agent_framework.meat_finder import MeatFinder
import agent_framework.meat_finder as meat_finder


class FakeResp:
    def __init__(self, status_code=200, payload=None, headers=None):
        self.status_code = status_code
        self._payload = payload or []
        self.headers = headers or {}

    def json(self):
        return self._payload


class MeatFinderTests(unittest.TestCase):
    def test_next_link_parsing(self):
        finder = MeatFinder()
        link = '<https://api.github.com/x?page=2>; rel="next", <https://api.github.com/x?page=3>; rel="last"'
        self.assertEqual(finder._next_link(link), "https://api.github.com/x?page=2")
        self.assertIsNone(finder._next_link(None))

    def test_headers_pick_up_runtime_token(self):
        prev_gh = os.environ.get("GH_TOKEN")
        prev_github = os.environ.get("GITHUB_TOKEN")
        try:
            os.environ.pop("GH_TOKEN", None)
            os.environ.pop("GITHUB_TOKEN", None)
            finder = MeatFinder()
            self.assertNotIn("Authorization", finder._github_headers())

            os.environ["GH_TOKEN"] = "abc123"
            self.assertEqual(
                finder._github_headers().get("Authorization"),
                "Bearer abc123",
            )
        finally:
            if prev_gh is None:
                os.environ.pop("GH_TOKEN", None)
            else:
                os.environ["GH_TOKEN"] = prev_gh
            if prev_github is None:
                os.environ.pop("GITHUB_TOKEN", None)
            else:
                os.environ["GITHUB_TOKEN"] = prev_github

    def test_extract_rtc_reward_and_report_ordering(self):
        finder = MeatFinder()
        self.assertEqual(finder._extract_rtc_reward("Bounty 75 RTC"), 75)
        self.assertEqual(finder._extract_rtc_reward("Mixed 20 rtc and 150 RTC"), 150)
        self.assertEqual(finder._extract_rtc_reward("No reward listed"), 0)

        finder.found_tasks = [
            {"platform": "GitHub", "id": "r#2", "title": "lower", "url": "u2", "reward_rtc": 25},
            {"platform": "GitHub", "id": "r#1", "title": "higher", "url": "u1", "reward_rtc": 100},
        ]
        report = finder.report()
        self.assertLess(report.find("higher"), report.find("lower"))
        self.assertIn("~100 RTC", report)

    def test_scan_skips_prs_and_follows_pagination(self):
        calls = []

        page1 = [
            {
                "number": 1,
                "title": "Automation helper",
                "body": "bot script",
                "html_url": "https://github.com/a/1",
                "labels": [{"name": "bounty"}],
            },
            {
                "number": 2,
                "title": "PR disguised",
                "body": "should skip",
                "html_url": "https://github.com/a/2",
                "labels": [{"name": "bounty"}],
                "pull_request": {"url": "https://api.github.com/..."},
            },
        ]
        page2 = [
            {
                "number": 3,
                "title": "Data crawler",
                "body": "automation",
                "html_url": "https://github.com/a/3",
                "labels": [{"name": "bounty"}],
            },
            {
                "number": 1,
                "title": "Automation helper",
                "body": "bot script",
                "html_url": "https://github.com/a/1",
                "labels": [{"name": "bounty"}],
            },
        ]

        def fake_get(url, headers=None, timeout=15):
            calls.append((url, headers))
            if "page=2" in url:
                return FakeResp(200, page2, headers={})
            return FakeResp(
                200,
                page1,
                headers={"Link": '<https://api.github.com/repos/Scottcjn/Rustchain/issues?state=open&labels=bounty&per_page=100&page=2>; rel="next"'},
            )

        original_get = meat_finder.requests.get
        meat_finder.requests.get = fake_get  # type: ignore[assignment]
        try:
            finder = MeatFinder()
            finder.scan_github_elyan()
        finally:
            meat_finder.requests.get = original_get  # type: ignore[assignment]

        self.assertGreaterEqual(len(finder.found_tasks), 2)
        ids = [task["id"] for task in finder.found_tasks]
        self.assertEqual(len(ids), len(set(ids)))  # duplicate issue IDs are de-duplicated
        self.assertTrue(any("#1" in i for i in ids))
        self.assertFalse(any("#2" in i for i in ids))
        # Ensure auth/user-agent headers are passed through requests
        self.assertIn("User-Agent", calls[0][1])


if __name__ == "__main__":
    unittest.main()
