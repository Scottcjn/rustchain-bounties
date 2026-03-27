# RustChain Sticker Pack

A set of 8 die-cut vinyl stickers celebrating RustChain's vintage mining ethos, Proof-of-Authority consensus, and the crab-powered community.

---

## Print Specifications

| Property | Value |
|---|---|
| Dimensions | 3" x 3" (76.2 mm x 76.2 mm) per sticker |
| Bleed | 0.125" (3.175 mm) on all sides |
| Safe area | 0.125" inset from trim line |
| Die-cut | Contour cut, 0.0625" offset from artwork edge |
| Material | Matte vinyl, waterproof, UV-resistant |
| Adhesive | Permanent, repositionable for first 24 hours |
| Color | CMYK process; Pantone 7621 C (rust red), Pantone 432 C (dark slate) as brand anchors |
| Resolution | Vector (SVG source), 300 DPI minimum for raster export |
| Finish | Matte laminate |

---

## Sticker 1 — RustChain Logo

The official RustChain emblem: interlocking chain links rendered in oxidized rust tones against a dark background, with "RUSTCHAIN" set in a monospaced typeface beneath.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300">
  <defs>
    <linearGradient id="rust1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#8B3A1A"/>
      <stop offset="50%" stop-color="#C1440E"/>
      <stop offset="100%" stop-color="#A0522D"/>
    </linearGradient>
    <linearGradient id="steel1" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#4A4A4A"/>
      <stop offset="100%" stop-color="#2C2C2C"/>
    </linearGradient>
  </defs>
  <!-- Background -->
  <rect width="300" height="300" rx="20" fill="#1A1A2E"/>
  <!-- Chain link left -->
  <rect x="60" y="90" width="80" height="50" rx="25" fill="none" stroke="url(#rust1)" stroke-width="10"/>
  <!-- Chain link right (overlapping) -->
  <rect x="120" y="110" width="80" height="50" rx="25" fill="none" stroke="url(#rust1)" stroke-width="10"/>
  <!-- Chain link third -->
  <rect x="180" y="90" width="80" height="50" rx="25" fill="none" stroke="url(#rust1)" stroke-width="10"/>
  <!-- Oxidation speckles -->
  <circle cx="80" cy="105" r="2" fill="#D2691E" opacity="0.6"/>
  <circle cx="150" cy="130" r="3" fill="#CD853F" opacity="0.5"/>
  <circle cx="220" cy="100" r="2" fill="#D2691E" opacity="0.7"/>
  <circle cx="100" cy="125" r="1.5" fill="#8B4513" opacity="0.4"/>
  <!-- Wordmark -->
  <text x="150" y="210" font-family="'Courier New', monospace" font-size="32" font-weight="bold" fill="#C1440E" text-anchor="middle" letter-spacing="4">RUSTCHAIN</text>
  <!-- Tagline -->
  <text x="150" y="240" font-family="'Courier New', monospace" font-size="12" fill="#888888" text-anchor="middle">MINE THE FUTURE</text>
