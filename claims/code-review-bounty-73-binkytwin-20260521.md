# Code Review Bounty Claim - #73

Claimant: `BinkyTwin`

Bounty: Scottcjn/rustchain-bounties#73

Status: submitted for maintainer assessment. Issue comments on #73 are disabled
because the issue has more than 2500 comments, so this claim is submitted as a
claim PR instead.

Payout details: not posted publicly in this claim file. They can be provided
separately if maintainers approve or request them.

## Reviews Submitted

### 1. Scottcjn/Rustchain#6028 - Approved Follow-Up

Review: https://github.com/Scottcjn/Rustchain/pull/6028#pullrequestreview-4336129364

Summary:

- Re-reviewed the updated head after the initial approval became stale.
- Verified the non-finite/overflow weight fix for `/epoch/enroll`.
- Direct Flask probing confirmed huge scalar weights now return
  `400 invalid_weights`, preserve the one-shot enrollment ticket, and create no
  `epoch_enroll` row.

### 2. Scottcjn/Rustchain#6030 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/6030#pullrequestreview-4336113761
Follow-up review on updated head:
https://github.com/Scottcjn/Rustchain/pull/6030#pullrequestreview-4337353795

Summary:

- Reviewed payout preflight miner-id type validation.
- Confirmed structured `from_miner` and `to_miner` values are rejected before
  list/dict stringification can turn malformed values into plausible miner IDs.
- Re-reviewed commit `f96e585d56d8fa3d5212d80a1deee86df60fa478` after the
  helper refactor and confirmed non-string empty values now report
  `invalid_from_or_to_type` consistently.
- Verified the focused tests and static checks documented below.

### 3. Scottcjn/Rustchain#6031 - Changes Requested

Review: https://github.com/Scottcjn/Rustchain/pull/6031#pullrequestreview-4336230820

Summary:

- Found a remaining filename/control-character gap in the passport machine-id
  validation.
- The patch rejected `ord(char) < 32`, but still accepted DEL (`\x7f`) and C1
  controls such as `\x85`.
- Local Flask probing returned `201` and created files like `bad\x7fid.json`
  and `bad\x85id.json`.
- Requested rejecting Unicode control categories and adding regression tests for
  those cases.

### 4. Scottcjn/Rustchain#6032 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/6032#pullrequestreview-4336281240

Summary:

- Reviewed `/utxo/transfer` string-field validation and installer checksum
  updates.
- Confirmed malformed JSON types for `from_address`, `to_address`,
  `public_key`, and `signature` now return explicit JSON 400 responses before
  address derivation or signature verification.
- Verified the macOS miner v2.5 checksum update against the checked-in artifact.

### 5. Scottcjn/rustchain-bounties#11536 - Security Changes Requested

Review: https://github.com/Scottcjn/rustchain-bounties/pull/11536#pullrequestreview-4336162126

Summary:

- Found a payment-path blocker in the Sophia auto-approve workflow.
- The workflow sends `RTC_ADMIN_KEY` to `/wallet/transfer` while using
  `verify=False`, disabling TLS server authentication.
- A MITM could capture the reusable admin key and issue arbitrary
  `/wallet/transfer` calls from `founder_community`; the 24-hour pending window
  does not protect the admin credential.
- Requested preserving TLS verification and avoiding reusable admin-key exposure
  in the automated payout path.

## Local Verification Evidence

Commands and probes used across the reviewed PRs included:

```bash
PYTHONPATH=passport uv run --no-project --with pytest --with flask python -m pytest passport/test_passport.py -q --tb=short
PYTHONPATH=passport uv run --no-project --with pytest --with flask python -m pytest passport/test_passport.py -q --tb=short --noconftest -o addopts=''
uv run --no-project --with pytest --with flask python -m pytest node/test_utxo_endpoints.py tests/test_utxo_transfer_json_validation.py -q --tb=short
uv run --no-project --with pytest --with flask python -m pytest tests/test_utxo_transfer_json_validation.py tests/test_install_miner_checksums.py tests/test_setup_miner_downloads.py -q --tb=short
uv run --no-project --with ruff python -m ruff check node/utxo_endpoints.py tests/test_utxo_transfer_json_validation.py setup_miner.py tests/test_install_miner_checksums.py tests/test_setup_miner_downloads.py
uv run --no-project --with ruff python -m ruff check scripts/sophia_auto_approve.py
python3 -m py_compile node/utxo_endpoints.py tests/test_utxo_transfer_json_validation.py setup_miner.py tests/test_install_miner_checksums.py tests/test_setup_miner_downloads.py
python3 -m py_compile scripts/sophia_auto_approve.py scripts/auto-pay.py
python3 tools/bcos_spdx_check.py --base-ref origin/main
git diff --check origin/main...HEAD -- node/utxo_endpoints.py tests/test_utxo_transfer_json_validation.py setup_miner.py tests/test_install_miner_checksums.py tests/test_setup_miner_downloads.py miners/checksums.sha256
git diff --check origin/main...HEAD -- .github/workflows/sophia-auto-approve.yml scripts/sophia_auto_approve.py
shasum -a 256 miners/macos/rustchain_mac_miner_v2.5.py
```

Additional direct probes:

- `/epoch/enroll` with extremely large weights now rejects before consuming the
  one-shot ticket or writing an enrollment row.
- `/api/passport` still accepted `bad\x7fid` and `bad\x85id` on PR #6031, which
  created control-character filenames.
- `/utxo/transfer` rejects list/dict/int/bool values for signed string fields
  before signature and address logic.
- `scripts/sophia_auto_approve.py` uses HTTPS transfer, disables TLS
  verification, sends an admin-key header, and derives the recipient from the PR
  author path.

## Reward Request

Please assess under the #73 reward structure:

- 2 security-focused changes-requested reviews with reproduced blockers
  (#6031, #11536).
- 3 functional reviews with local validation (#6028, #6030, #6032).

Payment is not assumed until maintainer assessment and separate payout proof
exist.
