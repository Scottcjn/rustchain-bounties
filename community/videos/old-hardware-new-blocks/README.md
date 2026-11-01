# Old Hardware, New Blocks — 3-video BoTTube series

Bounty: `[BOTTUBE: 5 RTC] Create a 3-Video Series on Any Tech Topic` (#2793)

A three-part explainer series on RustChain's Proof-of-Antiquity, built as original
slide + caption videos. No third-party footage, no reused assets.

| Part | Title | Length |
| --- | --- | --- |
| 1 | Old Hardware, New Blocks — Part 1 — Why Proof of Antiquity Exists | 36s |
| 2 | Old Hardware, New Blocks — Part 2 — Hardware Fingerprints | 36s |
| 3 | Old Hardware, New Blocks — Part 3 — Multipliers and Joining | 36s |

All three are within the 30 seconds – 5 minutes requirement and use the required
`Series Name — Part N` naming.

## Rebuild the videos locally

```bash
pip install pillow imageio-ffmpeg
python3 community/videos/old-hardware-new-blocks/make_video.py
```

Renders `out/old-hardware-new-blocks-part-1.mp4`, `-part-2.mp4`, `-part-3.mp4`
(1280x720, 20 fps, H.264 + faststart).

Preview a single slide without ffmpeg:

```bash
python3 community/videos/old-hardware-new-blocks/make_video.py --dry-run
```

## Narration script

### Part 1 — Why Proof of Antiquity Exists
1. Every chain rewards raw speed: newest GPU, biggest farm, highest hash rate.
2. Faster silicon means faster waste — working machines retired while they still work.
3. Antiquity flips the score: age becomes the scarce resource, one CPU one vote.

### Part 2 — Hardware Fingerprints
1. Machines have fingerprints: timing, cache and quirks that are hard to hide.
2. Cheap to check, costly to fake: honest machines answer in milliseconds.
3. Age is hard to counterfeit: the multiplier follows the attested hardware age.

### Part 3 — Multipliers and Joining
1. Multipliers reward age: vintage attested hardware out-earns modern hardware.
2. Attest first, then mine: install, attest, keep the machine online.
3. Old hardware, new blocks: start with one machine, measure, then add more.

## Claim comment (fill in the real URLs after upload)

```
Claiming #2793 — 3-video series "Old Hardware, New Blocks" (all original, AI-generated slide + TTS explainers).

Live-URL: https://bottube.ai/watch/<part-1-id>
Live-URL: https://bottube.ai/watch/<part-2-id>
Live-URL: https://bottube.ai/watch/<part-3-id>

Wallet: <RTC wallet>
```

Do not attach the MP4 files to the issue — the bounty only pays for published,
off-GitHub videos. Upload to https://bottube.ai first, then paste the watch URLs.

## Bonus checklist

- [ ] 10+ total upvotes across the 3 videos (+2 RTC)
- [ ] Someone posts a response video (+3 RTC)
