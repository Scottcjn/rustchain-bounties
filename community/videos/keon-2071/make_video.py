#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import shutil
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
VIDEO = ROOT / "rustchain-grandma-explainer-keon-2071.mp4"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


NARRATION = """
Grandma, RustChain is a reward network for useful old computers.
Mining here means your computer checks in, proves it is a real machine, and helps keep the network alive.
New computers can join, but older computers get a bigger thank you because they are harder to fake and often get thrown away.
So instead of sending every old laptop to a drawer or a landfill, RustChain gives it a job and pays small rewards.
If you have an old computer that still runs, you can install the miner, point rewards to your wallet, and let it help the network.
"""


SCENES = [
    ("A shelf of old computers", "Old machines usually end up forgotten."),
    ("RustChain gives them a job", "A computer checks in and helps the network."),
    ("Mining means helping", "It is like taking turns keeping the notebook honest."),
    ("Older computers get a bigger thank you", "The older the real machine, the stronger the reward boost."),
    ("Fake machines do not get the same trust", "The checks look for real hardware behavior."),
    ("Download the miner", "Use the miner, choose a wallet, and join the network."),
]


def draw_computer(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float, color: tuple[int, int, int]) -> None:
    w, h = int(150 * scale), int(95 * scale)
    draw.rounded_rectangle((x, y, x + w, y + h), radius=int(8 * scale), fill=color, outline=(35, 55, 60), width=2)
    draw.rectangle((x + int(16 * scale), y + int(15 * scale), x + w - int(16 * scale), y + h - int(24 * scale)), fill=(16, 35, 40))
    draw.rectangle((x + int(60 * scale), y + h, x + int(90 * scale), y + h + int(22 * scale)), fill=(78, 92, 96))
    draw.rounded_rectangle((x + int(30 * scale), y + h + int(21 * scale), x + w - int(30 * scale), y + h + int(32 * scale)), radius=4, fill=(78, 92, 96))


