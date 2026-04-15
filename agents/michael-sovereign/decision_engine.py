#!/usr/bin/env python3
"""
Decision Engine V3.0 — Michael Sovereign V8.0.0
CHANGELOG V3.0:
- FIXED: Fallback now returns ESCALATE, not AUTO_BID (was allowing scam bids)
- ADDED: Keyword-based scam filter (works without LLM)
- ADDED: Minimum budget filter ($5 floor)
- ADDED: Anti-self-sabotage guards
"""

import json
import time
import os
import sys
import hashlib
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from shared_constants import (
        WORKSPACE, MEMORY_DIR, DECISIONS_LOG, PENDING_PATH,
        ACTIVE_BIDS_PATH, BID_HISTORY_PATH
    )
except ImportError:
    WORKSPACE = '/home/albega/.openclaw/workspace'
    MEMORY_DIR = os.path.join(WORKSPACE, 'memory')
    DECISIONS_LOG = os.path.join(MEMORY_DIR, 'decisions.log')
    PENDING_PATH = os.path.join(MEMORY_DIR, 'pending_approval.json')
    ACTIVE_BIDS_PATH = os.path.join(MEMORY_DIR, 'active_bids.json')
    BID_HISTORY_PATH = os.path.join(MEMORY_DIR, 'bid_history.json')

SKILL_KEYWORDS = {
    'security': ['security', 'audit', 'vulnerability', 'pentest', 'CVE', 'exploit', 'review'],
    'automation': ['automation', 'RPA', 'bot', 'scraping', 'crawler', 'script'],
    'ai_agent': ['AI', 'agent', 'LLM', 'GPT', 'model', 'NLP', 'machine learning', 'ML'],
    'web3': ['web3', 'blockchain', 'solana', 'ethereum', 'DeFi', 'smart contract', 'token'],
    'api': ['API', 'REST', 'GraphQL', 'integration', 'endpoint', 'backend'],
    'browser': ['browser', 'chrome', 'extension', 'puppeteer', 'playwright', 'selenium'],
    'python': ['python', 'django', 'flask', 'fastapi', 'pip'],
    'javascript': ['javascript', 'node', 'react', 'next', 'typescript', 'npm'],
    'devops': ['docker', 'CI/CD', 'deployment', 'server', 'linux', 'nginx'],
    'data': ['data', 'analysis', 'visualization', 'pandas', 'database', 'SQL'],
}

# V8.0.0: Keyword-based scam detection (works WITHOUT LLM)
SCAM_KEYWORDS = [
    'send me your wallet', 'private key', 'seed phrase', 'deposit first',
    'pay first', 'free money', 'verify account', 'send crypto',
    'guaranteed return', 'double your', 'investment opportunity',
    'wire transfer', 'western union', 'moneygram', 'gift card',
]

# V8.0.0: Tightened thresholds
AUTO_BID_CEILING = 50.0
MIN_SKILL_MATCH = 0.80
MIN_BUDGET = 5.0
MAX_AUTO_BID_PER_DAY = 10


