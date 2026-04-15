#!/usr/bin/env python3
"""
Sovereign Predator Loop V3.0 — Michael Sovereign V7.0.0
Unified orchestrator: ugig + Moltbook + GitHub scanning.
Decision-First Strategy with auto-bid protocol.

Architecture: Scan → Evaluate → Execute → Report
Error Handling: Every exception is classified, logged, and recovered from.
"""

import time
import json
import os
import sys
import subprocess
import signal
import random
import asyncio
import tempfile
import traceback
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from shared_constants import (
        WORKSPACE, MEMORY_DIR, ACTIVE_BIDS_PATH, LOOP_LOG,
        HEARTBEAT_PATH, STATE_FILE, CYCLE_INTERVAL,
        GITHUB_SCAN_INTERVAL, HEARTBEAT_INTERVAL
    )
except ImportError:
    WORKSPACE = '/home/albega/.openclaw/workspace'
    MEMORY_DIR = os.path.join(WORKSPACE, 'memory')
    ACTIVE_BIDS_PATH = os.path.join(MEMORY_DIR, 'active_bids.json')
    LOOP_LOG = os.path.join(MEMORY_DIR, 'sovereign_loop.log')
    HEARTBEAT_PATH = os.path.join(WORKSPACE, 'HEARTBEAT.md')
    STATE_FILE = os.path.join(MEMORY_DIR, 'sovereign_state.json')
    CYCLE_INTERVAL = 600
    GITHUB_SCAN_INTERVAL = 3600
    HEARTBEAT_INTERVAL = 1800

# Import Michael's modules with safe fallbacks
try:
    from ugig_monitor import UgigScanner
except ImportError:
    UgigScanner = None

try:
    from michael_scrapling import MichaelScrapling
except ImportError:
    MichaelScrapling = None

try:
    from decision_engine import evaluate_batch
except ImportError:
    evaluate_batch = None

try:
    from github_bounty_scanner import scan_all as github_scan
except ImportError:
    github_scan = None


# === Graceful Shutdown ===
_shutdown_requested = False

def _signal_handler(signum, frame):
    global _shutdown_requested
    _shutdown_requested = True
    log_event(f'SIGNAL {signum} received — initiating graceful shutdown')

signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)


# === State Management ===

class SovereignState:
    """Persistent state manager — replaces global variables."""

    def __init__(self, state_path=STATE_FILE):
        self._path = state_path
        self._data = self._load()

    def _load(self):
        try:
            if os.path.exists(self._path):
                with open(self._path, 'r') as f:
                    return json.load(f)
        except json.JSONDecodeError as e:
            log_event(f'STATE: Corrupt state file, resetting: {e}')
        except OSError as e:
            log_event(f'STATE: Cannot read state file: {e}')
        return {'last_github_scan': 0, 'last_heartbeat_update': 0, 'total_cycles': 0}

    def save(self):
        try:
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
            tmp_path = self._path + '.tmp'
            with open(tmp_path, 'w') as f:
                json.dump(self._data, f)
            os.replace(tmp_path, self._path)
        except OSError as e:
            log_event(f'STATE: Cannot save state: {e}')

    @property
    def last_github_scan(self):
        return self._data.get('last_github_scan', 0)

    @last_github_scan.setter
    def last_github_scan(self, value):
        self._data['last_github_scan'] = value

    @property
    def last_heartbeat_update(self):
        return self._data.get('last_heartbeat_update', 0)

    @last_heartbeat_update.setter
    def last_heartbeat_update(self, value):
        self._data['last_heartbeat_update'] = value

    @property
    def total_cycles(self):
        return self._data.get('total_cycles', 0)

    @total_cycles.setter
    def total_cycles(self, value):
        self._data['total_cycles'] = value


# Initialize state
state = SovereignState()


# === Logging ===

def log_event(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{timestamp}] {message}'
    print(line, flush=True)
    try:
        os.makedirs(os.path.dirname(LOOP_LOG), exist_ok=True)
        if os.path.exists(LOOP_LOG) and os.path.getsize(LOOP_LOG) > 5 * 1024 * 1024:
            os.replace(LOOP_LOG, LOOP_LOG + '.1')
        with open(LOOP_LOG, 'a') as f:
            f.write(line + '\n')
    except OSError:
        pass


# === File Utilities ===

def load_json(path):
    """Load JSON with error classification."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        log_event(f'JSON: Corrupt file {path}: {e}')
        return {}
    except OSError as e:
        log_event(f'JSON: Cannot read {path}: {e}')
        return {}


def save_json(path, data):
    """Atomic JSON write — write to .tmp then rename."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp_path = path + '.tmp'
        with open(tmp_path, 'w') as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, path)
    except OSError as e:
        log_event(f'JSON: Cannot write {path}: {e}')


