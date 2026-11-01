#!/usr/bin/env python3
"""Render the "Old Hardware, New Blocks" three-part BoTTube mini-series.

Each part is 3 slides x 12s = 36s (within the 30s-5min bounty range).

Usage:
    python3 make_video.py                # writes out/old-hardware-new-blocks-part-{1,2,3}.mp4
    python3 make_video.py --part 2       # render a single part
    python3 make_video.py --dry-run      # write preview PNGs, no ffmpeg needed
"""
from __future__ import annotations

import argparse
import math
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"

WIDTH, HEIGHT = 1280, 720
FPS = 20
SECONDS_PER_SLIDE = 12
SERIES = "Old Hardware, New Blocks"

BG = "#101820"
PANEL = "#17242f"
ACCENT = "#f5c542"
TEXT = "#e9f1f7"
MUTED = "#93a6b5"


PARTS = [
    {
        "part": 1,
        "title": "Why Proof of Antiquity Exists",
        "slides": [
            {
                "heading": "Chains reward raw speed",
                "sub": "newest GPU, biggest farm, highest hash rate",
                "bullets": [
                    "The winner is whoever buys the most silicon",
                    "Everyone else races to keep up",
                ],
                "caption": "Part 1 - Why Proof of Antiquity Exists",
            },
            {
                "heading": "Faster silicon, faster waste",
                "sub": "hardware that is obsolete in eighteen months",
                "bullets": [
                    "Working machines get retired while they still work",
                    "The energy cost keeps climbing for everyone",
                ],
                "caption": "Part 1 - Why Proof of Antiquity Exists",
            },
            {
                "heading": "Antiquity flips the score",
                "sub": "age becomes the scarce resource",
                "bullets": [
                    "Old hardware earns because it is rare, not fast",
                    "One CPU, one vote: no arms race to win",
                ],
                "caption": "Part 1 - Why Proof of Antiquity Exists",
            },
        ],
    },
    {
        "part": 2,
        "title": "Hardware Fingerprints",
        "slides": [
            {
                "heading": "Machines have fingerprints",
                "sub": "timing, cache, and quirks that are hard to hide",
                "bullets": [
                    "A miner reports what the machine actually is",
                    "The report is checked before any reward is paid",
                ],
                "caption": "Part 2 - Hardware Fingerprints",
            },
            {
                "heading": "Cheap to check, costly to fake",
                "sub": "verification is quick, spoofing is not",
                "bullets": [
                    "Honest machines answer in milliseconds",
                    "Faked fingerprints take real work to maintain",
                ],
                "caption": "Part 2 - Hardware Fingerprints",
            },
            {
                "heading": "Age is hard to counterfeit",
                "sub": "a 1999 PowerMac cannot be emulated for free",
                "bullets": [
                    "The multiplier follows the attested hardware age",
                    "Rewards stay attached to machines that really exist",
                ],
                "caption": "Part 2 - Hardware Fingerprints",
            },
        ],
    },
    {
        "part": 3,
        "title": "Multipliers and Joining",
        "slides": [
            {
                "heading": "Multipliers reward age",
                "sub": "older attested hardware, larger share",
                "bullets": [
                    "A vintage machine out-earns a modern one",
                    "The token follows usefulness, not wattage",
                ],
                "caption": "Part 3 - Multipliers and Joining",
            },
            {
                "heading": "Attest first, then mine",
                "sub": "install, attest, and start earning RTC",
                "bullets": [
                    "Run the miner on the old box and let it report",
                    "Keep it online so the attestation stays fresh",
                ],
                "caption": "Part 3 - Multipliers and Joining",
            },
            {
                "heading": "Old hardware, new blocks",
                "sub": "the drawer laptop still has work to do",
                "bullets": [
                    "Start with one machine and measure the rewards",
                    "Add more vintage hardware once it pays off",
                ],
                "caption": "Part 3 - Multipliers and Joining",
            },
        ],
    },
]


def _font(size: int, bold: bool = True) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


HEADER_FONT = _font(30)
HEADING_FONT = _font(56)
SUB_FONT = _font(32, bold=False)
BULLET_FONT = _font(30, bold=False)
FOOT_FONT = _font(24, bold=False)


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt) -> float:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt, max_width: float) -> list[str]:
    lines: list[str] = []
    line = ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if not line or text_width(draw, candidate, fnt) <= max_width:
            line = candidate
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_frame(part: dict, slide_index: int, frame_in_slide: int) -> Image.Image:
    slide = part["slides"][slide_index]
    pulse = (frame_in_slide / FPS) * 1.6

    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    # Header bar
    draw.rectangle((0, 0, WIDTH, 96), fill=PANEL)
    draw.text((48, 30), SERIES.upper(), font=HEADER_FONT, fill=ACCENT)
    label = f"Part {part['part']} of 3"
    draw.text((WIDTH - 48 - text_width(draw, label, HEADER_FONT), 30), label, font=HEADER_FONT, fill=TEXT)

    # Slide text
    draw.text((72, 168), slide["heading"], font=HEADING_FONT, fill=TEXT)
    draw.text((72, 258), slide["sub"], font=SUB_FONT, fill=ACCENT)

    y = 360
    for bullet in slide["bullets"]:
        draw.ellipse((76, y + 12, 94, y + 30), fill=ACCENT)
        for line in wrap(draw, bullet, BULLET_FONT, 1020):
            draw.text((120, y), line, font=BULLET_FONT, fill=TEXT)
            y += 46
        y += 22

    # Decorative moving chips
    for i in range(6):
        x = 940 + i * 52
        cy = HEIGHT - 190 - 16 * math.sin(pulse + i * 0.7)
        fill = ACCENT if i % 2 == 0 else PANEL
        draw.rounded_rectangle((x, cy, x + 38, cy + 38), radius=8, fill=fill, outline=MUTED, width=2)

    # Footer
    draw.rectangle((0, HEIGHT - 78, WIDTH, HEIGHT), fill=PANEL)
    draw.text((48, HEIGHT - 56), slide["caption"], font=FOOT_FONT, fill=MUTED)

    return image


def render_part(part: dict) -> Path:
    OUT.mkdir(exist_ok=True)
    target = OUT / f"old-hardware-new-blocks-part-{part['part']}.mp4"
    with tempfile.TemporaryDirectory() as tmp:
        frames = Path(tmp)
        index = 0
        for slide_index, _ in enumerate(part["slides"]):
            for frame_in_slide in range(SECONDS_PER_SLIDE * FPS):
                frame = draw_frame(part, slide_index, frame_in_slide)
                frame.save(frames / f"frame_{index:05d}.png")
                index += 1
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-framerate",
                str(FPS),
                "-i",
                str(frames / "frame_%05d.png"),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(target),
            ],
            check=True,
        )
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the Old Hardware, New Blocks mini-series")
    parser.add_argument("--part", type=int, choices=[1, 2, 3], default=None)
    parser.add_argument("--dry-run", action="store_true", help="render preview PNGs only, skip ffmpeg")
    args = parser.parse_args()

    parts = [p for p in PARTS if args.part is None or p["part"] == args.part]
    for part in parts:
        if args.dry_run:
            OUT.mkdir(exist_ok=True)
            preview_dir = OUT / f"part-{part['part']}-previews"
            preview_dir.mkdir(exist_ok=True)
            for slide_index, _ in enumerate(part["slides"]):
                draw_frame(part, slide_index, 0).save(preview_dir / f"slide-{slide_index + 1}.png")
            print(preview_dir)
        else:
            print(render_part(part))


if __name__ == "__main__":
    main()
