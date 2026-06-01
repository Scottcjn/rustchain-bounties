# Code Review Bounty Claim: BoTTube PR #1292

- Reviewer: github:JONASXZB
- Bounty issue: https://github.com/Scottcjn/rustchain-bounties/issues/73
- Onboarding review claim: https://github.com/Scottcjn/rustchain-bounties/issues/2782#issuecomment-4588701867
- Reviewed PR: https://github.com/Scottcjn/bottube/pull/1292
- Review: https://github.com/Scottcjn/bottube/pull/1292#pullrequestreview-4397843202
- Reviewed head: `06337df500993b1117a25a2c7c57a44e8ad6b8e3`
- Decision: Approved

## What I Reviewed

- `base.html`
- `bottube_templates/base.html`
- `bottube_server.py`
- `tests/test_language_switch_and_csp.py`
- `tests/test_watch_tracking_and_csp.py`

## Substantive Observations

1. The language-switch fix replaces hard-coded `?lang=...` footer links with `language_switch_href(lc)`, so search pages keep active filters such as `/search?q=rustchain&page=2` when changing locale.
2. `_language_switch_href()` copies the current request query parameters and replaces only `lang`, which keeps the fix narrow and avoids changing unrelated search, paging, or filter state.
3. The CSP change updates both the runtime response header and the template meta policy to allow `https://www.google.com` in `connect-src`, matching the observed Google Analytics `/g/collect` request while preserving the existing GA and Tag Manager origins.
4. The new tests cover the query-preservation behavior, the no-query homepage behavior, and both CSP definitions.

## Verification

- `git diff --check` passed.
- `python3 -m compileall bottube_server.py` passed.
- `uv` was not installed locally, so I used a temporary venv and ran:
  `.venv/bin/python -m pytest tests/test_watch_tracking_and_csp.py tests/test_language_switch_and_csp.py -q`
- Result: `6 passed`.

## Disclosure

I received RTC compensation for this review.
