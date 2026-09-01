# SPDX-License-Identifier: MIT

"""Tests for gaussagent #16512 high-value bounty research submission."""

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SUBMISSION_DIR = REPO_ROOT / "submissions" / "16512-gaussagent-high-value-research"
AGENT_JSON = REPO_ROOT / "submissions" / "gaussagent-agent-bounty.json"
PLATFORMS_JSON = SUBMISSION_DIR / "platforms.json"
REPORT_MD = SUBMISSION_DIR / "research-report.md"


def load_validator():
    path = SUBMISSION_DIR / "validate_submission.py"
    spec = importlib.util.spec_from_file_location("gaussagent_validate", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestGaussagentHighValueResearch(unittest.TestCase):
    def test_artifacts_exist(self):
        for path in (AGENT_JSON, PLATFORMS_JSON, REPORT_MD):
            self.assertTrue(path.is_file(), f"missing {path}")

    def test_agent_json_issue_and_agent(self):
        data = json.loads(AGENT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(data["issue"], 16512)
        self.assertEqual(data["agent"], "gaussagent")
        self.assertEqual(data["bounty_type"], "research")
        self.assertEqual(data["schema"], "rustchain-agent-bounty/v1")

    def test_agent_json_artifact_paths_resolve(self):
        data = json.loads(AGENT_JSON.read_text(encoding="utf-8"))
        for rel_path in data["artifacts"].values():
            self.assertTrue((REPO_ROOT / rel_path).is_file(), rel_path)

    def test_platforms_cover_six_categories(self):
        data = json.loads(PLATFORMS_JSON.read_text(encoding="utf-8"))
        platforms = data["platforms"]
        self.assertGreaterEqual(len(platforms), 6)
        ids = {p["id"] for p in platforms}
        for platform_id in (
            "rustchain-bounties",
            "immunefi",
            "code4rena",
            "huntr",
            "bountybook",
            "hackerone",
        ):
            self.assertIn(platform_id, ids)

    def test_high_value_platforms_meet_threshold(self):
        data = json.loads(PLATFORMS_JSON.read_text(encoding="utf-8"))
        high_value = [p for p in data["platforms"] if p["max_bounty_usd"] >= 1000]
        self.assertGreaterEqual(len(high_value), 3)

    def test_rustchain_is_best_for_agents(self):
        data = json.loads(PLATFORMS_JSON.read_text(encoding="utf-8"))
        self.assertEqual(data["assessment"]["best_for_agents"], "rustchain-bounties")

    def test_validator_passes(self):
        mod = load_validator()
        errors = mod.validate_submission()
        self.assertEqual(errors, [], f"validation errors: {errors}")

    def test_recommended_targets_reference_open_issues(self):
        data = json.loads(PLATFORMS_JSON.read_text(encoding="utf-8"))
        issues = {t["issue"] for t in data["assessment"]["recommended_next_targets"]}
        self.assertIn(14089, issues)
        self.assertIn(16271, issues)

    def test_verify_script_exists_and_is_referenced(self):
        data = json.loads(AGENT_JSON.read_text(encoding="utf-8"))
        script = data["verify"]["script"]
        self.assertTrue(script.startswith("submissions/"))
        self.assertFalse(script.startswith("scripts/"))
        full_path = REPO_ROOT / script
        self.assertTrue(full_path.is_file(), script)

    def test_validator_cli_exit_zero(self):
        script = SUBMISSION_DIR / "validate_submission.py"
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("OK:", proc.stdout)


if __name__ == "__main__":
    unittest.main()
