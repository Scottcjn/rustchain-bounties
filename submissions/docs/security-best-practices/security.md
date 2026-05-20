# RustChain Security Best Practices

> Comprehensive security guide for wallet management, API integration, and smart contract development on the RustChain network.

---

## Table of Contents

1. [Wallet Security](#wallet-security)
2. [API Security](#api-security)
3. [Smart Contract Security](#smart-contract-security)
4. [Network Security](#network-security)
5. [Incident Response](#incident-response)
6. [Security Checklist](#security-checklist)

---

## Wallet Security

### Private Key Management

Your private key is the most critical piece of data in your RustChain ecosystem. Losing it means losing access to your assets forever.

#### Best Practices

- **Never store private keys in plaintext.** Use hardware wallets or encrypted key stores.
- **Use hierarchical deterministic (HD) wallets.** RustChain supports BIP-32/BIP-39 for deterministic key derivation.
- **Implement multi-signature wallets** for high-value accounts. Require M-of-N signatures for transactions above a threshold.
- **Rotate keys periodically.** Generate new addresses for different transaction categories.
- **Back up your seed phrase offline.** Store in multiple physical locations (metal plates recommended over paper).

#### Key Storage Solutions

| Solution | Security Level | Use Case |
|----------|---------------|----------|
| Hardware Wallet (Ledger/Trezor) | 鈽呪槄鈽呪槄鈽?| Long-term storage |
| Encrypted Software Wallet | 鈽呪槄鈽呪槄 | Daily transactions |
| RustChain CLI with `--encrypt` | 鈽呪槄鈽?| Development/testing |
| Environment Variables | 鈽呪槄 | Server-side apps (never for main wallets) |
| Plain Text File | 鈽?| **NEVER USE THIS** |

#### Example: Secure Key Generation

```bash
# Generate a new encrypted wallet
rustchain-wallet create --name my-wallet --encrypt

# Export public address only (safe to share)
rustchain-wallet export --name my-wallet --public-only

# NEVER do this:
# rustchain-wallet export --name my-wallet --private-key > key.txt
```

### Transaction Security

- **Always verify transaction details** before signing. Check recipient address, amount, and gas fees.
- **Use transaction simulation** to preview outcomes before committing.
- **Set spending limits** per day/week to limit exposure from compromised keys.
- **Enable transaction notifications** via webhooks for real-time monitoring.

### Address Validation

```rust
use rustchain_sdk::address::validate_address;

fn process_payment(addr: &str, amount: u64) -> Result<(), Error> {
    // Always validate addresses before processing
    let validated = validate_address(addr)
        .map_err(|_| Error::InvalidAddress)?;
    
    if validated.network != Network::Mainnet {
        return Err(Error::WrongNetwork);
    }
    
    // Proceed with transaction
    Ok(())
}
```

---

## API Security

### Authentication & Authorization

#### API Key Management

- **Use separate API keys** for different environments (development, staging, production).
- **Rotate API keys** every 90 days minimum.
- **Set appropriate permissions** per key 鈥?follow the principle of least privilege.
- **Monitor API key usage** and set rate limits per key.
- **Revoke compromised keys immediately.**

```rust
// Good: Scoped API client
let client = RustChainClient::builder()
    .api_key(env::var("RUSTCHAIN_API_KEY")?)
    .permissions(Permissions::READ_ONLY | Permissions::SEND_TRANSACTIONS)
    .rate_limit(RateLimit::per_second(10))
    .build()?;
```

#### JWT Token Security

- Use short-lived access tokens (15 minutes max) with refresh tokens.
- Store tokens in HTTP-only, secure cookies on web clients.
- Implement token revocation for compromised sessions.
- Validate token claims on every request.

### Rate Limiting

Protect your API endpoints from abuse:

```rust
use rustchain_sdk::middleware::RateLimiter;

let app = Router::new()
    .route("/api/v1/transactions", post(create_tx))
    .layer(RateLimiter::new()
        .max_requests(100)
        .per(Duration::from_minutes(1))
        .key_by(KeyBy::ApiKey));
```

### Input Validation

Never trust user input. Validate and sanitize everything:

```rust
use rustchain_sdk::validation::*;

fn handle_transfer_request(req: TransferRequest) -> Result<Transaction, ApiError> {
    // Validate amount
    if req.amount == 0 || req.amount > MAX_TRANSACTION_AMOUNT {
        return Err(ApiError::InvalidAmount);
    }
    
    // Validate and normalize address
    let to_address = validate_and_normalize_address(&req.to)?;
    
    // Validate memo length
    if req.memo.as_ref().map(|m| m.len()).unwrap_or(0) > 256 {
        return Err(ApiError::MemoTooLong);
    }
    
    // Sanitize memo content
    let memo = req.memo.map(|m| sanitize_utf8(&m));
    
    Ok(Transaction::new(to_address, req.amount, memo))
}
```

### HTTPS & TLS

- **Always use HTTPS** for API communications.
- Use TLS 1.3 where available, minimum TLS 1.2.
- Implement certificate pinning for mobile/desktop clients.
- Use HSTS headers for web applications.

### CORS Configuration

```rust
use tower_http::cors::{CorsLayer, Any};

let cors = CorsLayer::new()
    .allow_origin(["https://yourapp.com".parse()?])
    .allow_methods([Method::GET, Method::POST])
    .allow_headers([CONTENT_TYPE, AUTHORIZATION])
    .max_age(Duration::from_hours(24));
```

---

## Smart Contract Security

### Common Vulnerabilities

#### 1. Reentrancy Attacks

The most common and dangerous vulnerability in smart contracts.

```rust
// VULNERABLE 鈥?Do NOT use
fn withdraw(ctx: &mut Context, amount: u64) -> Result<()> {
    let balance = ctx.get_balance(ctx.caller())?;
    if balance < amount { return Err(Error::InsufficientFunds); }
    
    // External call BEFORE state update 鈥?VULNERABLE!
    ctx.send(ctx.caller(), amount)?;
    ctx.set_balance(ctx.caller(), balance - amount)?;
    Ok(())
}

// SECURE 鈥?State changes before external calls
fn withdraw(ctx: &mut Context, amount: u64) -> Result<()> {
    let balance = ctx.get_balance(ctx.caller())?;
    if balance < amount { return Err(Error::InsufficientFunds); }
    
    // Update state FIRST
    ctx.set_balance(ctx.caller(), balance - amount)?;
    // Then external call
    ctx.send(ctx.caller(), amount)?;
    Ok(())
}
```

#### 2. Integer Overflow/Underflow

Rust handles this better than Solidity, but still be explicit:

```rust
// Use checked arithmetic for financial operations
fn add_balance(current: u64, amount: u64) -> Result<u64> {
    current.checked_add(amount)
        .ok_or(Error::Overflow)
}

fn subtract_balance(current: u64, amount: u64) -> Result<u64> {
    current.checked_sub(amount)
        .ok_or(Error::Underflow)
}
```

#### 3. Access Control

```rust
use rustchain_contract::access::{Ownable, RoleBased};

#[derive(Ownable)]
struct Vault {
    owner: Address,
    admins: Vec<Address>,
    balances: Map<Address, u64>,
}

impl Vault {
    // Only owner can mint
    #[only_owner]
    fn mint(&mut self, to: Address, amount: u64) -> Result<()> {
        self.balances.insert(to, amount)?;
        Ok(())
    }
    
    // Admin or owner can freeze
    #[only_role("admin", "owner")]
    fn freeze(&mut self, account: Address) -> Result<()> {
        self.frozen.insert(account, true)?;
        Ok(())
    }
}
```

#### 4. Front-Running Protection

- Use commit-reveal schemes for sensitive operations.
- Implement minimum slippage tolerance for DEX operations.
- Consider using batch auctions for large trades.

#### 5. Unchecked External Calls

```rust
// Always check return values of external calls
fn process_payout(ctx: &mut Context, recipient: Address, amount: u64) -> Result<()> {
    let result = ctx.call_contract(
        "token_contract",
        "transfer",
        &[recipient.to_param(), amount.to_param()]
    );
    
    match result {
        Ok(_) => ctx.emit_event("PayoutSuccess", recipient, amount),
        Err(e) => {
            ctx.emit_event("PayoutFailed", recipient, amount);
            return Err(Error::TransferFailed(e));
        }
    }
    Ok(())
}
```

### Audit Checklist for Smart Contracts

- [ ] All external calls are made after state changes (CEI pattern)
- [ ] All arithmetic uses checked operations
- [ ] Access control is properly implemented and tested
- [ ] No hardcoded addresses or magic numbers
- [ ] Events are emitted for all state-changing operations
- [ ] Emergency pause mechanism is in place
- [ ] Upgrade path is defined (if applicable)
- [ ] Gas optimization doesn't compromise security

### Testing Security

```rust
#[cfg(test)]
mod security_tests {
    use super::*;
    
    #[test]
    fn test_reentrancy_protection() {
        let mut vault = Vault::new();
        vault.deposit(alice(), 1000);
        
        // Attempt reentrancy attack
        let result = vault.withdraw(attacker(), 1000);
        assert!(result.is_err());
        assert_eq!(vault.get_balance(alice()), 1000);
    }
    
    #[test]
    fn test_overflow_protection() {
        let mut vault = Vault::new();
        let max = u64::MAX;
        vault.deposit(alice(), max);
        
        let result = vault.deposit(alice(), 1);
        assert!(result.is_err()); // Should fail, not overflow
    }
    
    #[test]
    fn test_access_control() {
        let mut vault = Vault::new(owner());
        
        // Non-owner trying to mint should fail
        let result = vault.as_user(attacker()).mint(alice(), 1000);
        assert!(result.is_err());
    }
}
```

---

## Network Security

### Node Security

- **Run behind a firewall** 鈥?only expose necessary ports (RPC: 8545, P2P: 30303).
- **Keep software updated** 鈥?subscribe to RustChain security advisories.
- **Use dedicated hardware** for validator nodes.
- **Monitor for unusual behavior** 鈥?sudden peer count changes, abnormal block times.
- **Implement DDoS protection** for public-facing RPC nodes.

### Peer Management

```toml
# rustchain-node.toml
[network]
max_peers = 50
min_peers = 10
trusted_peers = [
    "enode://a1b2c3...@seed1.rustchain.io:30303",
    "enode://d4e5f6...@seed2.rustchain.io:30303",
]
banned_peers_update_interval = "1h"
```

### Monitoring & Alerting

Set up monitoring for:
- Block height lag (alert if > 5 blocks behind)
- Peer count drops (alert if < 10 peers)
- Unusual transaction patterns
- Disk space usage
- Memory consumption
- CPU spikes

---

## Incident Response

### Response Plan

1. **Detection** 鈥?Automated alerts via monitoring
2. **Assessment** 鈥?Determine scope and severity
3. **Containment** 鈥?Pause affected contracts, disable compromised keys
4. **Investigation** 鈥?Analyze logs, trace transactions
5. **Recovery** 鈥?Deploy fixes, migrate funds if needed
6. **Post-Mortem** 鈥?Document and share learnings

### Emergency Contacts

- RustChain Security Team: security@rustchain.io
- Bug Bounty Program: https://github.com/rustchain/bounty-program
- Emergency Discord: #security-incidents

---

## Security Checklist

### For Developers
- [ ] All private keys are encrypted at rest
- [ ] API keys are rotated regularly
- [ ] Input validation on all endpoints
- [ ] HTTPS everywhere
- [ ] Rate limiting configured
- [ ] Smart contracts follow CEI pattern
- [ ] All arithmetic is checked
- [ ] Access control properly implemented
- [ ] Comprehensive security tests written
- [ ] Code reviewed by at least one other developer

### For Node Operators
- [ ] Firewall configured (only necessary ports open)
- [ ] Software up to date
- [ ] Monitoring and alerting configured
- [ ] Regular backups of node data
- [ ] Dedicated hardware for validators
- [ ] Peer management configured
- [ ] DDoS protection in place

### For Users
- [ ] Seed phrase backed up in multiple physical locations
- [ ] Hardware wallet used for significant holdings
- [ ] Phishing awareness training completed
- [ ] Transaction details verified before signing
- [ ] Regular security review of connected dApps

---

## Additional Resources

- [RustChain Official Security Audits](https://github.com/rustchain/audits)
- [OWASP Blockchain Security Guide](https://owasp.org/www-community/vulnerabilities/)
- [RustChain Bug Bounty Program](https://github.com/rustchain/bounty-program)
- [Smart Contract Security Best Practices](https://github.com/rustchain/security-guidelines)

---

*This document is maintained by the RustChain community. Last updated: 2025-01-15.*

*Found a security issue? Report it responsibly to security@rustchain.io.*
