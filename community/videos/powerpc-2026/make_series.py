#!/usr/bin/env python3
"""Render the 3-part BoTTube series "PowerPC in 2026".

Each episode is a self contained 30 second explainer built from four animated
slides and encoded with the ffmpeg binary that ships with imageio-ffmpeg.
Narration is added with the macOS ``say`` command when it is available and is
silently skipped otherwise, so the script also runs on Linux and Windows.

Usage:
    python community/videos/powerpc-2026/make_series.py
    python community/videos/powerpc-2026/make_series.py part-2
"""
from __future__ import annotations

import math
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
FRAMES = ROOT / "frames"
WIDTH, HEIGHT = 1280, 720
FPS = 24
SECONDS = 30

BG = "#12181d"
PANEL = "#1b242c"
INK = "#e8f1f8"
ACCENT = "#f5c542"
COOL = "#4fc3f7"
VIOLET = "#7e6cf7"


EPISODES = [
    {
        "slug": "part-1",
        "name": "PowerPC in 2026 \u2014 Part 1 \u2014 Why Big Endian Still Matters",
        "narration": (
            "PowerPC ran Macs from nineteen ninety four to two thousand six. "
            "It is big endian, meaning the most significant byte of a word comes first, "
            "which makes hex dumps readable. Open Firmware, GCC and QEMU still support "
            "it today. That combination, documented, bootable and cheap, is why old "
            "PowerPC hardware is still useful in twenty twenty six. Part two revives a G4, "
            "and part three benchmarks it against modern ARM."
        ),
        "slides": [
            {
                "title": "PowerPC in 2026",
                "subtitle": "Part 1 - why old chips still matter",
                "caption": "1994 to 2006 on the desktop. Still booting in 2026.",
                "scene": "chip",
            },
            {
                "title": "Big endian",
                "subtitle": "most significant byte first",
                "caption": "Byte order is a design choice, easy to read in a hex dump.",
                "scene": "board",
            },
            {
                "title": "Still documented",
                "subtitle": "manual, ROM and toolchain all survive",
                "caption": "Open Firmware, GCC and QEMU still target these parts.",
                "scene": "chip",
            },
            {
                "title": "Why it matters",
                "subtitle": "hardware does not expire",
                "caption": "Part 2 revives a G4. Part 3 puts it up against ARM.",
                "scene": "board",
            },
        ],
    },
    {
        "slug": "part-2",
        "name": "PowerPC in 2026 \u2014 Part 2 \u2014 Reviving a Power Mac G4",
        "narration": (
            "This is a Power Mac G4 from nineteen ninety nine. A recap on the power "
            "supply, an SSD on the ATA bus, and it boots. Open Firmware is not a BIOS, "
            "so instead of a settings screen you get a command prompt, and one boot "
            "command gets you to the desktop. The original drive stays in a drawer, "
            "untouched. Next episode, the same workload runs on this machine and on a "
            "modern ARM board."
        ),
        "slides": [
            {
                "title": "The G4",
                "subtitle": "a 1999 tower that still boots",
                "caption": "One CPU, working RAM, and a power supply worth recapping.",
                "scene": "board",
            },
            {
                "title": "Boot media",
                "subtitle": "an SSD on the ATA bus",
                "caption": "Cheap, quiet, and the original drive stays in a drawer.",
                "scene": "chip",
            },
            {
                "title": "Firmware",
                "subtitle": "Open Firmware, not a BIOS",
                "caption": "Type the boot command and the machine comes up.",
                "scene": "board",
            },
            {
                "title": "Next",
                "subtitle": "part 3 is the benchmark",
                "caption": "Same workload next episode, three very different chips.",
                "scene": "bars",
            },
        ],
    },
    {
        "slug": "part-3",
        "name": "PowerPC in 2026 \u2014 Part 3 \u2014 Benchmarking Against Modern ARM",
        "narration": (
            "One small C program, compiled natively on each machine, timed with the same "
            "workload. The G4 finishes last, roughly where you would expect a chip from "
            "nineteen ninety nine to land. But performance is only one number. Measure "
            "idle wattage instead, and the old machine draws a fraction of the power, "
            "which matters when it runs all day. Slower is not the same as useless."
        ),
        "slides": [
            {
                "title": "The benchmark",
                "subtitle": "one build, three machines",
                "caption": "A small C program, built on each box, timed the same way.",
                "scene": "bars",
            },
            {
                "title": "Results",
                "subtitle": "old silicon is slower per second",
                "caption": "The G4 finishes last, and draws a fraction of the power.",
                "scene": "bars",
            },
            {
                "title": "But",
                "subtitle": "performance is not the only number",
                "caption": "Idle wattage matters when the machine runs all day.",
                "scene": "chip",
            },
            {
                "title": "Conclusion",
                "subtitle": "useful, not fastest",
                "caption": "Old hardware earns its keep when the workload fits.",
                "scene": "board",
            },
        ],
    },
]


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


TITLE_FONT = font(64)
SUBTITLE_FONT = font(38)
CAPTION_FONT = font(28)
LABEL_FONT = font(22)
CHIP_FONT = font(56)


def text_center(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt, fill: str) -> None:
    box = draw.textbbox((0, 0), text, font=fnt)
    x = xy[0] - (box[2] - box[0]) / 2
    draw.text((x, xy[1]), text, font=fnt, fill=fill)


