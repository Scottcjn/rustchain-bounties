# How to Submit a Clean PR (No node_modules)

> A step-by-step guide for RustChain contributors to avoid the most common PR rejection reasons.

## The Problem

Multiple PRs have been rejected because they committed `node_modules/`, `dist/`, or other build artifacts. This adds 800K+ lines to the diff, making code review impossible and cluttering the repository history.

This guide will fix it **permanently**.

---

## One-Time Setup (Do This Once Per Repo)

### 1. Create a proper `.gitignore`

```bash
# In your repo root
echo "node_modules/" >> .gitignore
echo "dist/" >> .gitignore
echo "out/" >> .gitignore
echo ".env" >> .gitignore
echo "*.log" >> .gitignore
echo ".vscode-test/" >> .gitignore
echo "*.vsix" >> .gitignore
```

### 2. Remove already-tracked build artifacts from git

If you've already committed `node_modules/` or `dist/`, remove them from tracking (this does **not** delete the files from disk):

```bash
git rm -r --cached --ignore-unmatch node_modules/ dist/ out/
git rm -r --cached dist/
git rm -r --cached out/
```

### 3. Commit the cleanup

```bash
git add .gitignore
git commit -m "chore: add .gitignore, remove build artifacts from tracking"
```

### 4. Verify

```bash
git status
# node_modules/ should NOT appear in the output
```

---

## Before Every PR — Pre-Submission Checklist

```bash
# 1. Check what files you're about to commit
git diff --stat origin/main...HEAD
# ⚠️ If you see node_modules/, dist/, or out/ in the list → STOP and fix .gitignore

# 2. Check your .gitignore exists and is correct
cat .gitignore | grep node_modules
# ✅ Should output: node_modules/

# 3. Verify your commit doesn't have too many files
git log --oneline --stat -1
# ✅ Should show only YOUR code changes, not thousands of dependency files
```

---

## VS Code Extension PRs — Additional Requirements

If you're submitting a VS Code extension (e.g., for bounty [#2868](https://github.com/Scottcjn/rustchain-bounties/issues/2868)):

### Required file structure

```
my-extension/
├── .gitignore           # MUST include node_modules/
├── .vscodeignore        # Excludes files from .vsix package
├── package.json         # MUST have "engines": { "vscode": "^1.60.0" }
├── tsconfig.json
├── src/
│   └── extension.ts     # Main entry point
├── test/
│   └── extension.test.ts
├── README.md
└── CHANGELOG.md
```

### `package.json` must include

```json
{
  "engines": {
    "vscode": "^1.60.0"
  }
}
```

> ⚠️ This is a **VS Code extension**, not an MCP server. Make sure `engines.vscode` is present.

### API endpoints to use

| Endpoint | URL |
|----------|-----|
| Health | `GET https://rustchain.org/health` |
| Balance | `GET https://rustchain.org/wallet/balance?miner_id={name}` |
| Epoch | `GET https://rustchain.org/epoch` |
| Miners | `GET https://rustchain.org/api/miners` |

> ⚠️ Use `miner_id` (not `wallet_id`) as the query parameter.

### `.vscodeignore` template

```
.vscode/**
.vscode-test/**
src/**
.gitignore
vsc-extension-quickstart.md
**/tsconfig.json
**/.eslintrc.json
**/*.map
**/*.ts
```

---

## Common Mistakes and How to Fix Them

| Mistake | Fix |
|---------|-----|
| Committed `node_modules/` | `git rm -r --cached --ignore-unmatch node_modules/ dist/ out/` then add to `.gitignore` |
| No `.gitignore` file | Create one at the repo root with the entries above |
| `.gitignore` exists but `node_modules` still tracked | Run `git rm -r --cached --ignore-unmatch node_modules/ dist/ out/` — `.gitignore` only prevents **new** tracking |
| Used `wallet_id` instead of `miner_id` | Change to `miner_id` in your API calls |
| Submitted MCP server code as VS Code extension | Add `engines.vscode` to `package.json` and restructure |
| PR diff has 800K+ lines | Almost certainly `node_modules/` — run the cleanup above |

---

## Quick Reference — Copy-Paste Commands

```bash
# Full cleanup in one block:
echo "node_modules/" >> .gitignore
echo "dist/" >> .gitignore
echo "out/" >> .gitignore
echo ".env" >> .gitignore
echo "*.log" >> .gitignore
git rm -r --cached --ignore-unmatch node_modules/ dist/ out/ 2>/dev/null
git rm -r --cached dist/ 2>/dev/null
git rm -r --cached out/ 2>/dev/null
git add .gitignore
git commit -m "chore: add .gitignore, remove build artifacts from tracking"
git push origin HEAD
```

---

## Need Help?

- Open an issue at [rustchain-bounties](https://github.com/Scottcjn/rustchain-bounties/issues)
- Read the [CONTRIBUTING.md](../CONTRIBUTING.md) guide
- Check the [GIG_APPLICANTS.md](../GIG_APPLICANTS.md) onramp for new contributors