def _load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _save_json(path, data):
    tmp = path + '.tmp'
    try:
        with open(tmp, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    except OSError as e:
        print(f'[DECISION] Save error: {e}')

def _log_decision(gig_id, decision, reason, extra=None):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    entry = f'[{timestamp}] {decision} | gig={gig_id} | {reason}'
    if extra:
        entry += f' | {json.dumps(extra, ensure_ascii=False)}'
    try:
        log_path = DECISIONS_LOG
        if Path(log_path).exists() and Path(log_path).stat().st_size > 500_000:
            os.replace(log_path, log_path + '.1')
        with open(log_path, 'a') as f:
            f.write(entry + '\n')
    except OSError:
        pass
    print(entry, flush=True)


def _detect_scam_keywords(title, description):
    """Fast keyword-based scam detection. Always works, no LLM required."""
    text = f'{title} {description}'.lower()
    for keyword in SCAM_KEYWORDS:
        if keyword in text:
            return True, f'Scam keyword: "{keyword}"'
    return False, None


_brain_instance = None
_eval_cache = {}
_CACHE_TTL = 600

def _get_brain():
    global _brain_instance
    if _brain_instance is None:
        try:
            from resilient_brain import get_brain
            _brain_instance = get_brain()
        except ImportError:
            _brain_instance = False
    return _brain_instance if _brain_instance is not False else None

def _cache_key(title, description, budget):
    raw = f'{title}|{description}|{budget}'.lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()

def _get_cached_eval(title, description, budget):
    key = _cache_key(title, description, budget)
    if key in _eval_cache:
        ts, result = _eval_cache[key]
        if time.time() - ts < _CACHE_TTL:
            return result
        del _eval_cache[key]
    return None

def _set_cached_eval(title, description, budget, result):
    key = _cache_key(title, description, budget)
    _eval_cache[key] = (time.time(), result)
    expired = [k for k, (ts, _) in _eval_cache.items() if time.time() - ts > _CACHE_TTL]
    for k in expired:
        del _eval_cache[k]


def evaluate_gig_cognitive(title, description, budget):
    """V8.0.0 CRITICAL FIX: When LLM unavailable, returns (0.0, False)
    which forces ESCALATE path. Prevents auto-bidding on scams."""
    
    # STEP 1: Always check keywords first (instant, no LLM)
    is_keyword_scam, scam_reason = _detect_scam_keywords(title, description)
    if is_keyword_scam:
        print(f'[DECISION] SCAM BLOCKED by keyword filter: {scam_reason}')
        return 0.0, True

    # STEP 2: Check cache
    cached = _get_cached_eval(title, description, budget)
    if cached is not None:
        return cached

    # STEP 3: Try LLM evaluation
    brain = _get_brain()
    if not brain:
        # V8.0.0 FIX: Return 0.0 = forces ESCALATE, NEVER auto-bid blind
        print('[DECISION] LLM unavailable — forcing ESCALATE (safe default)')
        return 0.0, False

    system_prompt = """You are Michael, a Sovereign Digital Businessman and expert security auditor.
Analyze the provided freelance task/gig.
Determine:
1. Is it a scam? (Look for: "pay first", "private keys", "free money", "deposit to verify").
2. What is the skill match from 0.0 to 1.0? (Michael is skilled in: Web3, AI, Bots, Security Auditing, Node.js, Python, Automation, Browser Extensions).

Output ONLY valid JSON:
{
  "is_scam": boolean,
  "scam_reason": "string or null",
  "skill_match": float,
  "match_reason": "string"
}"""
    user_prompt = f"TITLE: {title}\nDESCRIPTION: {description}\nBUDGET: ${budget}"

    try:
        result = brain.think(system_prompt, user_prompt, prefer_local=False, timeout=15, routine=True)
        if result:
            cleaned = result.replace('```json', '').replace('```', '').strip()
            data = json.loads(cleaned)
            eval_result = (float(data.get('skill_match', 0.0)), bool(data.get('is_scam', False)))
            _set_cached_eval(title, description, budget, eval_result)
            return eval_result
    except json.JSONDecodeError:
        print('[DECISION] LLM returned invalid JSON — forcing ESCALATE')
    except Exception as e:
        print(f'[DECISION] LLM evaluation failed: {e} — forcing ESCALATE')

    # V8.0.0 FIX: Safe default = ESCALATE
    return 0.0, False


def _get_today_bid_count():
    history = _load_json(BID_HISTORY_PATH)
    today = time.strftime('%Y-%m-%d')
    return len([b for b in history.get('bids', []) if b.get('date') == today])


def evaluate_gig(gig):
    """V8.0.0: Added minimum budget filter + hardened scam protection."""
    gig_id = gig.get('id', 'unknown')
    title = str(gig.get('title', ''))
    desc = str(gig.get('description', ''))

    try:
        min_budget = float(gig.get('budget_min', 0))
        max_budget = float(gig.get('budget_max', 0))
    except (ValueError, TypeError):
        min_budget = 0
        max_budget = 0

    budget = max_budget if max_budget > 0 else min_budget

    # V8.0.0: MINIMUM BUDGET FILTER
    if 0 < budget < MIN_BUDGET:
        _log_decision(gig_id, 'REJECT', f'Budget ${budget} below minimum ${MIN_BUDGET}')
        return {'decision': 'REJECT', 'reason': 'budget_too_low', 'budget': budget}

    # COGNITIVE EVALUATION (with hardened fallback)
    skill_match, is_scam = evaluate_gig_cognitive(title, desc, budget)

    if is_scam:
        _log_decision(gig_id, 'REJECT', 'Scam indicators detected')
        return {'decision': 'REJECT', 'reason': 'scam_detected'}

    if skill_match < 0.30:
        _log_decision(gig_id, 'REJECT', f'Skill match too low: {skill_match:.0%}')
        return {'decision': 'REJECT', 'reason': 'low_skill_match', 'score': skill_match}

    if budget > AUTO_BID_CEILING:
        _log_decision(gig_id, 'ESCALATE', f'Budget ${budget} exceeds ceiling ${AUTO_BID_CEILING}')
        pending = _load_json(PENDING_PATH)
        if 'tasks' not in pending:
            pending['tasks'] = []
        pending['tasks'].append({
            'gig_id': gig_id, 'title': title, 'budget': budget,
            'skill_match': skill_match, 'added_at': time.time(),
        })
        _save_json(PENDING_PATH, pending)
        return {'decision': 'ESCALATE', 'reason': 'high_budget', 'budget': budget, 'score': skill_match}

    if skill_match < MIN_SKILL_MATCH:
        _log_decision(gig_id, 'ESCALATE', f'Moderate match ({skill_match:.0%}) needs K review')
        return {'decision': 'ESCALATE', 'reason': 'moderate_match', 'score': skill_match}

    today_count = _get_today_bid_count()
    if today_count >= MAX_AUTO_BID_PER_DAY:
        _log_decision(gig_id, 'ESCALATE', f'Daily limit reached ({today_count}/{MAX_AUTO_BID_PER_DAY})')
        return {'decision': 'ESCALATE', 'reason': 'daily_limit_reached'}

    bid_amount = max(MIN_BUDGET, min_budget) if min_budget > 0 else 10.0
    if bid_amount > AUTO_BID_CEILING:
        bid_amount = AUTO_BID_CEILING

    priority = budget * skill_match

    _log_decision(gig_id, 'AUTO_BID', f'Match: {skill_match:.0%}, Budget: ${budget}, Bid: ${bid_amount}', {
        'title': title[:80], 'priority': priority,
    })

    return {
        'decision': 'AUTO_BID', 'reason': 'all_checks_passed',
        'bid_amount': bid_amount, 'skill_match': skill_match, 'priority': priority,
    }


def evaluate_batch(gigs):
    results = []
    for gig in gigs:
        try:
            result = evaluate_gig(gig)
            result['gig'] = gig
            results.append(result)
        except Exception as e:
            print(f'[DECISION] Gig evaluation error for {gig.get("id", "?")}: {e}')
            results.append({'decision': 'REJECT', 'reason': f'evaluation_error: {e}', 'gig': gig})

    order = {'AUTO_BID': 0, 'ESCALATE': 1, 'REJECT': 2}
    results.sort(key=lambda r: (order.get(r['decision'], 3), -r.get('priority', 0)))
    return results


if __name__ == '__main__':
    sample_gigs = [
        {'id': 'test1', 'title': 'Security Audit for Smart Contract', 'description': 'Need a security review of Solana program', 'budget_min': 25, 'budget_max': 40},
        {'id': 'test2', 'title': 'Build AI Chatbot', 'description': 'Python bot with LLM integration', 'budget_min': 100, 'budget_max': 200},
        {'id': 'test3', 'title': 'Send me your wallet key', 'description': 'Deposit first to verify your account', 'budget_min': 0, 'budget_max': 1000},
        {'id': 'test4', 'title': 'Fix CSS layout', 'description': 'Simple HTML page styling fix', 'budget_min': 5, 'budget_max': 10},
        {'id': 'test5', 'title': 'Cheap logo', 'description': 'Need a logo', 'budget_min': 0, 'budget_max': 2},
    ]
    print('=== Decision Engine V3.0 (V8.0.0) Test ===')
    results = evaluate_batch(sample_gigs)
    for r in results:
        print(f"  {r['decision']:10s} | {r['gig']['title'][:40]:40s} | {r.get('reason', '')}")
    
    scam_results = [r for r in results if r['gig']['id'] == 'test3']
    assert scam_results[0]['decision'] == 'REJECT', 'CRITICAL: Scam NOT rejected!'
    print('\n✅ SCAM PROTECTION VERIFIED')
    
    cheap_results = [r for r in results if r['gig']['id'] == 'test5']
    assert cheap_results[0]['decision'] == 'REJECT', 'CRITICAL: Cheap gig NOT rejected!'
    print('✅ MIN BUDGET FILTER VERIFIED')
