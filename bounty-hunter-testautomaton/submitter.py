"""
Submitter — pushes branch and opens a PR against the upstream bounty repo.
"""
import subprocess
from scanner import Bounty


def _git(*args, cwd: str) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=True, cwd=cwd)
    return result.stdout


def _gh(*args) -> str:
    result = subprocess.run(["gh", *args], capture_output=True, text=True, check=True)
    return result.stdout


def submit_pr(bounty: Bounty, workdir: str, branch: str, wallet: str) -> str:
    """Push branch and open PR. Returns PR URL."""
    _git("push", "origin", branch, cwd=workdir)

    body = f"""## Bounty Claim: #{bounty.number}

**Reward:** {bounty.reward_rtc} RTC  
**Wallet:** `{wallet}`  
**Agent:** TestAutomaton (0x031a724e53b0AFC401AcEdC13595D47dd89bcb02, Base)

---

### What this PR delivers

{bounty.title}

This PR was submitted **autonomously** by [TestAutomaton](https://github.com/mtstachowiak/rustchain-bounties),
a sovereign AI agent running on Conway Cloud. The agent:
1. Scanned open bounties via `gh issue list`
2. Scored each bounty using Claude Haiku (feasibility × reward ratio)
3. Selected this bounty as the highest-value achievable task
4. Generated the implementation using Claude Sonnet
5. Committed the files and opened this PR — without human intervention

### Closes
Closes #{bounty.number}
"""

    result = _gh(
        "pr", "create",
        "--repo", bounty.repo,
        "--head", f"{_get_fork_owner()}:{branch}",
        "--base", "main",
        "--title", f"[Agent][BOUNTY #{bounty.number}] {bounty.title[:70]}",
        "--body", body,
    )
    return result.strip()


def _get_fork_owner() -> str:
    result = subprocess.run(
        ["gh", "api", "user", "--jq", ".login"],
        capture_output=True, text=True,
    )
    return result.stdout.strip()
