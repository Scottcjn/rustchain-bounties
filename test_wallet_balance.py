import pytest
import responses
from wallet_balance import get_wallet_balance

@responses.activate
def test_valid_response():
    responses.add(
        responses.GET,
        "https://api.example.com/wallets/123",
        json={"balance": 100},
        status=200
    )
    assert get_wallet_balance("123") == 100

@responses.activate
def test_http_error():
    responses.add(
        responses.GET,
        "https://api.example.com/wallets/123",
        status=404
    )
    with pytest.raises(SystemExit) as excinfo:
        get_wallet_balance("123")
    assert excinfo.value.code == 2

@responses.activate
def test_network_error():
    responses.add(
        responses.GET,
        "https://api.example.com/wallets/123",
        body=requests.exceptions.ConnectionError("Connection refused")
    )
    with pytest.raises(SystemExit) as excinfo:
        get_wallet_balance("123")
    assert excinfo.value.code == 3

@responses.activate
def test_malformed_json():
    responses.add(
        responses.GET,
        "https://api.example.com/wallets/123",
        body="invalid json",
        status=200
    )
    with pytest.raises(SystemExit) as excinfo:
        get_wallet_balance("123")
    assert excinfo.value.code == 4

@responses.activate
def test_missing_balance_field():
    responses.add(
        responses.GET,
        "https://api.example.com/wallets/123",
        json={},
        status=200
    )
    with pytest.raises(SystemExit) as excinfo:
        get_wallet_balance("123")
    assert excinfo.value.code == 4

@responses.activate
def test_unexpected_error():
    responses.add(
        responses.GET,
        "https://api.example.com/wallets/123",
        body=Exception("Unexpected error"),
    )
    with pytest.raises(SystemExit) as excinfo:
        get_wallet_balance("123")
    assert excinfo.value.code == 5
