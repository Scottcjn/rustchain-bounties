import unittest
from pathlib import Path


class Bounty560ProofTests(unittest.TestCase):
    def test_bounty_560_proof_file_has_required_fields(self):
        proof_path = Path("bounty-560-saascity-upvote-proof.md")
        self.assertTrue(proof_path.exists(), "Expected bounty #560 proof file is missing")

        content = proof_path.read_text(encoding="utf-8")

        required_snippets = [
            "Bounty #560",
            "SaaS City",
            "BoTTube",
            "RustChain",
            "username",
            "screenshot",
        ]

        for snippet in required_snippets:
            self.assertIn(snippet, content, f"Missing required proof detail: {snippet}")


if __name__ == "__main__":
    unittest.main()
