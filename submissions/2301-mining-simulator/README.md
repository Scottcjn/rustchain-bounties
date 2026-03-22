# RustChain Interactive Mining Simulator — Bounty #2301

**Bounty**: #2301 — Interactive RustChain Mining Simulator (40 RTC + 10 RTC bonus)
**Reward**: 50 RTC (base + bonus)

## What This Delivers

A fully self-contained `index.html` (no backend, no dependencies) that walks users through
the complete RustChain mining loop step by step.

### Core Requirements ✅

| Requirement | Status |
|---|---|
| Browser-based, no backend | ✅ Single HTML file, pure JS |
| Hardware detection simulation | ✅ Shows fingerprint check details |
| Attestation payload display | ✅ Live JSON matching real `/attest/submit` schema |
| Epoch participation loop | ✅ Animated round-robin epoch steps |
| Reward calculation with antiquity multipliers | ✅ Live per-epoch and cumulative |
| PowerBook G4 (2.5×) | ✅ |
| Power Mac G5 (2.0×) | ✅ |
| Modern x86 (1.0×) | ✅ |
| VM (0.000000001×) | ✅ Anti-emulation fail shown |
| Real-time reward comparison between architectures | ✅ Animated bar chart |
| Link to miner download | ✅ CTA at bottom |

### Bonus Requirements ✅

| Bonus | Status |
|---|---|
| Animated fingerprint check visualization | ✅ 6-card grid with pulse/pass/fail states |
| "What would you earn?" calculator | ✅ Sliders: epochs/day, base reward, days |

## How to Use

Open `index.html` in any modern browser — no server needed.

1. **Pick hardware** — click a card (PowerBook G4, Power Mac G5, Modern x86, VM)
2. **Start simulation** — click ▶ Start or ⏭ Step through epochs manually
3. **Watch the fingerprint animation** — each of the 6 RIP-PoA checks animates pass/fail
4. **Read the payload** — the right panel shows the exact JSON sent to `/attest/submit`
5. **Compare rewards** — the bar chart updates in real time across all hardware types
6. **Use the calculator** — tune epochs/day, base reward, days to estimate your earnings

## Technical Notes

- Payload schema matches `rustchain-miner/src/payload.rs` exactly
- Fingerprint check names match `rustchain-miner/src/fingerprint/mod.rs`
- Epoch interval constant (600s) sourced from `rustchain-miner/src/config.rs`
- VM gets `anti_emulation`, `simd_identity`, `thermal_drift`, `instruction_jitter` failures
  matching real VM detection behaviour

## Deploy

Drop `index.html` at `rustchain.org/simulator` or serve from GitHub Pages — zero config needed.

## Wallet

RTC_WALLET_PLACEHOLDER
