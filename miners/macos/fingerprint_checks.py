#!/usr/bin/env python3
from fingerprint_core import validate_all_checks

if __name__ == "__main__":
    import json
    passed, results = validate_all_checks()
    print(json.dumps(results, indent=2, default=str))
