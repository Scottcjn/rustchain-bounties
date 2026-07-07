import unittest
import urllib.error
from unittest import mock

from scripts.auto_triage_claims import (
    ClaimResult,
    _apply_risk_scores,
    _build_report_md,
    _extract_bottube_user,
    _extract_wallet,
    _fetch_star_cache,
    _has_proof_link,
    _looks_like_claim,
)


class AutoTriageClaimsTests(unittest.TestCase):
    def test_extract_wallet_supports_miner_id_space(self):
        body = "Claim\nMiner id: abc_123_wallet\nProof: https://example.com/proof"
        self.assertEqual(_extract_wallet(body), "abc_123_wallet")

    def test_extract_wallet_supports_miner_id_hyphen(self):
        body = "Payout target miner-id: zk_worker_007"
        self.assertEqual(_extract_wallet(body), "zk_worker_007")

    def test_extract_wallet_supports_chinese_label(self):
        body = "钱包地址： zh_wallet_01"
        self.assertEqual(_extract_wallet(body), "zh_wallet_01")

    def test_extract_bottube_user_from_profile_link(self):
        body = "BoTTube profile: https://bottube.ai/@energypantry"
        self.assertEqual(_extract_bottube_user(body), "energypantry")

    def test_has_proof_link(self):
        self.assertTrue(_has_proof_link("Demo: https://github.com/foo/bar/pull/1"))
        self.assertFalse(_has_proof_link("No links included"))

    def test_looks_like_claim(self):
        self.assertTrue(_looks_like_claim("Claiming this bounty. Wallet: abc_123"))
        self.assertFalse(_looks_like_claim("General discussion about roadmap and release timing."))

    def test_build_report_includes_suspicious_claims_summary(self):
        results_by_issue = {
            "Scottcjn/rustchain-bounties#476": [
                ClaimResult(
                    claim_id="c-1",
                    user="fresh-bot",
                    issue_ref="Scottcjn/rustchain-bounties#476",
                    comment_url="https://example.com/c-1",
                    created_at="2026-02-28T00:00:00Z",
                    account_age_days=1,
                    wallet="shared_wallet",
                    bottube_user=None,
                    blockers=[],
                    proof_links=["https://example.com/proof"],
                    body="Claiming this bounty. Wallet: shared_wallet. Proof: https://example.com/proof",
                ),
                ClaimResult(
                    claim_id="c-2",
                    user="steady-user",
                    issue_ref="Scottcjn/rustchain-bounties#476",
                    comment_url="https://example.com/c-2",
                    created_at="2026-02-28T01:00:00Z",
                    account_age_days=400,
                    wallet="steady_wallet",
                    bottube_user=None,
                    blockers=[],
                    proof_links=["https://example.com/unique-proof"],
                    body="Claiming this bounty with a unique implementation plan.",
                ),
            ]
        }

        _apply_risk_scores(results_by_issue, "balanced")
        report = _build_report_md(
            "2026-02-28T02:00:00Z",
            results_by_issue,
            72,
            "balanced",
        )

        self.assertIn("#### Suspicious Claims", report)
        self.assertIn("@fresh-bot", report)
        self.assertIn("ACCOUNT_AGE", report)

    def test_fetch_star_cache_survives_cross_repo_403(self):
        # This reproduces the real failure: GitHub's "List stargazers"
        # endpoint returns 403 "Resource not accessible by integration"
        # for the default Actions GITHUB_TOKEN when the repo isn't the one
        # the workflow runs in, even for public repos. That used to raise
        # out of _gh_paginated and crash the whole triage run for every
        # bounty target, not just the ones needing that star.
        forbidden = urllib.error.HTTPError(
            url="https://api.github.com/repos/Scottcjn/Rustchain/stargazers",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=None,
        )

        def fake_paginated(path, token):
            if "good-repo" in path:
                return [{"login": "alice"}, {"login": "bob"}]
            raise forbidden

        with mock.patch(
            "scripts.auto_triage_claims._gh_paginated", side_effect=fake_paginated
        ):
            cache, errors = _fetch_star_cache(["good-repo", "blocked-repo"], "tok")

        self.assertEqual(cache["good-repo"], {"alice", "bob"})
        self.assertEqual(cache["blocked-repo"], set())
        self.assertNotIn("good-repo", errors)
        self.assertIn("blocked-repo", errors)
        self.assertIn("403", errors["blocked-repo"])

    def test_fetch_star_cache_prefers_star_token_when_set(self):
        seen_tokens = []

        def fake_paginated(path, token):
            seen_tokens.append(token)
            return [{"login": "alice"}]

        with mock.patch(
            "scripts.auto_triage_claims._gh_paginated", side_effect=fake_paginated
        ):
            _fetch_star_cache(["some-repo"], "default-tok", star_token="pat-tok")

        self.assertEqual(seen_tokens, ["pat-tok"])


if __name__ == "__main__":
    unittest.main()
