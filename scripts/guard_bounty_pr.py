#!/usr/bin/env python3
"""
Guard: flag bounty-submission PRs from untrusted authors that touch
protected automation/payout paths (closes the class of bug seen in #14981,
where a "solution" PR to an onboarding bounty gutted .github/scripts/*.py
automation instead of adding a submission file).

This is deliberately NOT a blanket "everything outside submissions/ is
banned" rule. Real merged bounty work in this repo routinely touches
docs/, apple2_miner/, museum/, star_tracker.py, bounties/<issue>/, and
plenty of other paths depending on what the bounty asked for (see #2093,
#2095, #142, #173, #2699). Banning that would break legitimate
contributors. Likewise, trusted contributors (OWNER/MEMBER/COLLABORATOR/
CONTRIBUTOR) routinely and legitimately touch scripts/ and .github/ as
part of normal maintenance (see #14990, #14546) -- that is not the
problem this guard exists to catch.

What actually differentiated the #14981 incident:
  - author_association == NONE (first-time, non-collaborator)
  - the PR touched automation/payout-critical paths
    (.github/workflows, .github/scripts, .github/actions,
     scripts/, bounties.json, BOUNTY_LEDGER.md, ...)

So the guard only fires when BOTH are true. It never blocks a trusted
contributor, and it never blocks an untrusted contributor whose PR stays
out of protected paths (which covers the overwhelming majority of real
bounty submissions).

On a hit, this posts an explanatory PR comment, applies a
`needs-maintainer-review` label, and exits non-zero so the check shows
red -- a request for human review, not a permanent block. A maintainer
can always merge past a failing, non-required check.

FOUR SILENT-SUCCESS PATHS CLOSED HERE (audit #16471)
----------------------------------------------------
Each of these made the guard exit 0 and print a clean verdict while the
change class it exists to catch went through unflagged and unlabelled.

1. `CONTRIBUTOR` was treated as trust, on the stated grounds that it
   "requires a prior merged PR reviewed by a human". It does not: GitHub
   sets that association after ONE commit lands in the repo, and this
   repo merges one-line README badge PRs as a 2 RTC bounty (#13949). So
   the price of permanently exempting an account from this guard was one
   line of README. `CONTRIBUTOR` still exempts ordinary automation paths
   (that is what #14546 is, and flagging it would be pure noise), but it
   no longer exempts MONEY paths -- the payout-destination registry, the
   ledger, and executable action definitions. For those, trust must be a
   real repository role or real write permission, checked against the
   API and failing CLOSED when it cannot be checked.

2. Path matching was case-sensitive, so `Scripts/bounty_payout.py` or
   `docs/Claimants.md` read as untouched. `scripts/auto-pay.py` had
   already learned this and normalises both sides; that fix had not
   reached here.

3. `.github/actions/` was protected but six other action definitions were
   not, including `glassworm-protocol/`, which `.github/workflows/
   glassworm.yml` executes via `uses: ./glassworm-protocol` with a
   writable GITHUB_TOKEN. The protected set is now DERIVED from the
   checked-out base tree (every directory holding an `action.yml`, plus
   every directory a workflow runs via `uses: ./...`) so it cannot drift
   again as actions are added or moved.

4. `previous_filename` was ignored, so renaming a protected file out of a
   protected path presented as a single non-protected path.
"""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Iterable

import requests

API = "https://api.github.com"

# Associations that ARE a real repository role: the person holds
# permissions granted by a human, and this guard never gates them.
ROLE_ASSOCIATIONS = {"OWNER", "MEMBER", "COLLABORATOR"}

# Authors at this trust level are not gated on ordinary automation paths.
# CONTRIBUTOR is kept here ONLY for that tier: it means "has one commit in
# the repo", which is enough to assume good faith on a scripts/ tweak
# (#14546) and not enough to wave through a payout-registry edit. See
# MONEY_* below and `is_money_path`.
TRUSTED_ASSOCIATIONS = ROLE_ASSOCIATIONS | {"CONTRIBUTOR"}

