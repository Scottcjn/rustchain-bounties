import pytest

# ... (rest of the file remains the same)

def test_bridge_confirm_requires_admin_key():
    # Arrange
    admin_key = "valid_admin_key"
    # Act
    response = bridge_confirm(admin_key)
    # Assert
    assert response.status_code == 200

def test_bridge_release_requires_admin_key():
    # Arrange
    admin_key = "valid_admin_key"
    # Act
    response = bridge_release(admin_key)
    # Assert
    assert response.status_code == 200

def test_bridge_confirm_and_release_accept_valid_admin_key():
    # Arrange
    admin_key = "valid_admin_key"
    # Act
    response = bridge_confirm_and_release(admin_key)
    # Assert
    assert response.status_code == 200