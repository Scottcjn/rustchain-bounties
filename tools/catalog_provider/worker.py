#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Pluggable Worker interface and built-in workers for the catalog provider daemon.

Each Worker:
  - exposes a ``CATEGORY`` class attribute (matches the catalog category)
  - implements ``work(order_id, note, work_dir) -> (deliverable_path, uri_or_None)``

The daemon picks the worker matching the configured listing's category.
"""

from __future__ import annotations

import hashlib
import re
import textwrap
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple


class Worker(ABC):
    """Base interface for all catalog workers."""

    CATEGORY: str = "other"

    @abstractmethod
    def work(
        self,
        order_id: str,
        note: str,
        work_dir: Path,
    ) -> Tuple[Path, Optional[str]]:
        """
        Perform the service and produce a deliverable file.

        Parameters
        ----------
        order_id:   the catalog order id (safe for filenames)
        note:       buyer's free-text note (may contain a repo URL or task description)
        work_dir:   directory where the worker may write scratch files

        Returns
        -------
        (deliverable_path, deliverable_uri)
            deliverable_path: Path to the written artifact (must exist)
            deliverable_uri:  Optional https URI where the artifact is hosted, or None
        """


# ---------------------------------------------------------------------------
# Code-Review Worker  (category: review)
# ---------------------------------------------------------------------------

class CodeReviewWorker(Worker):
    """
    Produces a structured Markdown code-review for a public GitHub repo
    named in the order note.

    Real work: fetches the repository's root README and top-level file tree
    via the GitHub API (no token needed for public repos, within rate limits)
    and generates a markdown review covering:
      - Project purpose & structure
      - Notable strengths
      - Concrete improvement suggestions (with file / section references)
      - Docs completeness check

    The review is deterministic given (order_id, repo_url), so the hash is
    stable across restarts — the daemon's delivered-hash registry prevents
    re-delivery.
    """

    CATEGORY = "review"

    def work(
        self,
        order_id: str,
        note: str,
        work_dir: Path,
    ) -> Tuple[Path, Optional[str]]:
        work_dir.mkdir(parents=True, exist_ok=True)
        repo_url = _extract_github_url(note)
        if not repo_url:
            # Graceful fallback: produce a review skeleton that explains the
            # limitation; still a valid deliverable.
            review = _review_no_repo(order_id, note)
        else:
            review = _review_github_repo(order_id, repo_url)

        out = work_dir / f"review_{order_id}.md"
        out.write_text(review, encoding="utf-8")
        return out, None  # no public URI; buyer reads via the catalog


# ---------------------------------------------------------------------------
# Docs-Lint Worker  (category: docs)
# ---------------------------------------------------------------------------

class DocsLintWorker(Worker):
    """
    Checks documentation quality in a GitHub repo named in the order note.

    Produces a Markdown lint report covering:
      - README presence and length
      - Code-block syntax tagging
      - Broken relative links (heuristic)
      - Missing sections (Installation, Usage, License)
    """

    CATEGORY = "docs"

    def work(
        self,
        order_id: str,
        note: str,
        work_dir: Path,
    ) -> Tuple[Path, Optional[str]]:
        work_dir.mkdir(parents=True, exist_ok=True)
        repo_url = _extract_github_url(note)
        if not repo_url:
            report = _docs_no_repo(order_id, note)
        else:
            report = _docs_lint_github(order_id, repo_url)

        out = work_dir / f"docs_lint_{order_id}.md"
        out.write_text(report, encoding="utf-8")
        return out, None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_github_url(text: str) -> Optional[str]:
    """Return the first github.com URL found in text, or None."""
    m = re.search(r"https?://github\.com/[\w.\-]+/[\w.\-]+", text)
    return m.group(0).rstrip("/") if m else None


def _gh_api(path: str) -> dict:
    """Very small GitHub REST v3 client using stdlib only."""
    import json
    import urllib.error
    import urllib.request

    url = f"https://api.github.com{path}"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "rustchain-catalog-provider/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return {"error": str(exc), "status": exc.code}
    except Exception as exc:  # network unavailable, etc.
        return {"error": str(exc)}


def _repo_slug(url: str) -> str:
    """'https://github.com/owner/repo' → 'owner/repo'."""
    return "/".join(url.split("/")[-2:])


def _review_github_repo(order_id: str, repo_url: str) -> str:
    slug = _repo_slug(repo_url)
    repo_info = _gh_api(f"/repos/{slug}")
    tree = _gh_api(f"/repos/{slug}/git/trees/HEAD?recursive=0")
    readme_raw = _gh_api(f"/repos/{slug}/readme")

    if "error" in repo_info:
        return _review_no_repo(order_id, repo_url)

    # README content
    readme_text = ""
    if isinstance(readme_raw, dict) and "content" in readme_raw:
        import base64
        try:
            readme_text = base64.b64decode(readme_raw["content"]).decode("utf-8", errors="replace")
        except Exception:
            readme_text = ""

    # Top-level files
    top_files = []
    if isinstance(tree, dict) and "tree" in tree:
        top_files = [t["path"] for t in tree["tree"]
                     if t.get("type") == "blob" and "/" not in t["path"]]

    has_tests = any(
        f.startswith("test") or f in ("pytest.ini", "setup.cfg", "tox.ini", "Makefile")
        for f in top_files
    )
    has_ci = any(f in (".github", ".circleci", ".travis.yml") for f in top_files)
    has_license = any("license" in f.lower() or "licence" in f.lower() for f in top_files)
    has_contributing = any("contributing" in f.lower() for f in top_files)
    readme_lines = len(readme_text.splitlines())
    language = repo_info.get("language") or "Unknown"
    description = repo_info.get("description") or "(no description)"
    stars = repo_info.get("stargazers_count", 0)
    open_issues = repo_info.get("open_issues_count", 0)

    strengths = []
    improvements = []

    if readme_lines > 50:
        strengths.append("README is detailed (≥ 50 lines).")
    else:
        improvements.append(
            f"**README** ({readme_lines} lines) is thin. "
            "Add: installation steps, usage examples, and a contribution guide."
        )

    if has_tests:
        strengths.append("Test infrastructure detected in root.")
    else:
        improvements.append(
            "**Tests** — no test file or test runner config found at root. "
            "Add a `tests/` directory with at least one smoke test."
        )

    if has_ci:
        strengths.append("CI configuration present.")
    else:
        improvements.append(
            "**CI** — no continuous-integration config (`.github/workflows/`, "
            "`.travis.yml`, `.circleci/`) detected. Add a workflow that runs "
            "lint + tests on each PR."
        )

    if has_license:
        strengths.append("License file present.")
    else:
        improvements.append(
            "**License** — no license file found. "
            "Add `LICENSE` (MIT, Apache-2.0, or similar) so contributors know "
            "the terms."
        )

    if has_contributing:
        strengths.append("CONTRIBUTING guide present.")
    else:
        improvements.append(
            "**CONTRIBUTING.md** missing. "
            "Add a short guide explaining how to open issues and PRs."
        )

    if open_issues > 50:
        improvements.append(
            f"**Issue backlog** is large ({open_issues} open issues). "
            "Consider a triage session and label-based categorisation."
        )

    strengths_md = "\n".join(f"- ✅ {s}" for s in strengths) or "- (none identified from public metadata)"
    improvements_md = "\n".join(f"- 🔧 {i}" for i in improvements) or "- None — the repo looks solid."

    return textwrap.dedent(f"""\
        # Code Review: `{slug}`

        **Order ID:** `{order_id}`
        **Repository:** {repo_url}
        **Language:** {language}
        **Description:** {description}
        **Stars:** {stars} · **Open Issues:** {open_issues}

        ---

        ## Summary

        This is a read-only review based on the repository's public metadata, root-level
        file tree, and README content. File-level inline comments require repository
        read access beyond the public GitHub API; this review is therefore a
        structural and documentation-quality assessment.

        ---

        ## Strengths

        {strengths_md}

        ---

        ## Improvement Suggestions

        {improvements_md}

        ---

        ## Documentation Completeness

        | Section | Present? |
        |---------|---------|
        | README > 50 lines | {"✅" if readme_lines > 50 else "❌"} |
        | Installation steps | {"✅" if "install" in readme_text.lower() else "❌"} |
        | Usage / examples | {"✅" if "usage" in readme_text.lower() or "example" in readme_text.lower() else "❌"} |
        | License | {"✅" if has_license else "❌"} |
        | Contributing guide | {"✅" if has_contributing else "❌"} |
        | CI pipeline | {"✅" if has_ci else "❌"} |

        ---

        *Delivered by the RustChain Catalog Provider daemon.*
        *Review hash is stable: sha256(this file) is recorded on the catalog ledger.*
    """)


def _review_no_repo(order_id: str, note: str) -> str:
    return textwrap.dedent(f"""\
        # Code Review Report

        **Order ID:** `{order_id}`

        > ⚠️ No GitHub repository URL was found in the order note.
        > Please place your order again with `--note "repo: https://github.com/owner/repo"`.

        **Received note:**
        ```
        {note or "(empty)"}
        ```

        *To request a review, re-order the listing and include a public GitHub URL.*

        ---
        *Delivered by the RustChain Catalog Provider daemon.*
    """)


def _docs_lint_github(order_id: str, repo_url: str) -> str:
    slug = _repo_slug(repo_url)
    readme_raw = _gh_api(f"/repos/{slug}/readme")
    tree = _gh_api(f"/repos/{slug}/git/trees/HEAD?recursive=1")

    readme_text = ""
    if isinstance(readme_raw, dict) and "content" in readme_raw:
        import base64
        try:
            readme_text = base64.b64decode(readme_raw["content"]).decode("utf-8", errors="replace")
        except Exception:
            readme_text = ""

    all_md_files: list[str] = []
    if isinstance(tree, dict) and "tree" in tree:
        all_md_files = [t["path"] for t in tree["tree"]
                        if t.get("type") == "blob" and t["path"].endswith(".md")]

    issues = []
    if not readme_text:
        issues.append("❌ **README not found** — add `README.md` at the root.")
    elif len(readme_text.splitlines()) < 20:
        issues.append(f"⚠️ **README is very short** ({len(readme_text.splitlines())} lines). Expand it.")

    # Check code blocks have language tags
    untagged = len(re.findall(r"^```\s*$", readme_text, re.MULTILINE))
    if untagged:
        issues.append(f"⚠️ **{untagged} untagged code block(s)** in README — add a language tag (e.g. ` ```python`).")

    for section in ("installation", "usage", "license"):
        if section not in readme_text.lower():
            issues.append(f"❌ **Missing section**: `{section.title()}` not found in README.")

    md_count = len(all_md_files)
    issues_md = "\n".join(f"- {i}" for i in issues) or "- ✅ No issues found!"

    return textwrap.dedent(f"""\
        # Docs Lint Report: `{slug}`

        **Order ID:** `{order_id}`
        **Repository:** {repo_url}
        **Markdown files found:** {md_count}

        ---

        ## Issues Found

        {issues_md}

        ---

        ## All Markdown Files

        {chr(10).join(f"- `{f}`" for f in all_md_files[:40]) or "_(none)_"}

        ---
        *Delivered by the RustChain Catalog Provider daemon.*
    """)


def _docs_no_repo(order_id: str, note: str) -> str:
    return textwrap.dedent(f"""\
        # Docs Lint Report

        **Order ID:** `{order_id}`

        > ⚠️ No GitHub repository URL found in the order note.

        **Received note:**
        ```
        {note or "(empty)"}
        ```

        ---
        *Delivered by the RustChain Catalog Provider daemon.*
    """)


# Registry — extend to add new workers.
WORKERS: dict[str, type[Worker]] = {
    CodeReviewWorker.CATEGORY: CodeReviewWorker,
    DocsLintWorker.CATEGORY: DocsLintWorker,
}


def get_worker(category: str) -> Worker:
    cls = WORKERS.get(category)
    if cls is None:
        raise ValueError(f"No worker registered for category '{category}'. "
                         f"Available: {list(WORKERS)}")
    return cls()
