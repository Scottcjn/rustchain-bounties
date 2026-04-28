<!-- SPDX-License-Identifier: MIT -->
# Self-Audit: wallet/

## Wallet
07b44b7ae97ec046f2bf8e59f76b829bf94c51f5RTC

## Module reviewed
- Path: wallet/ (rustchain_wallet_ppc.py, rustchain_wallet_gui.py, rustchain_wallet_secure.py, rustchain_wallet_ppc.py.tmp)
- Commit: 92888df05482
- Lines reviewed: ~800 lines across 4 files

## Deliverable: 3 specific findings

### 1. No cryptographic transaction signing — anyone can forge transfers
- **Severity:** critical
- **Location:** wallet/rustchain_wallet_ppc.py lines 137–141 (wallet derivation), lines 268–292 (unsigned send)
- **Description:** The PPC wallet derives its address deterministically from `os.uname()[1]` (hostname) via SHA256, with zero Ed25519 key generation. The `send_rtc` method constructs an unsigned JSON payload `{"from": self.wallet_address, "to": to_addr, "amount": ...}` and POSTs it without any signature. An attacker who discovers the target machine's hostname can compute the wallet address and forge arbitrary transfers from it — the server has no way to distinguish a legitimate sender from an impersonator.
- **Reproduction:**
  ```python
  import hashlib
  hostname = "victim-mac.local"  # obtainable via network scan or /etc/hostname
  addr = hashlib.sha256(f"ppc-wallet-{hostname}".encode()).hexdigest()[:40] + "RTC"
  # POST to wallet API: {"from": addr, "to": "attacker-addressRTC", "amount": 1000000}
  ```
- **Suggested fix:** Generate an Ed25519 keypair on first wallet creation, store the private key securely, and sign every transaction with it (matching the pattern already present in rustchain_wallet_secure.py).

### 2. Hardcoded internal server IP leaked in .tmp artifact
- **Severity:** critical
- **Location:** wallet/rustchain_wallet_ppc.py.tmp line 110
- **Description:** A stale `.tmp` file (likely from a merge conflict or editor backup) contains the bare internal server IP with HTTP: `NODE_URL = "http://50.28.86.131:8088"`. The production version uses `https://rustchain.org`, but this orphaned artifact exposes infrastructure details. The use of plain HTTP means any traffic through this URL is trivially sniffable. The IP 50.28.86.131 also appears in `cross-chain-airdrop/src/config.rs` line 75 as a hardcoded default — this is consistent with a known infrastructure secret leaking through code artifacts.
- **Reproduction:**
  ```bash
  grep -n "50.28" wallet/rustchain_wallet_ppc.py.tmp
  # 110:NODE_URL = "http://50.28.86.131:8088"
  ```
- **Suggested fix:** Delete the `.tmp` file. Add `*.tmp` to `.gitignore`. Audit the codebase for other editor artifacts (`*.swp`, `*.orig`, `*.bak`) and remove them.

### 3. SSL/TLS certificate verification unconditionally disabled in GUI wallet
- **Severity:** high
- **Location:** wallet/rustchain_wallet_gui.py lines 31, 35
- **Description:** The GUI wallet unconditionally sets `VERIFY_SSL = False` with no user-facing override. This means every balance query, transaction submission, and wallet operation travels over a connection that will accept any certificate — enabling man-in-the-middle interception of wallet addresses, balances, and signed transactions. The production `rustchain_wallet_secure.py` correctly gates this behind a `RUSTCHAIN_VERIFY_SSL` environment variable (lines 37-41), but the GUI wallet hardcodes the insecure setting. A user who runs the GUI wallet on a public network (coffee shop WiFi, conference network) is exposed to active MITM attacks.
- **Reproduction:**
  ```bash
  # Run the GUI wallet behind a proxy (mitmproxy, Burp Suite, etc.)
  python wallet/rustchain_wallet_gui.py
  # All API calls complete without TLS errors despite proxy intercepting.
  ```
- **Suggested fix:** Replace lines 31 and 35 with the environment-variable-gated pattern from rustchain_wallet_secure.py:
  ```python
  _ssl_env = os.environ.get("RUSTCHAIN_VERIFY_SSL", "1")
  VERIFY_SSL = _ssl_env != "0"
  if not VERIFY_SSL:
      urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
  ```

## Known failures of this audit
- **No runtime testing:** I did not deploy the wallet code against the live node at rustchain.org to confirm the forging attack succeeds end-to-end. The analysis is based on static code review showing the absence of any signing logic in the `send_rtc` path.
- **Did not audit wallet tests:** The test file `wallet/tests/test_wallet_network_errors.py` imports from a nonexistent module (`coinbase_wallet`) — I noted this but did not verify whether the wallet module has other, working tests that would catch these issues.
- **Did not review the Qt/PySide6 GUI logic:** The GUI wallet file (`rustchain_wallet_gui.py`) is ~900 lines; I focused on the TLS-disabling configuration at the top but did not review the event handlers for UI-triggered injection risks (e.g., amount parsing, address validation on paste).
- **Single-version analysis:** The audit covers only the latest `main` commit. Historical commits were not checked for credentials that may have been committed and later reverted.

## Confidence
- Overall confidence: 0.75
  - Finding 1 (unsigned transfers): 0.95 — unequivocal code path with no signing step
  - Finding 2 (hardcoded IP): 0.90 — the .tmp file exists on disk and contains the IP
  - Finding 3 (SSL disabled): 0.85 — `VERIFY_SSL = False` is a hardcoded constant; only uncertainty is whether a reverse proxy or config flag elsewhere overrides it at runtime
- Confidence is not 1.0 because I did not execute the exploits end-to-end against a live node, and because the unauthenticated wallet vulnerability (finding 1) depends on server-side validation behavior that I could only infer from the client code.

## What I would test next
1. **End-to-end forge test:** Spin up a local RustChain node, create a PPC wallet from hostname A, then craft a transfer from hostname B's derived address using a raw HTTP client — verify the node accepts the forged transaction.
2. **MITM GUI wallet test:** Route the GUI wallet through mitmproxy, verify that TLS interception succeeds silently, and check whether the intercepted traffic reveals sensitive data (private keys, balances).
3. **Network port scan against 50.28.86.131:** Confirm whether port 8088 is still open and what services are exposed on that IP, to assess real-world impact of the leaked infrastructure address.
