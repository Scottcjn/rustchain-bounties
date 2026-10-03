# Independent re-measurement kit — bounty #16517

Reproduce or falsify **one** published retro-console figure with raw counts and a 16-token gate. This tree is a harness only: it does not submit a claim, contact anyone, or spend RTC.

Pin the repo commit SHA **before** the first run. Measuring a moving tree is how these numbers get rubber.

## Figures under test

| console | published figure | first instrument to distrust |
|---|---|---|
| NES | 1,117,248 mean cycles/token (~0.62 s @ 1.789772 MHz 2A03); 10.688 cycles/MAC | MAME 0.277 `nes` + Lua write tap on `$0300` |
| SNES | 7.030 tok/s SlowROM (2.68 MHz), 8.019 tok/s FastROM (3.58 MHz); a separate 2.02× claim | PPU H/V latch `$2137` / `$213C` / `$213D` |
| Genesis | 1.674× speedup, cycle totals 220,579,814 → 142,972,761 | MAME 0.277 `genesis` + Lua taps |
| N64 | 1.23 tok/s scalar, 2.19 tok/s RSP (1.78×) | ares |
| GBC | 10.09× (476,200 → 47,200 frames over 16 tokens) | PyBoy + SameBoy |

Divide the published pair yourself before you trust the ratio:

- GBC `476200 / 47200 = 10.089` — matches 10.09×.
- N64 `2.19 / 1.23 = 1.780` — matches 1.78×.
- SNES `8.019 / 7.030 = 1.141` — **not** 2.02×. The 2.02× figure needs its own numerator and denominator; do not substitute the SlowROM/FastROM tok/s pair.
- Genesis `220579814 / 142972761 = 1.543` — **not** 1.674×. Report both cycle totals and recompute; do not paste the published ratio onto a different pair.

## Claim requirements (all five)

1. Figure name + the repo commit SHA that was actually measured.
2. Emulator name and exact version string.
3. Re-runnable harness (script, tap, or debugger config) sitting next to the log.
4. Raw counts on **both** sides of any ratio — not the ratio alone.
5. Token gate: 16 greedy tokens, byte-identical to the host reference.

## Failure modes to hit first

These have already produced fake wins:

- **V-counter wrap** — a 4.8× error came from wrapping the scanline counter. Log counter width and wrap handling.
- **~60 tok/s on N64** — that is frame rate, not token rate. The denominator must be emulated clocks (or frames you actually counted), not wall-clock vs vsync.
- **Host-CPU contamination** — Genesis “11.3×” was host time. Cycles must come from the emulated CPU, not `time.perf_counter()`.
- **Top-K scan-order bug** — first-K survivors instead of strongest-K. Dump selected indices and scores.
- Frame vs CPU-cycle mix-up; idle-loop included in the window; start/stop tap off-by-one.

## Cross-emulator targets (15 RTC tier)

| console | published on | try to break it on |
|---|---|---|
| NES | MAME | Mesen / FCEUX / Nintendulator |
| SNES | on-console | bsnes-hd / higan / Mesen-S / ares |
| Genesis | MAME | BlastEm / Genesis Plus GX / Exodus |
| N64 | ares | cen64 |
| GBC | PyBoy / SameBoy | Emulicious / BGB / Gambatte |

Same ROM image, unmodified, both sides.

## Procedure

1. Check out the pinned SHA. Build the ROM. Run the author’s harness. Save the raw log, not a screenshot of a mean.
2. Shape-check the log:

       python3 scripts/verify_retro_console.py --check --log docs/examples/bounty-16517-record.example.json

3. Port the tap to a second emulator. Do not retune the ROM.
4. Fill the comparison table: published vs your run vs cross-emulator, with percent delta.
5. If you falsify: attach a trace excerpt that shows the wrong denominator, tap, or selection — not just “I got a different number.”

`python3 scripts/verify_retro_console.py --example` prints a valid JSON skeleton. `python3 scripts/verify_retro_console.py --self-test` checks the checker.

## Report template

```
figure: <console + metric>
repo_commit: <sha>
emulator: <name version>
raw_counts: <16 per-token deltas>
tokens_hex: <16 tokens, hex, match Y/N vs host>
numerator: <left side of any claimed ratio>
denominator: <right side>
clock_source: emulated | host    # host is an automatic fail
harness: <path>
verdict: CONFIRM | DISAGREE (+/- % delta) | WRONG (trace attached)
```

JSON shape is the example file. `raw_counts` is sixteen independent per-token deltas, not the published mean copied sixteen times.
