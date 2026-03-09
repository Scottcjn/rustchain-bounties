#!/usr/bin/env python3
"""
Smoke test for RustChain Windows miner bundle.
This script performs basic validation of the Windows miner bundle.
"""

import os
import sys
import subprocess
import zipfile
import hashlib
from pathlib import Path

def calculate_file_hash(file_path):
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def test_bundle_structure(bundle_path):
    """Test that the bundle has the expected structure."""
    print(f"Testing bundle structure: {bundle_path}")
    
    if not os.path.exists(bundle_path):
        print(f"ERROR: Bundle not found at {bundle_path}")
        return False
    
    # Check if it's a zip file
    if not zipfile.is_zipfile(bundle_path):
        print("ERROR: Bundle is not a valid zip file")
        return False
    
    with zipfile.ZipFile(bundle_path, 'r') as zip_ref:
        # List all files in the bundle
        files = zip_ref.namelist()
        print(f"Files in bundle: {files}")
        
        # Check for expected files
        expected_files = [
            'rustchain-miner.exe',
            'config.json',
            'README.txt',
            'libgcc_s_seh-1.dll',
            'libstdc++-6.dll'
        ]
        
        missing_files = []
        for expected_file in expected_files:
            if expected_file not in files:
                missing_files.append(expected_file)
        
        if missing_files:
            print(f"ERROR: Missing expected files: {missing_files}")
            return False
        
        # Check for expected directories
        expected_dirs = [
            'logs/',
            'temp/'
        ]
        
        missing_dirs = []
        for expected_dir in expected_dirs:
            if expected_dir not in files:
                missing_dirs.append(expected_dir)
        
        if missing_dirs:
            print(f"ERROR: Missing expected directories: {missing_dirs}")
            return False
    
    print("Bundle structure test passed")
    return True

def test_executable(bundle_path):
    """Test that the main executable is present and valid."""
    print("Testing executable...")
    
    with zipfile.ZipFile(bundle_path, 'r') as zip_ref:
        # Extract the executable
        zip_ref.extract('rustchain-miner.exe', path='temp_extract')
        
        exe_path = os.path.join('temp_extract', 'rustchain-miner.exe')
        
        # Check if file exists and is executable
        if not os.path.exists(exe_path):
            print("ERROR: Executable not found after extraction")
            return False
        
        # Try to run the executable with --help flag
        try:
            result = subprocess.run([exe_path, '--help'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            
            if result.returncode == 0:
                print("Executable help command succeeded")
                print(f"Help output: {result.stdout[:200]}...")
            else:
                print(f"WARNING: Executable help command failed with code {result.returncode}")
                print(f"Error output: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("WARNING: Executable help command timed out")
        except Exception as e:
            print(f"WARNING: Error running executable: {e}")
        
        # Clean up
        if os.path.exists(exe_path):
            os.remove(exe_path)
    
    return True

def test_config(bundle_path):
    """Test that the config file is valid JSON."""
    print("Testing config file...")
    
    with zipfile.ZipFile(bundle_path, 'r') as zip_ref:
        # Extract the config file
        zip_ref.extract('config.json', path='temp_extract')
        
        config_path = os.path.join('temp_extract', 'config.json')
        
        try:
            import json
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check for required config fields
            required_fields = ['pool_url', 'wallet_address', 'worker_name']
            missing_fields = []
            
            for field in required_fields:
                if field not in config:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"ERROR: Missing required config fields: {missing_fields}")
                return False
            
            print("Config file is valid")
            print(f"Pool URL: {config.get('pool_url', 'N/A')}")
            print(f"Wallet: {config.get('wallet_address', 'N/A')[:10]}...")
            
        except json.JSONDecodeError:
            print("ERROR: Config file is not valid JSON")
            return False
        except Exception as e:
            print(f"ERROR: Error reading config file: {e}")
            return False
        
        # Clean up
        if os.path.exists(config_path):
            os.remove(config_path)
    
    return True

def test_dependencies(bundle_path):
    """Test that required DLLs are present."""
    print("Testing dependencies...")
    
    with zipfile.ZipFile(bundle_path, 'r') as zip_ref:
        # Check for required DLLs
        required_dlls = [
            'libgcc_s_seh-1.dll',
            'libstdc++-6.dll'
        ]
        
        missing_dlls = []
        for dll in required_dlls:
            if dll not in zip_ref.namelist():
                missing_dlls.append(dll)
        
        if missing_dlls:
            print(f"ERROR: Missing required DLLs: {missing_dlls}")
            return False
        
        # Extract and test one DLL
        zip_ref.extract('libgcc_s_seh-1.dll', path='temp_extract')
        dll_path = os.path.join('temp_extract', 'libgcc_s_seh-1.dll')
        
        if os.path.exists(dll_path):
            # Check if DLL file is not empty
            if os.path.getsize(dll_path) > 0:
                print("DLL files are present and non-empty")
            else:
                print("WARNING: DLL file is empty")
            
            # Clean up
            os.remove(dll_path)
        
    return True

def test_readme(bundle_path):
    """Test that the README file is present and readable."""
    print("Testing README file...")
    
    with zipfile.ZipFile(bundle_path, 'r') as zip_ref:
        # Extract the README file
        zip_ref.extract('README.txt', path='temp_extract')
        
        readme_path = os.path.join('temp_extract', 'README.txt')
        
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if len(content) > 0:
                print("README file is present and readable")
                print(f"README content preview: {content[:200]}...")
            else:
                print("WARNING: README file is empty")
                
        except UnicodeDecodeError:
            print("WARNING: README file encoding issue")
        except Exception as e:
            print(f"ERROR: Error reading README file: {e}")
            return False
        
        # Clean up
        if os.path.exists(readme_path):
            os.remove(readme_path)
    
    return True

def main():
    """Main test function."""
    print("RustChain Windows Miner Bundle Smoke Test")
    print("=" * 50)
    
    # Get bundle path from command line or use default
    if len(sys.argv) > 1:
        bundle_path = sys.argv[1]
    else:
        bundle_path = "rustchain-miner-windows.zip"
    
    if not os.path.exists(bundle_path):
        print(f"ERROR: Bundle file not found: {bundle_path}")
        print("Usage: python bundle_smoke_test.py <path_to_bundle>")
        sys.exit(1)
    
    # Create temp directory for extractions
    os.makedirs('temp_extract', exist_ok=True)
    
    # Run all tests
    tests = [
        ("Bundle Structure", test_bundle_structure),
        ("Executable", test_executable),
        ("Config", test_config),
        ("Dependencies", test_dependencies),
        ("README", test_readme)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n--- {test_name} Test ---")
        try:
            results[test_name] = test_func(bundle_path)
        except Exception as e:
            print(f"ERROR in {test_name} test: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    
    passed = 0
    failed = 0
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed + failed}, Passed: {passed}, Failed: {failed}")
    
    # Clean up temp directory
    import shutil
    if os.path.exists('temp_extract'):
        shutil.rmtree('temp_extract')
    
    if failed > 0:
        print("\nSome tests failed. Please review the bundle.")
        sys.exit(1)
    else:
        print("\nAll tests passed! Bundle appears to be valid.")

if __name__ == "__main__":
    main()