# Path prefixes that carry real blast radius: CI automation, payout
# scripts, and the ledger/registry files the payout scripts read.
PROTECTED_PREFIXES = (
    ".github/workflows/",
    ".github/scripts/",
    ".github/actions/",
    ".github/mcp_server/",
    "scripts/",
)
PROTECTED_EXACT_FILES = {
    ".github/dependabot.yml",
    ".github/supply-chain-allowlist.yml",
    "bounties.json",
    "BOUNTY_LEDGER.md",
    "expected_miners.txt",
    # Payout-destination registry: a single appended row here can silently
    # redirect another contributor's payout. Any change must be human-reviewed.
    "docs/CLAIMANTS.md",
}

# MONEY tier: a change here moves real RTC or runs with a writable token.
# No association-derived exemption applies; only a real repository role or
# verified write permission does.
MONEY_EXACT_FILES = {
    "docs/CLAIMANTS.md",
    "BOUNTY_LEDGER.md",
    "bounties.json",
    "expected_miners.txt",
}

# A file with this name DEFINES a GitHub Action: editing it (or anything in
# its directory) changes code that CI executes.
ACTION_DEFINITION_NAMES = {"action.yml", "action.yaml"}

# Lower-cased copies used for matching. The guard MUST be case-insensitive:
# git tracks `Scripts/`, `.GitHub/`, `BOUNTY_LEDGER.MD` etc. as distinct from
# their lower-case forms, so a case-sensitive `startswith` lets a PR touch
# payout / CI code under a re-cased path and read as untouched. This mirrors
# `is_sensitive_path` in scripts/auto-pay.py, which already closed the same
# bypass on the auto-tier side.
PROTECTED_PREFIXES_LC = tuple(p.lower() for p in PROTECTED_PREFIXES)
PROTECTED_EXACT_FILES_LC = frozenset(p.lower() for p in PROTECTED_EXACT_FILES)
MONEY_EXACT_FILES_LC = frozenset(p.lower() for p in MONEY_EXACT_FILES)

# Directories discovered in the checked-out base tree that hold an action
# definition or are run by a workflow via `uses: ./<dir>`. Populated by
# discover_action_dirs(); empty by default so the module stays a pure
# function set for tests that do not care about the repo layout.
ACTION_DIR_PREFIXES_LC: tuple[str, ...] = ()

LABEL_NAME = "needs-maintainer-review"
LABEL_COLOR = "d93f0b"
LABEL_DESCRIPTION = "Touches protected automation/payout paths -- flagged by guard-bounty-pr for human review"

# `uses: ./some/dir` in a workflow: the PR-editable code a job will run.
LOCAL_USES_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*['\"]?\./([^\s'\"#]+)", re.MULTILINE)


def _norm(path: str) -> str:
    """Comparison form of a repo path: forward slashes, lower case, no leading `./`."""
    p = (path or "").replace("\\", "/").strip()
    while p.startswith("./"):
        p = p[2:]
    return p.lower()


def discover_action_dirs(root: str = ".") -> tuple[str, ...]:
    """Directory prefixes that hold executable CI code, read off the base tree.

    Two sources, both derived rather than listed, so the set cannot drift as
    actions are added, renamed or moved:

      1. every directory containing an `action.yml` / `action.yaml`;
      2. every `uses: ./<dir>` target in `.github/workflows/*.y*ml`.

    On `ab5844cc` this finds `glassworm-protocol/`, `bounty-2864/`,
    `actions/rtc-reward/`, `rtc-reward-action/`, `github-tip-bot/` and
    `community/github-actions/rtc-reward/` -- none of which the static
    prefix list covered, while `.github/workflows/glassworm.yml` runs the
    first of them with a writable GITHUB_TOKEN.
    """
    dirs: set[str] = set()

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
        if any(name.lower() in ACTION_DEFINITION_NAMES for name in filenames):
            rel = os.path.relpath(dirpath, root)
            if rel not in (".", ""):
                dirs.add(_norm(rel) + "/")

    wf_dir = os.path.join(root, ".github", "workflows")
    if os.path.isdir(wf_dir):
        for name in sorted(os.listdir(wf_dir)):
            if not name.lower().endswith((".yml", ".yaml")):
                continue
            try:
                with open(os.path.join(wf_dir, name), encoding="utf-8") as fh:
                    text = fh.read()
            except OSError:
                # Unreadable workflow: fail CLOSED by keeping whatever we
                # already found rather than pretending the file said nothing.
                continue
            for match in LOCAL_USES_RE.finditer(text):
                target = _norm(match.group(1)).rstrip("/")
                if target:
                    dirs.add(target + "/")

    return tuple(sorted(dirs))