def draw_coin(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, text: str) -> None:
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(236, 187, 76), outline=(133, 92, 24), width=3)
    draw.text((cx, cy), text, anchor="mm", fill=(80, 48, 8), font=ImageFont.truetype(BOLD, max(12, r // 2)))


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, width: int) -> list[str]:
    out: list[str] = []
    for raw in text.splitlines():
        words = raw.split()
        line = ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if draw.textbbox((0, 0), candidate, font=font)[2] <= width:
                line = candidate
            else:
                if line:
                    out.append(line)
                line = word
        if line:
            out.append(line)
    return out


def render_frames() -> int:
    frames = ROOT / "frames"
    if frames.exists():
        shutil.rmtree(frames)
    frames.mkdir()

    title_font = ImageFont.truetype(BOLD, 42)
    body_font = ImageFont.truetype(FONT, 29)
    small_font = ImageFont.truetype(FONT, 20)
    fps = 12
    scene_seconds = 8
    total_seconds = len(SCENES) * scene_seconds
    idx = 0

    for scene_idx, (title, body) in enumerate(SCENES):
        for local in range(scene_seconds * fps):
            t = local / fps
            global_t = idx / fps
            img = Image.new("RGB", (1280, 720), (244, 247, 241))
            draw = ImageDraw.Draw(img)

            for y in range(720):
                shade = int(244 - 28 * y / 720)
                draw.line((0, y, 1280, y), fill=(shade, min(255, shade + 5), min(255, shade + 1)))

            draw.rounded_rectangle((70, 72, 1210, 628), radius=28, fill=(255, 252, 242), outline=(210, 220, 211), width=3)

            if scene_idx == 0:
                for n, color in enumerate([(151, 119, 90), (126, 145, 126), (166, 139, 98)]):
                    draw_computer(draw, 220 + n * 260, 320 + int(10 * math.sin(global_t + n)), 1.05, color)
                draw.line((170, 465, 1030, 465), fill=(126, 104, 80), width=8)
            elif scene_idx == 1:
                draw_computer(draw, 340, 300, 1.25, (126, 145, 126))
                draw.line((560, 350, 820, 250), fill=(15, 118, 110), width=6)
                draw.line((560, 350, 840, 430), fill=(15, 118, 110), width=6)
                draw_coin(draw, 870, 250, 52, "RTC")
                draw_coin(draw, 890, 430, 42, "RTC")
            elif scene_idx == 2:
                draw.rounded_rectangle((285, 300, 995, 470), radius=14, fill=(232, 239, 231), outline=(130, 150, 145), width=3)
                for n in range(5):
                    x = 340 + n * 120
                    draw.ellipse((x, 342, x + 62, 404), fill=(15, 118, 110))
                    draw.text((x + 31, 373), str(n + 1), anchor="mm", fill="white", font=ImageFont.truetype(BOLD, 24))
                draw.text((640, 438), "everyone takes turns", anchor="mm", fill=(62, 76, 72), font=small_font)
            elif scene_idx == 3:
                draw_computer(draw, 280, 315, 0.95, (171, 180, 181))
                draw.text((355, 285), "new", anchor="mm", fill=(83, 93, 95), font=small_font)
                draw_coin(draw, 640, 360, 42, "1x")
                draw_computer(draw, 760, 300, 1.15, (151, 119, 90))
                draw.text((850, 275), "old", anchor="mm", fill=(83, 63, 45), font=small_font)
                draw_coin(draw, 1050, 345, 58, "2.5x")
            elif scene_idx == 4:
                draw_computer(draw, 285, 305, 1.05, (126, 145, 126))
                draw.text((365, 280), "real", anchor="mm", fill=(21, 100, 76), font=small_font)
                draw.rounded_rectangle((735, 305, 925, 430), radius=8, fill=(210, 210, 210), outline=(140, 140, 140), width=3)
                draw.text((830, 365), "copy", anchor="mm", fill=(90, 90, 90), font=ImageFont.truetype(BOLD, 28))
                draw.line((720, 290, 950, 450), fill=(190, 42, 42), width=8)
            else:
                draw_computer(draw, 310, 310, 1.15, (126, 145, 126))
                draw.rounded_rectangle((685, 315, 1015, 420), radius=14, fill=(15, 118, 110))
                draw.text((850, 368), "Install miner", anchor="mm", fill="white", font=ImageFont.truetype(BOLD, 34))
                draw_coin(draw, 1040, 470, 48, "RTC")

            draw.text((105, 110), title, fill=(20, 31, 30), font=title_font)
            y = 176
            for line in wrap(draw, body, body_font, 1030)[:3]:
                draw.text((108, y), line, fill=(72, 84, 82), font=body_font)
                y += 40

            progress = int(1100 * (idx / max(1, total_seconds * fps - 1)))
            draw.rounded_rectangle((90, 662, 1190, 676), radius=7, fill=(224, 230, 222))
            draw.rounded_rectangle((90, 662, 90 + progress, 676), radius=7, fill=(15, 118, 110))
            draw.text((1040, 110), "RustChain.org", fill=(15, 118, 110), font=small_font)
            img.save(frames / f"frame_{idx:04d}.png")
            idx += 1

    return total_seconds


def main() -> None:
    duration = render_frames()
    (ROOT / "narration.txt").write_text(textwrap.dedent(NARRATION).strip() + "\n")
    subprocess.run(["say", "-r", "151", "-o", str(ROOT / "voice.aiff"), "-f", str(ROOT / "narration.txt")], check=True)
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "sine=frequency=220:duration=48:sample_rate=44100",
            "-af", "volume=0.035,afade=t=in:st=0:d=2,afade=t=out:st=45:d=3",
            str(ROOT / "music.wav"),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-framerate", "12", "-i", str(ROOT / "frames/frame_%04d.png"),
            "-i", str(ROOT / "voice.aiff"),
            "-i", str(ROOT / "music.wav"),
            "-filter_complex", "[1:a][2:a]amix=inputs=2:duration=longest:dropout_transition=1[a]",
            "-map", "0:v", "-map", "[a]",
            "-t", str(duration),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
            "-r", "24", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "64k",
            "-movflags", "+faststart",
            str(VIDEO),
        ],
        check=True,
    )
    (ROOT / "metadata.json").write_text(
        json.dumps(
            {
                "bounty": "rustchain-bounties #2071",
                "title": "RustChain to Grandma: Old Computers Can Help",
                "duration_seconds": duration,
                "wallet": "RTC1410e82d545ce0b3ffd21ca83e2465a8f2c3a64e",
                "notes": "Under 60 seconds; narration uses plain everyday language.",
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
