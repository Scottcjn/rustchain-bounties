#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.parse

def main():
    # Get inputs
    node_url = os.environ.get('INPUT_NODE-URL', 'https://50.28.86.131')
    amount = os.environ.get('INPUT_AMOUNT', '5')
    wallet_from = os.environ.get('INPUT_WALLET-FROM', '')
    admin_key = os.environ.get('INPUT_ADMIN-KEY', '')
    dry_run = os.environ.get('INPUT_DRY-RUN', 'false').lower() == 'true'
    
    # Get PR info from GitHub context
    github_event_path = os.environ.get('GITHUB_EVENT_PATH', '')
    with open(github_event_path, 'r') as f:
        event = json.load(f)
    
    # Get merged PR info
    if event.get('pull_request', {}).get('merged') != True:
        print('PR not merged, skipping...')
        return
    
    pr = event['pull_request']
    pr_title = pr.get('title', '')
    pr_body = pr.get('body', '') or ''
    pr_number = pr['number']
    pr_url = pr.get('html_url', '')
    repo_full_name = os.environ.get('GITHUB_REPOSITORY', '')
    
    # Try to extract wallet from PR body or .rtc-wallet file
    contributor_wallet = extract_wallet(pr_body)
    
    if not contributor_wallet:
        print('No contributor wallet found in PR body')
        post_comment(repo_full_name, pr_number, 'No RTC wallet address found. Please add your wallet address in the PR body.')
        return
    
    if dry_run:
        print(f'[DRY RUN] Would send {amount} RTC to {contributor_wallet}')
        post_comment(repo_full_name, pr_number, f'[DRY RUN] Would award {amount} RTC to {contributor_wallet}')
        return
    
    # Send transaction
    success, tx_hash = send_rtc_transaction(node_url, wallet_from, contributor_wallet, amount, admin_key)
    
    if success:
        post_comment(repo_full_name, pr_number, 
            f'RTC Reward Sent! \n' +
            f'- Amount: {amount} RTC\n' +
            f'- To: {contributor_wallet}\n' +
            f'- TX: {tx_hash}')
        print(f'Successfully sent {amount} RTC to {contributor_wallet}, tx: {tx_hash}')
    else:
        post_comment(repo_full_name, pr_number, f'Failed to send RTC reward: {tx_hash}')
        print(f'Failed to send RTC: {tx_hash}')
        sys.exit(1)

def extract_wallet(pr_body):
    # Look for wallet address patterns in PR body
    lines = pr_body.split('\n')
    for line in lines:
        line = line.strip()
        # Look for wallet: or address: prefix
        if 'wallet' in line.lower() and ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2 and len(parts[1].strip()) > 10:
                return parts[1].strip()
        # Look for raw addresses (40-42 chars, hex or base58)
        import re
        addr = re.search(r'0x[a-fA-F0-9]{40}', line)
        if addr:
            return addr.group(0)
    return None

def send_rtc_transaction(node_url, from_wallet, to_wallet, amount, admin_key):
    # Placeholder for actual RTC transaction
    # In production, this would call the RTC node API
    try:
        payload = json.dumps({
            'method': 'send',
            'params': {
                'from': from_wallet,
                'to': to_wallet,
                'amount': amount,
                'key': admin_key
            }
        }).encode('utf-8')
        
        req = urllib.request.Request(
            node_url,
            data=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('success'):
                return True, result.get('tx_hash', 'unknown')
            else:
                return False, result.get('error', 'Unknown error')
    except Exception as e:
        return False, str(e)

def post_comment(repo, pr_number, body):
    github_token = os.environ.get('GITHUB_TOKEN', '')
    api_url = f'https://api.github.com/repos/{repo}/issues/{pr_number}/comments'
    
    payload = json.dumps({'body': body}).encode('utf-8')
    req = urllib.request.Request(
        api_url,
        data=payload,
        headers={
            'Authorization': f'token {github_token}',
            'Content-Type': 'application/json'
        }
    )
    
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode('utf-8'))

if __name__ == '__main__':
    main()