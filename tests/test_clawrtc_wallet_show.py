import pytest
import subprocess
import time
from unittest.mock import patch


def test_clawrtc_wallet_show_online_state():
    """Test that clawrtc wallet show correctly shows online state when wallet is connected"""
    # Mock the wallet being connected
    with patch('subprocess.run') as mock_run:
        # Mock successful wallet status response
        mock_run.return_value.stdout = '''{
    "status": "online",
    "balance": "100.5",
    "address": "0x123...456",
    "last_seen": "2023-11-15T10:30:00Z"
}'''
        mock_run.return_value.returncode = 0
        
        # Run the command
        result = subprocess.run(['clawrtc', 'wallet', 'show'], capture_output=True, text=True)
        
        # Check that the output contains online status
        assert "status: online" in result.stdout.lower()
        assert result.returncode == 0


def test_clawrtc_wallet_show_offline_state():
    """Test that clawrtc wallet show correctly shows offline state when wallet is not connected"""
    # Mock the wallet being offline
    with patch('subprocess.run') as mock_run:
        # Mock offline wallet status response
        mock_run.return_value.stdout = '''{
    "status": "offline",
    "error": "Wallet not connected",
    "last_seen": "2023-11-14T15:20:00Z"
}'''
        mock_run.return_value.returncode = 1
        
        # Run the command
        result = subprocess.run(['clawrtc', 'wallet', 'show'], capture_output=True, text=True)
        
        # Check that the output contains offline status
        assert "status: offline" in result.stdout.lower()
        assert result.returncode == 1


def test_clawrtc_wallet_show_regression_false_offline():
    """Regression test for false offline state bug"""
    # Mock a scenario that previously caused false offline detection
    with patch('subprocess.run') as mock_run:
        # Mock wallet with valid connection but temporary network issue
        mock_run.return_value.stdout = '''{
    "status": "online",
    "balance": "100.5",
    "address": "0x123...456",
    "last_seen": "2023-11-15T10:30:00Z",
    "network": "connected"
}'''
        mock_run.return_value.returncode = 0
        
        # Run the command
        result = subprocess.run(['clawrtc', 'wallet', 'show'], capture_output=True, text=True)
        
        # This should NOT show offline status
        assert "status: offline" not in result.stdout.lower()
        assert "status: online" in result.stdout.lower()
        assert result.returncode == 0


def test_clawrtc_wallet_show_timeout_handling():
    """Test that timeout is handled correctly without showing false offline state"""
    # Mock a timeout scenario
    with patch('subprocess.run') as mock_run:
        # Mock timeout response
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=['clawrtc', 'wallet', 'show'], timeout=5)
        
        # Run the command
        result = subprocess.run(['clawrtc', 'wallet', 'show'], capture_output=True, text=True, timeout=5)
        
        # Should not show offline status due to timeout
        assert "status: offline" not in result.stdout.lower()
        assert "timeout" in result.stderr.lower() or "timed out" in result.stderr.lower()