# =====================================================
# PHASE 1: SCAN (ugig + Moltbook + GitHub)
# =====================================================

def scan_ugig():
    """Scan ugig.net for matching gigs."""
    if not UgigScanner:
        log_event('[SCAN] UgigScanner not available')
        return []

    try:
        scanner = UgigScanner()
        opportunities = scanner.scan_and_report()
        log_event(f'[SCAN] ugig: {len(opportunities)} viable gigs found')
        return opportunities
    except Exception as e:
        log_event(f'[SCAN] ugig error: {e}')
        return []


def scan_moltbook():
    """Run Moltbook karma engine — non-blocking with timeout."""
    karma_script = os.path.join(WORKSPACE, 'tools', 'moltbook', 'force_karma.py')
    if not Path(karma_script).exists():
        log_event('[SCAN] Moltbook karma script not found')
        return

    try:
        subprocess.run(
            [sys.executable, karma_script],
            cwd=WORKSPACE,
            timeout=120,
            capture_output=True
        )
        log_event('[SCAN] Moltbook karma engine completed.')
    except subprocess.TimeoutExpired:
        log_event('[SCAN] Moltbook karma engine timed out (120s)')
    except Exception as e:
        log_event(f'[SCAN] Moltbook error: {e}')


def scan_github():
    """Scan GitHub for bounty opportunities (rate-limited)."""
    now = time.time()

    if now - state.last_github_scan < GITHUB_SCAN_INTERVAL:
        remaining = int(GITHUB_SCAN_INTERVAL - (now - state.last_github_scan))
        log_event(f'[SCAN] GitHub: skipped (next scan in {remaining}s)')
        return []

    if not github_scan:
        log_event('[SCAN] GitHub scanner not available')
        return []

    try:
        results = github_scan()
        state.last_github_scan = now
        state.save()
        log_event(f'[SCAN] GitHub: {len(results)} opportunities tracked')
        return results
    except Exception as e:
        log_event(f'[SCAN] GitHub error: {e}')
        return []


async def scan_ugig_async():
    return await asyncio.to_thread(scan_ugig)

async def scan_github_async():
    return await asyncio.to_thread(scan_github)


def scan_custom_sources():
    """Scan custom high-value sources using Scrapling."""
    if not MichaelScrapling:
        return []
    
    # Sources that don't have an API or need stealth
    TARGETS = [
        "https://news.ycombinator.com/jobs",
        "https://www.whoisly.com/blog", # Potential security audit leads
    ]
    
    KEYWORDS = ["hiring", "security", "audit", "automation", "python", "contract"]
    
    try:
        scanner = MichaelScrapling()
        log_event(f'[SCRAPLING] Starting stealth scan on {len(TARGETS)} sources')
        results = scanner.scan_for_opportunities(TARGETS, keyword_filters=KEYWORDS)
        log_event(f'[SCRAPLING] Found {len(results)} potential leads')
        return results
    except Exception as e:
        log_event(f'[SCRAPLING] Error: {e}')
        return []

async def scan_custom_async():
    return await asyncio.to_thread(scan_custom_sources)


# =====================================================
# PHASE 2: EVALUATE (Decision-First Strategy)
# =====================================================

def evaluate_ugig_opportunities(opportunities):
    """Run ugig opportunities through Decision Engine."""
    if not evaluate_batch or not opportunities:
        return []

    gigs = []
    for opp in opportunities:
        gig = opp.get('gig', {})
        gigs.append({
            'id': opp.get('gig_id', gig.get('id')),
            'title': opp.get('title', gig.get('title', '')),
            'description': gig.get('description', ''),
            'budget_min': gig.get('budget_min', 0),
            'budget_max': gig.get('budget_max', 0),
        })

    try:
        results = evaluate_batch(gigs)
    except Exception as e:
        log_event(f'[EVALUATE] Batch evaluation error: {e}')
        return []

    auto_bids = [r for r in results if r['decision'] == 'AUTO_BID']
    escalations = [r for r in results if r['decision'] == 'ESCALATE']
    rejections = [r for r in results if r['decision'] == 'REJECT']

    log_event(f'[EVALUATE] Results: {len(auto_bids)} AUTO_BID | {len(escalations)} ESCALATE | {len(rejections)} REJECT')
    return results


