#!/usr/bin/env python3
"""Tests for beacon_discord_transport"""

import pytest
import sys
import time
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from importlib import reload

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestRateLimitConfig:
    """Test RateLimitConfig dataclass"""

    def test_default_config(self):
        from beacon_discord_transport import RateLimitConfig
        config = RateLimitConfig()
        
        assert config.max_retries == 5
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.strategy.value == "exponential_backoff"

    def test_custom_config(self):
        from beacon_discord_transport import RateLimitConfig, RateLimitStrategy
        config = RateLimitConfig(
            max_retries=10,
            base_delay=2.0,
            strategy=RateLimitStrategy.LINEAR_BACKOFF
        )
        
        assert config.max_retries == 10
        assert config.base_delay == 2.0
        assert config.strategy == RateLimitStrategy.LINEAR_BACKOFF


class TestDiscordMessage:
    """Test DiscordMessage dataclass"""

    def test_create_message(self):
        from beacon_discord_transport import DiscordMessage
        msg = DiscordMessage(
            id="123",
            channel_id="456",
            author="testuser",
            content="Hello!",
            timestamp="2026-02-19T00:00:00Z"
        )
        
        assert msg.id == "123"
        assert msg.channel_id == "456"
        assert msg.author == "testuser"
        assert msg.content == "Hello!"
        assert msg.guild_id is None

    def test_message_with_guild(self):
        from beacon_discord_transport import DiscordMessage
        msg = DiscordMessage(
            id="123",
            channel_id="456",
            author="testuser",
            content="Hello!",
            timestamp="2026-02-19T00:00:00Z",
            guild_id="789"
        )
        
        assert msg.guild_id == "789"


class TestDiscordTransport:
    """Test DiscordTransport class"""

    @patch('beacon_discord_transport.requests.Session')
    def test_init(self, mock_session):
        from beacon_discord_transport import DiscordTransport
        transport = DiscordTransport("test_token")
        
        assert transport.bot_token == "test_token"
        assert "Bot test_token" in transport.session.headers["Authorization"]

    @patch('beacon_discord_transport.requests.Session')
    def test_calculate_delay_exponential(self, mock_session):
        from beacon_discord_transport import DiscordTransport, RateLimitStrategy
        transport = DiscordTransport("test_token")
        transport.rate_limit_config.strategy = RateLimitStrategy.EXPONENTIAL_BACKOFF
        
        # Exponential: 1*2^0=1, 1*2^1=2, 1*2^2=4
        delay0 = transport._calculate_delay(0)
        delay1 = transport._calculate_delay(1)
        delay2 = transport._calculate_delay(2)
        
        assert delay0 >= 1.0
        assert delay1 >= 2.0
        assert delay2 >= 4.0
        assert delay0 <= 2.0  # With jitter
        assert delay1 <= 3.0

    @patch('beacon_discport_transport.requests.Session')
    def test_calculate_delay_linear(self, mock_session):
        from beacon_discord_transport import DiscordTransport, RateLimitStrategy
        transport = DiscordTransport("test_token")
        transport.rate_limit_config.strategy = RateLimitStrategy.LINEAR_BACKOFF
        
        delay0 = transport._calculate_delay(0)
        delay1 = transport._calculate_delay(1)
        
        assert delay0 >= 1.0
        assert delay1 >= 2.0

    @patch('beacon_discord_transport.requests.Session')
    def test_should_retry(self, mock_session):
        from beacon_discord_transport import DiscordTransport
        transport = DiscordTransport("test_token")
        
        assert transport._should_retry(429) is True
        assert transport._should_retry(500) is True
        assert transport._should_retry(502) is True
        assert transport._should_retry(200) is False
        assert transport._should_retry(404) is False


class TestListener:
    """Test message listener functionality"""

    @patch('beacon_discord_transport.requests.Session')
    def test_add_listener(self, mock_session):
        from beacon_discord_transport import DiscordTransport, DiscordMessage
        transport = DiscordTransport("test_token")
        
        callback = Mock()
        transport.add_listener(callback)
        
        assert callback in transport._listeners

    @patch('beacon_discord_transport.requests.Session')
    def test_remove_listener(self, mock_session):
        from beacon_discord_transport import DiscordTransport, DiscordMessage
        transport = DiscordTransport("test_token")
        
        callback = Mock()
        transport.add_listener(callback)
        transport.remove_listener(callback)
        
        assert callback not in transport._listeners

    @patch('beacon_discord_transport.requests.Session')
    def test_notify_listeners(self, mock_session):
        from beacon_discord_transport import DiscordTransport, DiscordMessage
        transport = DiscordTransport("test_token")
        
        callback = Mock()
        transport.add_listener(callback)
        
        msg = DiscordMessage(
            id="123",
            channel_id="456",
            author="testuser",
            content="Hello!",
            timestamp="2026-02-19T00:00:00Z"
        )
        
        transport._notify_listeners(msg)
        
        callback.assert_called_once_with(msg)

    @patch('beacon_discord_transport.requests.Session')
    def test_notify_listeners_error_handling(self, mock_session):
        from beacon_discord_transport import DiscordTransport, DiscordMessage
        transport = DiscordTransport("test_token")
        
        error_callback = Mock(side_effect=Exception("Test error"))
        transport.add_listener(error_callback)
        
        msg = DiscordMessage(
            id="123",
            channel_id="456",
            author="testuser",
            content="Hello!",
            timestamp="2026-02-19T00:00:00Z"
        )
        
        # Should not raise, just log error
        transport._notify_listeners(msg)


class TestConvenienceFunctions:
    """Test convenience factory functions"""

    @patch('beacon_discord_transport.requests.Session')
    def test_create_transport(self, mock_session):
        from beacon_discord_transport import create_transport, RateLimitConfig
        transport = create_transport("test_token", max_retries=3, base_delay=0.5)
        
        assert transport.bot_token == "test_token"
        assert transport.rate_limit_config.max_retries == 3
        assert transport.rate_limit_config.base_delay == 0.5


class TestErrorHandling:
    """Test error handling"""

    @patch('beacon_discord_transport.requests.Session')
    def test_rate_limit_error(self, mock_session):
        from beacon_discord_transport import RateLimitError
        error = RateLimitError("Rate limited", retry_after=5.0)
        
        assert "Rate limited" in str(error)
        assert error.retry_after == 5.0


class TestIntegration:
    """Integration tests"""

    @patch('beacon_discord_transport.requests.Session')
    def test_full_workflow(self, mock_session):
        from beacon_discord_transport import DiscordTransport, DiscordMessage, create_transport
        
        # Create transport
        transport = create_transport("test_token")
        
        # Add listener
        received = []
        def on_message(msg):
            received.append(msg)
        
        transport.add_listener(on_message)
        
        # Simulate message
        msg = DiscordMessage(
            id="123",
            channel_id="456",
            author="testuser",
            content="Test!",
            timestamp="2026-02-19T00:00:00Z"
        )
        transport._notify_listeners(msg)
        
        assert len(received) == 1
        assert received[0].content == "Test!"
        
        # Remove listener
        transport.remove_listener(on_message)
        transport._notify_listeners(msg)
        
        assert len(received) == 1  # Still 1, not called again


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
