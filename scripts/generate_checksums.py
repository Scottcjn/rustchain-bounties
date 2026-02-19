#!/usr/bin/env python3
"""
Generate and verify SHA256 checksums for RustChain artifacts.

Usage:
    python3 scripts/generate_checksums.py --generate
    python3 scripts/generate_checksums.py --verify
"""

import argparse
import hashlib
import os
import sys
from pathlib import Path


def sha256_checksum(file_path: Path) -> str:
    """Generate SHA256 checksum for a file."""
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


def generate_checksums(directory: Path, output_file: Path) -> None:
    """Generate checksums for all files in directory."""
    checksums = []
    
    for file_path in sorted(directory.rglob("*")):
        if file_path.is_file() and not file_path.name.startswith("."):
            checksum = sha256_checksum(file_path)
            relative_path = file_path.relative_to(directory)
            checksums.append(f"{checksum}  {relative_path}")
    
    output_file.write_text("\n".join(checksums) + "\n")
    print(f"Generated checksums for {len(checksums)} files")
    print(f"Checksum file: {output_file}")


def verify_checksums(directory: Path, checksum_file: Path) -> bool:
    """Verify checksums against the checksum file."""
    if not checksum_file.exists():
        print(f"Error: Checksum file not found: {checksum_file}")
        return False
    
    lines = checksum_file.read_text().strip().split("\n")
    all_valid = True
    
    for line in lines:
        if not line.strip():
            continue
        
        parts = line.split(None, 1)
        if len(parts) != 2:
            print(f"Warning: Invalid line format: {line}")
            continue
        
        expected_checksum, relative_path = parts
        file_path = directory / relative_path
        
        if not file_path.exists():
            print(f"MISSING: {relative_path}")
            all_valid = False
            continue
        
        actual_checksum = sha256_checksum(file_path)
        
        if actual_checksum == expected_checksum:
            print(f"OK: {relative_path}")
        else:
            print(f"FAIL: {relative_path}")
            print(f"  Expected: {expected_checksum}")
            print(f"  Actual:   {actual_checksum}")
            all_valid = False
    
    return all_valid


def main():
    parser = argparse.ArgumentParser(description="SHA256 checksum generator/verifier")
    parser.add_argument("--directory", "-d", default=".", help="Directory to process")
    parser.add_argument("--generate", "-g", action="store_true", help="Generate checksums")
    parser.add_argument("--verify", "-v", action="store_true", help="Verify checksums")
    parser.add_argument("--output", "-o", default="CHECKSUMS.txt", help="Output file")
    
    args = parser.parse_args()
    
    directory = Path(args.directory)
    output_file = Path(args.output)
    
    if args.generate:
        generate_checksums(directory, output_file)
    elif args.verify:
        success = verify_checksums(directory, output_file)
        if success:
            print("\n✓ All checksums verified!")
            sys.exit(0)
        else:
            print("\n✗ Checksum verification failed!")
            sys.exit(1)
    else:
        print("Specify --generate or --verify")
        sys.exit(1)


if __name__ == "__main__":
    main()
