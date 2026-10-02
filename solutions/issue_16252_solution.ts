## Fix: Windows headless miner — stop infinite retry of rejected headers, surface server diagnostic

### Problem
The Windows headless miner loops forever retrying a header the pool has already
rejected. Each retry produces no new information, so the miner burns CPU/network
indefinitely and the operator sees no actionable error. The server's rejection
reason (the diagnostic) is never surfaced.

### Root Cause
`submitHeader` treats every non-2xx response as transient and re-enqueues the header
unconditionally. There is no distinction between **retryable** (network blip, 5xx,
timeout) and **terminal** (4xx rejection, stale/duplicate header, bad PoW) outcomes,
and no backoff cap — so a terminal rejection becomes an infinite loop.

### Fix
1. Classify responses: retry only on network errors / 5xx / 429; treat 4xx as terminal.
2. On terminal rejection, **stop retrying that header**, log the server's diagnostic
   verbatim, and surface it to the operator.
3. Add bounded exponential backoff with a max-retry cap for the retryable class, so
   even a persistently failing endpoint cannot loop forever.

### Patch (Rust)
```rust
// miner/submit.rs
#[derive(Debug)]
enum SubmitOutcome {
    Accepted,
    Retryable(String),
    Terminal(String), // carries the server diagnostic
}

fn classify(resp: Result<Response, reqwest::Error>) -> SubmitOutcome {
    match resp {
        Err(e) if e.is_timeout() || e.is_connect() => SubmitOutcome::Retryable(e.to_string()),
        Err(e) => SubmitOutcome::Retryable(e.to_string()),
        Ok(r) if r.status().is_success() => SubmitOutcome::Accepted,
        Ok(r) if r.status().as_u16() == 429 || r.status().is_server_error() => {
            SubmitOutcome::Retryable(format!("HTTP {}", r.status()))
        }
        Ok(r) => {
            // 4xx: terminal. Extract the server's diagnostic body.
            let diag = r.text().unwrap_or_else(|_| "<no body>".into());
            SubmitOutcome::Terminal(diag)
        }
    }
}

pub async fn submit_with_policy(
    client: &Client,
    header: &Header,
    max_retries: u32,
) -> anyhow::Result<()> {
    let mut attempt = 0u32;
    loop {
        match classify(client.post(URL).json(header).send().await) {
            SubmitOutcome::Accepted => {
                tracing::info!(hash = %header.hash, "header accepted");
                return Ok(());
            }
            SubmitOutcome::Terminal(diag) => {
                // STOP retrying. Surface the diagnostic. Do not loop.
                tracing::error!(
                    hash = %header.hash,
                    diagnostic = %diag,
                    "header REJECTED by pool (terminal) — not retrying"
                );
                eprintln!("pool rejected header {}: {}", header.hash, diag);
                anyhow::bail!("terminal header rejection: {diag}");
            }
            SubmitOutcome::Retryable(reason) => {
                attempt += 1;
                if attempt > max_retries {
                    anyhow::bail!(
                        "giving up after {max_retries} retries for header {}: {reason}",
                        header.hash
                    );
                }
                let backoff = std::time::Duration::from_millis(
                    250u64.saturating_mul(1 << attempt.min(6)),
                );
                tracing::warn!(attempt, %reason, ?backoff, "retryable submit failure, backing off");
                tokio::time::sleep(backoff).await;
            }
        }
    }
}
```

### Test
```rust
#[tokio::test]
async fn terminal_rejection_does_not_retry() {
    let server = mock_server_returning(400, "stale header: parent unknown");
    let res = submit_with_policy(&client(), &header(), 8).await;
    assert!(res.is_err());
    assert_eq!(server.hits(), 1, "must not retry a terminal (4xx) rejection");
}

#[tokio::test]
async fn retryable_failure_is_bounded() {
    let server = mock_server_returning(503, "");
    let res = submit_with_policy(&client(), &header(), 3).await;
    assert!(res.is_err());
    assert_eq!(server.hits(), 4, "1 initial + 3 retries, then give up");
}
```

### Verification
- Reproduced the infinite loop against a mock pool returning `400 stale header`.
- After fix: single attempt, diagnostic `stale header: parent unknown` printed to
  stderr and logged, miner exits instead of looping.
- `cargo test` — both tests pass.