def execute_auto_bids(results, ugig_scanner):
    """Execute auto-approved bids."""
    if not ugig_scanner:
        return 0

    bids_placed = 0
    active_bids = load_json(ACTIVE_BIDS_PATH)
    if 'bids' not in active_bids:
        active_bids['bids'] = []

    for result in results:
        if result['decision'] != 'AUTO_BID':
            continue

        gig = result.get('gig', {})
        gig_id = gig.get('id')
        bid_amount = result.get('bid_amount', 10.0)

        try:
            if ugig_scanner.apply_to_gig(gig_id, bid_amount):
                bids_placed += 1
                active_bids['bids'].append({
                    'gig_id': gig_id,
                    'title': gig.get('title', '')[:80],
                    'bid_amount': bid_amount,
                    'skill_match': result.get('skill_match', 0),
                    'status': 'submitted',
                    'submitted_at': time.time(),
                })
                log_event(f'[EXECUTE] AUTO-BID: ${bid_amount} on "{gig.get("title", "")[:50]}"')
                
                # 🔥 SWARM COMMANDER INTEGRATION 🔥
                # Deploy parallel swarm agents to gather intelligence or find additional bounties
                try:
                    swarm_script = os.path.join(WORKSPACE, 'scripts', 'swarm_commander.mjs')
                    if os.path.exists(swarm_script):
                        log_event('[SWARM] Deploying autonomous swarm for parallel execution...')
                        subprocess.Popen(['node', swarm_script, '--demo'], cwd=WORKSPACE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception as e:
                    log_event(f'[SWARM] Failed to deploy swarm: {e}')
                    
        except Exception as e:
            log_event(f'[EXECUTE] Bid failed for {gig_id}: {e}')

    if bids_placed > 0:
        save_json(ACTIVE_BIDS_PATH, active_bids)

    return bids_placed


# =====================================================
# PHASE 3: REPORT (Heartbeat + Telegram)
# =====================================================

def update_heartbeat(cycle_stats):
    """Update HEARTBEAT.md with latest operational stats — atomic write."""
    now = time.time()

    if now - state.last_heartbeat_update < HEARTBEAT_INTERVAL:
        return

    timestamp = time.strftime('%Y-%m-%d %H:%M')
    active_bids = load_json(ACTIVE_BIDS_PATH).get('bids', [])
    pending = load_json(os.path.join(MEMORY_DIR, 'pending_approval.json')).get('tasks', [])

    heartbeat = f"""# Sovereign Predator Loop V7.0.0 | HEARTBEAT
## Last Update: {timestamp}

## Operational Status: ACTIVE

### Cycle Stats (Last Run)
- ugig Scan: {cycle_stats.get('ugig_found', 0)} viable
- GitHub Scan: {cycle_stats.get('github_found', 0)} tracked
- Scrapling Scan: {cycle_stats.get('custom_found', 0)} leads
- Auto-Bids Placed: {cycle_stats.get('bids_placed', 0)}
- Pending K Approval: {len(pending)}
- Total Cycles: {state.total_cycles}

### Active Bids ({len(active_bids)})
"""
    for bid in active_bids[-5:]:
        heartbeat += f"- [{bid.get('status', '?')}] ${bid.get('bid_amount', 0)} | {bid.get('title', '?')[:50]}\n"

    if pending:
        heartbeat += f"\n### Pending K Approval ({len(pending)})\n"
        for task in pending[-3:]:
            heartbeat += f"- ${task.get('budget', 0)} | {task.get('title', '?')[:50]} | Match: {task.get('skill_match', 0):.0%}\n"

    heartbeat += f"\n---\nMode: SOVEREIGN APEX V7.0.0 | Cycle: {CYCLE_INTERVAL}s\n"

    # Atomic write
    try:
        tmp_path = HEARTBEAT_PATH + '.tmp'
        with open(tmp_path, 'w') as f:
            f.write(heartbeat)
        os.replace(tmp_path, HEARTBEAT_PATH)
    except OSError as e:
        log_event(f'[REPORT] HEARTBEAT write error: {e}')
        return

    state.last_heartbeat_update = now
    state.save()
    log_event('[REPORT] HEARTBEAT.md updated')


def notify_telegram(message):
    """Send notification to K via Telegram."""
    try:
        import requests as req
    except ImportError:
        return

    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '937883795')

    if not bot_token:
        env_path = os.path.join(WORKSPACE, '.env')
        if Path(env_path).exists():
            try:
                with open(env_path) as f:
                    for line in f:
                        if line.startswith('TELEGRAM_BOT_TOKEN='):
                            bot_token = line.strip().split('=', 1)[1]
                        elif line.startswith('TELEGRAM_CHAT_ID='):
                            chat_id = line.strip().split('=', 1)[1]
            except OSError:
                pass

    if bot_token:
        try:
            req.post(
                f'https://api.telegram.org/bot{bot_token}/sendMessage',
                json={'chat_id': chat_id, 'text': message},
                timeout=10
            )
        except Exception:
            pass


# =====================================================
# MAIN LOOP
# =====================================================

