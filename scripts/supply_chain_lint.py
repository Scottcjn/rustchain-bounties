#!/usr/bin/env python3
"""
Supply-Chain Hygiene Linter for RustChain Bounties.

Checks docs, templates, workflows, and scripts for risky install patterns,
validates bounty issue template fields, and verifies PR template structure.

Usage:
    python scripts/supply_chain_lint.py           # Run with warnings
    python scripts/supply_chain_lint.py --strict   # Fail on any violation
    python scripts/supply_chain_lint.py --dry-run  # Show what would be checked

Reference: docs/BOUNTY_HYGIENE.md, SECURITY.md
Bounty: #352
"""

import argparse
import os
import re
import sys

try:
    import yaml
except ImportError:
    yaml = None

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWLIST_PATH = os.path.join(REPO_ROOT, ".github", "supply-chain-allowlist.yml")

# File extensions to scan for risky patterns
SCAN_EXTENSIONS = {
    ".md", ".yml", ".yaml", ".sh", ".bash", ".py", ".js", ".ts",
    ".txt", ".rst", ".html", ".toml", ".cfg", ".ini",
}

# Directories to skip entirely
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
}

# Risky install patterns — each is (regex, human description)
RISKY_PATTERNS = [
    (r"curl\s+[^|]*\|\s*(?:ba)?sh", "curl piped to shell (curl | bash)"),
    (r"wget\s+[^|]*\|\s*(?:ba)?sh", "wget piped to shell (wget | sh)"),
    (r"curl\s+[^|]*\|\s*sudo\s+(?:ba)?sh", "curl piped to sudo shell"),
    (r"wget\s+[^|]*\|\s*sudo\s+(?:ba)?sh", "wget piped to sudo shell"),
    (r"curl\s+[^|]*\|\s*python", "curl piped to python"),
    (r"wget\s+[^|]*\|\s*python", "wget piped to python"),
    (r"curl\s+[^|]*\|\s*perl", "curl piped to perl"),
    (r"curl\s+[^|]*\|\s*ruby", "curl piped to ruby"),
]

# Required fields in bounty issue template
BOUNTY_TEMPLATE_REQUIRED_FIELDS = ["target", "supply_chain", "disclosure"]

# Required section in PR template
PR_TEMPLATE_REQUIRED_SECTION = "Supply-Chain Proof"

# ---------------------------------------------------------------------------
# Allowlist loading
# ---------------------------------------------------------------------------


def load_allowlist(path):
    """Load the allowlist file. Returns dict with 'files' and 'patterns' keys."""
    default = {"files": [], "patterns": []}
    if not os.path.exists(path):
        return default

    if yaml is None:
        # Fallback: parse simple YAML-like structure without pyyaml
        allowlist = {"files": [], "patterns": []}
        current_key = None
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("files:"):
                    current_key = "files"
                elif stripped.startswith("patterns:"):
                    current_key = "patterns"
                elif stripped.startswith("- ") and current_key:
                    val = stripped[2:].strip().strip('"').strip("'")
                    allowlist[current_key].append(val)
        return allowlist

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return {
        "files": data.get("files") or [],
        "patterns": data.get("patterns") or [],
    }


def is_allowlisted(filepath, line, allowlist):
    """Check if a specific finding is allowlisted."""
    rel = os.path.relpath(filepath, REPO_ROOT).replace("\\", "/")
    if rel in allowlist.get("files", []):
        return True
    for pattern in allowlist.get("patterns", []):
        if re.search(pattern, line):
            return True
    return False


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def scan_risky_patterns(allowlist):
    """Scan all eligible files for risky install patterns."""
    findings = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        # Prune skipped directories
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        for fname in filenames:
            _, ext = os.path.splitext(fname)
            if ext.lower() not in SCAN_EXTENSIONS:
                continue

            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    for lineno, line in enumerate(f, 1):
                        for regex, desc in RISKY_PATTERNS:
                            if re.search(regex, line, re.IGNORECASE):
                                if not is_allowlisted(fpath, line, allowlist):
                                    rel = os.path.relpath(fpath, REPO_ROOT)
                                    findings.append({
                                        "file": rel.replace("\\", "/"),
                                        "line": lineno,
                                        "pattern": desc,
                                        "content": line.strip()[:120],
                                    })
            except (OSError, UnicodeDecodeError):
                continue

    return findings


