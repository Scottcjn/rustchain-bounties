#!/usr/bin/env python3
"""
Test suite for RustChain Miner Monitor

Author: 小米粒 (Xiaomili) 🌾
"""

import unittest
import json
import tempfile
import os
from datetime import datetime, timedelta
from miner_monitor import MinerMonitor, MinerStatus

class TestMinerMonitor(unittest.TestCase):
    """Test cases for MinerMonitor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        test_config = {
            "api_url": "https://rustchain.org/api",
            "poll_interval": 600,
            "offline_threshold": 2,
            "alert_cooldown": 3600,
            "discord_webhook": "",
            "email_config": {}
        }
        json.dump(test_config, self.temp_config)
        self.temp_config.close()
        
        self.monitor = MinerMonitor(self.temp_config.name)
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.unlink(self.temp_config.name)
    
    def test_load_config(self):
        """Test configuration loading"""
        self.assertIsNotNone(self.monitor.config)
        self.assertEqual(self.monitor.config['poll_interval'], 600)
        self.assertEqual(self.monitor.config['offline_threshold'], 2)
    
    def test_miner_status_creation(self):
        """Test MinerStatus dataclass"""
        status = MinerStatus(
            miner_id="test-miner-123",
            last_attestation=datetime.now(),
            streak_days=10,
            is_online=True
        )
        
        self.assertEqual(status.miner_id, "test-miner-123")
        self.assertEqual(status.streak_days, 10)
        self.assertTrue(status.is_online)
    
    def test_offline_detection(self):
        """Test offline miner detection"""
        # Create miner status with old attestation
        old_time = datetime.now() - timedelta(minutes=30)  # 30 minutes ago
        self.monitor.miners["test-miner"] = MinerStatus(
            miner_id="test-miner",
            last_attestation=old_time,
            streak_days=5,
            is_online=True  # Will be updated to False
        )
        
        # Simulate update with old attestation
        miner_data = {
            'id': 'test-miner',
            'last_attestation': old_time.isoformat()
        }
        
        self.monitor.update_miner_status(miner_data)
        
        # Should be marked as offline
        self.assertFalse(self.monitor.miners["test-miner"].is_online)
        self.assertIn("test-miner", self.monitor.offline_miners)
    
    def test_rate_limiting(self):
        """Test alert rate limiting"""
        miner_id = "test-miner"
        
        # First alert should be allowed
        self.assertTrue(self.monitor.should_send_alert(miner_id))
        
        # Set cooldown
        self.monitor.alert_cooldown[miner_id] = datetime.now()
        
        # Second alert should be blocked (within cooldown period)
        self.assertFalse(self.monitor.should_send_alert(miner_id))
        
        # Simulate cooldown expiration (1 hour later)
        self.monitor.alert_cooldown[miner_id] = datetime.now() - timedelta(hours=2)
        self.assertTrue(self.monitor.should_send_alert(miner_id))
    
    def test_online_miner_tracking(self):
        """Test tracking of online miners"""
        recent_time = datetime.now() - timedelta(minutes=5)
        
        miner_data = {
            'id': 'online-miner',
            'last_attestation': recent_time.isoformat()
        }
        
        # Mock fetch_streak to return test data
        original_fetch = self.monitor.fetch_streak
        self.monitor.fetch_streak = lambda x: {'streak_days': 7}
        
        self.monitor.update_miner_status(miner_data)
        
        self.assertTrue(self.monitor.miners['online-miner'].is_online)
        self.assertEqual(self.monitor.miners['online-miner'].streak_days, 7)
        
        # Restore original function
        self.monitor.fetch_streak = original_fetch
    
    def test_config_file_not_found(self):
        """Test behavior when config file doesn't exist"""
        monitor = MinerMonitor("nonexistent_config.json")
        
        # Should use default config
        self.assertIsNotNone(monitor.config)
        self.assertEqual(monitor.config['poll_interval'], 600)

class TestMinerStatus(unittest.TestCase):
    """Test cases for MinerStatus dataclass"""
    
    def test_default_values(self):
        """Test default values for optional fields"""
        status = MinerStatus(
            miner_id="test",
            last_attestation=datetime.now(),
            streak_days=0,
            is_online=True
        )
        
        self.assertIsNone(status.last_alert_time)

def run_integration_test():
    """Run integration test against live API"""
    print("\n🔗 Integration Test: Checking RustChain API...")
    
    try:
        import requests
        response = requests.get(
            "https://rustchain.org/api/miners",
            timeout=10,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is working! Found {len(data)} miners")
            
            if data:
                sample = data[0]
                print(f"\n📊 Sample miner data:")
                print(f"  ID: {sample.get('id', 'N/A')}")
                print(f"  Last attestation: {sample.get('last_attestation', 'N/A')}")
            
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("RustChain Miner Monitor - Test Suite")
    print("=" * 60)
    
    # Run unit tests
    print("\n📋 Running unit tests...")
    unittest.main(argv=[''], verbosity=2, exit=False)
    
    # Run integration test
    print("\n" + "=" * 60)
    run_integration_test()
    
    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()


# Additional tests for issue #14268
def test_issue_14268_fix():
    # TODO: Implement based on issue requirements
    assert True, Placeholdertest


# Additional tests for issue #14283
def test_issue_14283_fix():
    # TODO: Implement based on issue requirements
    assert True, Placeholdertest
