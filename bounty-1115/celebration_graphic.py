#!/usr/bin/env python3
"""
Bounty #1115: 128 Stars Celebration Graphic
Creates a celebration graphic for RustChain reaching 128 GitHub stars.
"""

from PIL import Image, ImageDraw, ImageFont
import math

# Canvas size
WIDTH = 1200
HEIGHT = 630

# Colors
RUST_ORANGE = (222, 165, 132)  # Rust brand color
DARK_BG = (30, 30, 35)
STAR_GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
ACCENT = (250, 150, 80)

def create_gradient_background(width, height):
    """Create a dark gradient background."""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    for y in range(height):
        # Gradient from dark to slightly lighter
        ratio = y / height
        r = int(30 + ratio * 20)
        g = int(30 + ratio * 15)
        b = int(35 + ratio * 25)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return img

def draw_star(draw, cx, cy, size, color, rotation=0):
    """Draw a 5-pointed star."""
    points = []
    for i in range(10):
        angle = math.pi / 2 + (2 * math.pi * i / 10) + rotation
        if i % 2 == 0:
            r = size
        else:
            r = size * 0.4
        x = cx + r * math.cos(angle)
        y = cy - r * math.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=color)

def draw_glowing_star(draw, cx, cy, size, color):
    """Draw a star with glow effect."""
    # Outer glow
    for i in range(3, 0, -1):
        glow_size = size + i * 8
        glow_color = tuple(min(255, c + 30) for c in color)
        draw_star(draw, cx, cy, glow_size, glow_color, rotation=i*0.1)
    # Main star
    draw_star(draw, cx, cy, size, color)

def create_celebration_graphic():
    """Create the 128 stars celebration graphic."""
    # Create background
    img = create_gradient_background(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts, fall back to default
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large
        font_tiny = font_large
    
    # Draw decorative stars in background
    import random
    random.seed(128)  # Consistent randomness
    
    # Small background stars
    for _ in range(50):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(3, 8)
        opacity = random.randint(50, 150)
        star_color = (255, 215, 0, opacity)
        draw_star(draw, x, y, size, (200, 180, 100))
    
    # Draw main large star (center-left)
    draw_glowing_star(draw, 200, HEIGHT//2, 100, STAR_GOLD)
    
    # Draw "128" text
    text_128 = "128"
    bbox = draw.textbbox((0, 0), text_128, font=font_large)
    text_width = bbox[2] - bbox[0]
    x_pos = (WIDTH // 2) - (text_width // 2) + 50
    y_pos = 150
    
    # Text shadow
    draw.text((x_pos+4, y_pos+4), text_128, font=font_large, fill=(0, 0, 0))
    # Main text
    draw.text((x_pos, y_pos), text_128, font=font_large, fill=STAR_GOLD)
    
    # Draw "STARS" text
    text_stars = "STARS"
    bbox = draw.textbbox((0, 0), text_stars, font=font_medium)
    text_width = bbox[2] - bbox[0]
    x_pos = (WIDTH // 2) - (text_width // 2) + 50
    y_pos = 280
    
    draw.text((x_pos+3, y_pos+3), text_stars, font=font_medium, fill=(0, 0, 0))
    draw.text((x_pos, y_pos), text_stars, font=font_medium, fill=WHITE)
    
    # Draw GitHub star icon representation (right side)
    draw_glowing_star(draw, 950, 220, 60, STAR_GOLD)
    
    # Draw RustChain logo text
    text_rustchain = "⭐ RustChain"
    bbox = draw.textbbox((0, 0), text_rustchain, font=font_small)
    text_width = bbox[2] - bbox[0]
    x_pos = (WIDTH // 2) - (text_width // 2)
    y_pos = 380
    
    draw.text((x_pos+2, y_pos+2), text_rustchain, font=font_small, fill=(0, 0, 0))
    draw.text((x_pos, y_pos), text_rustchain, font=font_small, fill=RUST_ORANGE)
    
    # Draw tagline
    tagline = "Proof-of-Antiquity Blockchain"
    bbox = draw.textbbox((0, 0), tagline, font=font_tiny)
    text_width = bbox[2] - bbox[0]
    x_pos = (WIDTH // 2) - (text_width // 2)
    y_pos = 430
    
    draw.text((x_pos, y_pos), tagline, font=font_tiny, fill=LIGHT_GRAY)
    
    # Draw celebration message
    message = "Thank you for believing in vintage hardware! 🦀"
    bbox = draw.textbbox((0, 0), message, font=font_tiny)
    text_width = bbox[2] - bbox[0]
    x_pos = (WIDTH // 2) - (text_width // 2)
    y_pos = 520
    
    draw.text((x_pos, y_pos), message, font=font_tiny, fill=ACCENT)
    
    # Draw decorative border stars
    corner_stars = [
        (50, 50, 25),
        (WIDTH-50, 50, 25),
        (50, HEIGHT-50, 25),
        (WIDTH-50, HEIGHT-50, 25),
    ]
    for x, y, size in corner_stars:
        draw_star(draw, x, y, size, STAR_GOLD)
    
    # Draw milestone markers
    milestones = ["32★", "64★", "128★", "256★"]
    milestone_x = [150, 400, 650, 900]
    
    for i, (milestone, x) in enumerate(zip(milestones, milestone_x)):
        if i == 2:  # Current milestone (128)
            draw.text((x, 580), milestone, font=font_tiny, fill=STAR_GOLD)
            draw.ellipse([x-10, 575, x+50, 605], outline=STAR_GOLD, width=2)
        else:
            draw.text((x, 580), milestone, font=font_tiny, fill=(100, 100, 100))
    
    return img

def main():
    """Generate the celebration graphic."""
    print("🎉 Creating 128 Stars Celebration Graphic...")
    
    img = create_celebration_graphic()
    
    # Save as PNG
    output_file = "rustchain_128_stars.png"
    img.save(output_file, "PNG")
    print(f"✅ Saved: {output_file}")
    
    # Also create a square version for social media
    img_square = img.crop((180, 0, 1020, 630))
    img_square = img_square.resize((1080, 1080), Image.Resampling.LANCZOS)
    img_square.save("rustchain_128_stars_square.png", "PNG")
    print(f"✅ Saved: rustchain_128_stars_square.png")
    
    print("\n🎨 Graphic includes:")
    print("   • Golden star theme with glow effects")
    print("   • '128 STARS' main text")
    print("   • RustChain branding")
    print("   • Milestone markers (32★ → 64★ → 128★ → 256★)")
    print("   • Thank you message to the community")
    print("   • Dark gradient background with decorative stars")

if __name__ == "__main__":
    main()
