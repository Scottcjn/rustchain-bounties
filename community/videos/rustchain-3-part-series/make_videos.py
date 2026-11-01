#!/usr/bin/env python3
"""Generate the 3-part BoTTube series "RustChain Mining in 3 Steps".

Run from the repository root::

    python community/videos/rustchain-3-part-series/make_videos.py

Three MP4 files are written to ``output/`` next to this script:

    part-1-install.mp4
    part-2-configure.mp4
    part-3-results.mp4

Each part is ~32 seconds (4 slides x 8 seconds), which fits the bounty's
30 second - 5 minute requirement. Narration is added automatically when the
macOS ``say`` command is available; otherwise the videos are silent.
"""
from __future__ import annotations

import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "output"
WIDTH, HEIGHT = 1280, 720
FPS = 24
SECONDS_PER_SLIDE = 8.0


PARTS = [
    {
        "slug": "part-1-install",
        "title": "RustChain Mining in 3 Steps - Part 1 - Install the Miner",
        "narration": (
            "Part one. RustChain mining in three steps. "
            "Step one is installation. The miner is a small program that runs on any CPU. "
            "RustChain uses Proof of Antiquity, where the age of the hardware matters more than raw speed. "
            "Install it with pip, then send your first attestation so the machine can prove how old it is."
        ),
        "slides": [
            {
                "title": "Step 1: Install",
                "subtitle": "one command, no GPU needed",
                "caption": "The miner is a small program that runs on any CPU.",
                "scene": "terminal",
            },
            {
                "title": "Proof of Antiquity",
                "subtitle": "age beats raw speed",
                "caption": "Older hardware earns a higher multiplier than a brand new machine.",
                "scene": "cpu",
            },
            {
                "title": "Get the miner",
                "subtitle": "pip install rustchain-miner",
                "caption": "Grab the code, then run it from the folder you installed it into.",
                "scene": "download",
            },
            {
                "title": "First attestation",
                "subtitle": "the machine proves its age",
                "caption": "The attestation records the hardware fingerprint on the network.",
                "scene": "network",
            },
        ],
    },
    {
        "slug": "part-2-configure",
        "title": "RustChain Mining in 3 Steps - Part 2 - Configure and Mine",
        "narration": (
            "Part two. Now that the miner is installed, point it at a RustChain node. "
            "Check the multiplier for your hardware so you know what to expect. "
            "Rewards land in your wallet every epoch. "
            "Keep the machine connected: one CPU, one vote, no ASIC arms race."
        ),
        "slides": [
            {
                "title": "Step 2: Configure",
                "subtitle": "point it at the RTC node",
                "caption": "Set the node address once, then start the miner in the background.",
                "scene": "terminal",
            },
            {
                "title": "Know your multiplier",
                "subtitle": "vintage hardware earns more",
                "caption": "A PowerMac or a POWER8 server beats a modern desktop on the reward curve.",
                "scene": "cpu",
            },
            {
                "title": "Watch the balance",
                "subtitle": "rewards land every epoch",
                "caption": "Your RTC wallet grows as long as attestations keep arriving.",
                "scene": "wallet",
            },
            {
                "title": "Stay connected",
                "subtitle": "one CPU, one vote",
                "caption": "Stable uptime matters far more than short bursts of hashing power.",
                "scene": "network",
            },
        ],
    },
    {
        "slug": "part-3-results",
        "title": "RustChain Mining in 3 Steps - Part 3 - Results and Tips",
        "narration": (
            "Part three. Results and tips. "
            "After a week of mining you can compare the rewards against the power draw. "
            "Avoid the common mistakes: sleep mode, thermal throttling and clock drift. "
            "Add more machines when you are ready, then join the community to keep learning."
        ),
        "slides": [
            {
                "title": "Step 3: Results",
                "subtitle": "what a week of mining looks like",
                "caption": "Compare the RTC you earned against the electricity the machine used.",
                "scene": "wallet",
            },
            {
                "title": "Common mistakes",
                "subtitle": "sleep, heat and clock drift",
                "caption": "Disable sleep and clean the fans before you leave a machine running.",
                "scene": "terminal",
            },
            {
                "title": "Add more hardware",
                "subtitle": "more machines, more attestations",
                "caption": "Each extra machine is another independent fingerprint on the network.",
                "scene": "network",
            },
            {
                "title": "Join the community",
                "subtitle": "open bounties and build guides",
                "caption": "Old hardware stays useful a little longer. That is RustChain.",
                "scene": "cpu",
            },
        ],
    },
]



