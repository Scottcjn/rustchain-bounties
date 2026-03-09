#!/usr/bin/env python3
"""
Test script for the fuzz_attest_submit.py script
This script verifies that the fuzzing logic works correctly
"""

import unittest
from fuzz_attest_submit import generate_random_attestation, generate_malformed_attestation, submit_attestation
import json


class TestFuzzAttestSubmit(unittest.TestCase):
    def test_generate_random_attestation(self):
        """Test that random attestations are generated correctly"""
        attestation = generate_random_attestation()
        
        # Check required fields
        self.assertIn("miner_id", attestation)
        self.assertIn("timestamp", attestation)
        self.assertIn("data", attestation)
        self.assertIn("signature", attestation)
        self.assertIn("version", attestation)
        
        # Check data structure
        self.assertIn("type", attestation["data"])
        self.assertIn("value", attestation["data"])
        self.assertIn("metadata", attestation["data"])
        
        # Check types
        self.assertIsInstance(attestation["miner_id"], str)
        self.assertIsInstance(attestation["timestamp"], int)
        self.assertIsInstance(attestation["data"], dict)
        self.assertIsInstance(attestation["signature"], str)
        self.assertIsInstance(attestation["version"], str)

    def test_generate_malformed_attestation(self):
        """Test that malformed attestations are generated correctly"""
        malformed = generate_malformed_attestation()
        
        # Malformed attestations should not have all required fields
        self.assertNotIn("miner_id", malformed or malformed["miner_id"] == "")
        self.assertNotIn("timestamp", malformed or not isinstance(malformed["timestamp"], int))
        self.assertNotIn("data", malformed or not isinstance(malformed["data"], dict))

    def test_submit_attestation(self):
        """Test submitting an attestation"""
        # This test will fail if the server is not running, but that's expected
        attestation = generate_random_attestation()
        status_code, response_text = submit_attestation(attestation)
        
        # Either we get a valid response or a connection error
        self.assertIsInstance(status_code, int)
        self.assertIsInstance(response_text, str)

    def test_attestation_structure(self):
        """Test the structure of generated attestations"""
        for _ in range(10):  # Test multiple random attestations
            attestation = generate_random_attestation()
            
            # Test that the JSON is valid
            json.dumps(attestation)
            
            # Test miner ID format
            self.assertTrue(len(attestation["miner_id"]) > 0)
            self.assertTrue(attestation["miner_id"].isalnum())
            
            # Test timestamp is reasonable
            self.assertTrue(attestation["timestamp"] > 0)
            
            # Test data types
            self.assertIn(attestation["data"]["type"], ['performance', 'availability', 'integrity'])
            self.assertIsInstance(attestation["data"]["value"], (int, float))
            
            # Test metadata structure
            self.assertIsInstance(attestation["data"]["metadata"], dict)
            
            # Test version format
            self.assertTrue(attestation["version"].startswith(('1.', '2.', '3.')))


if __name__ == "__main__":
    unittest.main()