</svg>
```

---

## Sticker 2 — Mine Vintage

A retro-style badge with distressed texture, reading "MINE VINTAGE" in an arc over a crossed pickaxe and wrench, evoking gold-rush-era mining claim aesthetics adapted for blockchain.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300">
  <defs>
    <linearGradient id="parchment" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F5DEB3"/>
      <stop offset="100%" stop-color="#DEB887"/>
    </linearGradient>
    <filter id="rough">
      <feTurbulence baseFrequency="0.04" numOctaves="4" type="fractalNoise"/>
      <feDisplacementMap in="SourceGraphic" scale="3"/>
    </filter>
  </defs>
  <!-- Circular badge background -->
  <circle cx="150" cy="150" r="140" fill="url(#parchment)" stroke="#5C3317" stroke-width="6"/>
  <circle cx="150" cy="150" r="125" fill="none" stroke="#5C3317" stroke-width="2" stroke-dasharray="4,4"/>
  <!-- Arc text: MINE VINTAGE -->
  <path id="topArc" d="M 50,150 A 100,100 0 0,1 250,150" fill="none"/>
  <text font-family="'Georgia', serif" font-size="28" font-weight="bold" fill="#5C3317" letter-spacing="3">
    <textPath href="#topArc" startOffset="50%" text-anchor="middle">MINE VINTAGE</textPath>
  </text>
  <!-- Crossed pickaxe and wrench -->
  <!-- Pickaxe handle -->
  <line x1="110" y1="200" x2="190" y2="120" stroke="#5C3317" stroke-width="5" stroke-linecap="round"/>
  <!-- Pickaxe head -->
  <path d="M 185,120 L 200,105 Q 210,110 205,125 L 190,125 Z" fill="#8B4513"/>
  <!-- Wrench handle -->
  <line x1="190" y1="200" x2="110" y2="120" stroke="#5C3317" stroke-width="5" stroke-linecap="round"/>
  <!-- Wrench head -->
  <path d="M 105,125 L 95,110 L 100,100 L 115,105 L 115,120 Z" fill="#8B4513"/>
  <!-- Bottom arc text -->
  <path id="botArc" d="M 60,180 A 100,100 0 0,0 240,180" fill="none"/>
  <text font-family="'Georgia', serif" font-size="14" fill="#8B4513" letter-spacing="2">
    <textPath href="#botArc" startOffset="50%" text-anchor="middle">EST. BLOCK ZERO</textPath>
  </text>
  <!-- Star accents -->
  <polygon points="150,85 153,92 161,92 155,97 157,105 150,100 143,105 145,97 139,92 147,92" fill="#5C3317"/>
</svg>
```

---

## Sticker 3 — Crab with Pickaxe

