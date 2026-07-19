import pytest
from grazer_mcp import (
    graze_trending,
    graze_discover,
    graze_feed,
    graze_platforms,
)
import responses

# Define the base URL for the backend
BASE_URL = "https://api.example.com"

# Define the expected error shape
EXPECTED_ERROR_SHAPE = {
    "ok": False,
    "error": {
        "code": None,
        "message": None,
        "retryable": None,
        "source": None,
        "details": None,
    }
}

# Define the expected success response shape
EXPECTED_SUCCESS_SHAPE = {
    "id": None,
    "title": None,
    "agent": None,
    "views": None,
    # Add other fields as necessary
}

# Parametrize the test with the four tools and their respective endpoints
@pytest.mark.parametrize(
    "tool, endpoint",
    [
        (graze_trending, "/trending"),
        (graze_discover, "/discover"),
        (graze_feed, "/feed"),
        (graze_platforms, "/platforms"),
    ],
)
def test_error_contract(tool, endpoint):
    # Mock the backend to return a 500 Internal Server Error
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, BASE_URL + endpoint, status=500)
        result = tool()
        assert result == {
            **EXPECTED_ERROR_SHAPE,
            "error": {
                "code": 500,
                "message": "Internal Server Error",
                "retryable": True,
                "source": "backend",
                "details": {},
            }
        }

    # Mock the backend to return a 404 Not Found
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, BASE_URL + endpoint, status=404)
        result = tool()
        assert result == {
            **EXPECTED_ERROR_SHAPE,
            "error": {
                "code": 404,
                "message": "Not Found",
                "retryable": False,
                "source": "backend",
                "details": {},
            }
        }

    # Mock the backend to timeout
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, BASE_URL + endpoint, body=TimeoutError())
        result = tool()
        assert result == {
            **EXPECTED_ERROR_SHAPE,
            "error": {
                "code": "timeout",
                "message": "Request timed out",
                "retryable": True,
                "source": "network",
                "details": {},
            }
        }

    # Mock the backend to return a malformed/non-JSON body
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, BASE_URL + endpoint, body="not json")
        result = tool()
        assert result == {
            **EXPECTED_ERROR_SHAPE,
            "error": {
                "code": "malformed",
                "message": "Malformed response",
                "retryable": True,
                "source": "backend",
                "details": {},
            }
        }

    # Mock the backend to return a successful response
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            BASE_URL + endpoint,
            json={
                "id": "123",
                "title": "Sample Title",
                "agent": "Sample Agent",
                "views": 1000,
                # Add other fields as necessary
            },
            status=200,
        )
        result = tool()
        assert result == {
            "ok": True,
            "data": {
                "id": "123",
                "title": "Sample Title",
                "agent": "Sample Agent",
                "views": 1000,
                # Add other fields as necessary
            }
        }

# Run the tests
if __name__ == "__main__":
    pytest.main()