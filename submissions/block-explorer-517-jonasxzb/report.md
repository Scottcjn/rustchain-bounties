# Block Explorer Bug Hunt Report — Issue #517

- Bounty: https://github.com/Scottcjn/rustchain-bounties/issues/517
- Tester: github:JONASXZB
- Date tested: 2026-06-01
- Browser/device: Headless Chromium 148 on macOS
- Pages visited:
  - `https://50.28.86.131/explorer/`
  - `https://rustchain.org/explorer/`
  - `https://rustchain.org/anchors`
  - `https://rustchain.org/health`
  - `https://rustchain.org/epoch`

## Screenshots

- Explorer page: `explorer-loading-miners.png`
- Anchors link result: `anchors-404.png`
- Health endpoint page: `health-page.png`
- Epoch endpoint page: `epoch-page.png`

## Finding 1: bounty URL fails browser TLS validation

### Steps to reproduce

1. Open `https://50.28.86.131/explorer/` in Chromium.
2. Wait for navigation.

### Expected

The bounty URL should load the explorer page directly, or the bounty should point to the canonical hostname with a matching certificate.

### Actual

Chromium blocks navigation with:

```text
net::ERR_CERT_COMMON_NAME_INVALID at https://50.28.86.131/explorer/
```

This happens because the HTTPS certificate is valid for a hostname, not the raw IP address used in the bounty instructions.

### Why it matters

The bounty's primary test URL is not directly accessible in a normal browser without bypassing a TLS warning. New testers may stop before reaching the explorer.

## Finding 2: explorer miner table stays on "Loading miners..."

### Steps to reproduce

1. Open `https://rustchain.org/explorer/`.
2. Observe the "Miners — Active Attestations" table.
3. Check network responses for `GET /api/miners`.

### Expected

The miner table should render the active miners returned by the API.

### Actual

The table remains stuck on:

```text
Loading miners...
```

The API call succeeds:

```text
GET https://rustchain.org/api/miners -> 200 application/json
```

and returns an object containing a `miners` array:

```json
{
  "miners": [
    {
      "miner": "victus-x86-scott",
      "device_arch": "modern",
      "last_attest": 1780274109
    }
  ],
  "pagination": {
    "count": 20,
    "limit": 100,
    "offset": 0,
    "total": 20
  }
}
```

The page script appears to check the response itself as an array:

```js
if (miners && miners.length) {
  document.getElementById('minerCount').textContent = miners.length;
  // ...
}
```

Since the response shape is `{ miners: [...], pagination: ... }`, `miners.length` is undefined and the table never renders.

### Why it matters

The API is healthy, but the explorer UI shows an indefinite loading state. This makes the block explorer look broken even while miner data is available.

## Finding 3: "Ergo Anchors" link returns 404

### Steps to reproduce

1. Open `https://rustchain.org/explorer/`.
2. Click the "Ergo Anchors" link in the header or footer.

### Expected

The link should open the anchors page, or it should point to the correct deployed route.

### Actual

The link navigates to:

```text
https://rustchain.org/anchors
```

which returns:

```text
404 Not Found
```

### Why it matters

The explorer exposes "Ergo Anchors" as a primary navigation item, but the route is missing on the canonical domain.

## Additional console evidence

On `https://rustchain.org/explorer/`, Chromium logged:

```text
Failed to load resource: the server responded with a status of 404 () @ https://rustchain.org/agent/stats
Failed to load resource: the server responded with a status of 404 () @ https://rustchain.org/agent/jobs
```

These 404s also explain why the Agent Economy cards remain on placeholder values such as `-- RTC` and `-- jobs`.