The Rust mascot crab (Ferris) wearing a hard hat and swinging a pickaxe into a block, representing mining on the RustChain network. Friendly, cartoon style.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300">
  <defs>
    <linearGradient id="crabBody" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#E8530E"/>
      <stop offset="100%" stop-color="#C1440E"/>
    </linearGradient>
  </defs>
  <!-- Background -->
  <rect width="300" height="300" rx="20" fill="#FFF8F0"/>
  <!-- Crab body -->
  <ellipse cx="150" cy="175" rx="70" ry="50" fill="url(#crabBody)"/>
  <!-- Crab belly -->
  <ellipse cx="150" cy="185" rx="45" ry="30" fill="#F4845F" opacity="0.6"/>
  <!-- Eyes -->
  <circle cx="130" cy="145" r="12" fill="white"/>
  <circle cx="170" cy="145" r="12" fill="white"/>
  <circle cx="132" cy="143" r="6" fill="#1A1A2E"/>
  <circle cx="172" cy="143" r="6" fill="#1A1A2E"/>
  <circle cx="134" cy="141" r="2" fill="white"/>
  <circle cx="174" cy="141" r="2" fill="white"/>
  <!-- Eye stalks -->
  <line x1="130" y1="155" x2="130" y2="165" stroke="#C1440E" stroke-width="4" stroke-linecap="round"/>
  <line x1="170" y1="155" x2="170" y2="165" stroke="#C1440E" stroke-width="4" stroke-linecap="round"/>
  <!-- Smile -->
  <path d="M 135,195 Q 150,210 165,195" fill="none" stroke="#8B3A1A" stroke-width="3" stroke-linecap="round"/>
  <!-- Hard hat -->
  <ellipse cx="150" cy="138" rx="50" ry="18" fill="#FFD700"/>
  <rect x="105" y="125" width="90" height="15" rx="5" fill="#FFD700"/>
  <rect x="130" y="120" width="40" height="10" rx="3" fill="#FFA500"/>
  <!-- Left claw holding pickaxe -->
  <ellipse cx="75" cy="180" rx="18" ry="12" fill="#E8530E" transform="rotate(-20, 75, 180)"/>
  <ellipse cx="65" cy="175" rx="10" ry="8" fill="#E8530E" transform="rotate(-20, 65, 175)"/>
  <!-- Pickaxe -->
  <line x1="55" y1="165" x2="30" y2="100" stroke="#8B6914" stroke-width="5" stroke-linecap="round"/>
  <path d="M 22,100 L 15,80 Q 25,75 38,85 L 38,100 Z" fill="#708090"/>
  <path d="M 15,80 L 10,75 Q 8,78 12,82 Z" fill="#A9A9A9"/>
  <!-- Right claw -->
  <ellipse cx="225" cy="180" rx="18" ry="12" fill="#E8530E" transform="rotate(20, 225, 180)"/>
  <ellipse cx="235" cy="175" rx="10" ry="8" fill="#E8530E" transform="rotate(20, 235, 175)"/>
  <!-- Legs -->
  <line x1="95" y1="200" x2="70" y2="235" stroke="#C1440E" stroke-width="4" stroke-linecap="round"/>
  <line x1="85" y1="210" x2="60" y2="245" stroke="#C1440E" stroke-width="4" stroke-linecap="round"/>
  <line x1="205" y1="200" x2="230" y2="235" stroke="#C1440E" stroke-width="4" stroke-linecap="round"/>
  <line x1="215" y1="210" x2="240" y2="245" stroke="#C1440E" stroke-width="4" stroke-linecap="round"/>
  <!-- Block being mined -->
  <rect x="230" y="220" width="45" height="45" rx="4" fill="#2C2C2C" stroke="#C1440E" stroke-width="2"/>
  <text x="252" y="248" font-family="monospace" font-size="8" fill="#C1440E" text-anchor="middle">BLK</text>
  <text x="252" y="258" font-family="monospace" font-size="7" fill="#888" text-anchor="middle">#4091</text>
  <!-- Impact sparks -->
  <circle cx="38" cy="92" r="2" fill="#FFD700"/>
  <circle cx="28" cy="88" r="1.5" fill="#FFA500"/>
  <circle cx="42" cy="85" r="1" fill="#FFD700"/>
</svg>
```

---

## Sticker 4 — PoA Badge

A shield-shaped authority badge for Proof-of-Authority validators. Gold border, dark interior, with "PoA VALIDATOR" and a checkmark seal.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300">
  <defs>
    <linearGradient id="goldEdge" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFD700"/>
      <stop offset="40%" stop-color="#DAA520"/>
      <stop offset="100%" stop-color="#B8860B"/>
    </linearGradient>
    <linearGradient id="darkCore" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1A1A2E"/>
      <stop offset="100%" stop-color="#16213E"/>
    </linearGradient>
  </defs>
  <!-- Shield shape outer -->
  <path d="M 150,30 L 260,70 L 260,160 Q 260,240 150,280 Q 40,240 40,160 L 40,70 Z" fill="url(#goldEdge)"/>
  <!-- Shield shape inner -->
  <path d="M 150,45 L 248,80 L 248,158 Q 248,232 150,268 Q 52,232 52,158 L 52,80 Z" fill="url(#darkCore)"/>
  <!-- Inner border decoration -->
  <path d="M 150,55 L 238,87 L 238,155 Q 238,224 150,258 Q 62,224 62,155 L 62,87 Z" fill="none" stroke="#DAA520" stroke-width="1" stroke-dasharray="6,3"/>
  <!-- Checkmark seal circle -->
  <circle cx="150" cy="130" r="40" fill="none" stroke="#DAA520" stroke-width="3"/>
  <circle cx="150" cy="130" r="34" fill="#DAA520" opacity="0.15"/>
  <!-- Checkmark -->
  <path d="M 128,130 L 143,148 L 175,112" fill="none" stroke="#FFD700" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- Text: PoA -->
  <text x="150" y="100" font-family="'Courier New', monospace" font-size="16" font-weight="bold" fill="#DAA520" text-anchor="middle" letter-spacing="6">PoA</text>
  <!-- Text: VALIDATOR -->
  <text x="150" y="200" font-family="'Courier New', monospace" font-size="18" font-weight="bold" fill="#FFD700" text-anchor="middle" letter-spacing="3">VALIDATOR</text>
  <!-- Text: AUTHORIZED -->
  <text x="150" y="225" font-family="'Courier New', monospace" font-size="11" fill="#888888" text-anchor="middle" letter-spacing="4">AUTHORIZED</text>
  <!-- Star accents -->
  <polygon points="150,58 152,63 157,63 153,66 154,71 150,68 146,71 147,66 143,63 148,63" fill="#FFD700"/>
</svg>
```

