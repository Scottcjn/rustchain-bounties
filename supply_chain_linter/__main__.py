#!/usr/bin/env python3
"""
Supply Chain Hygiene Linter

A security linter that detects:
- Credential leaks (API keys, tokens, passwords)
- Supply chain vulnerabilities
- GitHub Actions security issues
- Dependency problems

Usage:
    python -m supply_chain_linter /path/to/repo
    python -m supply_chain_linter . --output report.json
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueType(Enum):
    CREDENTIAL_LEAK = "credential_leak"
    SUSPICIOUS_PACKAGE = "suspicious_package"
    OUTDATED_DEPENDENCY = "outdated_dependency"
    GITHUB_ACTION_ISSUE = "github_action_issue"
    INSECURE_PATTERN = "insecure_pattern"
    SUPPLY_CHAIN_RISK = "supply_chain_risk"


@dataclass
class LintIssue:
    """Represents a found issue."""
    severity: Severity
    issue_type: IssueType
    message: str
    file_path: str
    line_number: Optional[int] = None
    rule_id: str = ""
    details: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "severity": self.severity.value,
            "issue_type": self.issue_type.value,
            "message": self.message,
            "file": self.file_path,
            "line": self.line_number,
            "rule": self.rule_id,
            "details": self.details,
        }


# ===== Credential Detection Patterns =====

CREDENTIAL_PATTERNS = [
    # Generic API keys
    (r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"][a-zA-Z0-9_-]{20,}['\"]", Severity.CRITICAL, "API key detected"),
    
    # GitHub tokens
    (r"ghp_[a-zA-Z0-9]{36}", Severity.CRITICAL, "GitHub personal access token detected"),
    (r"gho_[a-zA-Z0-9]{36}", Severity.CRITICAL, "GitHub OAuth token detected"),
    (r"ghu_[a-zA-Z0-9]{36}", Severity.CRITICAL, "GitHub user-to-server token detected"),
    (r"ghs_[a-zA-Z0-9]{36}", Severity.CRITICAL, "GitHub server-to-server token detected"),
    
    # AWS keys
    (r"AKIA[0-9A-Z]{16}", Severity.CRITICAL, "AWS access key detected"),
    
    # Private keys
    (r"-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----", Severity.CRITICAL, "Private key detected"),
    
    # Generic secrets
    (r"(?i)(secret|password|passwd|pwd|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]", Severity.HIGH, "Potential secret detected"),
    
    # Environment variables with secrets
    (r"export\s+(API_KEY|SECRET|PASSWORD|TOKEN)=", Severity.HIGH, "Secret in environment export"),
    
    # JWT tokens
    (r"eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+", Severity.HIGH, "JWT token detected"),
]

# ===== GitHub Actions Patterns =====

GITHUB_ACTION_ISSUES = [
    # Untrusted actions (no pinned version)
    (r"uses:\s+[\w-]+/[\w-]+@[\w.-]+$", Severity.MEDIUM, "Action not pinned to commit SHA"),
    (r"uses:\s+[\w-]+/[\w-]+$", Severity.MEDIUM, "Action without version (use SHA)"),
    
    # Permissions issues
    (r"permissions:\s*\{\}", Severity.LOW, "No permissions specified"),
    (r"contents:\s*read", Severity.LOW, "Unnecessary read permission"),
    
    # Secrets in workflow
    (r"\$\{\{\s*secrets\.[A-Z_]+\}\}", Severity.MEDIUM, "Using secrets in workflow"),
]

# ===== Dependency Patterns =====

SUSPICIOUS_PACKAGES = [
    "request",  # Deprecated, use requests
    "http Request", 
    "eval",
    "exec",
    "subprocess",
    "os.system",
]

OUTDATED_BETA_PATTERNS = [
    r"beta",
    r"alpha", 
    r"dev",
    r"rc\d+",
]


# ===== Linter =====

class SupplyChainLinter:
    """Main linter class."""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.issues: List[LintIssue] = []
        self.files_scanned = 0
        
    def scan(self) -> List[LintIssue]:
        """Scan the repository."""
        if not self.repo_path.exists():
            self.issues.append(LintIssue(
                severity=Severity.CRITICAL,
                issue_type=IssueType.SUPPLY_CHAIN_RISK,
                message=f"Repository path does not exist: {self.repo_path}",
                file_path=str(self.repo_path),
                rule_id="REPO_NOT_FOUND"
            ))
            return self.issues
        
        # Scan different file types
        self._scan_github_actions()
        self._scan_credential_patterns()
        self._scan_dependency_files()
        self._scan_scripts()
        
        return self.issues
    
    def _scan_github_actions(self):
        """Scan GitHub Actions workflows."""
        workflows_dir = self.repo_path / ".github" / "workflows"
        if not workflows_dir.exists():
            return
        
        for workflow_file in workflows_dir.glob("*.yml"):
            self.files_scanned += 1
            content = workflow_file.read_text()
            
            # Check for unpinned actions
            for line_num, line in enumerate(content.splitlines(), 1):
                # Unpinned action
                if re.search(r"uses:\s+[\w-]+/[\w-]+$", line):
                    self.issues.append(LintIssue(
                        severity=Severity.MEDIUM,
                        issue_type=IssueType.GITHUB_ACTION_ISSUE,
                        message="Action without version - pin to commit SHA for security",
                        file_path=str(workflow_file.relative_to(self.repo_path)),
                        line_number=line_num,
                        rule_id="GHA001"
                    ))
                
                # No permissions set
                if "permissions:" in line and "permissions: {}" in content:
                    self.issues.append(LintIssue(
                        severity=Severity.LOW,
                        issue_type=IssueType.GITHUB_ACTION_ISSUE,
                        message="No permissions specified in workflow",
                        file_path=str(workflow_file.relative_to(self.repo_path)),
                        line_number=line_num,
                        rule_id="GHA002"
                    ))
    
    def _scan_credential_patterns(self):
        """Scan for credential leaks."""
        extensions = {".py", ".js", ".ts", ".json", ".yml", ".yaml", ".sh", ".env"}
        
        for ext in extensions:
            for file_path in self.repo_path.rglob(f"*{ext}"):
                # Skip node_modules, .git, etc
                if any(skip in str(file_path) for skip in [".git", "node_modules", "__pycache__", ".venv"]):
                    continue
                
                self.files_scanned += 1
                self._scan_file_for_credentials(file_path)
    
    def _scan_file_for_credentials(self, file_path: Path):
        """Scan a single file for credentials."""
        try:
            content = file_path.read_text()
        except (UnicodeDecodeError, PermissionError):
            return
        
        for line_num, line in enumerate(content.splitlines(), 1):
            for pattern, severity, message in CREDENTIAL_PATTERNS:
                if re.search(pattern, line):
                    self.issues.append(LintIssue(
                        severity=severity,
                        issue_type=IssueType.CREDENTIAL_LEAK,
                        message=message,
                        file_path=str(file_path.relative_to(self.repo_path)),
                        line_number=line_num,
                        rule_id="CRED001"
                    ))
    
    def _scan_dependency_files(self):
        """Scan dependency files."""
        dep_files = [
            "requirements.txt",
            "package.json",
            "Pipfile",
            "poetry.lock",
            "package-lock.json",
            "yarn.lock",
            "Cargo.toml",
            "go.mod",
        ]
        
        for dep_file in dep_files:
            file_path = self.repo_path / dep_file
            if file_path.exists():
                self.files_scanned += 1
                self._scan_dep_file(file_path)
    
    def _scan_dep_file(self, file_path: Path):
        """Scan a dependency file."""
        try:
            content = file_path.read_text()
        except (UnicodeDecodeError, PermissionError):
            return
        
        # Check for suspicious packages
        for line in content.splitlines():
            for pkg in SUSPICIOUS_PACKAGES:
                if pkg in line.lower() and not line.startswith("#"):
                    self.issues.append(LintIssue(
                        severity=Severity.MEDIUM,
                        issue_type=IssueType.SUSPICIOUS_PACKAGE,
                        message=f"Suspicious package reference: {pkg}",
                        file_path=str(file_path.relative_to(self.repo_path)),
                        rule_id="DEP001"
                    ))
    
    def _scan_scripts(self):
        """Scan script files."""
        script_extensions = {".py", ".sh", ".js", ".ts"}
        
        for ext in script_extensions:
            for file_path in self.repo_path.rglob(f"*{ext}"):
                if any(skip in str(file_path) for skip in [".git", "__pycache__"]):
                    continue
                
                # Skip test files
                if "test" in file_path.name.lower():
                    continue
                
                self.files_scanned += 1
                self._scan_script_file(file_path)
    
    def _scan_script_file(self, file_path: Path):
        """Scan a script file for issues."""
        try:
            content = file_path.read_text()
        except (UnicodeDecodeError, PermissionError):
            return
        
        # Check for dangerous patterns
        dangerous_patterns = [
            (r"os\.system\s*\(", "os.system() call - potential command injection"),
            (r"subprocess\.(call|run|shell)", "subprocess call - validate inputs"),
            (r"eval\s*\(", "eval() call - potential code injection"),
            (r"exec\s*\(", "exec() call - potential code injection"),
        ]
        
        for line_num, line in enumerate(content.splitlines(), 1):
            for pattern, message in dangerous_patterns:
                if re.search(pattern, line):
                    self.issues.append(LintIssue(
                        severity=Severity.HIGH,
                        issue_type=IssueType.INSECURE_PATTERN,
                        message=message,
                        file_path=str(file_path.relative_to(self.repo_path)),
                        line_number=line_num,
                        rule_id="SCRIPT001"
                    ))
    
    def get_summary(self) -> Dict:
        """Get summary of issues."""
        return {
            "files_scanned": self.files_scanned,
            "total_issues": len(self.issues),
            "by_severity": {
                "critical": len([i for i in self.issues if i.severity == Severity.CRITICAL]),
                "high": len([i for i in self.issues if i.severity == Severity.HIGH]),
                "medium": len([i for i in self.issues if i.severity == Severity.MEDIUM]),
                "low": len([i for i in self.issues if i.severity == Severity.LOW]),
            },
            "by_type": {
                "credential_leak": len([i for i in self.issues if i.issue_type == IssueType.CREDENTIAL_LEAK]),
                "github_action": len([i for i in self.issues if i.issue_type == IssueType.GITHUB_ACTION_ISSUE]),
                "suspicious_package": len([i for i in self.issues if i.issue_type == IssueType.SUSPICIOUS_PACKAGE]),
                "insecure_pattern": len([i for i in self.issues if i.issue_type == IssueType.INSECURE_PATTERN]),
            }
        }


def main():
    parser = argparse.ArgumentParser(
        description="Supply Chain Hygiene Linter"
    )
    parser.add_argument(
        "path",
        help="Path to repository to scan"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file (JSON)"
    )
    parser.add_argument(
        "--severity",
        choices=["critical", "high", "medium", "low"],
        help="Minimum severity to report"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    # Run linter
    linter = SupplyChainLinter(args.path)
    issues = linter.scan()
    summary = linter.get_summary()
    
    # Filter by severity
    if args.severity:
        severity_order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]
        min_idx = severity_order.index(Severity(args.severity))
        issues = [i for i in issues if severity_order.index(i.severity) <= min_idx]
    
    # Output
    if args.format == "json":
        output = {
            "summary": summary,
            "issues": [i.to_dict() for i in issues]
        }
        
        if args.output:
            Path(args.output).write_text(json.dumps(output, indent=2))
            print(f"Report written to: {args.output}")
        else:
            print(json.dumps(output, indent=2))
    else:
        # Text output
        print(f"\n{'='*60}")
        print("SUPPLY CHAIN HYGIENE LINTER REPORT")
        print(f"{'='*60}")
        print(f"\nFiles scanned: {summary['files_scanned']}")
        print(f"Total issues: {summary['total_issues']}")
        
        print("\nBy Severity:")
        for sev, count in summary['by_severity'].items():
            if count > 0:
                print(f"  {sev.upper()}: {count}")
        
        print("\nBy Type:")
        for itype, count in summary['by_type'].items():
            if count > 0:
                print(f"  {itype}: {count}")
        
        if issues:
            print(f"\n{'='*60}")
            print("ISSUES FOUND")
            print(f"{'='*60}")
            
            for issue in issues:
                location = f"{issue.file_path}"
                if issue.line_number:
                    location += f":{issue.line_number}"
                
                print(f"\n[{issue.severity.value.upper()}] {issue.message}")
                print(f"  File: {location}")
                print(f"  Rule: {issue.rule_id}")
        
        print(f"\n{'='*60}")
        
        # Exit code based on severity
        if summary['by_severity']['critical'] > 0:
            sys.exit(2)
        elif summary['by_severity']['high'] > 0:
            sys.exit(1)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
