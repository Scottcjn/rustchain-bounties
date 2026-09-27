#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""The payout must refuse to pay from a pool whose bounty is not OPEN.

Every review claim this script pays is memo'd "Bounty #73", and #73 closed on
2026-06-05 (pool retired 06-14). The docstring bounty was retired (#16907).
Nothing in the script ever checked. The workflow happened to be disabled by
hand on 2026-08-09, so the only thing standing between a re-enable and a
payout from a closed pool was someone remembering.

Contract pinned here:
  - a closed bounty, an unconfigured bounty number, or an unreadable lookup
    -> the claim is REFUSED, no transfer is attempted, the run exits 1
  - an OPEN bounty -> the ordinary payout path runs
  - the check is memoised per pool so one run makes one lookup per pool
"""
import importlib.util
import io
import json
import os
import subprocess
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "bounty_payout.py"
WALLET = "RTC" + "a" * 40

CLAIM = {"number": 501, "title": "Bounty claim: PR review of #9000 (code review)",
         "labels": [{"name": "bounty-eligible"}]}
CLAIM_DETAIL = {"body": f"Wallet: {WALLET}", "comments": [], "author": {"login": "alice"}}


class _Result:
    def __init__(self, stdout="", rc=0):
        self.stdout, self.stderr, self.returncode = stdout, "", rc


def _run_script(review_state, env_extra=None):
    """Exec the script once with `gh` and the RTC node stubbed.

    Returns (exit_code, stdout, transfers, state_lookups).
    """
    transfers, lookups = [], []

    def fake_run(cmd, *a, **kw):
        args = cmd[1:]
        if args[:2] == ["issue", "list"]:
            return _Result(json.dumps([CLAIM]) if "bounty-eligible" in args else "[]")
        if args[:2] == ["issue", "view"] and args[-1] == "state":
            lookups.append(args[2])
            if review_state is None:
                return _Result("", rc=1)  # lookup failed
            if review_state == "garbage":
                return _Result("not json")
            return _Result(json.dumps({"state": review_state}))
        if args[:2] == ["issue", "view"]:
            return _Result(json.dumps(CLAIM_DETAIL))
        if args[:2] in (["issue", "comment"], ["issue", "close"]):
            return _Result("")
        raise AssertionError(f"unexpected gh call: {args}")

    class _Resp:
        """Stand-in for the node: accepts the transfer and reports it pending."""
        def __init__(self, req):
            transfers.append(json.loads(req.data))
        def read(self):
            return json.dumps({"ok": True, "phase": "pending", "confirms_in_hours": 24}).encode()
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False

    env = {"GITHUB_TOKEN": "dummy", "RTC_ADMIN_KEY": "dummy", "RTC_VPS_HOST": "127.0.0.1",
           "GH_REPO": "owner/repo", "RATE_RTC": "3", "MAX_PER_RUN": "40",
           "REVIEW_BOUNTY_ISSUE": "73", "DOCSTRING_BOUNTY_ISSUE": ""}
    env.update(env_extra or {})
    out = io.StringIO()
    spec = importlib.util.spec_from_file_location("bounty_payout_pool_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    rc = 0
    with patch.dict(os.environ, env, clear=False), \
         patch.object(subprocess, "run", side_effect=fake_run), \
         patch("urllib.request.urlopen", side_effect=lambda req, **kw: _Resp(req)), \
         patch("time.sleep", lambda *_: None), \
         redirect_stdout(out):
        try:
            spec.loader.exec_module(mod)
        except SystemExit as e:
            rc = int(e.code or 0)
    return rc, out.getvalue(), transfers, lookups


class PoolClosedFailsClosed(unittest.TestCase):
    def test_closed_review_bounty_refuses_and_exits_nonzero(self):
        rc, out, transfers, lookups = _run_script("CLOSED")
        self.assertEqual(transfers, [], "no RTC may move from a closed pool")
        self.assertEqual(rc, 1)
        self.assertIn("review pool is NOT open", out)
        self.assertIn("#501 refused", out)
        self.assertEqual(lookups, ["73"])

    def test_failed_lookup_refuses(self):
        rc, out, transfers, _ = _run_script(None)
        self.assertEqual(transfers, [])
        self.assertEqual(rc, 1)
        self.assertIn("lookup failed", out)

    def test_unreadable_lookup_refuses(self):
        rc, out, transfers, _ = _run_script("garbage")
        self.assertEqual(transfers, [])
        self.assertEqual(rc, 1)

    def test_unconfigured_bounty_number_refuses(self):
        rc, out, transfers, lookups = _run_script("OPEN", {"REVIEW_BOUNTY_ISSUE": ""})
        self.assertEqual(transfers, [])
        self.assertEqual(rc, 1)
        self.assertIn("no bounty issue configured", out)
        self.assertEqual(lookups, [], "an unset number is refused without a lookup")

    def test_open_bounty_pays_as_before(self):
        rc, out, transfers, lookups = _run_script("OPEN")
        self.assertEqual(rc, 0)
        self.assertEqual(len(transfers), 1)
        self.assertEqual(transfers[0]["to_miner"], WALLET)
        self.assertEqual(transfers[0]["idempotency_key"], "bounty73-claim-501")
        self.assertEqual(lookups, ["73"])
        self.assertIn("0 refused", out)


if __name__ == "__main__":
    unittest.main()
