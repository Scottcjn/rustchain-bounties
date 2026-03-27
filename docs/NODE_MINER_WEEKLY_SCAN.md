# Weekly Node + Miner Scan

Use this script to determine:

- which **node hosts** should receive weekly RTC payout
- which **miners** are currently eligible based on attestation freshness
- which expected miners are missing and should be contacted to restart/upgrade

Script:

- `scripts/node_miner_weekly_scan.py`

## Quick Run

```bash
python3 scripts/node_miner_weekly_scan.py
```

This scans the seed node (`https://50.28.86.131`), discovers registered nodes from `/api/nodes`, and prints a markdown report.

## Save Reports (JSON + Markdown)

```bash
python3 scripts/node_miner_weekly_scan.py \
  --out-json reports/node_miner_scan.json \
  --out-md reports/node_miner_scan.md
```

## Include Expected Miners (to catch outdated/wrong-node setups)

Create a file like `expected_miners.txt`:

```txt
# one miner id per line
freefrog-miner
victus-x86-scott
node-host-lab-g5
```

Run:

```bash
python3 scripts/node_miner_weekly_scan.py \
  --expected-miners-file expected_miners.txt
```

Any expected miner not visible in the public miner API is listed under **Expected Miners Missing** with action:

- `check_node_url_then_upgrade_miner`

## Recommended Weekly Ops Loop

1. Run the scan and save JSON/MD output.
2. Queue host payouts for rows marked `pay_weekly` or `pay_weekly_and_upgrade_node`.
3. Queue miner payouts for rows marked `weekly_eligible: yes`.
4. DM missing miners with restart + miner update instructions.
5. Re-run after upgrades/restarts.

## Notes

- TLS verification is disabled by default because the primary node currently uses self-signed certs.
- Use `--verify-tls` once trusted certs are in place.
- Version mismatch nodes are still payout-eligible by default, but explicitly flagged for upgrade.

## Repository Baseline + 24h Follow-up Helper

This repo now includes a live baseline file:

- `expected_miners.txt`

Use it directly:

```bash
python3 scripts/node_miner_weekly_scan.py --expected-miners-file expected_miners.txt
```

For issue `#374` 24h follow-up comments, use:

```bash
# dry run
./scripts/post_issue374_followup.sh 374 --dry-run

# post comment to GitHub issue
./scripts/post_issue374_followup.sh 374
```

See also:
- `docs/NODE_HOST_PREFLIGHT_CHECKLIST.md` for host onboarding + expected outputs.
