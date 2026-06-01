# Grandma RustChain Explainer

Submission for bounty #2071: "Explain RustChain to Your Grandma".

- Video: `grandma-rustchain-explainer.mp4`
- Duration target: under 60 seconds
- Style: simple household-object animation
- Jargon avoided: no consensus, attestation, epoch, settlement, or validator terms
- RTC wallet: `RTCc4e01222a53820fdde5e3f4adc6b6d46f965e467`

## Script

See `script.txt`.

## Build

The checked-in video was generated locally with:

```bash
python3 -m venv /tmp/grandma-video-venv
/tmp/grandma-video-venv/bin/python -m pip install pillow imageio-ffmpeg
/tmp/grandma-video-venv/bin/python make_video.py
```

The script uses macOS `say` for narration when available, then uses the
`imageio-ffmpeg` bundled ffmpeg binary to combine the generated frames and
audio into `grandma-rustchain-explainer.mp4`.
