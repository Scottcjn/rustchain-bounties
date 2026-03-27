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

def main():
    parser = argparse.ArgumentParser(description="RustChain Node Health Check CLI")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    results = [query_node(node) for node in NODES]

    if args.json:
        print(json.dumps(results, indent=2))
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
    print("\n")

if __name__ == "__main__":
    main()
