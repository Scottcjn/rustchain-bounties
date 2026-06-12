# Code review claim for PR 5933

Experiment, AI-assisted review claim for code review bounty #73.

Reviewed PR: https://github.com/Scottcjn/Rustchain/pull/5933
Bounty context: https://github.com/Scottcjn/rustchain-bounties/issues/73
Claim PR: https://github.com/Scottcjn/rustchain-bounties/pull/11480

## Review result

Blocking issue found, but direct upstream review/comment posting through the GitHub app returned `403 Resource not accessible by integration`. This claim file records the review publicly in the active claim branch instead.

## Finding

Current head reviewed: `26dd5cdd33cf6b739703c488213f0d912bb630fd`.

The new Agent Miner RPC webhook delivery path can still be used as an SSRF primitive through HTTP redirects. `_fire_webhook()` calls `requests.post(url, json=body, timeout=5)` with the Requests default redirect behavior. Even if the existing hostname/IP validation is fixed to reject loopback, RFC1918, link-local, and metadata hosts at registration time, an attacker-controlled public HTTPS webhook can return a `30x` redirect to `http://127.0.0.1`, `http://169.254.169.254/latest/meta-data`, or another internal service. Requests will follow that redirect unless redirects are disabled or every redirect target is revalidated.

This is separate from the already-reported DNS rebinding issue on PR #5933: DNS rebinding changes the resolved address for the original hostname; redirect-based SSRF changes the destination URL after the first accepted request.

## Suggested fix

- Disable redirects on webhook delivery with `allow_redirects=False`, or implement a redirect policy that validates every `Location` target before following it.
- Keep DNS/IP validation at registration and immediately before delivery.
- Add a regression that mocks a safe-looking webhook URL returning a redirect to loopback or metadata IP and asserts the internal target is never requested.

## Validation

- Reviewed the PR diff for `miners/agent_miner_rpc.py`.
- Reviewed existing PR comments to avoid duplicating the earlier auth, DNS rebinding, and non-object JSON findings.
- Attempted to post the upstream review directly, then attempted a top-level PR comment; both failed with GitHub app `403`, so this claim artifact is the fallback.

## Payout preference

If direct payout is available: PayPal https://www.paypal.com/paypalme/whathestock or ERC20/USDC `0x3a2719e116c9C69a2514F3F7287b4AAAb13B9726`.

If RustChain requires native RTC, a native RTC wallet is still needed from the user or maintainer.
