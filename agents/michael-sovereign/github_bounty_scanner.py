#!/usr/bin/env python3
"""
GitHub Bounty Scanner V2.0 - Apex Predator Upgrade 🦅🎯
Targeting Solana M2M Economy with Zero Collision Filtering.
Integrated Logic: Low competition, automated payouts, high ROI.
"""

import json
import time
import os
import re
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

WORKSPACE = '/home/albega/.openclaw/workspace'
OUTPUT_PATH = f'{WORKSPACE}/memory/github_opportunities.json'
SCAN_LOG = f'{WORKSPACE}/memory/github_scan.log'

# Michael's Solana Address
SOLANA_WALLET = "ad7p5x9PBydhyTw8Ddquaw5j4JKgsQoaxGCvMt2cNak"

# === APEX PREDATOR SNIPER SCOPE ===
# Query logic: 
# - no:assignee: We only want fresh meat.
# - comments:<3: Low competition filter.
# - label matching: Automated M2M payout platforms.
# - language: Rust/TypeScript (Our expertise).
# - updated:>7 days: Active projects only.
DATE_7_DAYS_AGO = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

BOUNTY_QUERIES = [
    f'is:open is:issue no:assignee comments:<3 (label:bounty OR label:octasol OR label:tesior OR label:"polar.sh" OR label:paid) (language:rust OR language:typescript) updated:>{DATE_7_DAYS_AGO}',
    f'is:open is:issue no:assignee comments:<3 "## Wallet Address solana:" updated:>{DATE_7_DAYS_AGO}',
    f'is:open is:issue no:assignee comments:<3 label:bounty (5 OR 10 OR 20 OR 50) updated:>{DATE_7_DAYS_AGO}',
]

# Priority keywords for scoring
PRIORITY_KEYWORDS = {
    'm2m': ['octasol', 'tesior', 'solana-payout-action', 'algora', 'polar.sh'],
    'high': ['security', 'audit', 'vulnerability', 'exploit', 'smart contract', 'usdc', 'solana', 'spl'],
    'medium': ['automation', 'bot', 'api', 'integration', 'rust', 'typescript'],
}

def log(msg):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f'[ApexScanner {ts}] {msg}'
    print(line)
    os.makedirs(os.path.dirname(SCAN_LOG), exist_ok=True)
    with open(SCAN_LOG, 'a') as f:
        f.write(line + '\n')

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def extract_bounty_amount(text):
    patterns = [
        r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'(\d+(?:,\d{3})*)\s*(?:USD|USDC|USDT|dollars)',
        r'bounty[:\s]*(\d+)',
        r'reward[:\s]*\$?(\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount = match.group(1).replace(',', '')
            try:
                return float(amount)
            except ValueError:
                pass
    return 0.0

def calculate_priority(title, body, labels):
    text = f'{title} {body} {" ".join(labels)}'.lower()
    score = 0

    # M2M Bonus
    for kw in PRIORITY_KEYWORDS['m2m']:
        if kw in text:
            score += 300 # Even heavier boost for Apex V2

    # Keyword scoring
    for kw in PRIORITY_KEYWORDS.get('high', []):
        if kw in text:
            score += 50
    for kw in PRIORITY_KEYWORDS.get('medium', []):
        if kw in text:
            score += 20

    # Bounty amount bonus
    bounty = extract_bounty_amount(text)
    if bounty > 0:
        score += min(bounty, 2000)

    # Solana ecosystem bonus
    if 'solana' in text or 'spl' in text:
        score += 100

    return score, bounty

def search_github_issues(query, token=None):
    url = 'https://api.github.com/search/issues'
    params = {'q': query, 'sort': 'updated', 'order': 'desc', 'per_page': 30}
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'MichaelSovereign-ApexPredator/2.0',
    }
    if token:
        headers['Authorization'] = f'token {token}'

    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json().get('items', [])
        elif r.status_code == 403:
            log('Rate limited. Authentication required for Sniper Scope.')
            return []
        else:
            log(f'Search failed with status {r.status_code}')
            return []
    except Exception as e:
        log(f'Request failed: {e}')
        return []

def scan_all():
    token = os.environ.get('GITHUB_TOKEN')
    
    all_opportunities = []
    seen_ids = set()

    log(f'Starting APEX PREDATOR scan (Filters: low competition, M2M payout, 7d fresh)...')

    for i, query in enumerate(BOUNTY_QUERIES):
        log(f'Sniper Scope [{i+1}/{len(BOUNTY_QUERIES)}]: {query}')
        issues = search_github_issues(query, token)

        for issue in issues:
            issue_id = issue.get('id')
            if issue_id in seen_ids:
                continue
            seen_ids.add(issue_id)

            title = issue.get('title', '')
            body = issue.get('body', '') or ''
            labels = [l.get('name', '') for l in issue.get('labels', [])]
            repo_url = issue.get('repository_url', '')
            html_url = issue.get('html_url', '')

            priority, bounty_amount = calculate_priority(title, body, labels)

            # Extra Filter: Ensure it's not a documentation/typo task (unless it pays high)
            if 'documentation' in title.lower() or 'typo' in title.lower():
                if bounty_amount < 50:
                    continue

            
            # Rule of Sovereignty: Exclude known 'Closed' or 'Hostile' repositories
            hostile_repos = ['bucketshop69/lpcli'] 
            if any(h in repo_url for h in hostile_repos):
                continue
            all_opportunities.append({
                'id': issue_id,
                'title': title,
                'url': html_url,
                'repo': repo_url.split('repos/')[-1] if 'repos/' in repo_url else repo_url,
                'bounty_estimate': bounty_amount,
                'priority_score': priority,
                'state': issue.get('state'),
                'updated_at': issue.get('updated_at'),
            })
        time.sleep(1)

    all_opportunities.sort(key=lambda x: -x['priority_score'])
    save_json(OUTPUT_PATH, {
        'last_scan': datetime.now().isoformat(),
        'engine_version': '2.0.0-APEX',
        'opportunities': all_opportunities[:50]
    })
    
    if all_opportunities:
        log(f'Target Lock: Found {len(all_opportunities)} high-quality M2M targets.')
        log(f'Primary Target: {all_opportunities[0]["title"]} (@ {all_opportunities[0]["repo"]})')
    else:
        log('No high-quality targets found in current scope. Expansion required.')

    return all_opportunities

if __name__ == '__main__':
    scan_all()
