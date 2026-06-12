Experiment, AI-assisted review claim for code review bounty #73.

Reviewed PR: https://github.com/Scottcjn/Rustchain/pull/5923
Bounty context: Scottcjn/rustchain-bounties#71, reviewed under code review bounty #73.

Review result: no blocking issue found.

Review notes:
- The PR routes documented dict-returning async SDK endpoints through `_get_object()` / `_post_object()` so scalar/list JSON does not flow into callers that expect dicts.
- The list-style helpers still tolerate both legacy bare-list responses and envelope objects, which preserves the API compatibility this client already had.
- Regression coverage includes the important crash class for `/health` returning non-object JSON and `/miners` returning a scalar response.

Non-blocking follow-up: the list helpers return `[]` for malformed envelopes like `{"miners": "bad"}`. That is acceptable for the current crash-prevention scope, but maintainers may later prefer strict `APIError` semantics for malformed envelopes.

Payout preference if direct payout is available: PayPal https://www.paypal.com/paypalme/whathestock or ERC20 USDC 0x3a2719e116c9C69a2514F3F7287b4AAAb13B9726.
