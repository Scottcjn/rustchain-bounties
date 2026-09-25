# SPDX-License-Identifier: MIT
"""do_claim() must not announce a claim that was never recorded.

The `claimed` label is the claim: do_sweep() and the "is this taken?" lookup
both go through it. add_label() already returns False on a failed `gh api`
call, but do_claim() ignored that result and posted the 🔒 "Claimed" comment
anyway, so a transient API failure told the claimant they were recorded while
the bounty stayed visibly free to everyone else — and the run stayed green.
"""
import io
import unittest
from contextlib import redirect_stderr

from scripts import bounty_claim as bc


class _Harness(unittest.TestCase):
    def setUp(self):
        self._gh, self._add = bc.gh, bc.add_label
        self.comments, self.label_calls = [], []
        self.issue = {"title": "[BOUNTY: 5 RTC] Do a thing", "state": "OPEN", "labels": []}

        def fake_gh(args, default=None):
            if args[:2] == ["issue", "view"]:
                return self.issue
            if args[:2] == ["issue", "comment"]:
                self.comments.append(args[args.index("--body") + 1])
                return None
            return []  # active_claim: no prior comments
        bc.gh = fake_gh

    def tearDown(self):
        bc.gh, bc.add_label = self._gh, self._add

    def _label_result(self, ok):
        def fake_add(num, name):
            self.label_calls.append((num, name))
            return ok
        bc.add_label = fake_add


class LabelFailureIsLoud(_Harness):
    def test_failed_label_returns_nonzero_and_never_says_claimed(self):
        self._label_result(False)
        err = io.StringIO()
        with redirect_stderr(err):
            rc = bc.do_claim(4242, "alice", "/claim")
        self.assertEqual(rc, 1, "a failed label must make the run red")
        self.assertEqual(self.label_calls, [(4242, bc.LABEL)])
        self.assertEqual(len(self.comments), 1)
        self.assertNotIn(bc.MARKER, self.comments[0], "no claim marker may be posted")
        self.assertNotIn("Claimed", self.comments[0])
        self.assertIn("could not record your claim", self.comments[0])
        self.assertIn("@alice", self.comments[0])
        self.assertIn("::error::", err.getvalue())

    def test_successful_label_still_claims(self):
        self._label_result(True)
        rc = bc.do_claim(4242, "alice", "/claim")
        self.assertEqual(rc, 0)
        self.assertEqual(len(self.comments), 1)
        self.assertIn(bc.MARKER, self.comments[0])
        self.assertIn("Claimed", self.comments[0])


if __name__ == "__main__":
    unittest.main()
