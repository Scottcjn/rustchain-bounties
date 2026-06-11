from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH = 1200
HEIGHT = 675
OUT = Path(__file__).with_name("rustchain-starstruck-128.png")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def text_size(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=face)
    return box[2] - box[0], box[3] - box[1]


def draw_centered(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, face: ImageFont.ImageFont, fill: str) -> None:
    w, h = text_size(draw, text, face)
    draw.text((x - w / 2, y - h / 2), text, font=face, fill=fill)


def star_points(cx: float, cy: float, outer: float, inner: float, points: int = 5) -> list[tuple[float, float]]:
    coords: list[tuple[float, float]] = []
    for i in range(points * 2):
        angle = -math.pi / 2 + i * math.pi / points
        radius = outer if i % 2 == 0 else inner
        coords.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
    return coords


def rounded_rectangle_gradient(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], radius: int, outline: str) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=(255, 255, 255, 18), outline=outline, width=2)


def make_background() -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), "#0d1420")
    px = img.load()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            dx = x / WIDTH
            dy = y / HEIGHT
            warm = max(0.0, 1.0 - ((dx - 0.75) ** 2 + (dy - 0.18) ** 2) * 5.0)
            cool = max(0.0, 1.0 - ((dx - 0.16) ** 2 + (dy - 0.72) ** 2) * 4.0)
            r = int(13 + 45 * warm + 5 * cool)
            g = int(20 + 36 * warm + 36 * cool)
            b = int(32 + 14 * warm + 52 * cool)
            px[x, y] = (r, g, b)
    return img


def draw_computer(draw: ImageDraw.ImageDraw) -> None:
    monitor = (786, 288, 1058, 456)
    screen = (812, 314, 1032, 418)
    draw.rounded_rectangle(monitor, radius=20, fill="#1c2632", outline="#80e0d4", width=3)
    draw.rounded_rectangle(screen, radius=12, fill="#0b1119", outline="#33495a", width=2)
    for i, color in enumerate(["#f7b267", "#4dd0c8", "#f26d85"]):
        x = 842 + i * 54
        draw.polygon(star_points(x, 366, 17, 7), fill=color)
    draw.rectangle((894, 456, 950, 491), fill="#202b38")
    draw.rounded_rectangle((842, 490, 1002, 512), radius=8, fill="#263543")
    draw.rounded_rectangle((808, 528, 1050, 575), radius=12, fill="#1c2632", outline="#5c7486", width=2)
    for i in range(10):
        x = 832 + i * 21
        draw.rounded_rectangle((x, 542, x + 12, 552), radius=3, fill="#8fa8b8")


def main() -> None:
    random.seed(128)
    base = make_background().convert("RGBA")
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, "RGBA")
    gd.ellipse((705, 58, 1170, 526), fill=(247, 178, 103, 45))
    gd.ellipse((46, 394, 486, 782), fill=(77, 208, 200, 30))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    base.alpha_composite(glow)

    draw = ImageDraw.Draw(base, "RGBA")
    for _ in range(82):
        x = random.randint(30, WIDTH - 30)
        y = random.randint(30, HEIGHT - 30)
        r = random.choice([1, 1, 2, 2, 3])
        alpha = random.randint(60, 155)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 238, 190, alpha))

    title = font(80, True)
    count = font(150, True)
    label = font(32, True)
    small = font(25)
    tiny = font(20, True)

    draw.text((78, 78), "RustChain", font=font(36, True), fill="#f7f2df")
    draw.text((80, 121), "Vintage Hardware DePIN", font=font(23), fill="#9fb3c2")

    draw.text((74, 196), "128", font=count, fill="#f7b267")
    draw.text((350, 231), "GitHub", font=title, fill="#f7f2df")
    draw.text((350, 312), "Stars", font=title, fill="#f7f2df")
    draw.rounded_rectangle((82, 418, 584, 477), radius=14, fill=(10, 17, 26, 160), outline="#f7b267", width=2)
    draw.text((108, 433), "Starstruck Bronze badge unlocked", font=label, fill="#f8dec1")
    draw.text((86, 510), "Old machines. New signal. Real silicon still matters.", font=small, fill="#bfd2dc")

    badge_cx, badge_cy = 942, 177
    draw.ellipse((badge_cx - 95, badge_cy - 95, badge_cx + 95, badge_cy + 95), fill="#9b5d28", outline="#ffe0a3", width=5)
    draw.ellipse((badge_cx - 72, badge_cy - 72, badge_cx + 72, badge_cy + 72), fill="#c9823a", outline="#5b351b", width=3)
    draw.polygon(star_points(badge_cx, badge_cy - 10, 49, 21), fill="#fff0bb", outline="#6c3e1d")
    draw_centered(draw, badge_cx, badge_cy + 57, "BRONZE", tiny, "#2c1b12")

    draw_computer(draw)

    rounded_rectangle_gradient(draw, (690, 596, 1088, 638), 18, "#4dd0c8")
    draw.text((714, 607), "Elyan Labs  /  Proof of Antiquity", font=font(23, True), fill="#d7fff9")

    draw.line((80, 612, 594, 612), fill=(247, 178, 103, 130), width=3)
    draw.text((82, 625), "Celebrating the first 128 people who noticed.", font=font(21), fill="#95aaba")

    base.convert("RGB").save(OUT, optimize=True)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