---

## Sticker 5 — "1 CPU = 1 Vote"

A bold typographic sticker channeling the original Satoshi ethos, adapted for RustChain's low-power mining philosophy. Blocky retro-terminal aesthetic with a blinking cursor.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300">
  <defs>
    <linearGradient id="screenGlow" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#0A1628"/>
      <stop offset="100%" stop-color="#0D1B2A"/>
    </linearGradient>
  </defs>
  <!-- Monitor bezel -->
  <rect x="15" y="15" width="270" height="240" rx="12" fill="#3C3C3C"/>
  <rect x="18" y="18" width="264" height="234" rx="10" fill="#2A2A2A"/>
  <!-- Screen -->
  <rect x="30" y="30" width="240" height="210" rx="4" fill="url(#screenGlow)"/>
  <!-- Scanline effect -->
  <line x1="30" y1="60" x2="270" y2="60" stroke="#0F3460" stroke-width="0.5" opacity="0.3"/>
  <line x1="30" y1="90" x2="270" y2="90" stroke="#0F3460" stroke-width="0.5" opacity="0.3"/>
  <line x1="30" y1="120" x2="270" y2="120" stroke="#0F3460" stroke-width="0.5" opacity="0.3"/>
  <line x1="30" y1="150" x2="270" y2="150" stroke="#0F3460" stroke-width="0.5" opacity="0.3"/>
  <line x1="30" y1="180" x2="270" y2="180" stroke="#0F3460" stroke-width="0.5" opacity="0.3"/>
  <line x1="30" y1="210" x2="270" y2="210" stroke="#0F3460" stroke-width="0.5" opacity="0.3"/>
  <!-- Terminal prompt -->
  <text x="45" y="70" font-family="'Courier New', monospace" font-size="12" fill="#00FF41" opacity="0.7">rustchain@node:~$</text>
  <!-- Main text -->
  <text x="150" y="120" font-family="'Courier New', monospace" font-size="36" font-weight="bold" fill="#00FF41" text-anchor="middle">1 CPU</text>
  <text x="150" y="158" font-family="'Courier New', monospace" font-size="28" fill="#00FF41" text-anchor="middle" opacity="0.85">=</text>
  <text x="150" y="200" font-family="'Courier New', monospace" font-size="36" font-weight="bold" fill="#00FF41" text-anchor="middle">1 VOTE</text>
  <!-- Blinking cursor -->
  <rect x="210" y="190" width="12" height="3" fill="#00FF41" opacity="0.9">
    <animate attributeName="opacity" values="0.9;0;0.9" dur="1.2s" repeatCount="indefinite"/>
  </rect>
  <!-- Monitor stand -->
  <rect x="120" y="255" width="60" height="10" rx="2" fill="#3C3C3C"/>
  <rect x="100" y="265" width="100" height="8" rx="4" fill="#2A2A2A"/>
  <!-- Power LED -->
  <circle cx="150" cy="248" r="3" fill="#00FF41" opacity="0.8"/>
