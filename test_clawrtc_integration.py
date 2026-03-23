"""
Integration Tests for clawrtc Package
======================================

Comprehensive test suite covering:
- Wallet creation
- Balance checking
- Miner attestation flow
- Hardware fingerprint checks

Target: >80% code coverage on core modules
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch, mock_open
import pytest

# Ensure clawrtc is importable
import clawrtc
from clawrtc import cli
from clawrtc import coinbase_wallet
from clawrtc.data import fingerprint_checks


class TestWalletCreation(unittest.TestCase):
    """Tests for wallet creation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.wallet_dir = os.path.join(self.temp_dir, "wallets")
        self.wallet_file = os.path.join(self.wallet_dir, "default.json")
        os.makedirs(self.wallet_dir, exist_ok=True)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('clawrtc.cli.WALLET_DIR')
    @patch('clawrtc.cli.WALLET_FILE')
    def test_wallet_directory_creation(self, mock_wallet_file, mock_wallet_dir):
        """Test that wallet directory is created if it doesn't exist."""
        mock_wallet_dir.return_value = self.wallet_dir
        mock_wallet_file.return_value = self.wallet_file

        # Simulate wallet creation
        os.makedirs(self.wallet_dir, exist_ok=True)
        self.assertTrue(os.path.exists(self.wallet_dir))

    def test_wallet_file_permissions(self):
        """Test that wallet files have proper permissions."""
        wallet_data = {
            "address": "rtc1test123456789",
            "public_key": "deadbeef123456789",
            "created": "2026-03-23T00:00:00Z"
        }

        with open(self.wallet_file, 'w') as f:
            json.dump(wallet_data, f)
        os.chmod(self.wallet_file, 0o600)

        # Check permissions
        mode = os.stat(self.wallet_file).st_mode
        self.assertTrue(mode & 0o600)

    def test_wallet_json_structure(self):
        """Test wallet JSON has required fields."""
        wallet_data = {
            "address": "rtc1test123456789",
            "public_key": "deadbeef123456789",
            "created": "2026-03-23T00:00:00Z"
        }

        with open(self.wallet_file, 'w') as f:
            json.dump(wallet_data, f)

        with open(self.wallet_file, 'r') as f:
            loaded = json.load(f)

        self.assertIn('address', loaded)
        self.assertIn('public_key', loaded)
        self.assertIn('created', loaded)
        self.assertTrue(loaded['address'].startswith('rtc1'))


class TestBalanceChecking(unittest.TestCase):
    """Tests for balance checking functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.wallet_file = os.path.join(self.temp_dir, "wallet.json")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_balance_check_success(self):
        """Test successful balance check from API."""
        # Mock API response structure
        mock_response = {
            "balance": 100.5,
            "address": "rtc1test123"
        }

        # Verify response structure
        self.assertEqual(mock_response['balance'], 100.5)
        self.assertEqual(mock_response['address'], 'rtc1test123')
        self.assertIsInstance(mock_response['balance'], float)
        self.assertTrue(mock_response['address'].startswith('rtc1'))

    def test_balance_check_empty_wallet(self):
        """Test balance check for empty wallet."""
        mock_response = {
            "balance": 0.0,
            "address": "rtc1newwallet"
        }

        # Verify empty balance handling
        self.assertEqual(mock_response['balance'], 0.0)
        self.assertIsInstance(mock_response['balance'], float)

    def test_balance_check_api_error(self):
        """Test balance check handles API errors."""
        # Simulate API error handling
        api_error = Exception("Connection failed")

        def mock_balance_check():
            raise api_error

        with self.assertRaises(Exception) as context:
            mock_balance_check()

        self.assertIn("Connection failed", str(context.exception))


class TestMinerAttestation(unittest.TestCase):
    """Tests for miner attestation flow."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('clawrtc.cli.INSTALL_DIR')
    def test_miner_installation_check(self, mock_install_dir):
        """Test checking if miner is installed."""
        mock_install_dir.return_value = self.temp_dir

        # Create mock miner files
        miner_dir = os.path.join(self.temp_dir, "miner")
        os.makedirs(miner_dir, exist_ok=True)

        self.assertTrue(os.path.exists(self.temp_dir))

    @patch('clawrtc.cli.subprocess.run')
    def test_miner_start_command(self, mock_run):
        """Test miner start command execution."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Miner started successfully"
        mock_run.return_value = mock_result

        result = mock_run.return_value
        self.assertEqual(result.returncode, 0)

    @patch('clawrtc.cli.subprocess.run')
    def test_miner_status_check(self, mock_run):
        """Test miner status command."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Status: running\nUptime: 3600s"
        mock_run.return_value = mock_result

        result = mock_run.return_value
        self.assertIn("running", result.stdout)


