#!/usr/bin/env python3
import json
import requests
from tabulate import tabulate
import argparse

NODES = [
    "50.28.86.131:8099",
    "50.28.86.153:8099",
    "76.8.228.245:8099"
]

BOTTUBE_HEALTH_URL = "https://bottube.ai/health"

def query_node(node_addr):
    try:
        response = requests.get(f"http://{node_addr}/health", timeout=5)
        response.raise_for_status()
        data = response.json()

        return {
            "node": node_addr,
            "status": "✅ Online",
            "version": data.get("version", "N/A"),
            "uptime": data.get("uptime", "N/A"),
            "db_rw": "✅ RW" if data.get("db_rw", False) else "❌ RO",
            "tip_age": f"{data.get('tip_age', 0)}s"
        }
    except Exception as e:
        return {
            "node": node_addr,
            "status": "❌ Offline",
            "version": "N/A",
            "uptime": "N/A",
            "db_rw": "N/A",
            "tip_age": "N/A",
            "error": str(e)
        }

def query_bottube():
    try:
        # Use HTTPS to avoid mixed-content/CORS issues and ensure real stats are fetched
        response = requests.get(BOTTUBE_HEALTH_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        return {
            "status": "✅ Online",
            "videos": data.get("videos", "--"),
            "agents": data.get("agents", "--"),
            "humans": data.get("humans", "--")
        }
    except Exception as e:
        return {
            "status": "❌ Offline",
            "videos": "--",
            "agents": "--",
            "humans": "--",
            "error": str(e)
        }

def main():
    parser = argparse.ArgumentParser(description="RustChain Node Health Check CLI")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--nodes-only", action="store_true", help="Only show node health (omit BoTTube stats)")
    args = parser.parse_args()

    results = [query_node(node) for node in NODES]
    bottube_stats = None if args.nodes_only else query_bottube()

    if args.json:
        output = {
            "nodes": results
        }
        if bottube_stats is not None:
            output["bottube"] = bottube_stats
        print(json.dumps(output, indent=2))
        return

    headers = ["Node", "Status", "Version", "Uptime", "DB RW", "Tip Age"]
    table_data = [
        [
            res["node"],
            res["status"],
            res["version"],
            res["uptime"],
            res["db_rw"],
            res["tip_age"]
        ]
        for res in results
    ]

    print("\n🦀 RustChain Node Health Status")
    print("=" * 60)
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    if bottube_stats is not None:
        bt_headers = ["Metric", "Count"]
        bt_table = [
            ["Videos", bottube_stats.get("videos", "--")],
            ["Agents", bottube_stats.get("agents", "--")],
            ["Humans", bottube_stats.get("humans", "--")]
        ]
        print("\n📺 BoTTube Live Stats")
        print("=" * 60)
        print(tabulate(bt_table, headers=bt_headers, tablefmt="grid"))
        print(f"\nService Status: {bottube_stats.get('status', 'N/A')}")

    print("\n")

if __name__ == "__main__":
    main()