def load_action_dirs(root: str = ".") -> tuple[str, ...]:
    """Discover and install the dynamic prefixes used by is_protected_path()."""
    global ACTION_DIR_PREFIXES_LC
    ACTION_DIR_PREFIXES_LC = discover_action_dirs(root)
    return ACTION_DIR_PREFIXES_LC


def is_action_definition(path: str) -> bool:
    """True for `action.yml` / `action.yaml` anywhere in the tree."""
    return _norm(path).rsplit("/", 1)[-1] in ACTION_DEFINITION_NAMES


def is_money_path(path: str) -> bool:
    """True if a change here moves RTC or runs with a writable token.

    These never get the `CONTRIBUTOR` exemption. The registry files decide
    WHERE money goes; an action definition (and the directory around it) is
    code a workflow executes.
    """
    norm = _norm(path)
    if norm in MONEY_EXACT_FILES_LC:
        return True
    if is_action_definition(norm):
        return True
    return any(norm.startswith(prefix) for prefix in ACTION_DIR_PREFIXES_LC)


def is_protected_path(path: str) -> bool:
    norm = _norm(path)
    if norm in PROTECTED_EXACT_FILES_LC:
        return True
    if norm.startswith(PROTECTED_PREFIXES_LC):
        return True
    return is_money_path(norm)


def has_write_access(owner: str, repo: str, user: str, headers: dict) -> bool:
    """Does `user` actually hold write/admin permission on this repo?

    Fails CLOSED: any non-200, any unexpected body, any transport error is
    "no", because the caller uses this to decide whether a money-path edit
    may skip human review. If the endpoint is unavailable to the workflow
    token the result is one extra maintainer-review flag, never one fewer.
    """
    try:
        resp = requests.get(
            f"{API}/repos/{owner}/{repo}/collaborators/{user}/permission",
            headers=headers,
            timeout=30,
        )
    except requests.RequestException as exc:
        print(f"permission lookup for {user} failed ({exc}); treating as untrusted.")
        return False
    if resp.status_code != 200:
        print(
            f"permission lookup for {user} returned HTTP {resp.status_code}; "
            "treating as untrusted. Grant the workflow token `administration: read` "
            "to make this check authoritative."
        )
        return False
    try:
        permission = (resp.json() or {}).get("permission", "")
    except ValueError:
        print(f"permission lookup for {user} returned non-JSON; treating as untrusted.")
        return False
    return permission in ("admin", "write", "maintain")


