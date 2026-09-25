#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Tests for scripts/bounty_claim.py.

Two things carry the weight:

  - `is_claim_request` must not fire on someone QUOTING the instructions. A
    false positive silently marks a bounty as taken and turns this feature into
    the very problem it exists to prevent.
  - `active_claim` must treat an expired claim as absent, or a bounty stays
    reserved forever by whoever touched it first.

And since 2026-09-25, the lock may only be granted on maintainer-posted
`bounty` issues, to accounts >= CLAIM_MIN_ACCOUNT_AGE_DAYS old holding fewer
than CLAIM_MAX_ACTIVE claims, and every lookup failure must REFUSE.
"""
import datetime
import importlib.util
import os
import unittest
from pathlib import Path

os.environ.setdefault("GITHUB_TOKEN", "dummy")
SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "bounty_claim.py"
spec = importlib.util.spec_from_file_location("bounty_claim_under_test", SCRIPT)
bc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bc)

TODAY = datetime.date.today()


class ClaimDetectionTests(unittest.TestCase):
    def test_slash_claim(self):
        self.assertTrue(bc.is_claim_request("/claim"))
        self.assertTrue(bc.is_claim_request("Sounds good, /claim"))

    def test_natural_phrasings(self):
        for s in ["claiming this", "I'm taking this", "taking this one",
                  "I will take this", "Im taking this"]:
            self.assertTrue(bc.is_claim_request(s), s)

    def test_quoted_instructions_do_not_claim(self):
        """Someone quoting the how-to must not accidentally claim the bounty."""
        body = "> Anyone can take it now by commenting `/claim`.\n\nHow long do claims last?"
        self.assertFalse(bc.is_claim_request(body))

    def test_ordinary_comment_does_not_claim(self):
        for s in ["This looks interesting", "What is the reward here?",
                  "I disclaimed any warranty", "", None]:
            self.assertFalse(bc.is_claim_request(s), repr(s))

    def test_disclaim_is_not_a_claim(self):
        """Word-boundary check: 'disclaim' must not match '/claim'."""
        self.assertFalse(bc.is_claim_request("I disclaim all responsibility"))


class ActiveClaimTests(unittest.TestCase):
    def setUp(self):
        self._gh = bc.gh

    def tearDown(self):
        bc.gh = self._gh

    def _comments(self, *bodies):
        bc.gh = lambda a, d=None: [{"body": b} for b in bodies]

    def _claim(self, who, days):
        d = (TODAY + datetime.timedelta(days=days)).isoformat()
        return f"{bc.MARKER}\n🔒 **Claimed.** holder: @{who} · expires: {d}"

    def test_unexpired_claim_is_active(self):
        self._comments(self._claim("alice", 3))
        got = bc.active_claim(1)
        self.assertIsNotNone(got)
        self.assertEqual(got[0], "alice")

    def test_expired_claim_is_not_active(self):
        """Otherwise a bounty stays reserved forever."""
        self._comments(self._claim("alice", -1))
        self.assertIsNone(bc.active_claim(1))

    def test_expiring_today_still_counts(self):
        self._comments(self._claim("alice", 0))
        self.assertIsNotNone(bc.active_claim(1))

    def test_newest_claim_wins(self):
        self._comments(self._claim("alice", 1), self._claim("bob", 5))
        self.assertEqual(bc.active_claim(1)[0], "bob")

    def test_renewal_supersedes_expired(self):
        self._comments(self._claim("alice", -3), self._claim("alice", 4))
        got = bc.active_claim(1)
        self.assertIsNotNone(got)
        self.assertEqual(got[0], "alice")

    def test_no_marker_means_no_claim(self):
        self._comments("just a normal comment", "another one")
        self.assertIsNone(bc.active_claim(1))

    def test_no_comments_at_all(self):
        bc.gh = lambda a, d=None: []
        self.assertIsNone(bc.active_claim(1))

    def test_paginated_comments_finds_claim_on_later_pages(self):
        """Claims past the 100-comment first page must not be dropped by active_claim."""
        page1 = [{"body": f"comment {i}"} for i in range(100)]
        page2 = [{"body": self._claim("charlie", 4)}]
        calls = []

        def mock_gh(args, default=None):
            calls.append(args)
            if args[1].endswith("&page=1"):
                return page1
            elif args[1].endswith("&page=2"):
                return page2
            return []

        bc.gh = mock_gh
        got = bc.active_claim(1)
        self.assertIsNotNone(got)
        self.assertEqual(got[0], "charlie")
        self.assertGreaterEqual(len(calls), 2)


OLD_ACCOUNT = "2019-01-01T00:00:00Z"


def _days_ago(n):
    ts = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=n)
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def _marker(who, days):
    d = (TODAY + datetime.timedelta(days=days)).isoformat()
    return f"{bc.MARKER}\n🔒 **Claimed.** holder: @{who} · expires: {d}"


class FakeGitHub:
    """In-memory stand-in for the three gh entry points the bot uses.

    - issues[num]: REST issue payload (fetch_issue)
    - comments[num]: list of comment bodies (active_claim; bot comments append)
    - users[login]: created_at string; missing login = lookup failure
    - search_fails: make the `claimed` label search fail
    """

    def __init__(self):
        self.issues, self.comments, self.users = {}, {}, {}
        self.search_fails = False
        self.added, self.removed = [], []

    def issue(self, num, title="[BOUNTY: 10 RTC] Do a thing", author="Scottcjn",
              assoc="OWNER", labels=("bounty",), state="open"):
        self.issues[num] = {"number": num, "title": title, "state": state,
                            "user": {"login": author}, "author_association": assoc,
                            "labels": [{"name": n} for n in labels]}
        self.comments.setdefault(num, [])

    def posted(self, num):
        return self.comments.get(num, [])

    # --- gh() : comments listing + posting
    def gh(self, args, default=None):
        if args[:2] == ["issue", "comment"]:
            self.comments.setdefault(int(args[2]), []).append(args[args.index("--body") + 1])
            return None
        if args[0] == "api" and "/comments?" in args[1]:
            num = int(args[1].split("/issues/")[1].split("/")[0])
            page = int(args[1].rsplit("page=", 1)[1])
            return [{"body": b} for b in self.comments.get(num, [])] if page == 1 else []
        return default

    # --- gh_strict() : issue, user, search
    def gh_strict(self, args):
        path = args[1] if args[1] != "-X" else args[3]
        if path.startswith(f"/repos/{bc.REPO}/issues/"):
            return self.issues.get(int(path.rsplit("/", 1)[1]))
        if path.startswith("users/"):
            created = self.users.get(path.split("/", 1)[1])
            return {"created_at": created} if created else None
        if path == "search/issues":
            if self.search_fails:
                return None
            items = [{"number": n} for n, i in self.issues.items()
                     if i["state"] == "open" and any(lb["name"] == bc.LABEL for lb in i["labels"])]
            return {"items": items}
        return None

    def add_label(self, num, name):
        self.added.append((int(num), name))
        lab = self.issues.get(int(num))
        if lab is not None:
            lab["labels"].append({"name": name})
        return True

    def remove_label(self, num, name):
        self.removed.append((int(num), name))
        lab = self.issues.get(int(num))
        if lab is not None:
            lab["labels"] = [lb for lb in lab["labels"] if lb["name"] != name]
        return True


class _BotCase(unittest.TestCase):
    def setUp(self):
        self._saved = (bc.gh, bc.gh_strict, bc.add_label, bc.remove_label)
        self.f = FakeGitHub()
        bc.gh, bc.gh_strict = self.f.gh, self.f.gh_strict
        bc.add_label, bc.remove_label = self.f.add_label, self.f.remove_label
        self.f.users["alice"] = OLD_ACCOUNT
        self.f.users["bob"] = OLD_ACCOUNT

    def tearDown(self):
        bc.gh, bc.gh_strict, bc.add_label, bc.remove_label = self._saved

    def assertLocked(self, num, who="alice"):
        self.assertIn((num, bc.LABEL), self.f.added)
        held = bc.active_claim(num)
        self.assertIsNotNone(held)
        self.assertEqual(held[0], who)

    def assertNotLocked(self, num):
        self.assertNotIn((num, bc.LABEL), self.f.added)
        self.assertIsNone(bc.active_claim(num))


class LiveUrlGateTests(_BotCase):
    """On `distribution` issues a claim without an allowlisted Live-URL must
    NOT lock the bounty — it gets an explanation instead. Everywhere else the
    gate is inert."""

    def test_distribution_without_live_url_is_explained_not_locked(self):
        self.f.issue(2798, labels=("bounty", "distribution"))
        bc.do_claim(2798, "alice", "/claim")
        self.assertNotLocked(2798)
        self.assertEqual(len(self.f.posted(2798)), 1)
        self.assertIn("Live-URL", self.f.posted(2798)[0])
        self.assertNotIn(bc.MARKER, self.f.posted(2798)[0])

    def test_distribution_with_off_list_url_is_explained_not_locked(self):
        self.f.issue(2798, labels=("bounty", "distribution"))
        bc.do_claim(2798, "alice", "/claim\nLive-URL: https://gist.github.com/alice/x")
        self.assertNotLocked(2798)
        self.assertIn("gist.github.com", self.f.posted(2798)[0])
        self.assertNotIn(bc.MARKER, self.f.posted(2798)[0])

    def test_distribution_with_live_url_locks(self):
        self.f.issue(2798, labels=("bounty", "distribution", "standard"))
        bc.do_claim(2798, "alice", "/claim\nLive-URL: https://x.com/alice/status/123")
        self.assertLocked(2798)
        self.assertIn(bc.MARKER, self.f.posted(2798)[0])

    def test_non_distribution_issue_unchanged(self):
        self.f.issue(16250, labels=("bounty", "standard"))
        bc.do_claim(16250, "alice", "/claim")
        self.assertLocked(16250)
        self.assertIn(bc.MARKER, self.f.posted(16250)[0])

    def test_gate_helper_direct(self):
        self.assertTrue(bc.live_url_gate(1, "a", "/claim", {"standard"}))
        self.assertFalse(bc.live_url_gate(1, "a", "/claim", {"distribution"}))
        self.assertTrue(bc.live_url_gate(1, "a", "Live-URL: https://youtu.be/dQw4w9WgXcQ",
                                         {"distribution"}))


class LockableIssueTests(_BotCase):
    """Only maintainer-authored issues carrying the `bounty` label can be locked."""

    def test_maintainer_bounty_locks(self):
        self.f.issue(10)
        bc.do_claim(10, "alice", "/claim")
        self.assertLocked(10)

    def test_collaborator_and_member_authors_are_maintainers(self):
        for n, assoc in ((11, "COLLABORATOR"), (12, "MEMBER")):
            self.f.issue(n, author="someone", assoc=assoc)
            bc.do_claim(n, "alice", "/claim")
            self.assertLocked(n)
            bc.do_unclaim(n, "Scottcjn", "OWNER")  # keep alice under the cap

    def test_allowlisted_login_counts_even_if_association_is_none(self):
        self.f.issue(13, author="Scottcjn", assoc="NONE")
        bc.do_claim(13, "alice", "/claim")
        self.assertLocked(13)

    def test_contributor_issue_titled_bounty_is_not_lockable(self):
        """The old check: 'bounty' in the title was enough. Not any more."""
        self.f.issue(20, title="Claim: [BOUNTY #123] my submission",
                     author="contrib", assoc="NONE", labels=("bounty",))
        bc.do_claim(20, "alice", "/claim")
        self.assertNotLocked(20)
        reply = self.f.posted(20)[0]
        self.assertIn("only for bounty issues posted by the maintainers", reply)
        self.assertNotIn(bc.MARKER, reply)

    def test_contributor_issue_with_bounty_label_is_not_lockable(self):
        self.f.issue(21, title="[BOUNTY] something", author="contrib",
                     assoc="CONTRIBUTOR", labels=("bounty",))
        bc.do_claim(21, "alice", "/claim")
        self.assertNotLocked(21)

    def test_claim_prefixed_title_never_lockable_even_by_maintainer(self):
        self.f.issue(22, title="  claim: [BOUNTY] tracker", author="Scottcjn",
                     assoc="OWNER", labels=("bounty",))
        bc.do_claim(22, "alice", "/claim")
        self.assertNotLocked(22)
        self.assertIn("tracks a submission", self.f.posted(22)[0])

    def test_maintainer_issue_without_bounty_label_is_not_lockable(self):
        self.f.issue(23, title="[BOUNTY: 35 RTC] security", labels=("security",))
        bc.do_claim(23, "alice", "/claim")
        self.assertNotLocked(23)

    def test_natural_phrasing_on_non_bounty_is_silent(self):
        """'taking this one' on an ordinary issue is conversation, not a claim."""
        self.f.issue(24, title="Some bug", labels=("bug",))
        bc.do_claim(24, "alice", "I'm taking this one")
        self.assertNotLocked(24)
        self.assertEqual(self.f.posted(24), [])

    def test_closed_issue_ignored(self):
        self.f.issue(25, state="closed")
        bc.do_claim(25, "alice", "/claim")
        self.assertNotLocked(25)
        self.assertEqual(self.f.posted(25), [])

    def test_issue_lookup_failure_refuses(self):
        self.f.comments[26] = []
        bc.do_claim(26, "alice", "/claim")  # no issue in fake -> lookup fails
        self.assertNotLocked(26)
        self.assertIn("could not verify", self.f.posted(26)[0])


class AccountAgeTests(_BotCase):
    def test_new_account_refused_kindly(self):
        self.f.users["newbie"] = _days_ago(2)
        self.f.issue(30)
        bc.do_claim(30, "newbie", "/claim")
        self.assertNotLocked(30)
        reply = self.f.posted(30)[0]
        self.assertIn("submit your work directly without claiming", reply)
        self.assertIn(str(bc.CLAIM_MIN_ACCOUNT_AGE_DAYS), reply)

    def test_account_exactly_at_threshold_allowed(self):
        self.f.users["edge"] = _days_ago(bc.CLAIM_MIN_ACCOUNT_AGE_DAYS)
        self.f.issue(31)
        bc.do_claim(31, "edge", "/claim")
        self.assertLocked(31, "edge")

    def test_account_one_day_short_refused(self):
        self.f.users["edge"] = _days_ago(bc.CLAIM_MIN_ACCOUNT_AGE_DAYS - 1)
        self.f.issue(32)
        bc.do_claim(32, "edge", "/claim")
        self.assertNotLocked(32)

    def test_user_lookup_failure_refuses_neutrally(self):
        self.f.issue(33)
        bc.do_claim(33, "ghost", "/claim")  # not in users -> lookup fails
        self.assertNotLocked(33)
        self.assertIn("could not verify", self.f.posted(33)[0])

    def test_threshold_is_configurable(self):
        saved = bc.CLAIM_MIN_ACCOUNT_AGE_DAYS
        try:
            bc.CLAIM_MIN_ACCOUNT_AGE_DAYS = 1
            self.f.users["newbie"] = _days_ago(2)
            self.f.issue(34)
            bc.do_claim(34, "newbie", "/claim")
            self.assertLocked(34, "newbie")
        finally:
            bc.CLAIM_MIN_ACCOUNT_AGE_DAYS = saved

    def test_account_age_days_parses_github_timestamp(self):
        self.f.users["x"] = _days_ago(40)
        self.assertEqual(bc.account_age_days("x"), 40)
        self.assertIsNone(bc.account_age_days("nobody"))
        self.assertIsNone(bc.account_age_days(""))


class ConcurrencyCapTests(_BotCase):
    def _hold(self, num, who):
        self.f.issue(num, labels=("bounty", bc.LABEL))
        self.f.comments[num] = [_marker(who, 3)]

    def test_third_claim_refused(self):
        self._hold(40, "alice")
        self._hold(41, "alice")
        self.f.issue(42)
        bc.do_claim(42, "alice", "/claim")
        self.assertNotLocked(42)
        self.assertIn(f"at most {bc.CLAIM_MAX_ACTIVE}", self.f.posted(42)[0])

    def test_second_claim_allowed(self):
        self._hold(40, "alice")
        self.f.issue(42)
        bc.do_claim(42, "alice", "/claim")
        self.assertLocked(42)

    def test_other_peoples_claims_do_not_count(self):
        self._hold(40, "bob")
        self._hold(41, "bob")
        self.f.issue(42)
        bc.do_claim(42, "alice", "/claim")
        self.assertLocked(42)

    def test_expired_claims_do_not_count(self):
        for n in (40, 41):
            self.f.issue(n, labels=("bounty", bc.LABEL))
            self.f.comments[n] = [_marker("alice", -2)]
        self.f.issue(42)
        bc.do_claim(42, "alice", "/claim")
        self.assertLocked(42)

    def test_holder_can_renew_while_at_cap(self):
        self._hold(40, "alice")
        self._hold(41, "alice")
        bc.do_claim(41, "alice", "/claim")
        self.assertIn("(renewed)", self.f.posted(41)[-1])
        self.assertEqual(bc.active_claim(41)[0], "alice")

    def test_search_failure_refuses(self):
        self.f.search_fails = True
        self.f.issue(42)
        bc.do_claim(42, "alice", "/claim")
        self.assertNotLocked(42)
        self.assertIn("could not verify", self.f.posted(42)[0])

    def test_already_claimed_by_someone_else_unchanged(self):
        self._hold(43, "bob")
        bc.do_claim(43, "alice", "/claim")
        self.assertIn("already claimed by **@bob**", self.f.posted(43)[-1])
        self.assertEqual(bc.active_claim(43)[0], "bob")


class UnclaimTests(_BotCase):
    def _held(self, num=50, who="alice"):
        self.f.issue(num, labels=("bounty", bc.LABEL))
        self.f.comments[num] = [_marker(who, 5)]
        return num

    def test_detection(self):
        self.assertTrue(bc.is_unclaim_request("/unclaim"))
        self.assertTrue(bc.is_unclaim_request("stale, /release please"))
        self.assertFalse(bc.is_unclaim_request("> comment `/unclaim` to release"))
        self.assertFalse(bc.is_unclaim_request("/claim"))
        self.assertFalse(bc.is_claim_request("/unclaim"))
        self.assertFalse(bc.is_unclaim_request(None))

    def test_maintainer_release(self):
        n = self._held()
        bc.do_unclaim(n, "Scottcjn", "OWNER")
        self.assertIsNone(bc.active_claim(n))
        self.assertIn((n, bc.LABEL), self.f.removed)
        self.assertIn(bc.MARKER, self.f.posted(n)[-1])

    def test_collaborator_release_by_association(self):
        n = self._held()
        bc.do_unclaim(n, "helper", "COLLABORATOR")
        self.assertIsNone(bc.active_claim(n))

    def test_released_bounty_can_be_claimed_again(self):
        n = self._held()
        bc.do_unclaim(n, "Scottcjn", "OWNER")
        bc.do_claim(n, "bob", "/claim")
        self.assertEqual(bc.active_claim(n)[0], "bob")

    def test_release_frees_a_cap_slot(self):
        self._held(51, "alice")
        self._held(52, "alice")
        bc.do_unclaim(52, "Scottcjn", "OWNER")
        self.f.issue(53)
        bc.do_claim(53, "alice", "/claim")
        self.assertEqual(bc.active_claim(53)[0], "alice")

    def test_holder_can_release_own_claim(self):
        n = self._held()
        bc.do_unclaim(n, "alice", "NONE")
        self.assertIsNone(bc.active_claim(n))

    def test_non_maintainer_cannot_release(self):
        n = self._held()
        bc.do_unclaim(n, "mallory", "NONE")
        self.assertEqual(bc.active_claim(n)[0], "alice")
        self.assertEqual(self.f.removed, [])
        self.assertIn("only a maintainer", self.f.posted(n)[-1])

    def test_nothing_to_release_is_quiet(self):
        self.f.issue(54)
        bc.do_unclaim(54, "Scottcjn", "OWNER")
        self.assertEqual(self.f.posted(54), [])
        self.assertEqual(self.f.removed, [])

    def test_main_routes_unclaim(self):
        n = self._held()
        env = {"ISSUE_NUMBER": str(n), "COMMENT_BODY": "/unclaim",
               "COMMENT_AUTHOR": "maint", "COMMENT_AUTHOR_ASSOCIATION": "MEMBER",
               "MODE": "claim"}
        saved = {k: os.environ.get(k) for k in env}
        os.environ.update(env)
        try:
            self.assertEqual(bc.main(), 0)
        finally:
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        self.assertIsNone(bc.active_claim(n))


class GhStrictTests(unittest.TestCase):
    """gh_strict must turn a non-zero exit into None, even when gh printed an
    error body to stdout (which gh() would have parsed as data)."""

    def setUp(self):
        self._run = bc.subprocess.run

    def tearDown(self):
        bc.subprocess.run = self._run

    def _fake(self, rc, out):
        class P:
            returncode, stdout, stderr = rc, out, "boom"
        bc.subprocess.run = lambda *a, **k: P()

    def test_error_body_with_nonzero_exit_is_none(self):
        self._fake(1, '{"message": "Not Found"}')
        self.assertIsNone(bc.gh_strict(["api", "users/x"]))

    def test_success_parses(self):
        self._fake(0, '{"created_at": "2020-01-01T00:00:00Z"}')
        self.assertEqual(bc.gh_strict(["api", "users/x"])["created_at"], "2020-01-01T00:00:00Z")

    def test_bad_json_is_none(self):
        self._fake(0, "not json")
        self.assertIsNone(bc.gh_strict(["api", "users/x"]))


if __name__ == "__main__":
    unittest.main()
