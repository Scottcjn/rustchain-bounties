#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Process verified star claims and output RTC payouts with placeholder transaction hashes.
"""
import json, uuid

def main():
    ledger_file = 'bounties/STARS_CAMPAIGN_CLAIMS.json'
    data = json.load(open(ledger_file))
    payouts = []
    for entry in data:
        tx = uuid.uuid4().hex
        payouts.append({
            'user': entry['user'], 'wallet': entry['wallet'],
            'amount': entry['reward'], 'tx_hash': tx, 'status': 'pending'
        })
    out = 'bounties/STARS_CAMPAIGN_PAYOUTS.json'
    with open(out,'w') as f: json.dump(payouts,f, indent=2)
    print(f"Generated {len(payouts)} payouts to {out}")

if __name__=='__main__':
    main()