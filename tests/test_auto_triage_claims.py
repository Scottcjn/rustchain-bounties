import unittest
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from auto_triage_claims import _extract_wallet, _extract_bottube_user, _has_proof_link, _looks_like_claim


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


if __name__ == "__main__":
    unittest.main()
