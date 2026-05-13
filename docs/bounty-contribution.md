# Production Brief: Mining Hardware Video

## Overview

This document specifies the production requirements for a RustChain mining hardware video. The bounty pays 15 RTC for the base variant (30s) and 25 RTC for the extended variant (60s). A pool of 200 RTC is allocated across all submissions.

## Duration Variants

| Variant | Duration | Payout | Max Submissions |
|---------|----------|--------|-----------------|
| Base    | 30s ±2s  | 15 RTC | 8               |
| Extended| 60s ±3s  | 25 RTC | 5               |

Both variants must use the same source footage. The extended variant adds two additional shots and extended voiceover.

## Shot List

### Base Variant (30s) — 6 shots

| Shot # | Duration | Visual | Voiceover | Pass Criteria |
|--------|----------|--------|-----------|---------------|
| 1      | 4s       | Close-up of RustChain miner PCB, fan spinning | "RustChain miners power the most efficient L1 network." | Fan must be visibly spinning, PCB clearly labeled |
| 2      | 5s       | Mid shot of miner with hash rate display overlay (HUD) | "Every hash contributes to BCOS consensus." | HUD must show real-time hash rate, not static image |
| 3      | 5s       | Rack of 3 miners, LED indicators blinking | "Scale from a single board to full racks." | All 3 miners must be powered on, LEDs active |
| 4      | 6s       | Split screen: miner on left, RustChain block explorer on right | "Your hardware, your rewards — verifiable on-chain." | Block explorer must show real transaction data |
| 5      | 5s       | Hand inserting miner into server rack | "Plug in. Mine. Earn RTC." | Clear insertion motion, no cuts |
| 6      | 5s       | Final frame: RustChain logo + "Get Started" CTA | "RustChain. Mine the future." | Logo must be official SVG, CTA links to rustchain.io |

### Extended Variant (60s) — 8 shots

Includes all base shots plus:

| Shot # | Duration | Visual | Voiceover | Pass Criteria |
|--------|----------|--------|-----------|---------------|
| 7      | 10s      | Cutaway to mining dashboard showing RTC balance increasing | "Track your earnings in real-time. No pool fees, no middlemen." | Dashboard must show live balance updates, not mockup |
| 8      | 10s      | Wide shot of home mining setup (desk, miner, monitor) | "Quiet enough for your living room. Powerful enough for serious mining." | Ambient noise must be ≤40dB, miner must be the focus |

## Asset Constraints

### Video
- Resolution: 1920x1080 minimum, 3840x2160 preferred
- Frame rate: 30fps or 60fps
- Codec: H.264 or H.265
- Bitrate: ≥15 Mbps (1080p), ≥40 Mbps (4K)
- No watermarks or channel branding

### Audio
- Voiceover: 48kHz, 16-bit, mono
- Background music: royalty-free, no vocals, -20dB relative to voiceover
- No silence gaps >1s

### Graphics
- RustChain logo: must use official SVG from `/assets/rustchain-logo.svg`
- Hash rate HUD: must use `Fira Code` font, size 24px, color `#00FF88`
- CTA button: `#FF6600` background, white text, 16px padding

## Voiceover Script

### Base Variant
```
[Shot 1] RustChain miners power the most efficient L1 network.
[Shot 2] Every hash contributes to BCOS consensus.
[Shot 3] Scale from a single board to full racks.
[Shot 4] Your hardware, your rewards — verifiable on-chain.
[Shot 5] Plug in. Mine. Earn RTC.
[Shot 6] RustChain. Mine the future.
```

### Extended Variant (additional)
```
[Shot 7] Track your earnings in real-time. No pool fees, no middlemen.
[Shot 8] Quiet enough for your living room. Powerful enough for serious mining.
```

## Captions

Generate SRT files with the following rules:
- Max 42 characters per line
- 2 lines max per caption
- Sync to voiceover timing ±0.5s
- Font: sans-serif, white with black outline
- Position: bottom center, 10% from bottom edge

## Submission Format

Submit a ZIP containing:
1. `rustchain-mining-base.mp4` or `rustchain-mining-extended.mp4`
2. `captions.srt`
3. `voiceover.wav` (separate from video)
4. `production-notes.md` — describe hardware used, recording setup, any deviations from spec

## Acceptance Criteria

Each shot is reviewed independently. A shot fails if:
- Duration deviates by more than ±0.5s from spec
- Visual elements are missing or incorrect
- Voiceover is out of sync by >1s
- Asset constraints are violated

A submission passes if all shots pass review. Partial payouts are not available — either the full bounty or nothing.

## Notes

- Use actual RustChain mining hardware. Simulated footage will be rejected.
- The hash rate display must show real data from a running miner, not a pre-recorded overlay.
- Block explorer footage must be screen-recorded live, not a screenshot.
- Ambient noise must be clean — no fans, AC, or background chatter in voiceover track.