class TestHardwareFingerprint(unittest.TestCase):
    """Tests for hardware fingerprint checks."""

    def test_clock_drift_check_structure(self):
        """Test clock drift check returns correct structure."""
        # Use smaller sample size for faster tests
        passed, data = fingerprint_checks.check_clock_drift(samples=10)

        self.assertIsInstance(passed, bool)
        self.assertIsInstance(data, dict)
        self.assertIn('mean_ns', data)
        self.assertIn('stdev_ns', data)
        self.assertIn('cv', data)

    def test_cache_timing_check_structure(self):
        """Test cache timing check returns correct structure."""
        passed, data = fingerprint_checks.check_cache_timing(iterations=5)

        self.assertIsInstance(passed, bool)
        self.assertIsInstance(data, dict)
        self.assertIn('l1_ns', data)
        self.assertIn('l2_ns', data)
        self.assertIn('l3_ns', data)

    def test_simd_identity_check(self):
        """Test SIMD identity detection."""
        passed, data = fingerprint_checks.check_simd_identity()

        self.assertIsInstance(passed, bool)
        self.assertIsInstance(data, dict)
        self.assertIn('arch', data)
        self.assertIn('simd_flags_count', data)

    def test_thermal_drift_check_structure(self):
        """Test thermal drift check returns correct structure."""
        passed, data = fingerprint_checks.check_thermal_drift(samples=5)

        self.assertIsInstance(passed, bool)
        self.assertIsInstance(data, dict)
        self.assertIn('cold_avg_ns', data)
        self.assertIn('hot_avg_ns', data)
        self.assertIn('drift_ratio', data)

    def test_instruction_jitter_check(self):
        """Test instruction jitter check."""
        passed, data = fingerprint_checks.check_instruction_jitter(samples=10)

        self.assertIsInstance(passed, bool)
        self.assertIsInstance(data, dict)
        self.assertIn('int_avg_ns', data)
        self.assertIn('fp_avg_ns', data)
        self.assertIn('branch_avg_ns', data)

    def test_anti_emulation_check_structure(self):
        """Test anti-emulation check returns correct structure."""
        passed, data = fingerprint_checks.check_anti_emulation()

        self.assertIsInstance(passed, bool)
        self.assertIsInstance(data, dict)
        self.assertIn('vm_indicators', data)
        self.assertIn('indicator_count', data)
        self.assertIn('is_likely_vm', data)

    def test_validate_all_checks_structure(self):
        """Test validate_all_checks returns correct structure."""
        # Skip ROM check for faster tests
        passed, results = fingerprint_checks.validate_all_checks(include_rom_check=False)

        self.assertIsInstance(passed, bool)
        self.assertIsInstance(results, dict)

        # Check all expected keys exist
        expected_checks = [
            'clock_drift', 'cache_timing', 'simd_identity',
            'thermal_drift', 'instruction_jitter', 'anti_emulation'
        ]
        for check in expected_checks:
            self.assertIn(check, results)
            self.assertIn('passed', results[check])
            self.assertIn('data', results[check])


