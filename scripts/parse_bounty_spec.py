#!/usr/bin/env python3
"""parse_bounty_spec.py — single source of truth for reading a bounty's
machine-readable spec out of a GitHub issue body.

Convention: a bounty issue contains ONE fenced block:

    ```bounty-spec
    paid: true
    reward_rtc: 7
    per: per-item        # one-time | per-item | per-pr
    cap: 1               # max payouts (multi-claim faucet guard)
    submit: [pr, email]  # pr | comment | email
    not_in_repo: true    # asset/code must not already exist in target repo
    target_repo: Scottcjn/xonotic-rustchain
    review_rubric: { min_findings: 2, line_level: true, already_merged_ok: false }
    ```

THE RULE: no `bounty-spec` block, or `paid: false`  =>  NOT PAYABLE.
That alone kills "claimed a feature-request issue" (#14041/#14047).

Used by: (1) agents deciding what/how to submit, (2) the payout pipeline
(refuse if not payable / enforce cap), (3) the PR-review & claim gate.

No external deps — a tiny YAML-subset parser so it runs anywhere (cron, CI,
the node box) without pip installs.
"""
from __future__ import annotations
import re, json, sys

FENCE = re.compile(r"```bounty-spec\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)

def _coerce(v: str):
    v = v.strip()
    if v.lower() in ("true", "yes"): return True
    if v.lower() in ("false", "no"): return False
    if re.fullmatch(r"-?\d+", v): return int(v)
    if re.fullmatch(r"-?\d+\.\d+", v): return float(v)
    if v.startswith("[") and v.endswith("]"):
        return [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
    if v.startswith("{") and v.endswith("}"):
        out = {}
        for pair in v[1:-1].split(","):
            if ":" in pair:
                k, val = pair.split(":", 1)
                out[k.strip()] = _coerce(val)
        return out
    return v.strip("'\"")

def parse_bounty_spec(issue_body: str) -> dict | None:
    """Return the spec dict, or None if the issue has no bounty-spec block."""
    if not issue_body:
        return None
    m = FENCE.search(issue_body)
    if not m:
        return None
    spec = {}
    for line in m.group(1).splitlines():
        line = line.split("#", 1)[0].rstrip()  # strip inline comments
        if not line.strip() or ":" not in line:
            continue
        key, val = line.split(":", 1)
        spec[key.strip()] = _coerce(val)
    return spec

def is_payable(spec: dict | None) -> tuple[bool, str]:
    """The one rule that fixes no-reward claims."""
    if spec is None:
        return False, "no bounty-spec block (not a paid bounty)"
    if not spec.get("paid", False):
        return False, "bounty-spec paid:false"
    if not spec.get("reward_rtc"):
        return False, "no reward_rtc"
    return True, "payable"

if __name__ == "__main__":
    # CLI: echo "$ISSUE_BODY" | parse_bounty_spec.py   -> prints JSON spec + payable verdict
    body = sys.stdin.read() if not sys.stdin.isatty() else (open(sys.argv[1]).read() if len(sys.argv) > 1 else "")
    spec = parse_bounty_spec(body)
    ok, why = is_payable(spec)
    print(json.dumps({"spec": spec, "payable": ok, "reason": why}, ensure_ascii=False, indent=2))
