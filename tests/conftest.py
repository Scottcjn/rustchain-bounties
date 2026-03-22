import pytest
import asyncio
from unittest.mock import AsyncMock
from clawrtc import ClawRTC, ClawRTCConfig


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_websocket():
    """Fixture providing a mock websocket"""
    ws = AsyncMock()
    ws.connect = AsyncMock()
    ws.send = AsyncMock()
    ws.recv = AsyncMock()
    ws.close = AsyncMock()
    return ws


@pytest.fixture
def test_config():
    """Fixture providing test configuration"""
    return ClawRTCConfig(
        server_url="ws://localhost:8080",
        api_key="test-api-key",
        max_retries=3,
        timeout=30
    )


@pytest.fixture
def test_clawrtc(test_config, mock_websocket):
    """Fixture providing a ClawRTC instance with mocked websocket"""
    clawrtc = ClawRTC(test_config)
    clawrtc._websocket = mock_websocket
    return clawrtc


@pytest.fixture
def sample_message():
    """Fixture providing a sample message"""
    return {
        "type": "test",
        "data": {"content": "Hello, World!"},
        "recipient": "test-user"
    }


@pytest.fixture
def sample_session():
    """Fixture providing a sample session"""
    return {
        "id": "test-session",
        "participants": ["user1", "user2"],
        "session_type": "video"
    }