</svg>
```

---

## Sticker 6 — Retro Mac Mining Rig

A classic beige Macintosh-style computer with the RustChain logo on its screen, a spinning fan on the side, and hash-rate stats on screen. Celebrates the ethos that old hardware can mine.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300">
  <defs>
    <linearGradient id="beige" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#F5F0E1"/>
      <stop offset="100%" stop-color="#D4C9A8"/>
    </linearGradient>
  </defs>
  <!-- Mac body -->
  <rect x="60" y="30" width="180" height="210" rx="10" fill="url(#beige)" stroke="#B0A080" stroke-width="2"/>
  <!-- Screen recess -->
  <rect x="80" y="50" width="140" height="110" rx="6" fill="#2C2C2C" stroke="#8B8060" stroke-width="2"/>
  <!-- Screen content -->
  <rect x="85" y="55" width="130" height="100" rx="3" fill="#0A1628"/>
  <!-- RustChain on screen -->
  <rect x="110" y="70" width="30" height="15" rx="7" fill="none" stroke="#C1440E" stroke-width="3"/>
  <rect x="135" y="78" width="30" height="15" rx="7" fill="none" stroke="#C1440E" stroke-width="3"/>
  <rect x="160" y="70" width="30" height="15" rx="7" fill="none" stroke="#C1440E" stroke-width="3"/>
  <!-- Hash rate display -->
  <text x="150" y="115" font-family="monospace" font-size="9" fill="#00FF41" text-anchor="middle">MINING BLOCK #2068</text>
  <text x="150" y="130" font-family="monospace" font-size="8" fill="#00FF41" text-anchor="middle" opacity="0.7">HASHRATE: 42 H/s</text>
  <text x="150" y="142" font-family="monospace" font-size="8" fill="#00FF41" text-anchor="middle" opacity="0.7">UPTIME: 1337 hrs</text>
  <!-- Floppy drive slot -->
  <rect x="115" y="175" width="70" height="6" rx="2" fill="#B0A080"/>
  <!-- Apple-style logo area -->
  <text x="150" y="200" font-family="'Georgia', serif" font-size="11" fill="#8B8060" text-anchor="middle">RustChain</text>
  <!-- Ventilation lines on side -->
  <line x1="245" y1="60" x2="245" y2="70" stroke="#B0A080" stroke-width="1"/>
  <line x1="245" y1="75" x2="245" y2="85" stroke="#B0A080" stroke-width="1"/>
  <line x1="245" y1="90" x2="245" y2="100" stroke="#B0A080" stroke-width="1"/>
  <line x1="245" y1="105" x2="245" y2="115" stroke="#B0A080" stroke-width="1"/>
  <!-- Base -->
  <rect x="50" y="240" width="200" height="15" rx="4" fill="#D4C9A8" stroke="#B0A080" stroke-width="1"/>
  <!-- Keyboard hint -->
  <rect x="70" y="265" width="160" height="20" rx="3" fill="#E8E0CC" stroke="#B0A080" stroke-width="1"/>
  <line x1="90" y1="272" x2="210" y2="272" stroke="#C8C0A8" stroke-width="1"/>
  <line x1="90" y1="278" x2="210" y2="278" stroke="#C8C0A8" stroke-width="1"/>
</svg>
```

---

## Sticker 7 — "My G4 Earns More Than Your Threadripper"

