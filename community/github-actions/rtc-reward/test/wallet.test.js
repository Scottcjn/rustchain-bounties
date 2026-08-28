const { extractRtcWallet } = require('../src/wallet');

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
  expect(extractRtcWallet(ISSUE_16327_BODY)).toBeNull();
});

test('accepts an exact RTC wallet in issue #16327 Markdown', () => {
  const body = ISSUE_16327_BODY.replace(
    '7doPxSPt1pmbHcUcVzK22FVECDhv8kV6nnd2XMKaFiRd',
    VALID_RTC_WALLET
  );

  expect(extractRtcWallet(body)).toBe(VALID_RTC_WALLET);
});

test('requires exactly 40 hexadecimal characters after RTC', () => {
  expect(extractRtcWallet(`Wallet: RTC${'a'.repeat(39)}`)).toBeNull();
  expect(extractRtcWallet(`Wallet: RTC${'a'.repeat(41)}`)).toBeNull();
  expect(extractRtcWallet(`Wallet: RTC${'g'.repeat(40)}`)).toBeNull();
});
