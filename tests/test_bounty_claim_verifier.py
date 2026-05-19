import unittest
import json
import os
import tempfile

from scripts import bounty_claim_verifier as verifier


class FakeResponse:
    def __init__(self, status, body):
        self.status = status
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.body.encode("utf-8")


class BountyClaimVerifierTests(unittest.TestCase):
    def test_extract_wallet_and_urls(self):
        body = "Claiming. Wallet: miner_abc123 Proof: https://dev.to/example/post."
        self.assertEqual(verifier.extract_wallet(body), "miner_abc123")
        self.assertEqual(verifier.extract_urls(body), ["https://dev.to/example/post"])

    def test_claim_from_event(self):
        event = {
            "issue": {"number": 747},
            "comment": {
                "id": 123,
                "html_url": "https://github.com/x/y/issues/747#issuecomment-123",
                "body": "Claiming with miner-id: rtc_worker_7",
                "user": {"login": "alice"},
            },
        }
        claim = verifier.claim_from_event(event)
        self.assertEqual(claim.user, "alice")
        self.assertEqual(claim.issue_number, 747)
        self.assertEqual(claim.wallet, "rtc_worker_7")

    def test_duplicate_claim_check_finds_prior_wallet(self):
        claim = verifier.Claim(
            user="alice",
            issue_number=1,
            comment_id=20,
            comment_url="",
            body="Claiming. Wallet: shared_wallet",
            wallet="shared_wallet",
            urls=[],
        )
        comments = [
            {"id": 10, "user": {"login": "bob"}, "body": "Claiming. Wallet: shared_wallet"},
            {"id": 20, "user": {"login": "alice"}, "body": claim.body},
        ]
        check = verifier.duplicate_claim_check(claim, comments)
        self.assertEqual(check.status, "needs-review")
        self.assertIn("wallet=1", check.detail)

    def test_duplicate_claim_check_ignores_bot_marker(self):
        claim = verifier.Claim("alice", 1, 20, "", "Claiming", "wallet1", [])
        comments = [
            {"id": 9, "user": {"login": "bot"}, "body": f"{verifier.BOT_MARKER} comment:20 --> wallet1"},
        ]
        check = verifier.duplicate_claim_check(claim, comments)
        self.assertEqual(check.status, "verified")

    def test_render_report_contains_comment_marker(self):
        claim = verifier.Claim("alice", 747, 123, "https://example.com/c", "Claiming", "wallet1", [])
        body = verifier.render_report(claim, [verifier.Check("Wallet", "verified", "ok")])
        self.assertIn("<!-- bounty-claim-verifier comment:123 -->", body)
        self.assertIn("| Wallet | verified | ok |", body)

    def test_main_skips_bot_report_comments(self):
        claim = verifier.Claim("github-actions[bot]", 747, 123, "https://example.com/c", "Claiming", "wallet1", [])
        event = {
            "issue": {"number": 747},
            "comment": {
                "id": 124,
                "html_url": "https://github.com/x/y/issues/747#issuecomment-124",
                "body": verifier.render_report(claim, [verifier.Check("Wallet", "verified", "ok")]),
                "user": {"login": "github-actions[bot]"},
            },
        }

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as fh:
            json.dump(event, fh)
            event_path = fh.name

        try:
            self.assertEqual(verifier.main(["--event-path", event_path]), 0)
        finally:
            os.unlink(event_path)

    def test_wallet_check_does_not_verify_zero_balance_response(self):
        def opener(_req, timeout=20):
            return FakeResponse(
                200,
                json.dumps({
                    "amount_i64": 0,
                    "amount_rtc": 0.0,
                    "miner_id": "definitely-not-real",
                }),
            )

        check = verifier.check_wallet_exists("definitely-not-real", opener=opener)

        self.assertEqual(check.status, "needs-review")
        self.assertIn("zero balance", check.detail)

    def test_text_extractor_counts_visible_text(self):
        parser = verifier.TextExtractor()
        parser.feed("<html><body><h1>Hello</h1><p>RustChain world</p></body></html>")
        self.assertIn("RustChain world", parser.text())


if __name__ == "__main__":
    unittest.main()