def round_rect(
    draw: ImageDraw.ImageDraw,
    box,
    radius: int,
    fill: str,
    outline: str | None = None,
    width: int = 1,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_background(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=BG)
    for x in range(0, WIDTH, 64):
        draw.line((x, 0, x, HEIGHT), fill="#182028")
    for y in range(0, HEIGHT, 64):
        draw.line((0, y, WIDTH, y), fill="#182028")
    draw.rectangle((0, 520, WIDTH, HEIGHT), fill=PANEL)
    draw.line((0, 520, WIDTH, 520), fill=ACCENT, width=3)


def draw_chip(draw: ImageDraw.ImageDraw, pulse: float) -> None:
    r = 150 + 10 * math.sin(pulse)
    draw.ellipse((640 - r, 370 - r, 640 + r, 370 + r), outline=ACCENT, width=3)
    for i in range(7):
        y = 290 + i * 30
        draw.line((480, y, 515, y), fill="#8fa3b3", width=8)
        draw.line((765, y, 800, y), fill="#8fa3b3", width=8)
    round_rect(draw, (515, 265, 765, 480), 18, "#243440", COOL, 4)
    round_rect(draw, (555, 305, 725, 440), 8, "#2f4657", COOL, 2)
    text_center(draw, (640, 345), "PPC", CHIP_FONT, INK)


def draw_board(draw: ImageDraw.ImageDraw, pulse: float) -> None:
    round_rect(draw, (400, 265, 880, 480), 16, "#1d3a2a", "#2f6b47", 4)
    for i in range(5):
        y = 300 + i * 36
        draw.line((430, y, 850, y), fill="#2f6b47", width=3)
    for i in range(6):
        x = 450 + i * 70
        draw.line((x, 300, x, 445), fill="#2f6b47", width=3)
    for i in range(4):
        x = 470 + i * 100
        lit = math.sin(pulse + i) > 0
        draw.ellipse((x, 445, x + 22, 467), fill=ACCENT if lit else "#3c4a3f")
    round_rect(draw, (530, 320, 750, 420), 10, "#111c16", "#2f6b47", 3)
    text_center(draw, (640, 340), "G4", CHIP_FONT, INK)


def draw_bars(draw: ImageDraw.ImageDraw, pulse: float) -> None:
    base = 480
    labels = ["G4", "M1", "M3"]
    colors = [ACCENT, COOL, VIOLET]
    heights = [110, 190, 250]
    for i, (label, color) in enumerate(zip(labels, colors)):
        x = 470 + i * 130
        h = heights[i] * (0.92 + 0.08 * math.sin(pulse + i))
        draw.rectangle((x, base - h, x + 90, base), fill=color)
        text_center(draw, (x + 45, base + 10), label, LABEL_FONT, INK)


def draw_frame(episode: dict, slide: dict, pulse: float) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw_background(draw)

    text_center(draw, (640, 58), slide["title"], TITLE_FONT, INK)
    text_center(draw, (640, 150), slide["subtitle"], SUBTITLE_FONT, ACCENT)

    if slide["scene"] == "chip":
        draw_chip(draw, pulse)
    elif slide["scene"] == "board":
        draw_board(draw, pulse)
    else:
        draw_bars(draw, pulse)

    round_rect(draw, (90, 575, 1190, 660), 20, "#0e1418", "#2c3a44", 3)
    text_center(draw, (640, 604), slide["caption"], CAPTION_FONT, INK)
    draw.text((28, 682), episode["name"] + "  |  bottube.ai", font=LABEL_FONT, fill="#6c8494")
    return image


def render_frames(episode: dict, frame_dir: Path) -> Path:
    frame_dir.mkdir(parents=True, exist_ok=True)
    slides = episode["slides"]
    per_slide = SECONDS / len(slides)
    for index in range(SECONDS * FPS):
        t = index / FPS
        slide_index = min(int(t // per_slide), len(slides) - 1)
        local_t = t - slide_index * per_slide
        draw_frame(episode, slides[slide_index], local_t * 2.2).save(
            frame_dir / ("frame_%04d.png" % index)
        )
    return frame_dir


def narrate(episode: dict) -> Path | None:
    if not shutil.which("say"):
        return None
    OUT.mkdir(parents=True, exist_ok=True)
    audio = OUT / (episode["slug"] + ".aiff")
    subprocess.run(["say", "-o", str(audio), episode["narration"]], check=True)
    return audio


def encode(episode: dict, frame_dir: Path, audio_path: Path | None) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    output = OUT / (episode["slug"] + ".mp4")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg,
        "-y",
        "-framerate",
        str(FPS),
        "-i",
        str(frame_dir / "frame_%04d.png"),
    ]
    if audio_path:
        cmd.extend(["-i", str(audio_path)])
    cmd.extend(["-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart"])
    if audio_path:
        cmd.extend(["-c:a", "aac", "-shortest"])
    cmd.append(str(output))
    subprocess.run(cmd, check=True)
    return output


def main(argv: list[str]) -> int:
    wanted = set(argv[1:])
    for episode in EPISODES:
        if wanted and episode["slug"] not in wanted:
            continue
        frame_dir = FRAMES / episode["slug"]
        render_frames(episode, frame_dir)
        audio_path = narrate(episode)
        output = encode(episode, frame_dir, audio_path)
        shutil.rmtree(frame_dir, ignore_errors=True)
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
