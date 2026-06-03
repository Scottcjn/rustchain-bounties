#!/usr/bin/env python3
"""Direct test runner for the RustChain bounties test suite."""

import unittest
import sys

# Import test modules
try:
    from tests.test_passport_redaction import TestPassportPublicRedaction
except ImportError:
    TestPassportPublicRedaction = None

def run_tests():
    """Discover and run all tests in the tests/ directory."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes explicitly to ensure they are always run
    if TestPassportPublicRedaction:
        suite.addTests(loader.loadTestsFromTestCase(TestPassportPublicRedaction))

    # Also discover any other tests in the tests/ directory
    discovered = loader.discover("tests", pattern="test_*.py")
    suite.addTests(discovered)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