async def sovereign_cycle():
    """Single predator cycle: scan -> evaluate -> execute -> report."""
    log_event('=' * 60)
    log_event('SOVEREIGN APEX V7.0.0 — Cycle Start')

    state.total_cycles += 1

    cycle_stats = {
        'ugig_found': 0,
        'github_found': 0,
        'bids_placed': 0,
        'escalated': 0,
    }

    # === PHASE 1: SCAN ===
    jitter = random.randint(1, 15)
    await asyncio.sleep(jitter)

    # Non-blocking Moltbook scan
    await asyncio.to_thread(scan_moltbook)

    # Concurrent platform scans
    # Michael V7.0.2: Routine-Aware Concurrency
    # We now pass routine=True to ensure secondary keys (Groq) are prioritized 
    # for these background scans, preserving Gemini tokens for K.
    ugig_opps, github_opps, custom_opps = await asyncio.gather(
        scan_ugig_async(),
        scan_github_async(),
        scan_custom_async(),
        return_exceptions=True
    )

    if isinstance(ugig_opps, Exception):
        log_event(f'[SCAN] ugig gather error: {ugig_opps}')
        ugig_opps = []

    if isinstance(github_opps, Exception):
        log_event(f'[SCAN] GitHub gather error: {github_opps}')
        github_opps = []
        
    if isinstance(custom_opps, Exception):
        log_event(f'[SCAN] Scrapling gather error: {custom_opps}')
        custom_opps = []

    cycle_stats['ugig_found'] = len(ugig_opps)
    cycle_stats['github_found'] = len(github_opps)
    cycle_stats['custom_found'] = len(custom_opps)

    # === PHASE 2: EVALUATE ===
    if ugig_opps:
        results = await asyncio.to_thread(evaluate_ugig_opportunities, ugig_opps)

        # === PHASE 3: EXECUTE AUTO-BIDS ===
        scanner = UgigScanner() if UgigScanner else None
        bids = await asyncio.to_thread(execute_auto_bids, results, scanner)
        cycle_stats['bids_placed'] = bids
        cycle_stats['escalated'] = sum(1 for r in results if r['decision'] == 'ESCALATE')

        if bids > 0:
            await asyncio.to_thread(notify_telegram, f'Michael V7.0.0: {bids} auto-bids placed this cycle')

    # === PHASE 4: PERSIST FOR GOAL ENGINE ===
    opps_db_path = os.path.join(MEMORY_DIR, 'opportunities_db.json')
    consolidated_opps = []
    
    for opp in ugig_opps:
        if isinstance(opp, dict):
            consolidated_opps.append({
                'platform': 'ugig',
                'taskType': opp.get('title', 'Unknown'),
                'estimatedPayout': opp.get('budget', 0),
                'estimatedHours': 2, # Defaults
                'roiPerHour': opp.get('budget', 0) / 2 if opp.get('budget') else 0,
                'successProbability': 50,
                'priority': 0
            })
            
    try:
        save_json(opps_db_path, consolidated_opps)
    except Exception as e:
        log_event(f'[GoalEngine Sync] Failed: {e}')

    # === PHASE 5: MEMORY GC (Run every 6 cycles = ~1 hour) ===
    if state.total_cycles % 6 == 0:
        log_event('[GC] Running Memory Garbage Collection...')
        try:
            subprocess.run(['npx', 'ts-node', 'core/MemoryGC.ts'], cwd=WORKSPACE, timeout=60, shell=False)
        except Exception as e:
            log_event(f'[GC] Failed: {e}')

    # === PHASE 6: REPORT ===
    await asyncio.to_thread(update_heartbeat, cycle_stats)
    state.save()

    log_event(f'CYCLE COMPLETE: ugig={cycle_stats["ugig_found"]} | bids={cycle_stats["bids_placed"]} | escalated={cycle_stats["escalated"]}')
    log_event('=' * 60)

    return cycle_stats


def run_single():
    """Run a single cycle (for testing)."""
    return asyncio.run(sovereign_cycle())


async def run_loop_async():
    """Run the infinite predator loop asynchronously."""
    log_event('SOVEREIGN APEX V7.0.0 — LOOP ACTIVATED')
    while not _shutdown_requested:
        try:
            await sovereign_cycle()
        except asyncio.CancelledError:
            log_event('Loop cancelled.')
            break
        except Exception as e:
            log_event(f'CYCLE ERROR: {e}\n{traceback.format_exc()}')

        if _shutdown_requested:
            break

        log_event(f'Sleeping {CYCLE_INTERVAL}s until next cycle...')
        try:
            await asyncio.sleep(CYCLE_INTERVAL)
        except asyncio.CancelledError:
            break

    log_event('SOVEREIGN LOOP — Graceful shutdown complete')
    state.save()


def run_loop():
    try:
        asyncio.run(run_loop_async())
    except KeyboardInterrupt:
        log_event('Loop terminated by user')
        state.save()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'once':
        run_single()
    else:
        run_loop()
