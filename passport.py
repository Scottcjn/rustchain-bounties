class Passport:
    """A simple passport data store with public/admin redaction support."""

    SENSITIVE_FIELDS = {"ssn", "credit_card", "password"}

    def __init__(self):
        self.data = {}

    def add_entry(self, key: str, value: str) -> None:
        """Add or update an entry in the passport."""
        self.data[key] = value

    def get_public(self) -> dict:
        """Return a redacted view of the passport data for public access.
        Sensitive fields are replaced with a masked value."""
        result = {}
        for key, value in self.data.items():
            if key in self.SENSITIVE_FIELDS:
                result[key] = "***-**-****" if key == "ssn" else "****"
            else:
                result[key] = value
        return result

    def get_admin(self) -> dict:
        """Return the full passport data for admin access."""
        return dict(self.data)
