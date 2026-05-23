# Code Review Bounty Claim: BoTTube PR #1214

## Claimant

- Reviewer: `@JacKane21`
- Wallet: `RTC7539aeed433526eba7f5a393b1bd455fcd48af176ec4e67d0f7f10cfa477175d`
- Bounty: Scottcjn/rustchain-bounties#73

## Review Submitted

- Repository: `Scottcjn/bottube`
- Pull request: https://github.com/Scottcjn/bottube/pull/1214
- Review: https://github.com/Scottcjn/bottube/pull/1214#pullrequestreview-4349506352
- Head commit reviewed: `344b10fc8282c8d011c1358af78f1649ca39c295`
- Review outcome: changes requested

## Finding Summary

The PR fixes several malformed JSON crashes in admin referral and badge
endpoints, but one malformed-body path remains in the same endpoint family.

`POST /api/admin/badges/assign` validates the top-level JSON body and
`badge_key`, but still passes unvalidated `agent_name` into
`_resolve_badge_target_agent()`. That helper performs `.strip()` on
`agent_name`, so a request with a valid `badge_key` and list-valued
`agent_name` still raises `AttributeError` before returning a deterministic
400 response.

Reproduction payload:

```json
{
  "agent_name": ["badgeguy"],
  "badge_key": "early_human_bottube"
}
```

I requested validation for `agent_name` before calling
`_resolve_badge_target_agent()`, or moving that validation into the helper so
all callers receive the same protection.

## Validation Performed

- `uv run --no-project --with pytest --with flask --with requests --with python-dotenv --with pillow --with qrcode --with pytest-cov python -m pytest -p no:cacheprovider tests/test_malformed_json_admin.py -q` -> 10 passed
- `uv run --no-project --with flask --with requests --with python-dotenv --with pillow --with qrcode python -m py_compile bottube_server.py tests/test_malformed_json_admin.py` -> passed
- `git diff --check origin/main...HEAD` -> passed

## Reward Request

Please assess this review under bounty issue #73. Direct issue-comment claims
are unavailable because GitHub disables comments after 2500 comments, so this
PR is the fallback claim path.
