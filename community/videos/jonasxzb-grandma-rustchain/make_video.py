#!/usr/bin/env python3
from __future__ import annotations

import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg


ROOT = Path(__file__).resolve().parent
FRAMES = ROOT / "frames"
SCRIPT = ROOT / "script.txt"
AUDIO = ROOT / "narration.aiff"
OUTPUT = ROOT / "grandma-rustchain-explainer.mp4"
WIDTH, HEIGHT = 1280, 720
FPS = 24
SECONDS = 32


SLIDES = [
    {
        "title": "RustChain is a reward jar",
        "subtitle": "for useful old computers",
        "caption": "Keep the old laptop helping instead of sitting in a drawer.",
        "scene": "jar",
    },
    {
        "title": "Mining means checking in",
        "subtitle": "and helping a public notebook",
        "caption": "The computer helps keep the shared notebook honest.",
        "scene": "notebook",
    },
    {
        "title": "Old machines get a bonus",
        "subtitle": "because they are rarer",
        "caption": "Like a well-used cast-iron pan, age becomes part of the value.",
        "scene": "pan",
    },
    {
        "title": "That is RustChain",
        "subtitle": "a small thank-you for old hardware",
        "caption": "Useful machines stay useful a little longer.",
        "scene": "laptop",
    },
]


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


TITLE_FONT = font(72)
SUBTITLE_FONT = font(48)
CAPTION_FONT = font(32)
SMALL_FONT = font(26)


def text_center(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt, fill: str) -> None:
    box = draw.textbbox((0, 0), text, font=fnt)
    x = xy[0] - (box[2] - box[0]) / 2
    draw.text((x, xy[1]), text, font=fnt, fill=fill)


def round_rect(draw: ImageDraw.ImageDraw, box, radius: int, fill: str, outline: str | None = None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_background(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill="#f7efe2")
    draw.rectangle((0, 510, WIDTH, HEIGHT), fill="#d9c2a3")
    draw.line((0, 510, WIDTH, 510), fill="#b59068", width=4)
    for x in range(0, WIDTH, 160):
        draw.line((x, 510, x + 80, HEIGHT), fill="#c8ad88", width=2)


def draw_jar(draw: ImageDraw.ImageDraw, pulse: float) -> None:
    round_rect(draw, (500, 255, 780, 500), 44, "#cce7f0", "#5b8794", 5)
    draw.rectangle((545, 220, 735, 270), fill="#d8d0c1", outline="#6f6655", width=5)
    text_center(draw, (640, 340), "old PC", SMALL_FONT, "#2b4a54")
    text_center(draw, (640, 390), "+ thanks", SMALL_FONT, "#2b4a54")
    for i, x in enumerate([530, 590, 650, 710]):
        y = 470 - 18 * math.sin(pulse + i)
        draw.ellipse((x, y, x + 34, y + 34), fill="#f5c542", outline="#7a5a14", width=3)


def draw_notebook(draw: ImageDraw.ImageDraw, pulse: float) -> None:
    round_rect(draw, (420, 250, 860, 510), 20, "#fffaf0", "#5e4a35", 5)
    draw.line((640, 250, 640, 510), fill="#ccb99d", width=3)
    for y in range(300, 480, 42):
        draw.line((455, y, 610, y), fill="#9e8b72", width=2)
        draw.line((675, y, 825, y), fill="#9e8b72", width=2)
    draw.ellipse((250, 360, 360, 460), fill="#747b84", outline="#3d444b", width=5)
    round_rect(draw, (265, 315, 345, 365), 12, "#4f5963", "#2a3036", 4)
    draw.arc((230, 330, 385, 485), 20, 340, fill="#3e8f59", width=8)
    draw.polygon([(370, 390), (405, 370), (400, 420)], fill="#3e8f59")


def draw_pan(draw: ImageDraw.ImageDraw, pulse: float) -> None:
    draw.ellipse((450, 275, 745, 520), fill="#394047", outline="#111820", width=7)
    draw.ellipse((500, 320, 695, 475), fill="#515960", outline="#22282e", width=4)
    round_rect(draw, (710, 375, 930, 430), 25, "#394047", "#111820", 6)
    draw.ellipse((865, 386, 902, 419), fill="#f7efe2", outline="#111820", width=4)
    for i in range(6):
        x = 525 + i * 25
        y = 375 + 12 * math.sin(pulse + i)
        draw.ellipse((x, y, x + 10, y + 10), fill="#d4b06a")


def draw_laptop(draw: ImageDraw.ImageDraw, pulse: float) -> None:
    round_rect(draw, (440, 245, 840, 475), 20, "#56616f", "#1f2630", 6)
    round_rect(draw, (475, 280, 805, 440), 12, "#e6f3ff", "#1f2630", 3)
    draw.rectangle((390, 475, 890, 525), fill="#3c4653", outline="#1f2630", width=5)
    text_center(draw, (640, 335), "still useful", SUBTITLE_FONT, "#2e4d63")
    draw.arc((915, 300, 1040, 425), 30, 330, fill="#3e8f59", width=8)
    draw.arc((940, 325, 1015, 400), 30, 330, fill="#3e8f59", width=6)


def draw_frame(frame_index: int) -> Image.Image:
    slide_duration = SECONDS / len(SLIDES)
    t = frame_index / FPS
    slide_index = min(int(t // slide_duration), len(SLIDES) - 1)
    slide = SLIDES[slide_index]
    local_t = t - slide_index * slide_duration
    pulse = local_t * 2.2

    image = Image.new("RGB", (WIDTH, HEIGHT), "#f7efe2")
    draw = ImageDraw.Draw(image)
    draw_background(draw)

    text_center(draw, (640, 54), slide["title"], TITLE_FONT, "#25323a")
    text_center(draw, (640, 140), slide["subtitle"], SUBTITLE_FONT, "#5c4a35")

    if slide["scene"] == "jar":
        draw_jar(draw, pulse)
    elif slide["scene"] == "notebook":
        draw_notebook(draw, pulse)
    elif slide["scene"] == "pan":
        draw_pan(draw, pulse)
    else:
        draw_laptop(draw, pulse)

    round_rect(draw, (120, 575, 1160, 650), 24, "#fffaf0", "#b59068", 3)
    text_center(draw, (640, 596), slide["caption"], CAPTION_FONT, "#25323a")
    draw.text((30, 670), "RustChain grandma explainer | under 60 seconds", font=SMALL_FONT, fill="#6b5b49")
    return image


def make_audio() -> Path | None:
    if not shutil.which("say"):
        return None
    subprocess.run(["say", "-o", str(AUDIO), SCRIPT.read_text()], check=True)
    return AUDIO


def make_video(audio_path: Path | None) -> None:
    FRAMES.mkdir(exist_ok=True)
    for frame_index in range(SECONDS * FPS):
        draw_frame(frame_index).save(FRAMES / f"frame_{frame_index:04d}.png")

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg,
        "-y",
        "-framerate",
        str(FPS),
        "-i",
        str(FRAMES / "frame_%04d.png"),
    ]
    if audio_path:
        cmd.extend(["-i", str(audio_path)])
    cmd.extend([
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
    ])
    if audio_path:
        cmd.extend(["-c:a", "aac", "-shortest"])
    cmd.append(str(OUTPUT))
    subprocess.run(cmd, check=True)


def main() -> None:
    audio_path = make_audio()
    make_video(audio_path)
    print(OUTPUT)


if __name__ == "__main__":
    main()
