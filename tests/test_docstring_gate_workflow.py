#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Behavioral tests for the docstring-gate workflow shell step."""

import os
import re
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "docstring-gate.yml"


def workflow_script():
    lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index("        run: |") + 1
    except ValueError as exc:
        raise AssertionError("could not find docstring-gate run block") from exc
    body = []
    for line in lines[start:]:
        if line and not line.startswith("          "):
            break
        body.append(line[10:] if line else "")
    script = "\n".join(body) + "\n"
    return re.sub(
        r'^single="\$\{\{.*\}\}"$',
        'single="${TEST_SINGLE:-}"',
        script,
        count=1,
        flags=re.MULTILINE,
    )


class WorkflowFailureTests(unittest.TestCase):
    def _run(self, *, single="", gh_exit=0, python_exit=0, gh_output="101"):
        script = workflow_script()
        with tempfile.TemporaryDirectory() as tmp:
            bindir = Path(tmp) / "bin"
            bindir.mkdir()
            for name, body in {
                "gh": f"#!/bin/sh\nprintf '%s\\n' {gh_output!r}\nexit {gh_exit}\n",
                "python3": f"#!/bin/sh\nexit {python_exit}\n",
            }.items():
                path = bindir / name
                path.write_text(body, encoding="utf-8")
                path.chmod(path.stat().st_mode | stat.S_IXUSR)
            env = {
                **os.environ,
                "PATH": f"{bindir}:{os.environ['PATH']}",
                "GH_REPO": "owner/repo",
                "TEST_SINGLE": single,
            }
            return subprocess.run(
                ["bash", "-c", script],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                timeout=20,
            )

    def test_single_issue_failure_is_not_forced_green(self):
        result = self._run(single="123", python_exit=7)
        self.assertNotEqual(result.returncode, 0)

    def test_scheduled_inventory_failure_is_not_an_empty_success(self):
        result = self._run(gh_exit=9)
        self.assertNotEqual(result.returncode, 0)

    def test_scheduled_claim_failure_finishes_red(self):
        result = self._run(python_exit=7)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("docstring gate failed for issue #101", result.stdout)

    def test_successful_scheduled_claim_finishes_green(self):
        result = self._run()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("adjudicated 1 claim(s); 0 failed", result.stdout)


if __name__ == "__main__":
    unittest.main()