def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


TITLE_FONT = font(64)
SUBTITLE_FONT = font(42)
CAPTION_FONT = font(30)
SMALL_FONT = font(24)


def text_center(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt, fill: str) -> None:
    box = draw.textbbox((0, 0), text, font=fnt)
    x = xy[0] - (box[2] - box[0]) / 2
    draw.text((x, xy[1]), text, font=fnt, fill=fill)


def round_rect(draw: ImageDraw.ImageDraw, box, radius: int, fill: str, outline: str | None = None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_background(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill="#f7efe2")
    draw.rectangle((0, 520, WIDTH, HEIGHT), fill="#d9c2a3")
    draw.line((0, 520, WIDTH, 520), fill="#b59068", width=4)
    for x in range(0, WIDTH, 160):
        draw.line((x, 520, x + 80, HEIGHT), fill="#c8ad88", width=2)


def draw_terminal(draw: ImageDraw.ImageDraw, pulse: float) -> None:
    round_rect(draw, (360, 230, 920, 520), 18, "#1f2630", "#0d1117", 6)
    draw.rectangle((360, 230, 920, 272), fill="#3c4653")
    for i, cx in enumerate([390, 415, 440]):
        color = ["#e06c75", "#e5c07b", "#98c379"][i]
        draw.ellipse((cx, 242, cx + 18, 260), fill=color)
    lines = [
        "$ pip install rustchain-miner",
        "$ rustchain-miner --attest",
        "OK   hardware fingerprint sent",
    ]
    y = 305
    for line in lines:
        draw.text((395, y), line, font=SMALL_FONT, fill="#98c379")
        y += 60
    if pulse % 2 < 1:
        draw.rectangle((830, 425, 848, 450), fill="#98c379")


def draw_cpu(draw: ImageDraw.ImageDraw, pulse: float) -> None:
    round_rect(draw, (520, 270, 760, 500), 16, "#56616f", "#1f2630", 6)
    text_center(draw, (640, 350), "OLD CPU", SUBTITLE_FONT, "#f7efe2")
    text_center(draw, (640, 410), "2x bonus", CAPTION_FONT, "#f5c542")
    for i in range(6):
        y = 285 + i * 36
        draw.rectangle((470, y, 520, y + 16), fill="#b59068")
        draw.rectangle((760, y, 810, y + 16), fill="#b59068")
    glow = 8 + 4 * math.sin(pulse)
    draw.ellipse((640 - glow, 500 - glow, 640 + glow, 500 + glow), fill="#f5c542")


def draw_download(draw: ImageDraw.ImageDraw, pulse: float) -> None:
    round_rect(draw, (490, 235, 790, 505), 24, "#fffaf0", "#5e4a35", 5)
    round_rect(draw, (540, 275, 740, 325), 10, "#e6dfd2", "#b59068", 2)
    text_center(draw, (640, 288), "rustchain-miner", SMALL_FONT, "#5c4a35")
    draw.line((640, 355, 640, 445), fill="#3e8f59", width=12)
    draw.polygon([(600, 430), (680, 430), (640, 480)], fill="#3e8f59")
    y = 500 - 10 * math.sin(pulse)
    draw.rectangle((520, y, 760, y + 16), fill="#c8ad88")


def draw_wallet(draw: ImageDraw.ImageDraw, pulse: float) -> None:
    round_rect(draw, (470, 280, 810, 490), 20, "#5e4a35", "#2b2118", 6)
    round_rect(draw, (515, 325, 765, 380), 10, "#f7efe2", "#2b2118", 3)
    text_center(draw, (640, 338), "RTC balance", SMALL_FONT, "#2b4a54")
    text_center(draw, (640, 400), "+5 RTC", TITLE_FONT, "#f5c542")
    shine = 6 + 3 * math.sin(pulse)
    draw.ellipse((640 - shine, 490 - shine, 640 + shine, 490 + shine), fill="#f5c542")


def draw_network(draw: ImageDraw.ImageDraw, pulse: float) -> None:
    center = (640, 300)
    nodes = [(450, 430), (830, 430), (520, 240), (760, 240)]
    for x, y in nodes:
        draw.line((center[0], center[1], x, y), fill="#b59068", width=4)
    for i, (x, y) in enumerate(nodes):
        r = 24 + 5 * math.sin(pulse + i)
        draw.ellipse((x - r, y - r, x + r, y + r), fill="#3e8f59", outline="#1f4a2e", width=3)
    r = 40 + 6 * math.sin(pulse)
    draw.ellipse((center[0] - r, center[1] - r, center[0] + r, center[1] + r), fill="#3e8f59", outline="#1f4a2e", width=4)
    text_center(draw, (center[0], center[1] - 14), "RTC", SMALL_FONT, "#f7efe2")


SCENES = {
    "terminal": draw_terminal,
    "cpu": draw_cpu,
    "download": draw_download,
    "wallet": draw_wallet,
    "network": draw_network,
}


def draw_frame(part: dict, frame_index: int) -> Image.Image:
    slides = part["slides"]
    t = frame_index / FPS
    slide_index = min(int(t // SECONDS_PER_SLIDE), len(slides) - 1)
    slide = slides[slide_index]
    pulse = (t - slide_index * SECONDS_PER_SLIDE) * 2.2

    image = Image.new("RGB", (WIDTH, HEIGHT), "#f7efe2")
    draw = ImageDraw.Draw(image)
    draw_background(draw)

    text_center(draw, (640, 40), part["title"], SMALL_FONT, "#6b5b49")
    text_center(draw, (640, 90), slide["title"], TITLE_FONT, "#25323a")
    text_center(draw, (640, 172), slide["subtitle"], SUBTITLE_FONT, "#5c4a35")

    SCENES[slide["scene"]](draw, pulse)

    round_rect(draw, (120, 580, 1160, 652), 24, "#fffaf0", "#b59068", 3)
    text_center(draw, (640, 600), slide["caption"], CAPTION_FONT, "#25323a")
    text_center(draw, (640, 672), part["slug"], SMALL_FONT, "#6b5b49")
    return image


def make_audio(part: dict) -> Path | None:
    if not shutil.which("say"):
        return None
    audio = OUT_DIR / f"{part['slug']}.aiff"
    subprocess.run(["say", "-o", str(audio), part["narration"]], check=True)
    return audio


def make_video(part: dict) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frames_dir = OUT_DIR / "frames" / part["slug"]
    frames_dir.mkdir(parents=True, exist_ok=True)

    total_frames = int(len(part["slides"]) * SECONDS_PER_SLIDE * FPS)
    for frame_index in range(total_frames):
        draw_frame(part, frame_index).save(frames_dir / f"frame_{frame_index:04d}.png")

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    output = OUT_DIR / f"{part['slug']}.mp4"
    cmd = [
        ffmpeg,
        "-y",
        "-framerate",
        str(FPS),
        "-i",
        str(frames_dir / "frame_%04d.png"),
    ]
    audio = make_audio(part)
    if audio:
        cmd.extend(["-i", str(audio)])
    cmd.extend(["-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart"])
    if audio:
        cmd.extend(["-c:a", "aac", "-shortest"])
    cmd.append(str(output))
    subprocess.run(cmd, check=True)

    shutil.rmtree(frames_dir, ignore_errors=True)
    return output


def main() -> None:
    for part in PARTS:
        path = make_video(part)
        print(f"{part['title']}\n  -> {path}")


if __name__ == "__main__":
    main()
