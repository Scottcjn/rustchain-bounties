# SPDX-License-Identifier: MIT
"""A sweep that cannot complete must render no verdict about anyone.

`paginate_all()` used to `break` on any non-200 and return the PARTIAL list
with the same type and shape as a complete one. `Rustchain` alone is ~6,800
stars (~69 pages at per_page=100), so a single 403 on page 3 returned ~300
logins as if that were everybody — and the bot then posted PUBLICLY, on the
claimants' own issues, that real contributors had not starred. Failure and
success were indistinguishable to every caller.

These tests pin: failures propagate, partial data never reaches a report, and
an inconclusive per-user check reports "not checked" rather than an accusation.
"""
import importlib.util
import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


def load_verify_bounties():
    os.environ.setdefault("GITHUB_TOKEN", "dummy-token-for-tests")
    requests_stub = types.SimpleNamespace(
        Session=lambda: types.SimpleNamespace(headers={}, get=None, post=None, patch=None)
    )
    sys.modules.setdefault("requests", requests_stub)
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "verify_bounties.py"
    spec = importlib.util.spec_from_file_location("verify_bounties_sweep", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, status_code, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload if payload is not None else []
        self.text = text
        self.headers = {"X-RateLimit-Remaining": "5000"}

    def json(self):
        return self._payload


def install_pages(mod, pages):
    """Make gh_get walk `pages` (a list of FakeResponse) in order."""
    calls = {"n": 0}

    def fake_get(url, params=None, session=None, **kwargs):
        i = calls["n"]
        calls["n"] += 1
        return pages[i] if i < len(pages) else FakeResponse(200, [])

    mod.gh_get = fake_get
    return calls


def full_page(prefix, n=100):
    return [{"login": f"{prefix}{i}"} for i in range(n)]


class PaginateAllPropagatesFailure(unittest.TestCase):
    def test_mid_sweep_403_raises_instead_of_returning_partial(self):
        mod = load_verify_bounties()
        install_pages(mod, [
            FakeResponse(200, full_page("p1_")),
            FakeResponse(200, full_page("p2_")),
            FakeResponse(403, text="secondary rate limit"),
        ])

        with self.assertRaises(mod.IncompleteSweep):
            mod.paginate_all("https://api.github.com/repos/Scottcjn/Rustchain/stargazers")

    def test_404_also_raises(self):
        """A renamed/moved repo must not silently become 'nobody starred it'."""
        mod = load_verify_bounties()
        install_pages(mod, [FakeResponse(404, text="Not Found")])

        with self.assertRaises(mod.IncompleteSweep):
            mod.paginate_all("https://api.github.com/repos/Scottcjn/Rustchain/stargazers")

    def test_complete_sweep_still_returns_everything(self):
        mod = load_verify_bounties()
        install_pages(mod, [
            FakeResponse(200, full_page("p1_")),
            FakeResponse(200, full_page("p2_", n=7)),   # short page ends the sweep
        ])

        got = mod.paginate_all("https://api.github.com/x")
        self.assertEqual(len(got), 107)


class NoStarForkWatchOrFollowRewards(unittest.TestCase):
    """GitHub's Acceptable Use Policies forbid rewarding stars, forks, watches or
    follows (Support, 2026-10-09). The bot must not even be able to verify them."""

    def test_star_and_follow_phases_are_gone(self):
        mod = load_verify_bounties()
        for name in ("STAR_REPOS", "STAR_BOUNTY_ISSUES", "FOLLOW_BOUNTY_ISSUES", "get_stargazers",
                     "get_all_stargazers", "verify_star_claims", "check_follows_owner", "verify_follow_claims"):
            self.assertFalse(hasattr(mod, name), name)

    def test_no_bounty_issue_list_names_a_metric_bounty(self):
        src = (Path(__file__).resolve().parents[1] / "scripts" / "verify_bounties.py").read_text()
        self.assertNotIn("/stargazers", src)
        self.assertNotIn("/following/", src)


class NoVerdictOnIncompleteData(unittest.TestCase):
    def test_badge_report_is_not_posted_when_comments_cannot_be_read(self):
        mod = load_verify_bounties()
        install_pages(mod, [FakeResponse(403, text="secondary rate limit")])

        with patch.object(mod, "post_comment") as post, \
             patch.object(mod, "update_comment") as update:
            with self.assertRaises(mod.IncompleteSweep):
                mod.verify_badge_claims(13949)

        post.assert_not_called()
        update.assert_not_called()

    def test_run_phase_skips_the_issue_and_reports_the_failure(self):
        mod = load_verify_bounties()

        def boom(issue):
            raise mod.IncompleteSweep("page 3 returned HTTP 403")

        with patch.object(mod, "is_issue_open", return_value=True):
            failures = mod.run_phase("Phase X", [1, 2], boom)

        self.assertEqual(len(failures), 2)
        self.assertIn("403", failures[0])


class InconclusiveChecksAreNotAccusations(unittest.TestCase):
    def test_badge_check_distinguishes_missing_from_unreadable(self):
        mod = load_verify_bounties()

        mod.gh_get = lambda url, params=None: FakeResponse(404)
        found, detail = mod.check_profile_badge("alice")
        self.assertIs(found, False)          # authoritative: no README

        mod.gh_get = lambda url, params=None: FakeResponse(403)
        found, detail = mod.check_profile_badge("alice")
        self.assertIsNone(found)             # inconclusive: did not look
        self.assertIn("not checked", detail.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
