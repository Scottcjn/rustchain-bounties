"""
Implementer — generates code or content for a bounty using Claude API,
then forks the target repo, commits the changes, and returns the branch info.
Falls back to template-based generation without an API key.
"""
import os
import json
import subprocess
import tempfile
import re
from pathlib import Path
from scanner import Bounty


def _gh(*args) -> str:
    result = subprocess.run(["gh", *args], capture_output=True, text=True, check=True)
    return result.stdout


def _git(*args, cwd: str) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=True, cwd=cwd)
    return result.stdout


def _claude_implement(bounty: Bounty, api_key: str) -> dict[str, str]:
    """Return {filename: content} for the deliverable."""
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are an autonomous coding agent completing a GitHub bounty.

Bounty #{bounty.number}: {bounty.title}
Reward: {bounty.reward_rtc} RTC

Requirements:
{bounty.body[:2000]}

Generate the minimal, clean implementation that satisfies this bounty.
Reply with a JSON object: {{"files": [{{"path": "...", "content": "..."}}]}}
Paths should be relative to the repo root. Keep files focused and under 200 lines each."""

    msg = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = msg.content[0].text.strip()
    data = json.loads(re.search(r'\{.*\}', text, re.DOTALL).group())
    return {f["path"]: f["content"] for f in data["files"]}


def _template_files(bounty: Bounty) -> dict[str, str]:
    """Minimal template when no API key available."""
    return {
        f"submissions/bounty-{bounty.number}/README.md": (
            f"# Bounty #{bounty.number}\n\n{bounty.title}\n\n"
            f"Reward: {bounty.reward_rtc} RTC\n\n"
            "## Implementation\n\n*Work in progress — see code below.*\n"
        )
    }


def fork_and_implement(bounty: Bounty, wallet: str) -> tuple[str, str]:
    """
    Fork the bounty repo, create a branch, write implementation files.
    Returns (fork_clone_path, branch_name).
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    files = _claude_implement(bounty, api_key) if api_key else _template_files(bounty)

    # Clone fork (gh will create if needed)
    workdir = tempfile.mkdtemp(prefix=f"bounty-{bounty.number}-")
    owner = subprocess.run(["gh", "api", "user", "--jq", ".login"],
                           capture_output=True, text=True).stdout.strip()
    
    # Fork the repo
    _gh("repo", "fork", bounty.repo, "--clone=false")
    clone_url = f"https://github.com/{owner}/{bounty.repo.split('/')[-1]}.git"
    subprocess.run(["git", "clone", "--depth=1", clone_url, workdir],
                   capture_output=True, check=True)

    branch = f"bounty-{bounty.number}-{owner}"
    _git("checkout", "-b", branch, cwd=workdir)

    for path, content in files.items():
        full = Path(workdir) / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content)
        _git("add", str(path), cwd=workdir)

    _git("commit", "-m",
         f"feat: bounty #{bounty.number} — {bounty.title[:60]} [{wallet}]",
         cwd=workdir)

    return workdir, branch
