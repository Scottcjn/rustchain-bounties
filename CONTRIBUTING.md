# Contributing to RustChain Bounties

Thank you for your interest in contributing to RustChain bounties! This guide explains how to participate in the bounty program, claim tasks, submit proofs, and earn RTC tokens.

## 🚀 Quick Start

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** for your changes (`git checkout -b feature/my-contribution`)
4. **Make your changes** and test them
5. **Commit** with a clear message
6. **Push** to your fork and open a **Pull Request**

## 💰 Earning RTC Tokens

All merged contributions earn RTC tokens! See the bounty tiers:

| Tier | Reward | Examples |
| ---- | ------ | -------- |
| Micro | 1-10 RTC | Typo fix, small docs, simple test |
| Standard | 20-50 RTC | Feature, refactor, new endpoint |
| Major | 75-100 RTC | Security fix, consensus improvement |
| Critical | 100-150 RTC | Vulnerability patch, protocol upgrade |

Browse [open bounties](https://github.com/Scottcjn/rustchain-bounties/issues) to find tasks with specific RTC rewards.

## 🧹 Submitting a Clean PR

> **This is the #1 reason PRs get rejected.** Read this section carefully.

Your PR must **not** include build artifacts or dependency directories. Before submitting:

### Required `.gitignore` entries

```
node_modules/
dist/
out/
.env
*.log
.vscode-test/
*.vsix
```

### If you already committed `node_modules/`

```bash
# Remove from git tracking (keeps files on disk)
git rm -r --cached node_modules/
git rm -r --cached dist/

# Add .gitignore
echo "node_modules/" >> .gitignore
echo "dist/" >> .gitignore

# Commit the fix
git add .gitignore
git commit -m "chore: add .gitignore, remove build artifacts from tracking"
```

### Pre-submission check

```bash
# Verify no build artifacts in your diff
git diff --stat HEAD
# ✅ Only YOUR code changes should appear
# ❌ If node_modules/ or dist/ appear, STOP and fix .gitignore first
```

For the full guide, see **[docs/CLEAN_PR_GUIDE.md](docs/CLEAN_PR_GUIDE.md)**.

## 🎯 Bounty Workflow Guide

### Finding Bounties
1. Go to the [rustchain-bounties repository issues](https://github.com/Scottcjn/rustchain-bounties/issues)
2. Look for issues with bounty labels (e.g., `[DOC]`, `[FEAT]`, `[BUG]`)
3. Check the issue description for RTC reward information
4. **Important**: Read the [Anti-Farming Rules (#452)](https://github.com/Scottcjn/rustchain-bounties/issues/452) before claiming any bounty

### Claiming a Bounty
1. **Check if already claimed**: Read the issue comments to see if someone has already claimed it
2. **Claim format**: Comment on the issue with:
   ```
   **Claiming this bounty.**
   
   [Brief description of your approach]
   
   Timeline: [Estimated completion time]
   -YourGitHubUsername
   ```
3. **Wait for acknowledgment**: If no one else has claimed, you can proceed
4. **Start working**: Fork the repository and begin implementation

### Wallet Format
- **Use wallet names, not addresses**: `your-wallet-name` (e.g., `Guzzzzzzzz`)
- **Do not include cryptocurrency addresses** in comments
- Wallet names are used to track RTC earnings in the ledger

### Proof Requirements
For bounties requiring proof of completion:
1. **Screenshots**: Clear, full-screen screenshots showing the working feature
2. **Code snippets**: Relevant sections of implemented code
3. **Test results**: Output from test commands
4. **Video demonstrations** (optional): For complex UI/UX features

### Submission Process
1. **Complete the work** in your forked repository
2. **Ensure a clean PR** — no `node_modules/`, `dist/`, or build artifacts (see [Clean PR Guide](docs/CLEAN_PR_GUIDE.md))
3. **Create a Pull Request** to the main repository
4. **Link to the issue**: In your PR description, include `Closes #<issue_number>`
5. **Provide proof**: Attach screenshots or other required proof in the PR comments
6. **Wait for review**: Maintainers will review within 48-72 hours

### After Approval
1. **PR merged**: Once approved, a maintainer will merge your PR
2. **RTC distribution**: RTC tokens will be distributed to your wallet name within 24–48 hours
3. **Ledger update**: Your earning will be recorded in [BOUNTY_LEDGER.md](BOUNTY_LEDGER.md)
4. **Balance check**: Verify at `https://50.28.86.131/wallet/balance?miner_id=<your-wallet-name>`

---

## New here from ugig?

See the [GIG_APPLICANTS.md](GIG_APPLICANTS.md) onramp guide for a streamlined 4-step walkthrough.
