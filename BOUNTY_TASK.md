# Bounty Fix

**Reward:** —
**Issue:** https://github.com/Scottcjn/rustchain-bounties/issues/16863
**Repo:** https://github.com/Scottcjn/rustchain-bounties

---

## Issue

[MICRO-BOUNTY: 0.1 RTC] Why did you choose to work on an Elyan Labs repo?

## One question, 0.1 RTC, honest answers only

**Why did you pick RustChain, BoTTube, or any other Elyan Labs repo to spend your time on?**

Not a testimonial. Not marketing copy. We want the real reason, including the unflattering ones: the bounty was easy, your agent found it in a search, you liked the vintage-hardware angle, you were testing whether we actually pay, a friend sent you, you wanted a first merged PR anywhere. All of those are useful to us and all of them pay.

## What to post

- **2 to 6 sentences**, in your own words (or your agent's, disclosed).
- Which repo or bounty you started with, and what nearly made you leave.
- One thing we could change that would have made you do more.
- Your `RTC…` wallet address (40 hex) or your GitHub handle for a hosted wallet.

## Rules

- **0.1 RTC per person, once.** Pool: 25 RTC. Closes when the pool is spent or on 2026-10-05.
- Must have at least one merged PR, accepted bounty, or verified claim in an Elyan Labs repo — this is for people who actually did the work.
- One-liners, generic praise, and copy-paste answers are not paid. Criticism is.
- Agents welcome; say you are one.
- Email fallback (GitHub App 403): send it to sophia.eagent@gmail.com with this issue number in the subject.

## Why we are asking

We have paid out to a few hundred contributors and we mostly know *what* you built. We know almost nothing about *why you showed up*, and that decides what we build next for you. The answers stay public here so future contributors can read them too.

```yaml
bounty:
  reward_rtc: 0.1
  pool_rtc: 25
  per_person: 1
  closes: 2026-10-05
  requires: one accepted contribution in any Elyan Labs repo
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
- git commit -m "fix: [MICRO-BOUNTY: 0.1 RTC] Why did you choose to work on an Elyan Labs repo"
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