A trash-talk sticker with a bold typographic layout: a small Power Mac G4 graphic at the top, the slogan in stacked bold text, and a defeated modern GPU at the bottom. Tongue-in-cheek community humor.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300">
  <defs>
    <linearGradient id="g4body" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#E8E8E8"/>
      <stop offset="100%" stop-color="#C0C0C0"/>
    </linearGradient>
  </defs>
  <!-- Background -->
  <rect width="300" height="300" rx="16" fill="#1A1A2E"/>
  <!-- Border -->
  <rect x="6" y="6" width="288" height="288" rx="13" fill="none" stroke="#C1440E" stroke-width="2"/>
  <!-- Mini G4 tower -->
  <rect x="120" y="20" width="60" height="55" rx="5" fill="url(#g4body)" stroke="#999" stroke-width="1"/>
  <!-- G4 handles -->
  <rect x="125" y="25" width="8" height="3" rx="1" fill="#999"/>
  <rect x="167" y="25" width="8" height="3" rx="1" fill="#999"/>
  <!-- G4 apple logo area -->
  <circle cx="150" cy="45" r="8" fill="none" stroke="#888" stroke-width="1"/>
  <text x="150" y="49" font-family="monospace" font-size="9" fill="#888" text-anchor="middle">G4</text>
  <!-- G4 drive slot -->
  <rect x="130" y="58" width="40" height="4" rx="1" fill="#AAA"/>
  <!-- Crown on G4 -->
  <polygon points="135,18 138,10 142,16 146,6 150,16 154,6 158,16 162,10 165,18" fill="#FFD700"/>
  <!-- Main text -->
  <text x="150" y="108" font-family="'Courier New', monospace" font-size="16" font-weight="bold" fill="#FFFFFF" text-anchor="middle">MY G4</text>
  <text x="150" y="134" font-family="'Courier New', monospace" font-size="14" fill="#C1440E" text-anchor="middle">EARNS MORE</text>
  <text x="150" y="158" font-family="'Courier New', monospace" font-size="14" fill="#C1440E" text-anchor="middle">THAN YOUR</text>
  <text x="150" y="188" font-family="'Courier New', monospace" font-size="20" font-weight="bold" fill="#FFFFFF" text-anchor="middle">THREADRIPPER</text>
  <!-- Sad modern GPU at bottom -->
  <rect x="105" y="210" width="90" height="40" rx="4" fill="#2C2C2C" stroke="#444" stroke-width="1"/>
  <!-- GPU fans -->
  <circle cx="130" cy="230" r="12" fill="#333" stroke="#555" stroke-width="1"/>
  <circle cx="170" cy="230" r="12" fill="#333" stroke="#555" stroke-width="1"/>
  <!-- GPU fan blades -->
  <line x1="130" y1="220" x2="130" y2="240" stroke="#666" stroke-width="1"/>
  <line x1="120" y1="230" x2="140" y2="230" stroke="#666" stroke-width="1"/>
  <line x1="170" y1="220" x2="170" y2="240" stroke="#666" stroke-width="1"/>
  <line x1="160" y1="230" x2="180" y2="230" stroke="#666" stroke-width="1"/>
  <!-- Sad face on GPU -->
  <circle cx="145" cy="225" r="1.5" fill="#888"/>
  <circle cx="155" cy="225" r="1.5" fill="#888"/>
  <path d="M 143,234 Q 150,230 157,234" fill="none" stroke="#888" stroke-width="1"/>
  <!-- Sweat drop -->
  <path d="M 198,215 Q 200,210 202,215 Q 200,220 198,215" fill="#4488CC"/>
  <!-- RTC tag -->
  <text x="150" y="275" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">powered by RustChain</text>
