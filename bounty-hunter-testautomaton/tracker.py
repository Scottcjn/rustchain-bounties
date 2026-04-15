"""
EarningsTracker — persists bounty submission history in a local JSON log.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path


LOG_PATH = Path.home() / ".bounty-hunter" / "earnings.json"


def _load() -> list[dict]:
    if LOG_PATH.exists():
        return json.loads(LOG_PATH.read_text())
    return []


def _save(records: list[dict]):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps(records, indent=2))


def record_submission(bounty_number: int, title: str, reward_rtc: float,
                      pr_url: str, wallet: str):
    records = _load()
    records.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "bounty": bounty_number,
        "title": title,
        "reward_rtc": reward_rtc,
        "pr_url": pr_url,
        "wallet": wallet,
        "status": "pending",
    })
    _save(records)
    print(f"📝 Recorded submission — {len(records)} total in log")


def total_pending_rtc() -> float:
    return sum(r["reward_rtc"] for r in _load() if r["status"] == "pending")


def print_summary():
    records = _load()
    pending = [r for r in records if r["status"] == "pending"]
    paid = [r for r in records if r["status"] == "paid"]
    print(f"\n💰 Earnings Summary")
    print(f"   Submissions:    {len(records)}")
    print(f"   Pending RTC:    {sum(r['reward_rtc'] for r in pending):.1f}")
    print(f"   Earned RTC:     {sum(r['reward_rtc'] for r in paid):.1f}")
    if records:
        print(f"\n   Recent submissions:")
        for r in records[-5:]:
            print(f"   #{r['bounty']} — {r['reward_rtc']} RTC — {r['status']} — {r['pr_url']}")
