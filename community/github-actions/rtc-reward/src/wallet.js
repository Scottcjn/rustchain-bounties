'use strict';

// RustChain wallets are the literal RTC prefix followed by exactly 40 hex
// characters. The surrounding character is consumed (but not captured) so a
// wallet embedded in Markdown such as **Wallet:** `RTC...` is accepted without
// accepting a longer or unrelated identifier.
const RTC_WALLET_RE = /(?:^|[^0-9A-Za-z])(RTC[0-9a-fA-F]{40})(?![0-9a-fA-F])/;

function extractRtcWallet(text) {
  if (typeof text !== 'string') return null;
  const match = RTC_WALLET_RE.exec(text);
  return match ? match[1] : null;
}

module.exports = { extractRtcWallet, RTC_WALLET_RE };