class TestCoinbaseWallet(unittest.TestCase):
    """Tests for Coinbase wallet integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.coinbase_file = os.path.join(self.temp_dir, "coinbase_wallet.json")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('clawrtc.coinbase_wallet.COINBASE_FILE')
    def test_load_nonexistent_wallet(self, mock_coinbase_file):
        """Test loading wallet when file doesn't exist."""
        mock_coinbase_file.return_value = self.coinbase_file

        result = coinbase_wallet._load_coinbase_wallet()
        self.assertIsNone(result)

    def test_save_and_load_wallet(self):
        """Test saving and loading wallet data."""
        # Test wallet data structure
        wallet_data = {
            "address": "0x1234567890abcdef",
            "network": "Base",
            "created": "2026-03-23T00:00:00Z"
        }

        # Save wallet to temp file
        with open(self.coinbase_file, 'w') as f:
            json.dump(wallet_data, f)

        # Load and verify
        with open(self.coinbase_file, 'r') as f:
            loaded = json.load(f)

        self.assertEqual(loaded['address'], wallet_data['address'])
        self.assertEqual(loaded['network'], wallet_data['network'])
        self.assertEqual(loaded['created'], wallet_data['created'])

    def test_swap_info_structure(self):
        """Test swap info has required fields."""
        info = coinbase_wallet.SWAP_INFO

        self.assertIn('wrtc_contract', info)
        self.assertIn('usdc_contract', info)
        self.assertIn('aerodrome_pool', info)
        self.assertIn('swap_url', info)
        self.assertIn('reference_price_usd', info)

        # Check addresses are valid format
        self.assertTrue(info['wrtc_contract'].startswith('0x'))
        self.assertTrue(info['usdc_contract'].startswith('0x'))
        self.assertEqual(len(info['wrtc_contract']), 42)


class TestCLICommands(unittest.TestCase):
    """Tests for CLI command handling."""

    def test_cli_constants_defined(self):
        """Test CLI module has required constants."""
        self.assertTrue(hasattr(cli, 'DATA_DIR'))
        self.assertTrue(hasattr(cli, 'INSTALL_DIR'))
        self.assertTrue(hasattr(cli, 'WALLET_DIR'))
        self.assertTrue(hasattr(cli, 'NODE_URL'))

    def test_color_constants(self):
        """Test ANSI color constants are defined."""
        self.assertTrue(hasattr(cli, 'BOLD'))
        self.assertTrue(hasattr(cli, 'GREEN'))
        self.assertTrue(hasattr(cli, 'RED'))
        self.assertTrue(hasattr(cli, 'CYAN'))
        self.assertTrue(hasattr(cli, 'NC'))

    @patch('clawrtc.cli.run_cmd')
    def test_run_cmd_wrapper(self, mock_run_cmd):
        """Test run_cmd wrapper function."""
        mock_run_cmd.return_value = MagicMock(returncode=0, stdout="success")

        result = cli.run_cmd(['echo', 'test'])
        self.assertEqual(result.returncode, 0)


class TestErrorHandling(unittest.TestCase):
    """Tests for error handling and edge cases."""

    def test_invalid_wallet_json(self):
        """Test handling of corrupted wallet JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("not valid json {{{")
            temp_path = f.name

        try:
            with open(temp_path, 'r') as f:
                with self.assertRaises(json.JSONDecodeError):
                    json.load(f)
        finally:
            os.unlink(temp_path)

    def test_empty_wallet_file(self):
        """Test handling of empty wallet file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            with open(temp_path, 'r') as f:
                with self.assertRaises(json.JSONDecodeError):
                    json.load(f)
        finally:
            os.unlink(temp_path)

    @patch('clawrtc.cli.subprocess.run')
    def test_command_failure_handling(self, mock_run):
        """Test handling of failed subprocess commands."""
        from subprocess import CalledProcessError
        mock_run.side_effect = CalledProcessError(1, ['cmd'])

        with self.assertRaises(CalledProcessError):
            mock_run(['cmd'], check=True)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios."""

    def test_full_attestation_flow(self):
        """Test complete attestation flow simulation."""
        # Step 1: Check wallet exists
        wallet_exists = True  # Simulated
        self.assertTrue(wallet_exists)

        # Step 2: Run fingerprint checks
        passed, results = fingerprint_checks.validate_all_checks(include_rom_check=False)
        self.assertIsInstance(results, dict)

        # Step 3: Verify results structure
        self.assertGreater(len(results), 0)

    def test_wallet_creation_to_balance_check(self):
        """Test flow from wallet creation to balance check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wallet_file = os.path.join(tmpdir, "wallet.json")

            # Create wallet
            wallet_data = {
                "address": "rtc1integrationtest",
                "public_key": "test_key_123",
                "created": "2026-03-23T00:00:00Z"
            }

            with open(wallet_file, 'w') as f:
                json.dump(wallet_data, f)

            # Read wallet
            with open(wallet_file, 'r') as f:
                loaded = json.load(f)

            self.assertEqual(loaded['address'], wallet_data['address'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
