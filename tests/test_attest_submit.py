import unittest
import json
from fuzzing_tool import (
    generate_missing_field_payload,
    generate_wrong_type_payload,
    generate_oversized_payload,
    generate_injection_payload
)

class TestAttestSubmitFuzzing(unittest.TestCase):
    def test_missing_field_payload(self):
        """Test missing field payload generation"""
        payload = generate_missing_field_payload()
        self.assertEqual(len(payload), 2)  # One field should be missing
        self.assertNotIn("attestation", payload) or \
            self.assertNotIn("signature", payload) or \
            self.assertNotIn("public_key", payload)

    def test_wrong_type_payload(self):
        """Test wrong type payload generation"""
        payload = generate_wrong_type_payload()
        self.assertIsInstance(payload["attestation"], int)
        self.assertIsInstance(payload["signature"], int)
        self.assertIsInstance(payload["public_key"], int)

    def test_oversized_payload(self):
        """Test oversized payload generation"""
        payload = generate_oversized_payload()
        self.assertGreater(len(payload["attestation"]), 1000)
        self.assertGreater(len(payload["signature"]), 1000)
        self.assertGreater(len(payload["public_key"]), 1000)

    def test_injection_payload(self):
        """Test injection payload generation"""
        payload = generate_injection_payload()
        injection_strings = [
            "<script>alert('xss')</script>",
            "' OR '1'='1",
            "DROP TABLE users;--",
            "UNION SELECT * FROM users"
        ]
        self.assertIn(payload["attestation"], injection_strings) or \
            self.assertIn(payload["signature"], injection_strings) or \
            self.assertIn(payload["public_key"], injection_strings)

if __name__ == "__main__":
    unittest.main()