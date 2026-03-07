#!/usr/bin/env python3
"""
RustChain Health Check CLI Tool
Queries all 3 attestation nodes and displays health status.
Bounty #1111 - 8 RTC
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Optional

# Attestation node endpoints
NODES = [
    {"name": "Node Alpha", "ip": "50.28.86.131", "port": 8099},
    {"name": "Node Beta", "ip": "50.28.86.153", "port": 8099},
    {"name": "Node Gamma", "ip": "76.8.228.245", "port": 8099},
]

# ANSI color codes for terminal output
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "green": "\033[32m",
    "red": "\033[31m",
    "yellow": "\033[33m",
    "cyan": "\033[36m",
    "gray": "\033[90m",
}


def colorize(text: str, color: str) -> str:
    """Apply color to text."""
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"


def format_uptime(seconds: float) -> str:
    """Format uptime in human-readable form."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    elif seconds < 86400:
        return f"{seconds/3600:.1f}h"
    else:
        return f"{seconds/86400:.1f}d"


def format_tip_age(seconds: float) -> str:
    """Format tip age with color coding."""
    if seconds < 60:
        return colorize(f"{seconds:.0f}s", "green")
    elif seconds < 300:
        return colorize(f"{seconds:.0f}s", "yellow")
    else:
        return colorize(f"{seconds:.0f}s ({seconds/60:.1f}m)", "red")


def format_db_rw(db_rw) -> str:
    """Format database read/write status."""
    # Handle boolean from API
    if isinstance(db_rw, bool):
        db_rw = "readwrite" if db_rw else "readonly"
    
    if db_rw == "readwrite":
        return colorize("✓ readwrite", "green")
    elif db_rw == "readonly":
        return colorize("⚠ readonly", "yellow")
    else:
        return colorize(f"✗ {db_rw}", "red")


def query_node(node: Dict) -> Optional[Dict]:
    """Query a single node for health information."""
    url = f"http://{node['ip']}:{node['port']}/health"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            "name": node["name"],
            "ip": node["ip"],
            "port": node["port"],
            "status": "online",
            "version": data.get("version", "unknown"),
            "uptime": data.get("uptime_s", 0),
            "db_rw": data.get("db_rw", "unknown"),
            "tip_age": data.get("tip_age_slots", 0),
            "backup_age": data.get("backup_age_hours"),
            "raw": data,
        }
    except requests.exceptions.Timeout:
        return {
            "name": node["name"],
            "ip": node["ip"],
            "port": node["port"],
            "status": "timeout",
            "error": "Connection timed out after 10s",
        }
    except requests.exceptions.ConnectionError:
        return {
            "name": node["name"],
            "ip": node["ip"],
            "port": node["port"],
            "status": "offline",
            "error": "Connection refused",
        }
    except requests.exceptions.HTTPError as e:
        return {
            "name": node["name"],
            "ip": node["ip"],
            "port": node["port"],
            "status": "error",
            "error": f"HTTP {e.response.status_code}",
        }
    except Exception as e:
        return {
            "name": node["name"],
            "ip": node["ip"],
            "port": node["port"],
            "status": "error",
            "error": str(e),
        }


def print_header():
    """Print CLI header."""
    print()
    print(colorize("╔══════════════════════════════════════════════════════════════╗", "cyan"))
    print(colorize("║           🦀 RustChain Health Check CLI v1.0                 ║", "cyan"))
    print(colorize("╚══════════════════════════════════════════════════════════════╝", "cyan"))
    print(f"  {colorize('Timestamp:', 'gray')} {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()


def print_node_status(node_data: Dict):
    """Print status for a single node."""
    name = node_data["name"]
    ip = node_data["ip"]
    port = node_data["port"]
    status = node_data["status"]
    
    # Status indicator
    if status == "online":
        status_icon = colorize("● ONLINE", "green")
    elif status == "offline":
        status_icon = colorize("● OFFLINE", "red")
    elif status == "timeout":
        status_icon = colorize("● TIMEOUT", "yellow")
    else:
        status_icon = colorize("● ERROR", "red")
    
    print(f"┌─ {colorize(name, 'bold')} ({ip}:{port})")
    print(f"│  Status:    {status_icon}")
    
    if status == "online":
        version = node_data.get("version", "unknown")
        uptime = format_uptime(node_data.get("uptime", 0))
        db_rw = node_data.get("db_rw", "unknown")
        tip_age = node_data.get("tip_age", 0)
        backup_age = node_data.get("backup_age")
        
        print(f"│  Version:   {version}")
        print(f"│  Uptime:    {uptime}")
        print(f"│  DB Status: {format_db_rw(db_rw)}")
        print(f"│  Tip Age:   {format_tip_age(tip_age)}")
        if backup_age is not None:
            print(f"│  Backup:    {backup_age}h ago")
    else:
        error = node_data.get("error", "Unknown error")
        print(f"│  {colorize('Error:', 'red')} {error}")
    
    print("└")
    print()


def print_summary(results: list):
    """Print overall network health summary."""
    online_count = sum(1 for r in results if r["status"] == "online")
    total_count = len(results)
    
    print(colorize("═══════════════════════════════════════════════════════════════", "cyan"))
    print(f"  {colorize('Network Summary:', 'bold')}")
    print(f"    Nodes Online: {colorize(str(online_count), 'green' if online_count == total_count else 'yellow')}/{total_count}")
    
    if online_count == total_count:
        print(f"    Status: {colorize('✓ All systems operational', 'green')}")
    elif online_count == 0:
        print(f"    Status: {colorize('✗ Network down', 'red')}")
    else:
        print(f"    Status: {colorize('⚠ Degraded performance', 'yellow')}")
    
    print(colorize("═══════════════════════════════════════════════════════════════", "cyan"))
    print()


def print_json_output(results: list):
    """Print results in JSON format."""
    output = {
        "timestamp": datetime.now().isoformat(),
        "nodes": results,
        "summary": {
            "total": len(results),
            "online": sum(1 for r in results if r["status"] == "online"),
            "offline": sum(1 for r in results if r["status"] == "offline"),
            "errors": sum(1 for r in results if r["status"] not in ["online", "offline"]),
        }
    }
    print(json.dumps(output, indent=2, default=str))


def main():
    """Main entry point."""
    # Check for JSON output flag
    json_mode = "--json" in sys.argv or "-j" in sys.argv
    
    if not json_mode:
        print_header()
    
    # Query all nodes
    results = []
    for node in NODES:
        result = query_node(node)
        results.append(result)
        if not json_mode:
            print_node_status(result)
    
    if json_mode:
        print_json_output(results)
    else:
        print_summary(results)
        
        # Print usage hint
        print(colorize("Tip: Use --json flag for machine-readable output", "gray"))
        print()


if __name__ == "__main__":
    main()
