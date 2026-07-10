#!/usr/bin/env python3
"""
Staking SDK — stake_and_acquire(skill, bond_rtc)
LangChain Tool + MCP server for RustChain staked self-improvement
Fail-safe: gate unavailable -> stake returned
"""
import json, os, hashlib
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from urllib.request import Request, urlopen
from urllib.error import URLError

GATE_URL = os.environ.get('RTC_GATE_URL', 'https://explorer.rustchain.org')
DEFAULT_TIMEOUT = 15

@dataclass
class StakeResult:
    verdict: str
    refunded: bool
    attestation: Optional[str] = None
    error: Optional[str] = None
    skill: Optional[str] = None
    bond_rtc: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}

def _call_gate(skill: str, bond_rtc: float, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    payload = json.dumps({'skill': skill, 'bond_rtc': bond_rtc}).encode()
    req = Request(f'{GATE_URL}/skill/gate', data=payload,
                  headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except URLError as e:
        return {'error': f'gate_unavailable:{getattr(e, "code", 0)}', 'refunded': True}
    except Exception as e:
        return {'error': f'gate_error:{str(e)}', 'refunded': True}

def stake_and_acquire(skill: str, bond_rtc: float = 1.0) -> StakeResult:
    """Stake RTC to acquire a skill improvement. Fail-safe refund on error."""
    result = _call_gate(skill, bond_rtc)
    if result.get('refunded') or result.get('error'):
        return StakeResult(verdict='error', refunded=True,
                           error=result.get('error', 'unknown'), skill=skill, bond_rtc=bond_rtc)
    return StakeResult(verdict=result.get('verdict', 'unknown'), refunded=False,
                       attestation=result.get('attestation'), skill=skill, bond_rtc=bond_rtc)