def check_bounty_template():
    """Verify bounty issue template has required fields."""
    template_path = os.path.join(
        REPO_ROOT, ".github", "ISSUE_TEMPLATE", "bounty.yml"
    )
    if not os.path.exists(template_path):
        return [{"issue": "Bounty issue template not found at .github/ISSUE_TEMPLATE/bounty.yml"}]

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    if yaml is not None:
        data = yaml.safe_load(content) or {}
        field_ids = set()
        for item in data.get("body", []):
            if "id" in item:
                field_ids.add(item["id"])
    else:
        # Fallback: regex-based field detection
        field_ids = set(re.findall(r"^\s+id:\s*(\w+)", content, re.MULTILINE))

    missing = []
    for field in BOUNTY_TEMPLATE_REQUIRED_FIELDS:
        if field not in field_ids:
            missing.append({
                "issue": f"Bounty template missing required field: '{field}'",
                "remediation": f"Add a form field with id: {field} to .github/ISSUE_TEMPLATE/bounty.yml",
            })

    return missing


def check_pr_template():
    """Verify PR template includes Supply-Chain Proof section."""
    pr_path = os.path.join(
        REPO_ROOT, ".github", "PULL_REQUEST_TEMPLATE.md"
    )
    if not os.path.exists(pr_path):
        return [{"issue": "PR template not found at .github/PULL_REQUEST_TEMPLATE.md"}]

    with open(pr_path, "r", encoding="utf-8") as f:
        content = f.read()

    if PR_TEMPLATE_REQUIRED_SECTION.lower() not in content.lower():
        return [{
            "issue": f"PR template missing '{PR_TEMPLATE_REQUIRED_SECTION}' section",
            "remediation": f"Add a '## {PR_TEMPLATE_REQUIRED_SECTION}' section to .github/PULL_REQUEST_TEMPLATE.md",
        }]

    return []


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def print_findings(title, findings, icon="!"):
    """Print findings in a CI-friendly format."""
    if not findings:
        print(f"  PASS  {title}")
        return 0

    print(f"\n  FAIL  {title}")
    for f in findings:
        if "file" in f:
            print(f"  [{icon}] {f['file']}:{f['line']} — {f['pattern']}")
            print(f"      {f['content']}")
            print(f"      Remediation: Remove or allowlist this pattern.")
            print(f"      Allowlist: add file path to .github/supply-chain-allowlist.yml")
        elif "issue" in f:
            print(f"  [{icon}] {f['issue']}")
            if "remediation" in f:
                print(f"      Remediation: {f['remediation']}")
        print()

    return len(findings)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Supply-chain hygiene linter for RustChain bounties"
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Exit with non-zero status on any finding"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be checked without running checks"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  Supply-Chain Hygiene Linter")
    print("  Reference: docs/BOUNTY_HYGIENE.md | SECURITY.md")
    print("=" * 60)
    print()

    if args.dry_run:
        print("DRY RUN — showing check plan:\n")
        print("1. Scan all files for risky install patterns:")
        for regex, desc in RISKY_PATTERNS:
            print(f"   - {desc}")
        print(f"\n2. Verify bounty template fields: {BOUNTY_TEMPLATE_REQUIRED_FIELDS}")
        print(f"\n3. Verify PR template has '{PR_TEMPLATE_REQUIRED_SECTION}' section")
        print(f"\n4. Allowlist: {ALLOWLIST_PATH}")
        print(f"\nExtensions scanned: {sorted(SCAN_EXTENSIONS)}")
        print(f"Directories skipped: {sorted(SKIP_DIRS)}")
        return 0

    allowlist = load_allowlist(ALLOWLIST_PATH)
    total_issues = 0

    # Check 1: Risky patterns
    print("[1/3] Scanning for risky install patterns...")
    pattern_findings = scan_risky_patterns(allowlist)
    total_issues += print_findings(
        "Risky install patterns", pattern_findings
    )

    # Check 2: Bounty template
    print("[2/3] Checking bounty issue template fields...")
    template_findings = check_bounty_template()
    total_issues += print_findings(
        "Bounty template fields", template_findings
    )

    # Check 3: PR template
    print("[3/3] Checking PR template structure...")
    pr_findings = check_pr_template()
    total_issues += print_findings(
        "PR template Supply-Chain Proof section", pr_findings
    )

    # Summary
    print()
    print("=" * 60)
    if total_issues == 0:
        print(f"  All checks passed.")
    else:
        print(f"  {total_issues} issue(s) found.")
        if args.strict:
            print("  Strict mode: failing CI.")
    print("=" * 60)

    if args.strict and total_issues > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
