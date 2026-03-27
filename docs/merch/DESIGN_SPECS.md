# RustChain Merch — Design Specifications

Print-ready specifications for all RustChain merchandise designs.

---

## Color Palette

| Name            | Hex       | Pantone (nearest) | Usage                        |
|-----------------|-----------|--------------------|------------------------------|
| Rust Orange     | `#FF6B35` | Pantone 1655 C     | Primary brand, crab, accents |
| Deep Orange     | `#E55A2B` | Pantone 1665 C     | Shadows, outlines            |
| Chain Gold      | `#FFD700` | Pantone 116 C      | Chain links, highlights      |
| Amber Gold      | `#FFA500` | Pantone 144 C      | Gold gradient endpoint       |
| Dark Navy       | `#1A1A2E` | Pantone 5395 C     | Backgrounds                  |
| Deep Black      | `#0F0F1A` | Pantone Black 6 C  | Background gradient end      |
| Terminal Green  | `#33FF33` | Pantone 802 C      | CRT text, code accents       |
| Light Grey      | `#C0C0C0` | Pantone Cool Gray 5| Body text, taglines          |

## Typography

| Element         | Font                          | Weight | Size (at print) | Tracking     |
|-----------------|-------------------------------|--------|-----------------|--------------|
| Wordmark        | Courier New / Fira Code       | Bold   | Varies by item  | +18px        |
| Tagline         | Courier New / Fira Code       | Regular| Varies by item  | +14px        |
| Body / Code     | Courier New                   | Regular| Varies by item  | +2px         |
| Labels          | Courier New                   | Regular| 8-10pt          | +4-8px       |

Monospace fonts are used exclusively to reinforce the developer/terminal aesthetic.

**Font Licensing:** Courier New ships with all major OS distributions. Fira Code is open-source (OFL). Both are safe for commercial use.

---

## T-Shirt Design

**File:** `t-shirt-design.svg`

### Dimensions
- **Print Area:** 12" x 16" (3048 x 4064 px at 254 DPI)
- **SVG Canvas:** 2400 x 3200 px (scale to print size)
- **Resolution:** 300 DPI minimum for final raster export
- **Bleed:** None required (design sits within print area)

### Print Method
- **Recommended:** Direct-to-Garment (DTG) for full-color gradient support
- **Alternative:** Screen print (requires color separation — 4 screens: orange, gold, white, grey)

### Garment Specs
- **Base Color:** Black or Charcoal Heather (Gildan 5000 or Bella+Canvas 3001)
- **Placement:** Center chest, 2" below collar
- **Sizes:** S through 3XL (scale proportionally, maintain 1" minimum margin)

### Design Elements
1. Stylized Ferris crab with blockchain chain overlay
2. "RUSTCHAIN" wordmark (RUST in orange, CHAIN in gold)
3. Decorative chain-link band
4. "PROOF OF ANTIQUITY" tagline
5. Hex hash decoration (subtle)
6. Circuit-board background pattern (very subtle, 6% opacity)

---

## Poster Design

**File:** `poster-design.svg`

### Dimensions
- **Print Size:** 18" x 27" (457 x 686 mm)
- **SVG Canvas:** 3600 x 5400 px
- **Resolution:** 300 DPI minimum (final raster: 5400 x 8100 px)
- **Bleed:** 0.125" (3mm) all sides
- **Safe Zone:** 0.25" (6mm) inside trim edge

### Print Method
- **Recommended:** Offset lithography or high-quality digital (Giclée)
- **Paper Stock:** 100lb gloss text or 80lb matte cover
- **Finish:** Satin or matte lamination

### Design Elements
1. Vintage CRT monitor with green phosphor terminal output
2. RustChain CLI session showing mining, verification, wallet commands
3. Animated cursor blink (SVG animation — static in print)
4. Ferris crab watermark (30% opacity, decorative)
5. Three feature cards: Zero-Copy Transactions, Borrow Checked Blocks, Lifetime Guarantees
6. Vintage border frame with corner ornaments
7. "THE CHAIN THAT NEVER SEGFAULTS" secondary tagline
8. Scanline overlay effect for CRT authenticity

### Color Notes
- Background is near-black (#0A0A14 to #141428 gradient)
- CRT text uses Terminal Green (#33FF33) with glow filter
- Gold verification message stands out from green terminal text

---

## Sticker Designs

**File:** `sticker-designs.svg`

### Sheet Layout
- **Sheet Size:** 10" x 10" (2400 x 2400 px SVG)
- **Individual Stickers:** 3" x 3" each (die-cut shapes vary)
- **Resolution:** 300 DPI minimum

### Sticker 1 — Logo Badge
- **Shape:** Circle (3" diameter)
- **Content:** Ferris crab + RUSTCHAIN wordmark + chain links + "EST. 2024"
- **Background:** Dark navy gradient
- **Border:** Rust Orange, 6px

### Sticker 2 — Proof of Antiquity Seal
- **Shape:** Rounded square (3" x 3", 60px radius)
- **Content:** Vintage seal/cog design, genesis block "#0" icon, "PROOF OF ANTIQUITY", "VERIFIED ON-CHAIN"
- **Background:** Dark navy gradient
- **Border:** Chain Gold, 5px

### Sticker 3 — I Mine RTC
- **Shape:** Hexagon (3" point-to-point)
- **Content:** Pickaxe icon with gold sparkles, "I MINE RTC", block chain icons, "HASH POWER"
- **Background:** Dark navy gradient
- **Border:** Rust Orange, 5px

### Sticker 4 — Code Terminal
- **Shape:** Rounded square (3" x 3", 80px radius)
- **Content:** Terminal window with syntax-highlighted Rust code (`mine_block` function), Ferris watermark, "MEMORY SAFE. THREAD SAFE. CHAIN SAFE."
- **Background:** Near-black (#0A0A14)
- **Border:** Terminal Green, 4px
- **Syntax Colors:** VS Code Dark+ theme palette

### Print Method
- **Material:** Vinyl (waterproof, UV-resistant)
- **Finish:** Gloss or matte laminated
- **Adhesive:** Permanent or removable (vendor choice)
- **Die-cut:** Kiss-cut on backing sheet or individual die-cut

---

## File Export Guide

| Format | Use Case               | Settings                              |
|--------|------------------------|---------------------------------------|
| SVG    | Source / vector edit    | As provided                           |
| PDF    | Print vendor submission| CMYK, 300 DPI, fonts outlined         |
| PNG    | Web preview / mockups  | sRGB, 300 DPI, transparent background |
| AI/EPS | Print vendor (alt)     | Convert from SVG, embed fonts         |

### CMYK Conversion Notes
| Screen (RGB)     | Print (CMYK approx.)    |
|------------------|--------------------------|
| #FF6B35 (Orange) | C:0 M:70 Y:85 K:0       |
| #FFD700 (Gold)   | C:0 M:15 Y:95 K:0       |
| #1A1A2E (Navy)   | C:80 M:75 Y:45 K:70     |
| #33FF33 (Green)  | C:65 M:0 Y:90 K:0       |

---

## Production Checklist

- [ ] Convert all text to outlines/paths before sending to printer
- [ ] Verify CMYK color accuracy with test proof
- [ ] Ensure minimum 300 DPI at final print size
- [ ] Add crop marks and bleed for poster
- [ ] Confirm garment color matches design contrast requirements
- [ ] Request physical proof before full production run
