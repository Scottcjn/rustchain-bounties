#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 submissions/16512-gaussagent-high-value-research/validate_submission.py
python3 -m pytest tests/test_gaussagent_high_value_research.py -q
python3 tools/bcos_spdx_check.py --base-ref origin/main
