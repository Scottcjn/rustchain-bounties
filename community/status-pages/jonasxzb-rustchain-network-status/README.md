# RustChain Network Status Page

Static status page submission for bounty #38.

## What it shows

- Health checks for three public RustChain endpoints:
  - `https://rustchain.org/health`
  - `https://explorer.rustchain.org/health`
  - `https://50.28.86.131/health`
- Active miner count from `/api/miners`
- Miner architecture and device-family breakdown
- Current epoch, slot progress, epoch pot, enrolled miners, and estimated time until next settlement from `/epoch`
- Client-observed incident log for failed node checks
- Automatic refresh every 60 seconds

Browsers cannot bypass a certificate common-name mismatch for the direct IP endpoint. The page therefore shows the direct IP as a manual/verifier check while the included verification script checks it with TLS verification disabled, matching the bounty's `curl -k` guidance.

## How to run

Open `index.html` directly in a browser, or serve the directory as static files:

```bash
python3 -m http.server 5173
```

Then open:

```text
http://127.0.0.1:5173/community/status-pages/jonasxzb-rustchain-network-status/
```

## Verification

Run the no-dependency verification script from the repository root:

```bash
node community/status-pages/jonasxzb-rustchain-network-status/verify-status-page.mjs
```

The script checks that the HTML contains the required sections and that the public RustChain endpoints return usable health, miner, and epoch data. It disables TLS rejection only inside the verification process so the direct IP endpoint can be checked like the bounty's `curl -k` example.

## Notes

The page has no backend and does not store credentials. It uses browser `fetch()` calls against public RustChain endpoints with CORS enabled.
