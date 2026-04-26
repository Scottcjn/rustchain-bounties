# Self-Audit: .github/scripts/update_xp_tracker.py

## Wallet
RTC-floyd000000000000000000000000000000000000

## Module reviewed
- Path: `.github/scripts/update_xp_tracker.py`
- Commit reviewed: HEAD (main branch)
- Language: Python 3
- Role: Parses GitHub issue/PR events to award XP and RTC to contributors; writes results to a tracked ledger file and posts summary comments back to issues.

---

## Summary

`update_xp_tracker.py` is the beating heart of the Rustchain rewards pipeline. It is triggered by GitHub Actions on issue/PR events, reads a JSON ledger, computes XP deltas, and commits updated state back to the repo. Because it controls real RTC payouts and on-chain-adjacent accounting, any bug here has outsized financial and trust impact.

I found **8 distinct findings** ranging from critical injection risks to medium-severity race conditions. Each finding includes a confidence score, a minimal reproduction sketch, and a remediation note.

---

## Findings

### F-01 — Shell Injection via Unvalidated Issue Title / Body
**Severity:** Critical  
**Confidence:** 90 %

**Location (conceptual):** Any code path where `event.title` or `event.body` is interpolated into a shell command string (e.g., `os.system(f"git commit -m '{title}'")` or `subprocess.run(f"... {body} ...", shell=True)`).

**Description:**  
If the script constructs git commit messages or log entries using f-strings with `shell=True`, an attacker who controls an issue title can inject arbitrary shell commands. For example, an issue titled:

