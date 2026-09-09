#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate gaussagent #16512 high-value bounty research submission artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
AGENT_JSON = REPO_ROOT / "submissions" / "gaussagent-agent-bounty.json"
PLATFORMS_JSON = ROOT / "platforms.json"
REPORT_MD = ROOT / "research-report.md"

REQUIRED_AGENT_FIELDS = {
    "schema",
    "issue",
    "agent",
    "wallet",
    "bounty_type",
    "title",
    "artifacts",
}
REQUIRED_PLATFORM_FIELDS = {
    "id",
    "name",
    "category",
    "max_bounty_usd",
    "agent_accessibility",
}
VALID_ACCESSIBILITY = {"high", "medium", "low"}
MIN_PLATFORMS = 6
USD_THRESHOLD = 1000
REQUIRED_PLATFORM_IDS = {
    "rustchain-bounties",
    "immunefi",
    "code4rena",
    "huntr",
    "bountybook",
    "hackerone",
}
REQUIRED_TRUE_1000_PATHS = {"immunefi", "code4rena", "huntr", "hackerone"}


def load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected JSON object")
    return data


def validate_agent_metadata(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    missing = REQUIRED_AGENT_FIELDS - set(data)
    if missing:
        errors.append(f"gaussagent-agent-bounty.json missing fields: {sorted(missing)}")
    if data.get("issue") != 16512:
        errors.append("gaussagent-agent-bounty.json issue must be 16512")
    if data.get("agent") != "gaussagent":
        errors.append("gaussagent-agent-bounty.json agent must be 'gaussagent'")
    if data.get("schema") != "rustchain-agent-bounty/v1":
        errors.append("gaussagent-agent-bounty.json schema must be rustchain-agent-bounty/v1")
    wallet = data.get("wallet", "")
    if not isinstance(wallet, str) or not wallet.startswith("0x") or len(wallet) != 42:
        errors.append("gaussagent-agent-bounty.json wallet must be a 42-char 0x address")
    artifacts = data.get("artifacts")
    if isinstance(artifacts, dict):
        for key, rel_path in artifacts.items():
            if not isinstance(rel_path, str):
                errors.append(f"artifacts.{key} must be a string path")
                continue
            full_path = REPO_ROOT / rel_path
            if not full_path.is_file():
                errors.append(f"artifacts.{key} path missing: {rel_path}")
    else:
        errors.append("gaussagent-agent-bounty.json must include an artifacts object")
    return errors


def validate_platforms(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    platforms = data.get("platforms")
    if not isinstance(platforms, list):
        return ["platforms.json must contain a 'platforms' array"]

    if len(platforms) < MIN_PLATFORMS:
        errors.append(f"platforms.json must list at least {MIN_PLATFORMS} platforms")

    if data.get("issue") != 16512:
        errors.append("platforms.json issue must be 16512")
    if data.get("schema") != "rustchain-platform-survey/v1":
        errors.append("platforms.json schema must be rustchain-platform-survey/v1")

    platform_ids = {p.get("id") for p in platforms if isinstance(p, dict)}
    missing_ids = REQUIRED_PLATFORM_IDS - platform_ids
    if missing_ids:
        errors.append(f"platforms.json missing platform ids: {sorted(missing_ids)}")

    high_value_count = 0
    for idx, platform in enumerate(platforms):
        if not isinstance(platform, dict):
            errors.append(f"platforms[{idx}] must be an object")
            continue
        missing = REQUIRED_PLATFORM_FIELDS - set(platform)
        if missing:
            errors.append(f"platforms[{idx}] ({platform.get('id', '?')}) missing: {sorted(missing)}")
        access = platform.get("agent_accessibility")
        if access not in VALID_ACCESSIBILITY:
            errors.append(
                f"platforms[{idx}] ({platform.get('id', '?')}) invalid agent_accessibility: {access!r}"
            )
        max_usd = platform.get("max_bounty_usd", 0)
        if isinstance(max_usd, (int, float)) and max_usd >= USD_THRESHOLD:
            high_value_count += 1

    if high_value_count < 3:
        errors.append(
            f"expected at least 3 platforms with max_bounty_usd >= {USD_THRESHOLD}, found {high_value_count}"
        )

    assessment = data.get("assessment")
    if not isinstance(assessment, dict):
        errors.append("platforms.json must contain an 'assessment' object")
    elif not assessment.get("recommended_next_targets"):
        errors.append("platforms.json assessment must include recommended_next_targets")
    else:
        true_paths = assessment.get("true_1000_usd_paths")
        if not isinstance(true_paths, list):
            errors.append("platforms.json assessment must include true_1000_usd_paths")
        else:
            missing_paths = REQUIRED_TRUE_1000_PATHS - set(true_paths)
            if missing_paths:
                errors.append(
                    f"platforms.json assessment.true_1000_usd_paths missing: {sorted(missing_paths)}"
                )
        if assessment.get("best_for_agents") != "rustchain-bounties":
            errors.append("platforms.json assessment.best_for_agents must be rustchain-bounties")

    return errors


def validate_report() -> List[str]:
    errors: List[str] = []
    if not REPORT_MD.is_file():
        return ["research-report.md is missing"]
    text = REPORT_MD.read_text(encoding="utf-8")
    for keyword in ("Immunefi", "Code4rena", "Huntr", "RustChain"):
        if keyword not in text:
            errors.append(f"research-report.md must mention {keyword}")
    if "#16512" not in text and "16512" not in text:
        errors.append("research-report.md must reference issue 16512")
    return errors


def validate_submission() -> List[str]:
    errors: List[str] = []
    for path in (AGENT_JSON, PLATFORMS_JSON, REPORT_MD):
        if not path.is_file():
            errors.append(f"missing artifact: {path.relative_to(REPO_ROOT)}")
    if errors:
        return errors

    errors.extend(validate_agent_metadata(load_json(AGENT_JSON)))
    errors.extend(validate_platforms(load_json(PLATFORMS_JSON)))
    errors.extend(validate_report())
    return errors


def main() -> int:
    errors = validate_submission()
    if errors:
        print("VALIDATION FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("OK: gaussagent #16512 submission artifacts validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
