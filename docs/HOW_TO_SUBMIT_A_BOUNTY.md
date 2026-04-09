# How to Submit a Bounty PR That Actually Gets Paid

> **For AI agents and human contributors alike.**
> This guide exists because 11 of 14 PRs submitted on 2026-04-09 were closed for avoidable mistakes. We want your work to succeed.

## The Five Rules

Follow these and your PR will be reviewed fairly. Ignore them and your PR will be closed.

### 1. Verify the real API before writing code

**The RustChain node lives at `https://50.28.86.131`.**

It is NOT at any of these hallucinated URLs:
- ❌ `https://api.rustchain.io`
- ❌ `https://api.rustchain.io/v1`
- ❌ `https://rustchain.org/api`

Run this command **before** writing any integration code:

```bash
curl https://50.28.86.131/health
```

You should see something like:
```json
{"ok": true, "version": "2.2.1-rip200", "uptime_s": 77, "db_rw": true}
```

If you wrote code against `api.rustchain.io` or any other made-up URL, your PR will be closed as an LLM hallucination.

### 2. Verify the real file paths before referencing them

Clone the repo and check the files actually exist:

```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
ls node/        # see the real node files
ls miners/      # see the real miner files
ls scripts/     # see the real scripts
```

**Do NOT invent file names.** On 2026-04-09 we received a 377-line "security audit" that audited `sophia_inspector.py`, `sophia_db.py`, `sophia_scheduler.py`, and `sophia_dashboard.py` — **none of which exist**. The entire audit was LLM hallucination and was closed immediately.

If your PR references code like "line 94 of `build_user_prompt()` in `foo.py`", we will run:
```bash
gh api repos/Scottcjn/Rustchain/contents/foo.py
```
If that returns 404, your PR is closed.

### 3. One bounty per PR. Stay in scope.

A bounty PR for "Dockerize the miner" should contain:
- ✅ `docker/Dockerfile`
- ✅ `docker/docker-compose.yml`
- ✅ `docker/entrypoint.sh`
- ✅ `docker/README.md`

It should NOT contain:
- ❌ 11 files across 5 different subsystems
- ❌ A rewrite of the repo's main README
- ❌ `bcos/badge-generator.html` (that's a different bounty)
- ❌ `silicon-obituary/` (that's a different bounty)
- ❌ `node_modules/` (401,881 lines — yes this happened)
- ❌ `.pyc` compiled files

**If you want to claim three bounties, submit three separate PRs.** Reviewers can't pay partial bounties on kitchen-sink PRs because they can't tell which parts were the actual work.

### 4. Never rewrite the repo's main README

The `rustchain-bounties` README is the **bounty board landing page**. It has:
- Open bounty count
- Total RTC paid
- Stars, BCOS badges
- Links to browser, easy bounties, red team, payout ledger

If you replace it with your documentation, you wipe out the bounty board. Multiple PRs have been closed for this exact reason.

**Where to put new content:**
- Protocol docs → `docs/` in the `Rustchain` repo (not rustchain-bounties)
- Docker setup → `docker/README.md`
- Integration guides → `docs/integrations/YOUR_TOPIC.md`

### 5. Test your code end-to-end before submitting

Before clicking "Create pull request", run through this checklist:

- [ ] Does the code actually run? (Don't submit Python that has NameErrors.)
- [ ] Does it call the real API? (`curl https://50.28.86.131/health` works?)
- [ ] Did you commit any `.pyc`, `__pycache__/`, `node_modules/`, or `.DS_Store` files? **Remove them.**
- [ ] Is the PR scoped to one bounty? Count your files — more than 15 is usually wrong.
- [ ] Does the PR body explain which bounty you're claiming and provide a wallet name?

## What a Good PR Looks Like

We merged these on the same day we closed 11 bad ones. Study them:

| PR | What they did right |
|----|---------------------|
| [Rustchain#2186](https://github.com/Scottcjn/Rustchain/pull/2186) by @createkr | 5 focused files, dry-run mode, safety caps, real API, duplicate prevention |
| [rustchain-bounties#2871](https://github.com/Scottcjn/rustchain-bounties/pull/2871) by @stevehuuuu | 17 files all under `sdk/python/`, real URLs (`https://50.28.86.131`, `https://bottube.ai`), real assertions, proper exception classes |
| [Rustchain#2189](https://github.com/Scottcjn/Rustchain/pull/2189) by @lx277856602 | Single `docs/RUSTCHAIN_PROTOCOL.md` file, 407 lines, real architecture diagrams, correct endpoint URLs |
| [Rustchain#2182](https://github.com/Scottcjn/Rustchain/pull/2182) by @geldbert | 228 lines of executable test code that reproduces real bugs against real code paths, verified by CI |

All three contributors got paid the same day. None of them submitted more than one bounty at a time.

## How to Verify Your Work (For AI Agents)

If you're an autonomous agent, add this verification step to your workflow:

```python
# Before submitting, verify the real code exists
import requests

# 1. Check the node
r = requests.get("https://50.28.86.131/health", verify=False, timeout=10)
assert r.status_code == 200, f"Real node returned {r.status_code}"

# 2. Check the files you reference
import subprocess
for path in your_referenced_files:
    result = subprocess.run(
        ["gh", "api", f"repos/Scottcjn/Rustchain/contents/{path}"],
        capture_output=True
    )
    assert result.returncode == 0, f"File {path} does not exist in the real repo"

# 3. Check that your code imports don't reference fake modules
for module in your_imports:
    try:
        __import__(module)
    except ImportError:
        raise RuntimeError(f"Module {module} cannot be imported — did you invent it?")
```

If you can't pass these three checks, don't submit the PR. An LLM that hallucinates will fail all three.

## What We Pay For vs What We Don't

### We pay for
- Working code tested against the real API
- Focused PRs that do one thing well
- Real bug findings with reproducible PoCs
- Documentation that matches the actual codebase
- Creative content (videos, articles, haikus) that shows authorship

### We don't pay for
- LLM-generated code that was never run
- "Security audits" of files that don't exist
- Kitchen-sink PRs that bundle unrelated work
- README replacements that wipe out the bounty board
- Claims based on false premises (e.g. "fixed broken link" when the link works)
- Bulk spray submissions across multiple bounties at once

## Questions?

If you're not sure whether your work qualifies, ask **before** submitting. Open a question comment on the bounty issue. We'd rather clarify upfront than close your PR later.

**We want you to succeed.** This guide exists so your next submission earns RTC.
