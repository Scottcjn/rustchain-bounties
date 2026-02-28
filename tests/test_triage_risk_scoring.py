import unittest

from scripts.triage_risk_scoring import ClaimRiskInput, bucket_for_score, score_claims


class TriageRiskScoringTests(unittest.TestCase):
    def test_scoring_across_benign_and_suspicious_fixtures(self):
        fixtures = [
            # 1) benign baseline
            ClaimRiskInput(
                user="benign1",
                issue_ref="Scottcjn/rustchain-bounties#87",
                repo="rustchain-bounties",
                created_at="2026-02-28T00:00:00Z",
                body_text="Claim with unique text and unique proof",
                account_age_days=300,
                wallet="benign_wallet_1",
                bottube_user="benign_bt_1",
                proof_links=["https://example.com/proof/a"],
                comment_timestamps=["2026-02-28T00:00:00Z"],
            ),
            # 2) very new account
            ClaimRiskInput(
                user="newbie",
                issue_ref="Scottcjn/rustchain-bounties#103",
                repo="rustchain-bounties",
                created_at="2026-02-28T01:00:00Z",
                body_text="claim text",
                account_age_days=2,
                wallet="new_wallet_1",
                bottube_user=None,
                proof_links=["https://example.com/proof/b"],
                comment_timestamps=["2026-02-28T01:00:00Z"],
            ),
            # 3-5) velocity burst (same user 3 claims in 24h)
            ClaimRiskInput(
                user="burstuser",
                issue_ref="Scottcjn/rustchain-bounties#87",
                repo="rustchain-bounties",
                created_at="2026-02-28T02:00:00Z",
                body_text="burst one",
                account_age_days=120,
                wallet="burst_wallet",
                bottube_user=None,
                proof_links=["https://example.com/proof/c1"],
                comment_timestamps=["2026-02-28T02:00:00Z", "2026-02-28T02:05:00Z", "2026-02-28T02:08:00Z"],
            ),
            ClaimRiskInput(
                user="burstuser",
                issue_ref="Scottcjn/Rustchain#47",
                repo="Rustchain",
                created_at="2026-02-28T03:00:00Z",
                body_text="burst two",
                account_age_days=120,
                wallet="burst_wallet",
                bottube_user=None,
                proof_links=["https://example.com/proof/c2"],
                comment_timestamps=["2026-02-28T03:00:00Z"],
            ),
            ClaimRiskInput(
                user="burstuser",
                issue_ref="Scottcjn/bottube#74",
                repo="bottube",
                created_at="2026-02-28T04:00:00Z",
                body_text="burst three",
                account_age_days=120,
                wallet="burst_wallet",
                bottube_user=None,
                proof_links=["https://example.com/proof/c3"],
                comment_timestamps=["2026-02-28T04:00:00Z"],
            ),
            # 6-7) template reuse + shared wallet + duplicate proof
            ClaimRiskInput(
                user="templ1",
                issue_ref="Scottcjn/rustchain-bounties#157",
                repo="rustchain-bounties",
                created_at="2026-02-28T05:00:00Z",
                body_text="I starred project and joined. same exact reusable template phrase",
                account_age_days=90,
                wallet="shared_wallet",
                bottube_user="shared_bt",
                proof_links=["https://example.com/proof/shared"],
                comment_timestamps=["2026-02-28T05:00:00Z"],
            ),
            ClaimRiskInput(
                user="templ2",
                issue_ref="Scottcjn/rustchain-bounties#158",
                repo="rustchain-bounties",
                created_at="2026-02-28T05:30:00Z",
                body_text="I starred project and joined. same exact reusable template phrase",
                account_age_days=88,
                wallet="shared_wallet",
                bottube_user="shared_bt",
                proof_links=["https://example.com/proof/shared"],
                comment_timestamps=["2026-02-28T05:30:00Z"],
            ),
            # 8) missing optional features should not hard-fail
            ClaimRiskInput(
                user="no-data",
                issue_ref="Scottcjn/rustchain-bounties#87",
                repo="rustchain-bounties",
                created_at="2026-02-28T06:00:00Z",
                body_text="",
                account_age_days=None,
                wallet=None,
                bottube_user=None,
                proof_links=[],
                comment_timestamps=[],
            ),
        ]

        scored = score_claims(fixtures)

        benign = scored["Scottcjn/rustchain-bounties#87:benign1"]
        self.assertEqual(benign.score, 0)
        self.assertEqual(benign.bucket, "low")

        newbie = scored["Scottcjn/rustchain-bounties#103:newbie"]
        self.assertGreaterEqual(newbie.score, 35)
        self.assertTrue(any(r.startswith("ACCOUNT_AGE_VERY_NEW") for r in newbie.reasons))

        burst = scored["Scottcjn/rustchain-bounties#87:burstuser"]
        self.assertTrue(any("CLAIM_BURST" in r for r in burst.reasons))
        self.assertTrue(any("MULTI_REPO_BURST" in r for r in burst.reasons))
        self.assertTrue(any("CADENCE_TIGHT_WINDOW" in r for r in burst.reasons))

        templ = scored["Scottcjn/rustchain-bounties#157:templ1"]
        self.assertTrue(any("TEMPLATE_REUSE" in r for r in templ.reasons))
        self.assertTrue(any("SHARED_WALLET" in r for r in templ.reasons))
        self.assertTrue(any("SHARED_BOTTUBE" in r for r in templ.reasons))
        self.assertTrue(any("DUPLICATE_PROOF_LINKS" in r for r in templ.reasons))
        self.assertEqual(templ.bucket, "high")

        nodata = scored["Scottcjn/rustchain-bounties#87:no-data"]
        self.assertIsNotNone(nodata)
        self.assertIn(nodata.bucket, {"low", "medium", "high"})

    def test_bucket_for_score(self):
        self.assertEqual(bucket_for_score(0), "low")
        self.assertEqual(bucket_for_score(30), "medium")
        self.assertEqual(bucket_for_score(80), "high")


if __name__ == "__main__":
    unittest.main()
