# Self-Audit: `wallet/rustchain_wallet_secure.py`

## Wallet
RTC019e78d600fb3131c29d7ba80aba8fe644be426e

## Module reviewed
- Path: `wallet/rustchain_wallet_secure.py`
- Size: ~28,494 chars
- Language: Python 3 (Electrum-style GUI wallet with BIP39 seed + Ed25519)

---

## Known Failures

### 🔴 HIGH — Unverified External Crypto Dependency
**Confidence: 8/10**

The module imports:
```python
from rustchain_crypto import RustChainWallet, verify_transaction
```
This `rustchain_crypto` module is never defined or committed in the repository. No source. No test vector. No audit trail. If this module is absent, the wallet silently fails at import; if it contains a weakened or backdoored Ed25519 implementation, all transaction signing is compromised.

**Evidence:** The import statement has no corresponding file in the repo root or `wallet/` directory. GitHub search for `rustchain_crypto` returns no definition.

**Fix:** Vendor the crypto primitives, or verify the module exists via a hash-pinned subprocess call.

---

### 🔴 HIGH — SSL Verification Can Be Disabled via Env Var
**Confidence: 9/10**

```python
_ssl_env = os.environ.get("RUSTCHAIN_VERIFY_SSL", "1")
VERIFY_SSL = _ssl_env != "0"
if not VERIFY_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

An attacker with local shell access (or a malicious `.env` file) can set `RUSTCHAIN_VERIFY_SSL=0` and intercept all RPC traffic. The wallet then displays a cosmetic warning ("WARNING: SSL verification disabled") but still proceeds to send signed transactions.

**Fix:** Default to `True`; require `DEBUG=1` flag (not env-var) to disable. Log to persistent audit trail.

---

### 🟡 MEDIUM — Hardcoded Node URL, No TLS Pinning
**Confidence: 7/10**

```python
NODE_URL = "https://rustchain.org"
```

`rustchain.org` has no TLS certificate pinning. Any CA compromise or BGP hijack can redirect traffic. The wallet trusts whatever cert the OS trust store accepts.

**Fix:** Pin leaf certificate (SHA-256) or use TACK/HPKP. Alternatively, use `TOFU` with first-connect fingerprint confirmation.

---

### 🟡 MEDIUM — Password Entered in GUI Entry, Shown as `*`
**Confidence: 6/10**

Password is read from a `ttk.Entry` widget with `show="*"`. This is standard, but:
- The password is stored in memory as plaintext for the session lifetime.
- `send_signed_payment` reads it at call time; no clear on error path.
- Screen readers / macOS Accessibility can read widget contents.

**Fix:** Use a platform-native secure text field (macOS Keychain for unlock, not for signing).

---

### 🟡 MEDIUM — Seed Phrase Displayed in GUI Widget
**Confidence: 7/10**

`show_seed_phrase()` displays the 24-word BIP39 seed in a GUI label. This exposes the full wallet key to:
- Any process with screen capture (macOS screen recording permission)
- Any process with window introspection
- The clipboard (if user copies it manually)

**Fix:** Show seed phrase exactly once at creation; never re-display. Offer QR-code offline export instead.

---

### 🟢 LOW — No Multi-Sig Validation
**Confidence: 5/10**

The `send_signed_payment` function does not verify that transactions respect any multi-sig policy or rate-limit. A compromised key could drain the wallet in one session with no confirmation step for large amounts.

**Fix:** Require explicit confirmation dialog for transactions above a threshold (e.g., > 100 RTC).

---

### 🟢 LOW — Retry Loop Has No Rate Limit Cap
**Confidence: 4/10**

`MAX_RETRIES=3` limits retry count, but the loop `time.sleep(delay)` between retries can be manipulated by an attacker who controls `INITIAL_RETRY_DELAY` or `MAX_RETRY_DELAY` env vars. Not a direct exploit, but poor hygiene.

**Fix:** Cap `delay` at a hard-coded upper bound regardless of env vars.

---

## What I Would Test Next

1. **Unit test `rustchain_crypto`**: Import it in isolation; verify Ed25519 signing against known test vectors (e.g., RFC 8032 vectors).
2. **Man-in-the-middle test**: Set `RUSTCHAIN_VERIFY_SSL=0`, start a mitmproxy, verify wallet refuses to connect (it should fail silently).
3. **Clipboard exposure test**: After `show_seed_phrase()`, check if seed appears in macOS clipboard history.
4. **Key leakage via exception path**: Force `verify_transaction` to throw; check if password or seed is in the traceback.
5. **Replay attack**: Re-submit a signed transaction; verify nonce/timestamp prevents replay.

## Submission Info
- Bounty: #6460
- Fork: FlintLeng/rustchain-bounties (haiku-submission branch)
- File: `submissions/self-audits/flintleng-rustchain_wallet_secure.md`
