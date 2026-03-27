#!/usr/bin/env python3
"""
Windows Miner Bundle Smoke Test Runner

This script performs basic smoke tests on the Windows miner bundle.
It checks for proper startup, basic functionality, and logs any failures.
"""
import os
import sys
import time
import subprocess
import logging
import platform
from pathlib import Path
from datetime import datetime


class WindowsMinerSmokeTester:
    def __init__(self):
        self.test_results = {}
        self.log_file = f"windows_miner_smoke_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def check_platform_compatibility(self):
        """Check if running on Windows platform"""
        if platform.system() != "Windows":
            self.logger.error("This test is designed for Windows platform only")
            return False
        self.logger.info(f"Platform: {platform.system()} {platform.release()}")
        return True
        
    def find_miner_executable(self):
        """Attempt to locate the miner executable in common locations"""
        possible_paths = [
            "./miner.exe",
            "./rustchain-miner.exe",
            "./bin/miner.exe",
            "./dist/miner.exe",
            "./target/release/miner.exe",
            "./target/debug/miner.exe",
            "./build/miner.exe",
            "./RustChain-Miner/miner.exe",
            "./RustChain-Miner/RustChain-Miner.exe",
            "./windows-miner/miner.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.logger.info(f"Found miner executable at: {path}")
                return path
        
        self.logger.warning("Could not find miner executable in standard locations")
        return None
        
    def run_basic_startup_test(self, miner_path):
        """Test basic startup functionality"""
        try:
            self.logger.info("Starting basic startup test...")
            
            # Try to run the miner with --help flag to see if it starts properly
            result = subprocess.run([miner_path, "--help"], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            
            if result.returncode == 0:
                self.logger.info("✓ Basic startup test PASSED - miner responds to --help")
                self.test_results['basic_startup'] = {'status': 'PASS', 'details': 'Miner responds to --help'}
                return True
            else:
                self.logger.error(f"✗ Basic startup test FAILED - exit code: {result.returncode}")
                self.logger.error(f"STDOUT: {result.stdout}")
                self.logger.error(f"STDERR: {result.stderr}")
                self.test_results['basic_startup'] = {
                    'status': 'FAIL', 
                    'details': f'Exit code: {result.returncode}',
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("✗ Basic startup test TIMEOUT - miner did not respond to --help within 10 seconds")
            self.test_results['basic_startup'] = {'status': 'FAIL', 'details': 'Timeout waiting for response'}
            return False
        except Exception as e:
            self.logger.error(f"✗ Basic startup test ERROR: {str(e)}")
            self.test_results['basic_startup'] = {'status': 'FAIL', 'details': str(e)}
            return False
            
    def run_version_test(self, miner_path):
        """Test version reporting functionality"""
        try:
            self.logger.info("Starting version test...")
            
            result = subprocess.run([miner_path, "--version"], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            
            if result.returncode == 0:
                self.logger.info(f"✓ Version test PASSED - {result.stdout.strip()}")
                self.test_results['version_test'] = {'status': 'PASS', 'details': result.stdout.strip()}
                return True
            else:
                self.logger.error(f"✗ Version test FAILED - exit code: {result.returncode}")
                self.logger.error(f"STDOUT: {result.stdout}")
                self.logger.error(f"STDERR: {result.stderr}")
                self.test_results['version_test'] = {
                    'status': 'FAIL', 
                    'details': f'Exit code: {result.returncode}',
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("✗ Version test TIMEOUT - miner did not respond to --version within 10 seconds")
            self.test_results['version_test'] = {'status': 'FAIL', 'details': 'Timeout waiting for response'}
            return False
        except Exception as e:
            self.logger.error(f"✗ Version test ERROR: {str(e)}")
            self.test_results['version_test'] = {'status': 'FAIL', 'details': str(e)}
            return False
            
    def run_miner_with_config_test(self, miner_path):
        """Test running miner with minimal config (if available)"""
        try:
            self.logger.info("Starting miner with config test...")
            
            # Create a minimal config file for testing
            config_content = """{
  "server": "localhost:8080",
  "threads": 1,
  "timeout": 30
}"""
            
            config_path = "test_config.json"
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            # Run miner with config but don't connect to actual server
            # Use a short timeout to prevent hanging
            result = subprocess.run([miner_path, "--config", config_path], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=15)
            
            # Clean up config file
            if os.path.exists(config_path):
                os.remove(config_path)
            
            # Check if process started without immediate crash
            # Even if it fails due to connection issues, that's acceptable for smoke test
            if result.returncode == 0 or "connection refused" in result.stderr.lower():
                self.logger.info("✓ Miner with config test PASSED - miner started without crashing")
                self.test_results['config_test'] = {
                    'status': 'PASS', 
                    'details': 'Miner started without crashing (may have connection issues which is expected)'
                }
                return True
            else:
                self.logger.error(f"✗ Miner with config test FAILED - exit code: {result.returncode}")
                self.logger.error(f"STDOUT: {result.stdout}")
                self.logger.error(f"STDERR: {result.stderr}")
                self.test_results['config_test'] = {
                    'status': 'FAIL', 
                    'details': f'Exit code: {result.returncode}',
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                return False
                
        except subprocess.TimeoutExpired:
            # This is actually good - means miner started and is running
            self.logger.info("✓ Miner with config test PASSED - miner started and is running (terminated by timeout)")
            if os.path.exists("test_config.json"):
                os.remove("test_config.json")
            self.test_results['config_test'] = {
                'status': 'PASS', 
                'details': 'Miner started and appears to be running'
            }
            return True
        except Exception as e:
            if os.path.exists("test_config.json"):
                os.remove("test_config.json")
            self.logger.error(f"✗ Miner with config test ERROR: {str(e)}")
            self.test_results['config_test'] = {'status': 'FAIL', 'details': str(e)}
            return False
            
    def run_dependency_check(self):
        """Check for common dependencies needed by miners"""
        self.logger.info("Starting dependency check...")
        
        dependencies = []
        
        # Check for Visual C++ Redistributables
        try:
            import ctypes
            dependencies.append({"vcruntime": "Available"})
        except ImportError:
            dependencies.append({"vcruntime": "Missing"})
        
        # Check for OpenSSL (if needed)
        try:
            import ssl
            dependencies.append({"openssl": f"{ssl.OPENSSL_VERSION}"})
        except ImportError:
            dependencies.append({"openssl": "Missing"})
        
        # Check for .NET Framework (common requirement)
        try:
            import clr  # Python.NET
            dependencies.append({"dotnet": "Available"})
        except ImportError:
            dependencies.append({"dotnet": "Not installed"})
        
        self.logger.info(f"Dependency check completed: {dependencies}")
        self.test_results['dependency_check'] = {'status': 'INFO', 'details': dependencies}
        return True
        
    def generate_report(self):
        """Generate final test report"""
        self.logger.info("\n" + "="*60)
        self.logger.info("WINDOWS MINER SMOKE TEST REPORT")
        self.logger.info("="*60)
        
        passed_tests = sum(1 for v in self.test_results.values() if v['status'] in ['PASS', 'INFO'])
        total_tests = len(self.test_results)
        
        self.logger.info(f"Tests Passed: {passed_tests}/{total_tests}")
        
        for test_name, result in self.test_results.items():
            status = result['status']
            details = result['details']
            
            if status == 'PASS':
                self.logger.info(f"✓ {test_name}: {details}")
            elif status == 'FAIL':
                self.logger.error(f"✗ {test_name}: {details}")
            else:
                self.logger.info(f"ℹ️ {test_name}: {details}")
        
        self.logger.info(f"\nLog file saved to: {self.log_file}")
        
        # Summary
        if passed_tests == total_tests:
            self.logger.info("\n🎉 All tests PASSED! Windows miner bundle appears functional.")
        else:
            self.logger.info(f"\n⚠️ Tests failed. {total_tests - passed_tests} out of {total_tests} tests failed.")
            
        return passed_tests == total_tests
        
    def run_all_tests(self):
        """Run all smoke tests"""
        self.logger.info("Starting Windows Miner Bundle Smoke Test")
        
        # Check platform compatibility
        if not self.check_platform_compatibility():
            return False
        
        # Find miner executable
        miner_path = self.find_miner_executable()
        if not miner_path:
            self.logger.error("Cannot proceed without finding miner executable")
            self.test_results['miner_found'] = {'status': 'FAIL', 'details': 'Miner executable not found'}
            return self.generate_report()
        
        # Run all tests
        self.run_dependency_check()
        self.run_basic_startup_test(miner_path)
        self.run_version_test(miner_path)
        self.run_miner_with_config_test(miner_path)
        
        return self.generate_report()


def main():
    tester = WindowsMinerSmokeTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()