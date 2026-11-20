# Bounty Fix

**Reward:** —
**Issue:** https://github.com/Scottcjn/rustchain-bounties/issues/1102
**Repo:** https://github.com/Scottcjn/rustchain-bounties

---

## Issue

[EASY BOUNTY: 2-3 RTC] Find and Report a BoTTube Bug

## Find and Report a BoTTube Bug — 3-5 RTC

**Reward:** 3 RTC (UI bug) / 5 RTC (functional bug)
**Difficulty:** Easy-Medium

### What to do:
1. Use [bottube.ai](https://bottube.ai) — browse, search, upload, comment, vote
2. If something breaks, looks wrong, or behaves unexpectedly — report it\!
3. Include: what you did, what happened, what you expected, browser/device info
4. Screenshots or screen recordings are gold

### Bug report template:
- **URL:** where it happened
- **Steps to reproduce:** 1, 2, 3...
- **Expected:** what should happen
- **Actual:** what actually happened
- **Browser/Device:** Chrome/Firefox/Safari, Desktop/Mobile

### Rules:
- Must be a real bug (not a feature request)
- Duplicate bugs do not count
- 3 RTC for cosmetic/UI bugs, 5 RTC for functional bugs

*Help us make BoTTube better for everyone\!*

<!-- machine-readable bounty spec -->
```bounty-spec
paid: true
reward_rtc: 3
per: per-item
cap: 2
submit: [pr, email, comment]
target_repo: Scottcjn/bottube
```

---

## Process

### 1. Orient yourself first
Before touching any code:
- Read the README and any relevant docs
- Run: find . -type f | grep -v node_modules | grep -v .git | grep -v dist | head -60
- Grep for the key terms from the issue title to find the relevant files
- Read the files around the bug — understand what's currently happening

### 2. Find and read the tests
- Look for test files near the relevant code (*.test.ts, *.spec.js, __tests__, etc.)
- Read them — they tell you what behavior is expected
- Understand what a passing fix looks like before writing a line

### 3. Implement the fix
- Make the MINIMAL change that fixes the issue — nothing more
- Do not refactor, rename, reorganize, or clean up unrelated code
- Do not add dependencies unless the issue explicitly requires it
- Do not modify config files (package.json, tsconfig.json, etc.) unless that IS the fix
- One logical change, one commit

### 4. Verify
- Run the test suite: check package.json scripts for "test", "lint", "typecheck"
  Common commands: npm test, yarn test, pnpm test, pytest, go test ./..., cargo test
- If TypeScript is present: npx tsc --noEmit
- Fix any test failures your change caused — if a test was wrong before, update it

### 5. Commit and document
- git add -A
- git commit -m "fix: [EASY BOUNTY: 2-3 RTC] Find and Report a BoTTube Bug"
- Write AGENT_SUMMARY.md with:
  - Root cause: what was wrong and why
  - Fix: what you changed and the reasoning
  - Verification: how to confirm it works
  - Concerns: anything a reviewer should know

---

## Stop conditions

If ANY of these are true, write "UNCERTAIN: [reason]" at the top of AGENT_SUMMARY.md, make NO code changes, and stop:
- The fix requires changing more than ~5 files
- You cannot determine what the correct behavior should be
- The issue requires a database migration, API key, or external service
- You find 3+ open PRs already attempting this fix (high competition)
- The repo is not in a language/framework you can reason about confidently

A clean UNCERTAIN is better than a bad PR.
