# RustChain Block Explorer Dashboard

Issue: [#686](https://github.com/Scottcjn/rustchain-bounties/issues/686)

This is a dependency-free static dashboard for the live RustChain explorer APIs.

## Implemented Scope

Tier 1 miner dashboard:

- Fetches `https://explorer.rustchain.org/api/miners`.
- Shows active miners, online count, vintage node count, and top antiquity multiplier.
- Renders architecture badges, hardware type, multiplier bars, attestation age, and online/stale status.
- Includes search, family filter, status filter, sorting, manual refresh, and 30-second refresh cadence.

Tier 2 Agent Economy view:

- Fetches `https://explorer.rustchain.org/agent/stats`.
- Fetches `https://explorer.rustchain.org/agent/jobs`.
- Looks up wallet reputation with `https://explorer.rustchain.org/agent/reputation/{wallet}`.
- Shows active agents, open jobs, escrow balance, fee rate, total RTC volume, category distribution, and job lifecycle states.
- Includes category filtering and an empty state when no open jobs are returned by the API.

## Files

- `index.html` - dashboard layout.
- `styles.css` - responsive dashboard styling.
- `app.js` - API loading, normalization, filters, sorting, and rendering.

## Local Validation

Open `index.html` in a browser, or serve the folder with any static file server.

```powershell
python -m http.server 8080
```

Then open `http://localhost:8080/block-explorer-dashboard/`.

## API Notes

The dashboard is read-only. It does not require a wallet, token, server secret, or write access. If an API call fails, the page keeps the rest of the successful data visible and shows a partial-data warning.
