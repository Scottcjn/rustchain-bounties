# RustChain Mining in 3 Steps — BoTTube 3-video series

Submission for bounty **#2793 — [BOTTUBE: 5 RTC] Create a 3-Video Series on Any Tech Topic**.

## Series

Theme: *RustChain Mining in 3 Steps* (tech tutorial, 3 related episodes).

| Part | Title | Length |
| --- | --- | --- |
| 1 | RustChain Mining in 3 Steps — Part 1 — Install the Miner | ~32 s |
| 2 | RustChain Mining in 3 Steps — Part 2 — Configure and Mine | ~32 s |
| 3 | RustChain Mining in 3 Steps — Part 3 — Results and Tips | ~32 s |

Naming follows the bounty requirement (`Series Name — Part N`), and every
episode is between 30 seconds and 5 minutes.

## Generate the videos

From the repository root:

```bash
python community/videos/rustchain-3-part-series/make_videos.py
```

Output goes to `community/videos/rustchain-3-part-series/output/`:

```
part-1-install.mp4
part-2-configure.mp4
part-3-results.mp4
```

The script mirrors the approach already used in
`community/videos/jonasxzb-grandma-rustchain/make_video.py`: Pillow renders the
slides, and `imageio_ffmpeg` encodes them as H.264 MP4. Narration is added
automatically on macOS via `say`; on other platforms the videos are silent and
narration can be recorded separately.

## Upload to BoTTube

Upload each MP4 with the BoTTube API (agents can use the MCP endpoint):

```bash
for f in community/videos/rustchain-3-part-series/output/*.mp4; do
  curl -s -X POST https://bottube.ai/api/videos \
    -H "Authorization: Bearer $BOTTUBE_API_KEY" \
    -F "file=@$f" \
    -F "title=$(basename "$f" .mp4)" \
    -F "category=ai-art" \
    -F "tags=rustchain,mining,tutorial"
done
```

## Claim block

Once the three uploads are live, comment on issue #2793 with this block and
replace each placeholder with the returned watch ID:

```
Live-URL: https://bottube.ai/watch/<part-1-video-id>
Live-URL: https://bottube.ai/watch/<part-2-video-id>
Live-URL: https://bottube.ai/watch/<part-3-video-id>

Wallet: <your RTC wallet>
```

All three videos are original generated slide/TTS explainers about RustChain
mining, created for this bounty.
