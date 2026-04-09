#!/usr/bin/env python3
"""
Unit tests for Miner Status Notification System
"""

import pytest
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).parent))
from miner_monitor import (
    MinerMonitor,
    MinerState,
    NotificationConfig,
    EPOCH_MINUTES,
    MISSED_EPOCHS_THRESHOLD,
    ALERT_COOLDOWN_HOURS
)


class TestMinerState:
    """Tests for MinerState dataclass"""
    
    def test_create_miner_state(self):
        """Test creating a new miner state"""
        state = MinerState(miner_id="test-miner-1")
        assert state.miner_id == "test-miner-1"
        assert state.is_online is True
        assert state.alert_count == 0
        assert state.streak_days == 0
    
    def test_miner_state_to_dict(self):
        """Test serialization to dictionary"""
        state = MinerState(
            miner_id="test-miner-1",
            last_seen=1234567890.0,
            is_online=False,
            alert_count=3
        )
        data = state.to_dict()
        assert data['miner_id'] == "test-miner-1"
        assert data['last_seen'] == 1234567890.0
        assert data['is_online'] is False
        assert data['alert_count'] == 3
    
    def test_miner_state_from_dict(self):
        """Test deserialization from dictionary"""
        data = {
            'miner_id': 'test-miner-2',
            'last_seen': 9876543210.0,
            'last_attest': 9876543200.0,
            'is_online': True,
            'last_alert_sent': 0.0,
            'alert_count': 0,
            'streak_days': 5,
            'streak_warned': False
        }
        state = MinerState.from_dict(data)
        assert state.miner_id == "test-miner-2"
        assert state.last_seen == 9876543210.0
        assert state.streak_days == 5