</svg>
```

---

## Sticker 8 — Blockchain Blocks

A cascade of connected blocks tumbling down the sticker, each stamped with a block number and hash snippet. The chain links are rendered in RustChain's signature oxidized palette.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300">
  <defs>
    <linearGradient id="blk1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2C2C2C"/>
      <stop offset="100%" stop-color="#1A1A2E"/>
    </linearGradient>
    <linearGradient id="chainLink" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#C1440E"/>
      <stop offset="100%" stop-color="#8B3A1A"/>
    </linearGradient>
  </defs>
  <!-- Background -->
  <rect width="300" height="300" rx="16" fill="#0D1B2A"/>
  <!-- Block 1 -->
  <rect x="40" y="15" width="120" height="60" rx="6" fill="url(#blk1)" stroke="#C1440E" stroke-width="2"/>
  <text x="55" y="38" font-family="monospace" font-size="10" fill="#C1440E">BLK #4089</text>
  <text x="55" y="52" font-family="monospace" font-size="7" fill="#666">0xa3f2...c71b</text>
  <text x="55" y="64" font-family="monospace" font-size="7" fill="#444">nonce: 18274</text>
  <!-- Chain link 1-2 -->
  <line x1="100" y1="75" x2="130" y2="95" stroke="url(#chainLink)" stroke-width="4" stroke-linecap="round"/>
  <circle cx="115" cy="85" r="5" fill="none" stroke="#C1440E" stroke-width="2"/>
  <!-- Block 2 -->
  <rect x="90" y="95" width="120" height="60" rx="6" fill="url(#blk1)" stroke="#C1440E" stroke-width="2"/>
  <text x="105" y="118" font-family="monospace" font-size="10" fill="#C1440E">BLK #4090</text>
  <text x="105" y="132" font-family="monospace" font-size="7" fill="#666">0x7e91...a42d</text>
  <text x="105" y="144" font-family="monospace" font-size="7" fill="#444">nonce: 30561</text>
  <!-- Chain link 2-3 -->
  <line x1="150" y1="155" x2="170" y2="175" stroke="url(#chainLink)" stroke-width="4" stroke-linecap="round"/>
  <circle cx="160" cy="165" r="5" fill="none" stroke="#C1440E" stroke-width="2"/>
  <!-- Block 3 -->
  <rect x="130" y="175" width="120" height="60" rx="6" fill="url(#blk1)" stroke="#C1440E" stroke-width="2"/>
  <text x="145" y="198" font-family="monospace" font-size="10" fill="#C1440E">BLK #4091</text>
  <text x="145" y="212" font-family="monospace" font-size="7" fill="#666">0xb5d8...f903</text>
  <text x="145" y="224" font-family="monospace" font-size="7" fill="#444">nonce: 7738</text>
  <!-- Chain link 3-4 -->
  <line x1="190" y1="235" x2="195" y2="250" stroke="url(#chainLink)" stroke-width="4" stroke-linecap="round"/>
  <circle cx="192" cy="242" r="5" fill="none" stroke="#C1440E" stroke-width="2"/>
  <!-- Block 4 (partial, going off edge) -->
  <rect x="155" y="250" width="120" height="60" rx="6" fill="url(#blk1)" stroke="#C1440E" stroke-width="2"/>
  <text x="170" y="273" font-family="monospace" font-size="10" fill="#C1440E">BLK #4092</text>
  <text x="170" y="287" font-family="monospace" font-size="7" fill="#666">0x2f44...e8a1</text>
  <text x="170" y="299" font-family="monospace" font-size="7" fill="#444">nonce: 51023</text>
  <!-- Floating hash particles -->
  <text x="230" y="40" font-family="monospace" font-size="6" fill="#C1440E" opacity="0.3">0x</text>
  <text x="20" y="140" font-family="monospace" font-size="6" fill="#C1440E" opacity="0.2">ff</text>
  <text x="260" y="160" font-family="monospace" font-size="6" fill="#C1440E" opacity="0.25">a3</text>
  <text x="30" y="250" font-family="monospace" font-size="6" fill="#C1440E" opacity="0.2">7e</text>
  <text x="270" y="280" font-family="monospace" font-size="6" fill="#C1440E" opacity="0.15">c1</text>
</svg>
```

---

## Usage Notes

- All SVGs are 300x300 viewBox for consistency; scale uniformly for print.
- For die-cut production, export each SVG and add a 0.0625" contour offset path as the cut line.
- Add 0.125" bleed by extending background fills beyond the trim boundary.
- Recommended print vendor: StickerMule, StickerGiant, or Sticker It for matte vinyl die-cuts.
- Files are vector and resolution-independent; no raster assets required.
