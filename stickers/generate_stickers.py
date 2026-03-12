#!/usr/bin/env python3
"""
RustChain Sticker Pack Generator
Generates stickers in multiple sizes and formats for RustChain community
"""

from PIL import Image, ImageDraw, ImageFont
import os
import json

# Output directories
OUTPUT_DIR = "rustchain-stickers"
SIZES = {
    "small": 64,
    "medium": 128,
    "large": 256,
    "xl": 512
}

# RustChain color palette
COLORS = {
    "rust_orange": "#DEA584",
    "rust_dark": "#8B4513",
    "chain_blue": "#4169E1",
    "chain_dark": "#1E3A8A",
    "token_gold": "#FFD700",
    "success_green": "#10B981",
    "bg_transparent": (0, 0, 0, 0),
    "white": "#FFFFFF",
    "black": "#000000"
}

def create_base_image(size):
    """Create a transparent base image"""
    return Image.new('RGBA', (size, size), COLORS["bg_transparent"])

def draw_rust_logo(draw, size, offset=0):
    """Draw Rust programming language inspired logo"""
    center = size // 2
    radius = size // 2 - offset - 10
    
    # Outer circle
    draw.ellipse(
        [center - radius, center - radius, center + radius, center + radius],
        fill=COLORS["rust_orange"],
        outline=COLORS["rust_dark"],
        width=max(2, size // 32)
    )
    
    # Inner "R" shape (simplified)
    r_size = radius // 2
    draw.rectangle(
        [center - r_size, center - radius + 10, center - r_size + 20, center + radius - 10],
        fill=COLORS["white"]
    )
    draw.rectangle(
        [center - r_size, center - radius + 10, center + r_size, center - r_size + 10],
        fill=COLORS["white"]
    )
    draw.ellipse(
        [center - r_size + 10, center - r_size, center + r_size + 10, center + r_size],
        fill=COLORS["white"]
    )

def draw_chain_links(draw, size):
    """Draw blockchain chain links"""
    center = size // 2
    link_width = size // 4
    link_height = size // 3
    
    # Draw three interconnected links
    for i in range(-1, 2):
        x = center + i * link_width
        # Link outline
        draw.rounded_rectangle(
            [x - link_width//2, center - link_height//2, 
             x + link_width//2, center + link_height//2],
            radius=link_width//4,
            outline=COLORS["chain_blue"],
            width=max(3, size // 25)
        )

def draw_rocket(draw, size):
    """Draw a rocket symbol"""
    center = size // 2
    rocket_height = size // 2
    rocket_width = size // 4
    
    # Rocket body
    draw.polygon(
        [
            (center, center - rocket_height//2),
            (center - rocket_width//2, center + rocket_height//2),
            (center + rocket_width//2, center + rocket_height//2)
        ],
        fill=COLORS["success_green"]
    )
    
    # Rocket flame
    flame_height = rocket_height // 3
    draw.polygon(
        [
            (center - rocket_width//4, center + rocket_height//2),
            (center, center + rocket_height//2 + flame_height),
            (center + rocket_width//4, center + rocket_height//2)
        ],
        fill=COLORS["rust_orange"]
    )

def draw_token(draw, size):
    """Draw RTC token design"""
    center = size // 2
    radius = size // 2 - 15
    
    # Outer ring
    draw.ellipse(
        [center - radius, center - radius, center + radius, center + radius],
        fill=COLORS["token_gold"],
        outline=COLORS["rust_dark"],
        width=max(3, size // 25)
    )
    
    # Inner "RTC" text (simplified as circle for now)
    inner_radius = radius // 2
    draw.ellipse(
        [center - inner_radius, center - inner_radius, 
         center + inner_radius, center + inner_radius],
        fill=COLORS["white"],
        outline=COLORS["token_gold"],
        width=max(2, size // 32)
    )
    
    # Add "R" letter
    try:
        font_size = size // 3
        font = ImageFont.truetype("arial.ttf", font_size)
        text = "R"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = center - text_width // 2
        text_y = center - text_height // 2
        draw.text((text_x, text_y), text, fill=COLORS["rust_dark"], font=font)
    except:
        # Fallback without font
        draw.rectangle(
            [center - 10, center - 15, center + 10, center + 15],
            fill=COLORS["rust_dark"]
        )

def draw_crab(draw, size):
    """Draw Rust crab mascot (simplified)"""
    center = size // 2
    body_radius = size // 5
    
    # Body
    draw.ellipse(
        [center - body_radius, center - body_radius//2, 
         center + body_radius, center + body_radius//2],
        fill=COLORS["rust_orange"]
    )
    
    # Claws
    claw_size = body_radius // 2
    draw.ellipse(
        [center - body_radius - claw_size, center - claw_size//2,
         center - body_radius, center + claw_size//2],
        fill=COLORS["rust_orange"]
    )
    draw.ellipse(
        [center + body_radius, center - claw_size//2,
         center + body_radius + claw_size, center + claw_size//2],
        fill=COLORS["rust_orange"]
    )
    
    # Eyes
    eye_size = body_radius // 4
    draw.ellipse(
        [center - body_radius//3 - eye_size//2, center - body_radius//2 - eye_size//2,
         center - body_radius//3 + eye_size//2, center - body_radius//2 + eye_size//2],
        fill=COLORS["white"]
    )
    draw.ellipse(
        [center + body_radius//3 - eye_size//2, center - body_radius//2 - eye_size//2,
         center + body_radius//3 + eye_size//2, center - body_radius//2 + eye_size//2],
        fill=COLORS["white"]
    )

def draw_shield(draw, size):
    """Draw security shield"""
    center = size // 2
    shield_width = size // 2
    shield_height = size // 2 + 20
    
    # Shield shape
    points = [
        (center - shield_width//2, center - shield_height//3),
        (center + shield_width//2, center - shield_height//3),
        (center + shield_width//2, center + shield_height//3),
        (center, center + shield_height//2),
        (center - shield_width//2, center + shield_height//3)
    ]
    draw.polygon(points, fill=COLORS["chain_blue"], outline=COLORS["white"], width=2)
    
    # Checkmark
    check_size = shield_width // 2
    draw.line(
        [(center - check_size//3, center), 
         (center - check_size//6, center + check_size//3),
         (center + check_size//2, center - check_size//3)],
        fill=COLORS["success_green"],
        width=max(3, size // 25)
    )

def draw_network(draw, size):
    """Draw distributed network"""
    center = size // 2
    node_radius = size // 8
    network_radius = size // 3
    
    # Draw nodes in a circle
    import math
    num_nodes = 6
    for i in range(num_nodes):
        angle = (2 * math.pi * i) / num_nodes
        x = center + int(network_radius * math.cos(angle))
        y = center + int(network_radius * math.sin(angle))
        
        # Draw node
        draw.ellipse(
            [x - node_radius, y - node_radius, x + node_radius, y + node_radius],
            fill=COLORS["chain_blue"],
            outline=COLORS["white"],
            width=2
        )
        
        # Draw connections to center
        draw.line([(center, center), (x, y)], fill=COLORS["chain_blue"], width=2)
    
    # Center node
    draw.ellipse(
        [center - node_radius, center - node_radius, 
         center + node_radius, center + node_radius],
        fill=COLORS["success_green"],
        outline=COLORS["white"],
        width=2
    )

def generate_sticker(design_name, draw_func, sizes):
    """Generate a sticker design in all sizes"""
    print(f"[GENERATING] {design_name} stickers...")
    
    for size_name, size in sizes.items():
        # Create base image
        img = create_base_image(size)
        draw = ImageDraw.Draw(img)
        
        # Draw the design
        draw_func(draw, size)
        
        # Save in different formats
        base_filename = f"{design_name}_{size_name}"
        
        # PNG format
        png_path = os.path.join(OUTPUT_DIR, f"{base_filename}.png")
        img.save(png_path, 'PNG')
        print(f"  [OK] {png_path}")
        
        # WebP format
        webp_path = os.path.join(OUTPUT_DIR, f"{base_filename}.webp")
        img.save(webp_path, 'WebP')
        print(f"  [OK] {webp_path}")

def generate_svg_templates():
    """Generate SVG template files"""
    svg_templates = {
        "rust_logo": f'''<?xml version="1.0" encoding="UTF-8"?>
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="45" fill="{COLORS["rust_orange"]}" stroke="{COLORS["rust_dark"]}" stroke-width="3"/>
  <text x="50" y="60" font-size="40" text-anchor="middle" fill="white" font-family="Arial">R</text>
</svg>''',
        
        "chain_links": f'''<?xml version="1.0" encoding="UTF-8"?>
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <rect x="15" y="40" width="25" height="20" rx="5" fill="none" stroke="{COLORS["chain_blue"]}" stroke-width="3"/>
  <rect x="37" y="40" width="25" height="20" rx="5" fill="none" stroke="{COLORS["chain_blue"]}" stroke-width="3"/>
  <rect x="60" y="40" width="25" height="20" rx="5" fill="none" stroke="{COLORS["chain_blue"]}" stroke-width="3"/>
</svg>''',
        
        "rocket": f'''<?xml version="1.0" encoding="UTF-8"?>
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <polygon points="50,20 35,60 65,60" fill="{COLORS["success_green"]}"/>
  <polygon points="40,60 50,80 60,60" fill="{COLORS["rust_orange"]}"/>
</svg>''',
        
        "token": f'''<?xml version="1.0" encoding="UTF-8"?>
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="45" fill="{COLORS["token_gold"]}" stroke="{COLORS["rust_dark"]}" stroke-width="3"/>
  <circle cx="50" cy="50" r="25" fill="white" stroke="{COLORS["token_gold"]}" stroke-width="2"/>
  <text x="50" y="58" font-size="24" text-anchor="middle" fill="{COLORS["rust_dark"]}" font-family="Arial">R</text>
</svg>'''
    }
    
    for name, svg_content in svg_templates.items():
        svg_path = os.path.join(OUTPUT_DIR, f"{name}.svg")
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f"  [OK] {svg_path}")

def create_manifest():
    """Create a JSON manifest file for the sticker pack"""
    manifest = {
        "name": "RustChain Sticker Pack",
        "version": "1.0.0",
        "description": "Official RustChain community sticker pack",
        "author": "AI Agent (牛) for RustChain Bounty #1611",
        "license": "MIT",
        "formats": ["PNG", "WebP", "SVG"],
        "sizes": {
            "small": "64x64px",
            "medium": "128x128px",
            "large": "256x256px",
            "xl": "512x512px"
        },
        "stickers": [
            {"name": "rust_logo", "description": "RustChain official logo"},
            {"name": "chain_links", "description": "Blockchain chain links"},
            {"name": "rocket", "description": "Rocket symbol for speed"},
            {"name": "token", "description": "RTC token design"},
            {"name": "crab", "description": "Rust crab mascot"},
            {"name": "shield", "description": "Security shield"},
            {"name": "network", "description": "Distributed network"}
        ],
        "usage": "Free for RustChain community use"
    }
    
    manifest_path = os.path.join(OUTPUT_DIR, "manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    print(f"  [OK] {manifest_path}")

def main():
    """Main function to generate all stickers"""
    print("[RustChain Sticker Pack Generator]")
    print("=" * 50)
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Define all designs
    designs = [
        ("rust_logo", draw_rust_logo),
        ("chain_links", draw_chain_links),
        ("rocket", draw_rocket),
        ("token", draw_token),
        ("crab", draw_crab),
        ("shield", draw_shield),
        ("network", draw_network)
    ]
    
    # Generate all stickers
    for design_name, draw_func in designs:
        generate_sticker(design_name, draw_func, SIZES)
    
    # Generate SVG templates
    print("\n[STEP] Generating SVG templates...")
    generate_svg_templates()
    
    # Create manifest
    print("\n[STEP] Creating manifest...")
    create_manifest()
    
    print("\n[SUCCESS] Sticker pack generation complete!")
    print(f"[OUTPUT] Directory: {OUTPUT_DIR}/")
    print(f"[TOTAL] Files: {len(designs) * len(SIZES) * 2 + len(designs) + 2}")

if __name__ == "__main__":
    main()
