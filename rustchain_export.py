import argparse
import requests
import csv
import json
import os
from datetime import datetime

BASE_URL = "https://50.28.86.131"

def fetch_data(endpoint):
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", verify=False, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}")
        return []

def export_csv(data, filename):
    if not data: return
    keys = data[0].keys()
    with open(filename, 'w', newline='') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

def main():
    parser = argparse.ArgumentParser(description="RustChain Data Export Tool")
    parser.add_argument("--format", choices=['csv', 'json'], default='csv')
    parser.add_argument("--output", default="./data")
    parser.add_argument("--from", dest="start_date", help="YYYY-MM-DD")
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    endpoints = {
        "miners.csv": "api/miners",
        "epochs.csv": "api/epochs",
        "rewards.csv": "api/rewards"
    }

    for filename, endpoint in endpoints.items():
        data = fetch_data(endpoint)
        if args.format == 'csv':
            export_csv(data, os.path.join(args.output, filename))
        else:
            with open(os.path.join(args.output, filename.replace('.csv', '.json')), 'w') as f:
                json.dump(data, f)

if __name__ == "__main__":
    main()