def fetch_changed_files(owner: str, repo: str, pr_number: int, headers: dict) -> list[str]:
    """Every path the PR touches, INCLUDING the pre-rename path.

    GitHub's pull-files object carries `previous_filename` on a rename. Reading
    only `filename` let `scripts/bounty_payout.py` -> `docs/payout-notes.py`
    present as a single non-protected path.
    """
    paths: list[str] = []
    page = 1
    while True:
        resp = requests.get(
            f"{API}/repos/{owner}/{repo}/pulls/{pr_number}/files",
            headers=headers,
            params={"per_page": 100, "page": page},
            timeout=30,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        for item in batch:
            for key in ("filename", "previous_filename"):
                value = item.get(key)
                if value:
                    paths.append(value)
        if len(batch) < 100:
            break
        page += 1
    return paths


def ensure_label(owner: str, repo: str, headers: dict) -> None:
    resp = requests.get(f"{API}/repos/{owner}/{repo}/labels/{LABEL_NAME}", headers=headers, timeout=30)
    if resp.status_code == 200:
        return
    requests.post(
        f"{API}/repos/{owner}/{repo}/labels",
        headers=headers,
        json={"name": LABEL_NAME, "color": LABEL_COLOR, "description": LABEL_DESCRIPTION},
        timeout=30,
    )


def apply_label(owner: str, repo: str, pr_number: int, headers: dict) -> None:
    ensure_label(owner, repo, headers)
    requests.post(
        f"{API}/repos/{owner}/{repo}/issues/{pr_number}/labels",
        headers=headers,
        json={"labels": [LABEL_NAME]},
        timeout=30,
    )


def post_comment(owner: str, repo: str, pr_number: int, protected_hits: Iterable[str], author: str, headers: dict) -> None:
    hits = sorted(protected_hits)
    hit_list = "\n".join(f"- `{p}`" + ("  **(payout/CI-executed)**" if is_money_path(p) else "") for p in hits)
    body = (
        "**guard-bounty-pr**: this PR is from a first-time/non-collaborator "
        f"contributor (`{author}`) and touches automation or payout-critical paths:\n\n"
        f"{hit_list}\n\n"
        "Bounty/onboarding submissions are normally expected to add their own "
        "content (docs, a submissions/ entry, a small standalone script, etc.), "
        "not modify existing CI workflows, `.github/scripts/`, `scripts/`, or "
        "the bounty ledger/registry files. This is exactly the pattern seen in "
        "#14981, where a \"solution\" PR replaced working automation scripts "
        "with stubs.\n\n"
        "This is **not** an automatic rejection -- a maintainer needs to look "
        "at the diff before this merges. If the changes to these paths are "
        "legitimate and intentional, a maintainer can dismiss this and merge "
        "normally."
    )
    requests.post(
        f"{API}/repos/{owner}/{repo}/issues/{pr_number}/comments",
        headers=headers,
        json={"body": body},
        timeout=30,
    )


def main() -> None:
    github_token = os.environ.get("GITHUB_TOKEN", "")
    if not github_token:
        sys.exit("GITHUB_TOKEN environment variable is required")

    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not event_path or not os.path.exists(event_path):
        sys.exit("GITHUB_EVENT_PATH not found -- this script must run inside a pull_request(_target) job")

    repo_slug = os.environ.get("GITHUB_REPOSITORY", "Scottcjn/rustchain-bounties")
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    with open(event_path, encoding="utf-8") as f:
        event = json.load(f)

    pr = event.get("pull_request")
    if not pr:
        print("No pull_request in event payload, nothing to do.")
        return

    owner, repo = repo_slug.split("/", 1)
    pr_number = pr["number"]
    author = pr["user"]["login"]
    association = (pr.get("author_association") or "NONE").upper()

    # Derived from the checked-out BASE tree (the workflow checks out
    # base.sha, never the PR head), so this reflects trusted content.
    discovered = load_action_dirs(os.environ.get("GITHUB_WORKSPACE") or ".")
    if discovered:
        print(f"CI-executed directories discovered in the base tree: {', '.join(discovered)}")

    if association in ROLE_ASSOCIATIONS:
        print(f"Author {author} has association {association} (repository role) -- skipping guard.")
        return

    changed = fetch_changed_files(owner, repo, pr_number, headers)
    protected_hits = [p for p in changed if is_protected_path(p)]

    if not protected_hits:
        print(f"Author {author} ({association}) touched no protected paths -- skipping guard.")
        return

    money_hits = [p for p in protected_hits if is_money_path(p)]

    if association in TRUSTED_ASSOCIATIONS and not money_hits:
        # Ordinary automation maintenance from someone who has landed a commit
        # here before (#14546). Flagging this would be noise.
        print(f"Author {author} ({association}) touched protected but non-money paths -- skipping guard.")
        return

    if association in TRUSTED_ASSOCIATIONS and money_hits:
        # CONTRIBUTOR is one merged commit, not a permission. On money paths
        # the exemption has to be earned by a real permission, checked now.
        if has_write_access(owner, repo, author, headers):
            print(f"Author {author} has verified write permission -- skipping guard.")
            return
        print(
            f"Author {author} ({association}) has no verified write permission and "
            f"touched {len(money_hits)} payout/CI-executed path(s) -- guard applies."
        )

    print(f"Author {author} ({association}) touched protected paths:")
    for p in protected_hits:
        print(f"  - {p}{'  (payout/CI-executed)' if is_money_path(p) else ''}")

    post_comment(owner, repo, pr_number, protected_hits, author, headers)
    apply_label(owner, repo, pr_number, headers)

    sys.exit(
        "guard-bounty-pr: PR from a non-collaborator touches protected "
        "automation/payout paths -- flagged for maintainer review "
        f"(see {len(protected_hits)} path(s) above and the PR comment)."
    )


if __name__ == "__main__":
    main()
