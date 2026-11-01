# PowerPC in 2026 — 3-video BoTTube series

Bounty: **#2793 — [BOTTUBE: 5 RTC] Create a 3-Video Series on Any Tech Topic**

Theme: *PowerPC in 2026* — three 30-second explainers on why 1990s big-endian
hardware is still worth running, how to revive a Power Mac G4, and how it
compares with modern ARM under the same workload.

## Episodes

| # | Title | File | Length |
|---|-------|------|--------|
| 1 | PowerPC in 2026 — Part 1 — Why Big Endian Still Matters | `out/part-1.mp4` | 30 s |
| 2 | PowerPC in 2026 — Part 2 — Reviving a Power Mac G4 | `out/part-2.mp4` | 30 s |
| 3 | PowerPC in 2026 — Part 3 — Benchmarking Against Modern ARM | `out/part-3.mp4` | 30 s |

Naming follows the bounty requirement `Series Name — Part N`. All three clips
sit inside the required 30 s – 5 min window and are original, hand-built
slide + narration explainers (no reused footage).

## Render

```bash
pip install pillow imageio-ffmpeg
python community/videos/powerpc-2026/make_series.py          # all three
python community/videos/powerpc-2026/make_series.py part-2   # just one
```

MP4s are written to `community/videos/powerpc-2026/out/`. On macOS the
narration track is generated with `say`; on other platforms the script renders
the same clips without audio instead of failing.

## Upload

Upload each `out/part-*.mp4` to <https://bottube.ai> (web UI or the BoTTube
API/MCP) using the titles from the table above, tagged `rustchain`, `powerpc`,
`retrocomputing`, `vintage-hardware`.

## Claim comment for issue #2793

Replace the three watch IDs and the wallet before posting:

```text
Claiming bounty #2793 — 3-video series: PowerPC in 2026

Live-URL: https://bottube.ai/watch/<id-part-1>   PowerPC in 2026 — Part 1 — Why Big Endian Still Matters
Live-URL: https://bottube.ai/watch/<id-part-2>   PowerPC in 2026 — Part 2 — Reviving a Power Mac G4
Live-URL: https://bottube.ai/watch/<id-part-3>   PowerPC in 2026 — Part 3 — Benchmarking Against Modern ARM

Wallet: <RTC wallet>
```

Each `Live-URL:` line points at a published video, as required by the updated
submission rules — no files are attached to the issue.
