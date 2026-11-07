#!/usr/bin/env python3
"""
Bounty #17182: Miner Config Reconcile - Path Normalization
Normalizes and reconciles miner configuration paths across different platforms.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional


def normalize_path(filepath: str) -> str:
    """
    Normalize a file path to a consistent format.
    
    Handles:
    - Windows backslashes -> forward slashes
    - Relative path resolution
    - Double slashes
    - Dot segments (., ..)
    """
    # Convert Windows backslashes to forward slashes
    normalized = filepath.replace("\\", "/")
    
    # Remove duplicate slashes
    normalized = re.sub(r"/+", "/", normalized)
    
    # Resolve the path
    try:
        # Try to resolve as an absolute path
        if not os.path.isabs(normalized):
            # If relative, make it relative to current directory
            normalized = Path.cwd() / normalized
        normalized = str(normalized.resolve())
    except (FileNotFoundError, OSError):
        # If path doesn't exist, just normalize what we can
        normalized = Path(normalized).resolve(as_posix=True)
    
    return normalized


def reconcile_miner_path(
    config_path: str,
    platform: str = "auto",
) -> Dict[str, Any]:
    """
    Reconcile a miner configuration path for the given platform.
    
    Args:
        config_path: The raw path from miner configuration
        platform: Target platform ("windows", "linux", "darwin", or "auto")
    
    Returns:
        Dict with normalized path and platform-specific adjustments
    """
    # Normalize the path first
    normalized = normalize_path(config_path)
    
    # Determine platform if auto
    if platform == "auto":
        platform = "windows" if "\\" in config_path or os.name == "nt" else "linux"
    
    # Platform-specific adjustments
    adjustments = {
        "windows": {
            "drive_letter": "",
            "unc_path": False,
            "separator": "\\",
        },
        "linux": {
            "separator": "/",
            "leading_slash": normalized.startswith("/"),
        },
        "darwin": {
            "separator": "/",
            "leading_slash": normalized.startswith("/"),
        },
    }
    
    platform_config = adjustments.get(platform, adjustments["linux"])
    
    # Extract drive letter for Windows paths
    drive_letter = ""
    if platform == "windows" and len(normalized) > 1 and normalized[1] == ":":
        drive_letter = normalized[0].upper() + ":"
        normalized = normalized[2:]
    
    # Ensure leading slash for POSIX systems
    if platform in ("linux", "darwin") and not normalized.startswith("/") and not drive_letter:
        # Relative path - ensure it's consistent
        pass
    
    return {
        "original_path": config_path,
        "normalized_path": normalized,
        "platform": platform,
        "drive_letter": drive_letter,
        "separator": platform_config["separator"],
        "adjusted": normalized != config_path,
    }


def reconcile_config_file(config_path: str) -> Dict[str, Any]:
    """
    Reconcile an entire miner configuration file.
    
    Reads a JSON config file and normalizes all path values.
    """
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return {"error": str(e)}
    
    paths_reconciled = []
    
    def process_value(key, value):
        """Recursively process config values to find and normalize paths."""
        result = {}
        
        if isinstance(value, str):
            # Check if this looks like a path
            if any(keyword in key.lower() for keyword in 
                   ["path", "dir", "file", "config", "worker", "mine"]):
                normalized = normalize_path(value)
                if normalized != value:
                    result[key] = {
                        "original": value,
                        "normalized": normalized,
                        "changed": True,
                    }
                else:
                    result[key] = {
                        "original": value,
                        "normalized": normalized,
                        "changed": False,
                    }
            else:
                result[key] = value
        
        elif isinstance(value, dict):
            result[key] = {}
            for k, v in value.items():
                sub_result = process_value(k, v)
                result[key].update(sub_result)
        
        elif isinstance(value, list):
            result[key] = []
            for item in value:
                if isinstance(item, dict):
                    processed = {}
                    for k, v in item.items():
                        sub_result = process_value(k, v)
                        processed.update(sub_result)
                    result[key].append(processed)
                else:
                    result[key].append(item)
        
        else:
            result[key] = value
        
        return result
    
    # Process top-level keys
    for key, value in config.items():
        reconciled = process_value(key, value)
        paths_reconciled.append({
            "key": key,
            "reconciled": reconciled,
        })
    
    return {
        "config_path": config_path,
        "platform": platform,
        "paths_reconciled": paths_reconciled,
        "total_modifications": sum(
            1 for pr in paths_reconciled 
            for k, v in pr["reconciled"].items() 
            if isinstance(v, dict) and v.get("changed", False)
        ),
    }


def main():
    """Main entry point for path normalization."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Normalize and reconcile miner configuration paths"
    )
    parser.add_argument("path", help="Path to normalize or config file")
    parser.add_argument(
        "--platform", 
        choices=["windows", "linux", "darwin", "auto"],
        default="auto",
        help="Target platform (default: auto-detect)",
    )
    
    args = parser.parse_args()
    
    # Check if it's a file or a single path
    if os.path.isfile(args.path):
        result = reconcile_config_file(args.path)
    else:
        result = reconcile_miner_path(args.path, args.platform)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()