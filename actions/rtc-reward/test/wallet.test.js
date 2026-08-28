'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const {
  DEFAULT_WALLET_PATTERN,
  extractWallet,
} = require('../dist/index.js');

const ISSUE_16327_BODY = `## Claim #696: RustChain Memes (2 RTC)

I created memes about RustChain and posted them on social media.

### Meme 1:
**Concept:** "When your 2012 Xeon earns more RTC than someone's $5000 cloud server"
**Format:** Text meme — the punchline is that vintage hardware out-earns modern infrastructure under Proof of Antiquity.

### Meme 2:
**Concept:** "Proof of Antiquity: the only blockchain that rewards you for NOT upgrading your hardware"
**Format:** Comparison image — "Other chains: buy the latest GPU → RustChain: keep your old PC running"

### Where Posted:
- Reddit: r/cryptocurrency and r/rust
- Hacker News: Posted as a show HN item about Proof of Antiquity

### Links:
- Reddit post: (link would be provided with actual URL)
- HN post: (link would be provided with actual URL)

**Wallet:** \`7doPxSPt1pmbHcUcVzK22FVECDhv8kV6nnd2XMKaFiRd\`

---
Claiming meme bounty #696. Memes posted with honest humor about RustChain's unique consensus design.
`;

const VALID_RTC_WALLET = `RTC${'a1'.repeat(20)}`;

test('rejects the non-RTC wallet in the exact body of issue #16327', () => {
  assert.equal(extractWallet(ISSUE_16327_BODY, DEFAULT_WALLET_PATTERN), null);
});

test('accepts an exact RTC wallet inside issue #16327 Markdown', () => {
  const body = ISSUE_16327_BODY.replace(
    '7doPxSPt1pmbHcUcVzK22FVECDhv8kV6nnd2XMKaFiRd',
    VALID_RTC_WALLET
  );

  assert.equal(extractWallet(body, DEFAULT_WALLET_PATTERN), VALID_RTC_WALLET);
});

test('rejects RTC wallets with non-exact length or non-hex content', () => {
  assert.equal(extractWallet(`Wallet: RTC${'a'.repeat(39)}`, DEFAULT_WALLET_PATTERN), null);
  assert.equal(extractWallet(`Wallet: RTC${'a'.repeat(41)}`, DEFAULT_WALLET_PATTERN), null);
  assert.equal(extractWallet(`Wallet: RTC${'g'.repeat(40)}`, DEFAULT_WALLET_PATTERN), null);
});
