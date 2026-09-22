# SPDX-License-Identifier: MIT
"""A PR number belongs to its named repository, even if the default has it too."""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pr_review_gate.py"
SUMMARY = (
    "Bug in scripts/example.py line 40: the loop returns before handling the "
    "final element. Move the return after the loop to preserve all results."
)


def load_gate():
    spec = importlib.util.spec_from_file_location("gate_repo_collision", SCRIPT)
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    gate.NUM = "42"
    gate.REPO = "Scottcjn/rustchain-bounties"
    gate.TARGET = "Scottcjn/Rustchain"
    return gate


class RepositoryCollisionTests(unittest.TestCase):
    def run_claim(self, title, body="", reviewers=None):
        gate = load_gate()
        calls, labels, comments, updates = [], [], [], []
        if reviewers is None:
            reviewers = {"Scottcjn/Rustchain": "bob", "Scottcjn/bottube": "alice"}

        def api(path, method="GET", data=None, strict=False):
            calls.append((method, path))
            if method == "POST" and path.endswith("/labels"):
                labels.extend(data["labels"])
                return {}
            if method == "POST" and path.endswith("/comments"):
                comments.append(data["body"])
                return {}
            if method == "PATCH":
                updates.append(data)
                return {}
            if path == "/repos/Scottcjn/rustchain-bounties/issues/42":
                return {"state": "open", "labels": [], "title": title,
                        "body": body, "user": {"login": "alice"}}
            if path.startswith("/search/issues"):
                return {"total_count": 0}
            for repo, reviewer in reviewers.items():
                if path == f"/repos/{repo}/pulls/123/reviews":
                    if reviewer is None:
                        return None
                    return [{"id": 1, "user": {"login": reviewer},
                             "submitted_at": "2026-09-01T12:00:00Z", "body": SUMMARY}]
                if path == f"/repos/{repo}/pulls/123/comments?per_page=100":
                    return []
            raise AssertionError(f"Unexpected API call: {method} {path}")

        with patch.object(gate, "api", side_effect=api):
            gate.main()
        return calls, labels, comments, updates

    def test_body_reference_keeps_its_own_repository_and_number(self):
        gate = load_gate()
        self.assertEqual(
            gate.pr_ref("Bounty #73 code review: PR #99", "Reviewed bottube PR #123"),
            ("Scottcjn/bottube", "123"))

    def test_owner_qualified_single_digit_reference(self):
        gate = load_gate()
        self.assertEqual(
            gate.pr_ref("Bounty #73 code review: Scottcjn/rustchain-dialup#4", ""),
            ("Scottcjn/rustchain-dialup", "4"))

    def test_named_repo_wins_when_default_has_same_pr_number(self):
        for title in ["Bounty #73 code review: bottube PR #123",
                      "Bounty #73 code review: Scottcjn/bottube PR #123",
                      "Bounty #73 code review: Scottcjn/bottube#123"]:
            with self.subTest(title=title):
                calls, labels, comments, updates = self.run_claim(title)
                self.assertIn("bounty-eligible", labels)
                self.assertEqual(updates, [])
                self.assertTrue(any("Scottcjn/bottube#123" in c for c in comments))
                self.assertFalse(any("/Rustchain/pulls/" in p for _, p in calls))

    def test_wrong_repo_reviewer_cannot_make_claim_eligible(self):
        calls, labels, comments, updates = self.run_claim(
            "Bounty #73 code review: bottube PR #123",
            reviewers={"Scottcjn/Rustchain": "alice", "Scottcjn/bottube": "bob"})
        self.assertNotIn("bounty-eligible", labels)
        self.assertEqual(updates, [{"state": "closed", "state_reason": "not_planned"}])
        self.assertTrue(any("Scottcjn/bottube#123" in c for c in comments))

    def test_named_repo_lookup_failure_is_held_not_redirected(self):
        calls, labels, comments, updates = self.run_claim(
            "Bounty #73 code review: bottube PR #123",
            reviewers={"Scottcjn/Rustchain": "alice", "Scottcjn/bottube": None})
        self.assertIn("needs-human", labels)
        self.assertNotIn("bounty-eligible", labels)
        self.assertEqual(updates, [])
        self.assertFalse(any("/Rustchain/pulls/" in p for _, p in calls))

    def test_explicit_url_keeps_precedence_over_prose(self):
        calls, labels, _, updates = self.run_claim(
            "Bounty #73 code review: bottube PR #123",
            "https://github.com/Scottcjn/Rustchain/pull/123",
            reviewers={"Scottcjn/Rustchain": "alice", "Scottcjn/bottube": "bob"})
        self.assertIn("bounty-eligible", labels)
        self.assertEqual(updates, [])
        self.assertFalse(any("/bottube/pulls/" in p for _, p in calls))

    def test_external_owner_in_prose_is_held_for_human(self):
        calls, labels, _, updates = self.run_claim(
            "Bounty #73 code review: other-owner/bottube PR #123")
        self.assertIn("needs-human", labels)
        self.assertNotIn("bounty-eligible", labels)
        self.assertEqual(updates, [])
        self.assertFalse(any("/pulls/" in p for _, p in calls))

    def test_bare_pr_number_still_uses_default_repo(self):
        calls, labels, _, updates = self.run_claim(
            "Bounty #73 code review: PR #123",
            reviewers={"Scottcjn/Rustchain": "alice"})
        self.assertIn("bounty-eligible", labels)
        self.assertEqual(updates, [])
        self.assertIn(("GET", "/repos/Scottcjn/Rustchain/pulls/123/reviews"), calls)


if __name__ == "__main__":
    unittest.main()
