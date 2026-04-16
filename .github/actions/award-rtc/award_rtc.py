#!/usr/bin/env python3
"""
RustChain Auto-Award RTC GitHub Action
Automatically awards RTC tokens to contributors when their PR is merged.
Issue: https://github.com/Scottcjn/rustchain-bounties/issues/2864
"""
import json, os, sys, urllib.request, urllib.error

def main():
    node_url = os.environ.get('RUSTCHAIN_NODE_URL', 'https://50.28.86.131')
    admin_key = os.environ.get('ADMIN_KEY', '')
    contributor = os.environ.get('CONTRIBUTOR', '')
    pr_number = os.environ.get('PR_NUMBER', '0')
    reward_rtc = int(os.environ.get('REWARD_RTC', '10'))
    
    if not admin_key:
        print('::error::ADMIN_KEY secret is required')
        sys.exit(1)
    if not contributor:
        print('::warning::CONTRIBUTOR not set, skipping')
        sys.exit(0)

    transfer_data = {
        'from_miner': 'rustchain-treasury',
        'to_miner': contributor,
        'amount_rtc': reward_rtc,
        'reason': f'bounty_reward:PR#{pr_number}'
    }

    try:
        url = f'{node_url}/wallet/transfer'
        data = json.dumps(transfer_data).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={
            'Content-Type': 'application/json',
            'X-Admin-Key': admin_key
        }, method='POST')
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            if result.get('ok'):
                tx = result.get('tx_hash', 'unknown')
                print(f'::notice::Awarded {reward_rtc} RTC to {contributor} (TX: {tx})')
            else:
                print(f'::warning::Transfer failed: {result.get("error", "unknown")}')
    except urllib.error.HTTPError as e:
        print(f'::error::HTTP {e.code}: {e.read().decode()[:200]}')
    except Exception as e:
        print(f'::warning::Error: {e}')

if __name__ == '__main__':
    main()
