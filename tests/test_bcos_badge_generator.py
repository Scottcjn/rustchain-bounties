import pytest

# ... (rest of the file remains the same)

class TestFlaskIntegration:
    # ... (rest of the class remains the same)

    @pytest.mark.parametrize("include_qr", ["false", "true", 1, None])
    def test_generate_badge_rejects_non_boolean_include_qr(self, include_qr):
        # Arrange
        if include_qr not in [True, False]:
            # Act and Assert
            with pytest.raises(AssertionError):
                generate_badge(include_qr=include_qr)
        else:
            # Act
            response = generate_badge(include_qr=include_qr)
            # Assert
            assert response.status_code == 200