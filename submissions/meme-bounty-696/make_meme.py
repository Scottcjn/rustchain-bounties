from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1200
HEIGHT = 1200
OUT = Path(__file__).with_name("rustchain-proof-of-antiquity-meme.png")

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

BG = (13, 20, 32)
PANEL = (28, 38, 50)
TEAL = (128, 224, 212)
AMBER = (247, 178, 103)
PINK = (242, 109, 133)
GREEN = (77, 208, 200)
TEXT = (224, 232, 240)
MUTED = (148, 163, 184)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT, size=size)


def text_size(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=face)
    return box[2] - box[0], box[3] - box[1]


def draw_centered(draw: ImageDraw.ImageDraw, cx: int, y: int, text: str, face: ImageFont.ImageFont, fill: str) -> None:
    w, h = text_size(draw, text, face)
    draw.text((cx - w / 2, y - h / 2), text, font=face, fill=fill)


def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if text_size(draw, trial, face)[0] <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_panel(draw: ImageDraw.ImageDraw, y: int, h: int, title: str, title_color: str, body: str) -> None:
    draw.rounded_rectangle((60, y, WIDTH - 60, y + h), radius=24, fill=PANEL, outline=(51, 73, 90), width=2)
    title_face = font(40, bold=True)
    draw_centered(draw, WIDTH // 2, y + 42, title, title_face, title_color)
    body_face = font(30)
    lines = wrap(draw, body, body_face, WIDTH - 180)
    total = len(lines) * 40
    start_y = y + 86 - (total - 40) / 2
    for i, line in enumerate(lines):
        draw_centered(draw, WIDTH // 2, int(start_y + i * 40), line, body_face, TEXT)


def draw_icons(draw: ImageDraw.ImageDraw) -> None:
    cx = WIDTH // 2

    draw.rounded_rectangle((cx - 60, 175, cx + 60, 235), radius=10, fill=(20, 28, 38), outline=AMBER, width=3)
    for i in range(4):
        draw.rounded_rectangle((cx - 45 + i * 30, 190, cx - 30 + i * 30, 220), radius=3, fill=AMBER)
    draw.line((cx - 30, 235, cx + 30, 235), fill=AMBER, width=4)

    cy = 175 + 60
    draw.ellipse((cx - 70, cy - 60, cx - 10, cy), outline=GREEN, width=6)
    draw.ellipse((cx + 10, cy - 60, cx + 70, cy), outline=GREEN, width=6)
    draw.rectangle((cx - 8, cy - 52, cx + 8, cy - 8), fill=GREEN)
    draw.rounded_rectangle((cx - 22, cy - 8, cx + 22, cy + 14), radius=6, fill=GREEN)

    cy = 175 + 60 + 8
    draw.rounded_rectangle((cx - 56, cy - 6, cx + 56, cy + 6), radius=6, fill=(255, 255, 255, 30), outline=TEAL, width=2)
    draw.polygon([(cx - 30, cy - 2), (cx - 20, cy - 10), (cx - 10, cy - 2), (cx + 10, cy - 2), (cx + 20, cy - 10), (cx + 30, cy - 2), (cx + 30, cy + 2), (cx + 20, cy + 10), (cx + 10, cy + 2), (cx - 10, cy + 2), (cx - 20, cy + 10), (cx - 30, cy + 2)], fill=TEAL)


def make_meme() -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    draw.ellipse((-200, -250, 500, 450), fill=(16, 26, 42))
    draw.ellipse((WIDTH - 400, 850, WIDTH + 250, 1450), fill=(16, 26, 42))

    draw_panel(draw, 150, 270, "PROOF OF WORK", AMBER,
               "1000W GPU rig burning the electric bill for 0.001 BTC")
    draw_panel(draw, 470, 270, "PROOF OF STAKE", GREEN,
               "Need $30k minimum to even join. The rich get richer.")
    draw_panel(draw, 790, 270, "PROOF OF ANTIQUITY", TEAL,
               "2003 Power Mac G4 from a pawn shop. Now it mines RTC.")

    footer_y = 1120
    caption_face = font(32, bold=True)
    draw_centered(draw, WIDTH // 2, footer_y, "RustChain: your vintage Mac out-earns the GPU rig", caption_face, TEXT)
    sub_face = font(26)
    draw_centered(draw, WIDTH // 2, footer_y + 46, "@RustchainPOA  |  rustchain.org  |  #ProofOfAntiquity", sub_face, MUTED)

    return img


if __name__ == "__main__":
    img = make_meme()
    img.save(OUT, "PNG")
    print(f"Saved {OUT} ({OUT.stat().st_size} bytes)")