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


def submit_pr(bounty: Bounty, workdir: str, branch: str, wallet: str, *, used_claude: bool = False) -> str:
    """Push branch and open PR. Returns PR URL.

    The `used_claude` flag is propagated by `agent.py` so the PR body
    can describe the actual generation method honestly. Without this,
    R-03 (misleading PR body when template fallback is used) lets an
    operator submit a stub-file PR while the body claims Claude
    generated the implementation.
    """
    _git("push", "origin", branch, cwd=workdir)

    if used_claude:
        provenance_block = (
            "1. Scanned open bounties via `gh issue list`\n"
            "2. Scored each bounty using Claude Haiku (feasibility x reward ratio)\n"
            "3. Selected this bounty as the highest-value achievable task\n"
            "4. Generated the implementation using Claude Sonnet\n"
            "5. Committed the files and opened this PR -- without human intervention"
        )
        headline = (
            "This PR was submitted **autonomously** by [TestAutomaton]"
            "(https://github.com/mtstachowiak/rustchain-bounties),\n"
            "a sovereign AI agent running on Conway Cloud. The agent:"
        )
    else:
        provenance_block = (
            "1. Scanned open bounties via `gh issue list`\n"
            "2. Selected this bounty manually from the top of the list\n"
            "3. Generated a **template stub** (no ANTHROPIC_API_KEY was available to the agent at submission time)\n"
            "4. Committed the stub and opened this PR -- implementation is intentionally left for a follow-up pass"
        )
        headline = (
            "This PR was submitted by [TestAutomaton](https://github.com/mtstachowiak/rustchain-bounties)\n"
            "in **template-stub mode** (no Anthropic API key was available when the agent ran). The agent:"
        )

    body = f"""## Bounty Claim: #{bounty.number}

**Reward:** {bounty.reward_rtc} RTC
**Wallet:** `{wallet}`
**Agent:** TestAutomaton (0x031a724e53b0AFC401AcEdC13595D47dd89bcb02, Base)

---

### What this PR delivers

{bounty.title}

{headline}
{provenance_block}

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
