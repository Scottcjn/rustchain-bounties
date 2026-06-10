# Code Review Bounty Claim - #73

Claimant: `jonasxzb`

Bounty: Scottcjn/rustchain-bounties#73

Wallet ID: `jonasxzb`

Status: submitted for maintainer assessment. The original #73 issue is not accepting new comments, so this PR records the claim.

## Review Submitted

### Scottcjn/bottube#1197 - Changes Requested

Review: https://github.com/Scottcjn/bottube/pull/1197#pullrequestreview-4397895297

Summary:

- Re-checked updated head `f4fa0e47f3927b27c2b80f91726b397116430078` after a previous reviewer-requested fix.
- Verified the earlier falsy non-object JSON issue is now covered by the PR's focused tests.
- Found a remaining comment JSON validation blocker: `parent_id` is still accepted without type validation.
- Reproduced 500 responses for malformed `parent_id` payloads:
  - API route: `parent_id=[]` and `parent_id={}` reach SQLite and raise binding errors.
  - Web route: `parent_id=[]`, `parent_id={}`, and `parent_id="abc"` raise `TypeError` or `ValueError` during `int(parent_id)`.
- Requested a shared optional parent-id parser that accepts integers or digit strings and returns 400 for list/dict/booleans/non-numeric strings, with regressions on both comment routes.

## Local Verification Evidence

Commands run:

```bash
git diff --check origin/main...HEAD
python3 -m py_compile bottube_server.py tests/test_comment_input_validation.py
.venv/bin/python -m pytest tests/test_comment_input_validation.py -q
```

Focused pytest result:

```text
6 passed, 3 warnings in 0.64s
```

Local Flask probe result:

```text
api parent_id=[] -> 500
api parent_id={} -> 500
api parent_id="abc" -> 404 Parent comment not found
web parent_id=[] -> 500
web parent_id={} -> 500
web parent_id="abc" -> 500
```

## Reward Request

Please assess this under the #73 code review reward structure as one substantive changes-requested review.

Reference rate in #73: `1 RTC = $0.10 USD`. At the posted minimum of 5 RTC per accepted review, this claim requests 5 RTC / $0.50 equivalent.
