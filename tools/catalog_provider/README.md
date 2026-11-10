# Catalog Provider — README

A provider daemon for the [RustChain](https://rustchain.org) Service Catalog.
Ships with two real workers (`review` and `docs`) and a full test suite.

## Quick start

```bash
# From the Rustchain repo root
pip install cryptography

# Create and register a Beacon identity first:
#   beacon identity new
#   (register in the Beacon Atlas)

# List your service:
python tools/catalog_cli.py offer \
  --title "Code review — public GitHub repos" \
  --category review \
  --price-rtc 1 \
  --unit "per repo" \
  --turnaround-hours 24 \
  --description "Markdown review: strengths, improvement suggestions, docs check."

# Note the returned lst_… id, then start the daemon:
PROVIDER_LISTING=lst_<id> \
PROVIDER_CATEGORY=review \
BEACON_IDENTITY_PATH=~/.beacon/identity/agent.key \
  python -m tools.catalog_provider.daemon --listing lst_<id> --category review
```

## Configuration

| Flag | Env var | Default | Description |
|------|---------|---------|-------------|
| `--listing` | `$PROVIDER_LISTING` | (required) | Catalog listing id |
| `--category` | `$PROVIDER_CATEGORY` | `review` | Category matching the listing |
| `--node` | `$RUSTCHAIN_NODE` | `https://rustchain.org` | Node base URL |
| `--identity` | `$BEACON_IDENTITY_PATH` | `~/.beacon/identity/agent.key` | Beacon key file |
| `--poll-interval` | — | `60` | Seconds between order polls |
| `--max-concurrent` | — | `3` | Max parallel orders |
| `--state-dir` | — | `./provider_state` | Persistent state directory |
| `--work-dir` | — | `./provider_work` | Work artifacts directory |
| `--log-level` | — | `INFO` | Logging verbosity |

## Kill switch

```bash
touch provider_state/kill_switch   # daemon halts cleanly on next poll
```

## Workers

| Category | Worker class | What it does |
|----------|-------------|--------------|
| `review` | `CodeReviewWorker` | Fetches repo metadata via GitHub API; produces a structured Markdown code review. |
| `docs` | `DocsLintWorker` | Checks README quality, section presence, code-block tagging; produces a Markdown lint report. |

Add a new worker by subclassing `Worker` in `worker.py` and adding it to `WORKERS`.

## Tests

```bash
pytest tests/test_catalog_provider.py -v
```

Tests use an in-memory fake transport — no network or real Beacon identity required.

## Safety

- Private key is **never** printed or logged.
- `delivered.json` prevents re-delivery across restarts.
- Server-side hash-uniqueness conflicts (HTTP 409) are handled gracefully: the
  daemon appends the order-id as a distinguishing suffix and retries.
- Rate-limited by `--poll-interval`; concurrency bounded by `--max-concurrent`.
- Kill switch stops the daemon cleanly between polls.
- `status.json` exports aggregate counts only — no RTC totals.