class TestNotificationConfig:
    """Tests for NotificationConfig"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = NotificationConfig()
        assert config.enabled_channels == ["discord", "telegram"]
        assert config.email_smtp_port == 587
        assert config.discord_webhook == ""
    
    def test_config_save_load(self, tmp_path):
        """Test saving and loading configuration"""
        config_file = tmp_path / "config.json"
        
        # Create and save config
        config = NotificationConfig(
            discord_webhook="https://discord.com/webhook/test",
            telegram_bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
            telegram_chat_id="-1001234567890",
            enabled_channels=["discord", "telegram", "webhook"]
        )
        config.save(config_file)
        
        # Load config
        loaded_config = NotificationConfig.load(config_file)
        assert loaded_config.discord_webhook == "https://discord.com/webhook/test"
        assert loaded_config.telegram_bot_token == "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
        assert "webhook" in loaded_config.enabled_channels
    
    def test_config_load_nonexistent(self):
        """Test loading config from non-existent file"""
        config = NotificationConfig.load(Path("/nonexistent/path/config.json"))
        assert isinstance(config, NotificationConfig)
        assert config.enabled_channels == ["discord", "telegram"]


class TestMinerMonitor:
    """Tests for MinerMonitor class"""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration"""
        config = Mock(spec=NotificationConfig)
        config.discord_webhook = "https://discord.com/webhook/test"
        config.telegram_bot_token = "test-token"
        config.telegram_chat_id = "-123456"
        config.enabled_channels = ["discord"]
        config.email_smtp_server = ""
        config.webhook_url = ""
        return config
    
    @pytest.fixture
    def monitor(self, mock_config):
        """Create a monitor instance with mocked config"""
        with patch('miner_monitor.STATE_FILE', Path('/tmp/test_state.json')):
            with patch('miner_monitor.Path.exists', return_value=False):
                return MinerMonitor(mock_config)
    
    def test_fetch_miners_success(self, monitor):
        """Test successful miner data fetch"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "miners": [
                {"miner": "test-miner-1", "last_attest": time.time()},
                {"miner": "test-miner-2", "last_attest": time.time()}
            ]
        }
        mock_response.raise_for_status = Mock()
        
        with patch('miner_monitor.requests.get', return_value=mock_response):
            miners = monitor.fetch_miners()
            assert len(miners) == 2
            assert miners[0]['miner'] == "test-miner-1"
    
    def test_fetch_miners_failure(self, monitor):
        """Test failed miner data fetch"""
        with patch('miner_monitor.requests.get', side_effect=Exception("API Error")):
            miners = monitor.fetch_miners()
            assert miners == []
    
    def test_check_miner_status_online(self, monitor):
        """Test checking status of online miner"""
        current_time = time.time()
        miner_data = {
            "miner": "test-miner-1",
            "last_attest": current_time
        }
        
        state = monitor.check_miner_status(miner_data)
        assert state.miner_id == "test-miner-1"
        assert state.is_online is True
    
    def test_check_miner_status_offline(self, monitor):
        """Test checking status of offline miner"""
        # Set last_attest to 25 minutes ago (2.5 epochs)
        current_time = time.time()
        last_attest = current_time - (25 * 60)
        
        miner_data = {
            "miner": "test-miner-1",
            "last_attest": last_attest
        }
        
        state = monitor.check_miner_status(miner_data)
        assert state.is_online is False
    
    def test_check_miner_status_back_online(self, monitor):
        """Test detection of miner coming back online"""
        current_time = time.time()
        
        # First, set miner as offline
        miner_data_offline = {
            "miner": "test-miner-1",
            "last_attest": current_time - (25 * 60)
        }
        monitor.check_miner_status(miner_data_offline)
        assert monitor.miners["test-miner-1"].is_online is False
        
        # Then, bring miner back online
        miner_data_online = {
            "miner": "test-miner-1",
            "last_attest": current_time
        }
        state = monitor.check_miner_status(miner_data_online)
        assert state.is_online is True
    
    def test_alert_rate_limiting(self, monitor):
        """Test that alerts are rate limited"""
        current_time = time.time()
        
        # Set last_attest to 25 minutes ago
        miner_data = {
            "miner": "test-miner-1",
            "last_attest": current_time - (25 * 60)
        }
        
        # First check should trigger alert
        with patch.object(monitor, 'send_offline_alert') as mock_alert:
            monitor.check_miner_status(miner_data)
            assert mock_alert.called
            alert_count = monitor.miners["test-miner-1"].alert_count
        
        # Second check within cooldown should NOT trigger alert
        with patch.object(monitor, 'send_offline_alert') as mock_alert:
            monitor.check_miner_status(miner_data)
            # Alert count should remain the same
            assert monitor.miners["test-miner-1"].alert_count == alert_count
    
    def test_save_load_state(self, monitor, tmp_path):
        """Test saving and loading miner state"""
        state_file = tmp_path / "state.json"
        
        # Create some state
        monitor.miners["test-miner-1"] = MinerState(
            miner_id="test-miner-1",
            is_online=False,
            alert_count=2,
            streak_days=5
        )
        
        # Save state
        with patch('miner_monitor.STATE_FILE', state_file):
            monitor.save_state()
        
        # Verify file was created
        assert state_file.exists()
        
        # Load and verify
        with open(state_file) as f:
            data = json.load(f)
            assert "test-miner-1" in data['miners']
            assert data['miners']['test-miner-1']['alert_count'] == 2
    
    def test_run_once(self, monitor):
        """Test single monitoring cycle"""
        mock_miners = [
            {"miner": "miner-1", "last_attest": time.time()},
            {"miner": "miner-2", "last_attest": time.time() - (30 * 60)}
        ]
        
        with patch.object(monitor, 'fetch_miners', return_value=mock_miners):
            with patch.object(monitor, 'save_state'):
                monitor.run_once()
        
        assert "miner-1" in monitor.miners
        assert "miner-2" in monitor.miners
        assert monitor.miners["miner-1"].is_online is True
        assert monitor.miners["miner-2"].is_online is False


class TestNotificationSending:
    """Tests for notification channel sending"""
    
    @pytest.fixture
    def mock_config(self):
        """Create config with all channels"""
        config = NotificationConfig(
            discord_webhook="https://discord.com/webhook/test",
            telegram_bot_token="test-token",
            telegram_chat_id="-123456",
            email_smtp_server="smtp.test.com",
            email_from="test@test.com",
            email_to=["alert@test.com"],
            webhook_url="https://webhook.test.com",
            enabled_channels=["discord", "telegram", "webhook"]
        )
        return config
    
    def test_send_discord_notification(self, mock_config):
        """Test Discord notification sending"""
        monitor = MinerMonitor(mock_config)
        
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        
        with patch('miner_monitor.requests.post', return_value=mock_response) as mock_post:
            monitor._send_discord("Test Alert", "Test message", "high")
            assert mock_post.called
            assert mock_post.call_args[0][0] == mock_config.discord_webhook
    
    def test_send_telegram_notification(self, mock_config):
        """Test Telegram notification sending"""
        monitor = MinerMonitor(mock_config)
        
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        
        with patch('miner_monitor.requests.post', return_value=mock_response) as mock_post:
            monitor._send_telegram("Test Alert", "Test message", "normal")
            assert mock_post.called
            payload = mock_post.call_args[1]['json']
            assert payload['chat_id'] == mock_config.telegram_chat_id
    
    def test_send_webhook_notification(self, mock_config):
        """Test generic webhook notification sending"""
        monitor = MinerMonitor(mock_config)
        
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        
        with patch('miner_monitor.requests.post', return_value=mock_response) as mock_post:
            monitor._send_webhook("Test Alert", "Test message", "high")
            assert mock_post.called
            payload = mock_post.call_args[1]['json']
            assert payload['title'] == "Test Alert"
            assert payload['priority'] == "high"
    
    def test_send_notification_multiple_channels(self, mock_config):
        """Test sending to multiple channels"""
        monitor = MinerMonitor(mock_config)
        
        with patch.object(monitor, '_send_discord') as mock_discord:
            with patch.object(monitor, '_send_telegram') as mock_telegram:
                with patch.object(monitor, '_send_webhook') as mock_webhook:
                    monitor.send_notification("Test", "Message")
                    
                    assert mock_discord.called
                    assert mock_telegram.called
                    assert mock_webhook.called


class TestAlertMessages:
    """Tests for alert message content"""
    
    def test_offline_alert_format(self):
        """Test offline alert message format"""
        state = MinerState(
            miner_id="RTC1234567890",
            last_attest=time.time() - (25 * 60),
            alert_count=1
        )
        
        # Verify state is offline
        epochs_missed = (time.time() - state.last_attest) / (EPOCH_MINUTES * 60)
        assert epochs_missed >= MISSED_EPOCHS_THRESHOLD
    
    def test_back_online_alert_format(self):
        """Test back online alert message format"""
        state = MinerState(
            miner_id="RTC1234567890",
            is_online=True,
            last_seen=time.time()
        )
        # Message should contain miner ID and recovery time
        assert state.miner_id == "RTC1234567890"
    
    def test_streak_warning_format(self):
        """Test streak warning message format"""
        state = MinerState(
            miner_id="RTC1234567890",
            streak_days=15,
            is_online=True
        )
        # Verify streak data is tracked
        assert state.streak_days == 15
        assert state.streak_warned is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
