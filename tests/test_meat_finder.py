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
        prev_max = os.environ.get("MEAT_MAX_RESULTS")
        prev_min = os.environ.get("MEAT_MIN_RTC")
        try:
            finder = MeatFinder()
            self.assertEqual(finder._extract_rtc_reward("Bounty 75 RTC"), 75)
            self.assertEqual(finder._extract_rtc_reward("Mixed 20 rtc and 150 RTC"), 150)
            self.assertEqual(finder._extract_rtc_reward("Payout up to 1,200 RTC"), 1200)
            self.assertEqual(finder._extract_rtc_reward("Payout up to 1，200 RTC"), 1200)
            self.assertEqual(finder._extract_rtc_reward("Top reward 1.5k RTC"), 1500)
            self.assertEqual(finder._extract_rtc_reward("Top reward 1.2M RTC"), 1200000)
            self.assertEqual(finder._extract_rtc_reward("Top reward 3w RTC"), 30000)
            self.assertEqual(finder._extract_rtc_reward("Top reward 2万 RTC"), 20000)
            self.assertEqual(finder._extract_rtc_reward("Reward: RTC 500"), 500)
            self.assertEqual(finder._extract_rtc_reward("Reward: RTC: 500"), 500)
            self.assertEqual(finder._extract_rtc_reward("Reward RTC-2k"), 2000)
            self.assertEqual(finder._extract_rtc_reward("Bonus RTC 2k available"), 2000)
            self.assertEqual(finder._extract_rtc_reward("Approx ~500 RTC"), 500)
            self.assertEqual(finder._extract_rtc_reward("Reward 500+ RTC"), 500)
            self.assertEqual(finder._extract_rtc_reward("Reward RTC~2k"), 2000)
            self.assertEqual(finder._extract_rtc_reward("No reward listed"), 0)

            finder.found_tasks = [
                {"platform": "GitHub", "id": "r#3", "title": "zero", "url": "u3", "reward_rtc": 0},
                {"platform": "GitHub", "id": "r#2", "title": "lower", "url": "u2", "reward_rtc": 25},
                {"platform": "GitHub", "id": "r#1", "title": "higher", "url": "u1", "reward_rtc": 100},
            ]
            report = finder.report()
            self.assertLess(report.find("higher"), report.find("lower"))
            self.assertIn("~100 RTC", report)

            os.environ["MEAT_MAX_RESULTS"] = "1"
            limited_report = finder.report()
            self.assertIn("higher", limited_report)
            self.assertNotIn("lower", limited_report)
            self.assertIn("and 2 more matches", limited_report)

            os.environ["MEAT_MIN_RTC"] = "50"
            filtered_report = finder.report()
            self.assertIn("higher", filtered_report)
            self.assertNotIn("lower", filtered_report)
            self.assertNotIn("zero", filtered_report)

            os.environ["MEAT_MIN_RTC"] = "999"
            empty_report = finder.report()
            self.assertEqual(empty_report, "No new 'meat' found in this cycle.")
        finally:
            if prev_max is None:
                os.environ.pop("MEAT_MAX_RESULTS", None)
            else:
                os.environ["MEAT_MAX_RESULTS"] = prev_max
            if prev_min is None:
                os.environ.pop("MEAT_MIN_RTC", None)
            else:
                os.environ["MEAT_MIN_RTC"] = prev_min

    def test_github_repos_env_override(self):
        prev = os.environ.get("MEAT_GITHUB_REPOS")
        try:
            finder = MeatFinder()
            os.environ.pop("MEAT_GITHUB_REPOS", None)
            self.assertEqual(
                finder._github_repos(),
                ["Scottcjn/Rustchain", "Scottcjn/bottube", "Scottcjn/rustchain-bounties"],
            )

            os.environ["MEAT_GITHUB_REPOS"] = "owner/a, owner/b ,,invalid"
            self.assertEqual(finder._github_repos(), ["owner/a", "owner/b"])

            os.environ["MEAT_GITHUB_REPOS"] = "invalid-only"
            self.assertEqual(
                finder._github_repos(),
                ["Scottcjn/Rustchain", "Scottcjn/bottube", "Scottcjn/rustchain-bounties"],
            )
        finally:
            if prev is None:
                os.environ.pop("MEAT_GITHUB_REPOS", None)
            else:
                os.environ["MEAT_GITHUB_REPOS"] = prev

    def test_keywords_env_override(self):
        prev = os.environ.get("MEAT_KEYWORDS")
        try:
            finder = MeatFinder()
            os.environ.pop("MEAT_KEYWORDS", None)
            self.assertIn("automation", finder._keywords())

            os.environ["MEAT_KEYWORDS"] = "agent, parser  ,"
            self.assertEqual(finder._keywords(), ["agent", "parser"])

            os.environ["MEAT_KEYWORDS"] = "   ,  "
            self.assertIn("python", finder._keywords())
        finally:
            if prev is None:
                os.environ.pop("MEAT_KEYWORDS", None)
            else:
                os.environ["MEAT_KEYWORDS"] = prev

    def test_keyword_matcher_word_boundary_for_short_tokens(self):
        finder = MeatFinder()
        self.assertTrue(finder._text_matches_keywords("Need a bot for moderation", ["bot"]))
        self.assertFalse(finder._text_matches_keywords("bottube analytics task", ["bot"]))
        self.assertTrue(finder._text_matches_keywords("Python automation helper", ["python"]))

    def test_scan_skips_false_positive_short_keyword_substrings(self):
        page = [
            {
                "number": 7,
                "title": "Improve bottube onboarding",
                "body": "no scripting required",
                "html_url": "https://github.com/a/7",
                "labels": [{"name": "bounty"}],
            }
        ]

        def fake_get(_url, headers=None, timeout=15):
            return FakeResp(200, page, headers={})

        original_get = meat_finder.requests.get
        meat_finder.requests.get = fake_get  # type: ignore[assignment]
        prev_keywords = os.environ.get("MEAT_KEYWORDS")
        try:
            os.environ["MEAT_KEYWORDS"] = "bot"
            finder = MeatFinder()
            finder.scan_github_elyan()
        finally:
            meat_finder.requests.get = original_get  # type: ignore[assignment]
            if prev_keywords is None:
                os.environ.pop("MEAT_KEYWORDS", None)
            else:
                os.environ["MEAT_KEYWORDS"] = prev_keywords

        self.assertEqual(len(finder.found_tasks), 0)

    def test_scan_retries_transient_failures(self):
        calls = {"count": 0}

        page = [
            {
                "number": 9,
                "title": "Automation helper",
                "body": "bot script",
                "html_url": "https://github.com/a/9",
                "labels": [{"name": "bounty"}],
            }
        ]

        def fake_get(url, headers=None, timeout=15):
            calls["count"] += 1
            if calls["count"] == 1:
                return FakeResp(502, {"message": "bad gateway"}, headers={})
            return FakeResp(200, page, headers={})

        original_get = meat_finder.requests.get
        original_sleep = meat_finder.time.sleep
        meat_finder.requests.get = fake_get  # type: ignore[assignment]
        meat_finder.time.sleep = lambda *_args, **_kwargs: None  # type: ignore[assignment]
        try:
            finder = MeatFinder()
            finder.scan_github_elyan()
        finally:
            meat_finder.requests.get = original_get  # type: ignore[assignment]
            meat_finder.time.sleep = original_sleep  # type: ignore[assignment]

        self.assertGreaterEqual(calls["count"], 2)
        ids = [task["id"] for task in finder.found_tasks]
        self.assertTrue(any("#9" in i for i in ids))

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
