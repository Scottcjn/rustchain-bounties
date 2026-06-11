# Code Review Bounty Claim - #73

Claimant: `jonasxzb`

Bounty: Scottcjn/rustchain-bounties#73

Wallet ID: `jonasxzb`

Status: submitted for maintainer assessment. The original #73 issue is not accepting new comments, so this PR records the claim.

## Review Submitted

### Scottcjn/Rustchain#6684 - Changes Requested

Review: https://github.com/Scottcjn/Rustchain/pull/6684#pullrequestreview-4397930152

Summary:

- Reviewed the BCOS badge generator v2 static page changes.
- Verified the inline JavaScript parses successfully with a Node `new Function(script)` check.
- Found a blocking runtime issue in the new live directory and verify flows: both call `https://50.28.86.131`, whose certificate is not valid for the raw IP.
- Reproduced normal TLS/browser-style fetch failures for the new `/bcos/directory` and `/bcos/verify` calls.
- Requested using a browser-valid HTTPS hostname, same-origin proxy, or a static fallback until the API origin is usable.

## Local Verification Evidence

Commands/probes run:

```bash
node -e "... extract inline script from static/bcos/badge-generator.html and new Function(script) ..."
node - <<'NODE'
const NODE_URL = 'https://50.28.86.131';
for (const path of ['/bcos/directory?limit=1','/bcos/verify/BCOS-e9aae86d']) {
  try {
    const r = await fetch(NODE_URL + path, { signal: AbortSignal.timeout(5000) });
    console.log(path, r.status);
  } catch (e) {
    console.log(path, e.name + ': ' + e.message);
    if (e.cause) console.log('cause', e.cause.code || e.cause.message);
  }
}
NODE
```

Probe result:

```text
/bcos/directory?limit=1 TypeError: fetch failed
cause ERR_TLS_CERT_ALTNAME_INVALID
/bcos/verify/BCOS-e9aae86d TypeError: fetch failed
cause ERR_TLS_CERT_ALTNAME_INVALID
```

## Reward Request

Please assess this under the #73 code review reward structure as one substantive changes-requested review.

Reference rate in #73: `1 RTC = $0.10 USD`. At the posted minimum of 5 RTC per accepted review, this claim requests 5 RTC / $0.50 equivalent.
