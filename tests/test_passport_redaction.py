import unittest
from passport import Passport

class TestPassportPublicRedaction(unittest.TestCase):
    """Tests for public/admin redaction behavior on Passport."""

    def setUp(self):
        self.passport = Passport()
        self.passport.add_entry("name", "Alice")
        self.passport.add_entry("ssn", "123-45-6789")
        self.passport.add_entry("address", "123 Main St")

    def test_public_redaction_hides_sensitive_fields(self):
        """Public view should redact sensitive fields like SSN."""
        public = self.passport.get_public()
        self.assertIn("name", public)
        self.assertNotIn("ssn", public)
        self.assertIn("address", public)
        self.assertEqual(public["ssn"], "***-**-****")

    def test_admin_redaction_shows_all_fields(self):
        """Admin view should show all fields including sensitive ones."""
        admin = self.passport.get_admin()
        self.assertIn("name", admin)
        self.assertIn("ssn", admin)
        self.assertIn("address", admin)
        self.assertEqual(admin["ssn"], "123-45-6789")

    def test_redaction_does_not_affect_original_data(self):
        """Redaction should not mutate the underlying passport data."""
        original_ssn = self.passport.data["ssn"]
        _ = self.passport.get_public()
        self.assertEqual(self.passport.data["ssn"], original_ssn)

    def test_empty_passport_redaction(self):
        """Empty passport should return empty dict for both views."""
        empty = Passport()
        self.assertEqual(empty.get_public(), {})
        self.assertEqual(empty.get_admin(), {})

if __name__ == "__main__":
    unittest.main()
