# BoTTube Keyboard Shortcuts Module

**Bounty #2140** | Reward: **5 RTC**  
**Issue:** Scottcjn/rustchain-bounties#2140  
**Wallet:** `RTCd5fbce79a0e0826d41a3736cfeacd5a5b921e6e5`

---

## Overview

This module adds YouTube-style keyboard shortcuts to the BoTTube video player. The implementation is pure JavaScript with no framework dependencies.

## Files

- `keyboard-shortcuts.ts` - TypeScript module with full type definitions
- `demo-keyboard-shortcuts.html` - Interactive demo showcasing all shortcuts
- `embed.ts` - Original BoTTube embed code generator
- `embed.html` - Base player template

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` / `K` | Play / Pause |
| `J` | Seek back 10 seconds |
| `L` | Seek forward 10 seconds |
| `M` | Toggle mute |
| `F` | Toggle fullscreen |
| `←` | Seek back 5 seconds |
| `→` | Seek forward 5 seconds |
| `↑` | Volume up 10% |
| `↓` | Volume down 10% |

## Features

- **YouTube-style overlay** - Brief visual indicator shows action taken
- **Input protection** - Shortcuts are disabled when typing in comment boxes or text inputs
- **Configurable** - Adjustable seek intervals and volume steps
- **TypeScript support** - Full type definitions included
- **Zero dependencies** - Pure vanilla JavaScript

## Usage

### Quick Start (HTML Demo)

Open `demo-keyboard-shortcuts.html` in a browser to see the shortcuts in action.

### Integration

```typescript
import { KeyboardShortcuts, setupKeyboardShortcuts } from './keyboard-shortcuts';

// Option 1: Factory function
const shortcuts = setupKeyboardShortcuts('#video-player', '#player-container');

// Option 2: Class-based
const video = document.querySelector('#video-player') as HTMLVideoElement;
const container = document.querySelector('#player-container') as HTMLElement;

const shortcuts = new KeyboardShortcuts({
    videoElement: video,
    containerElement: container,
    seekBackwardSeconds: 10,
    seekForwardSeconds: 10,
    volumeStep: 0.1,
    overlayDuration: 800
});

// Disable temporarily
shortcuts.setEnabled(false);

// Cleanup
shortcuts.detach();
```

### Vanilla JavaScript

```javascript
// The demo HTML includes an inline standalone version
// See demo-keyboard-shortcuts.html for the self-contained implementation
```

## Bounty Claim

```
Issue: Scottcjn/rustchain-bounties#2140
Reward: 5 RTC
Wallet: RTCd5fbce79a0e0826d41a3736cfeacd5a5b921e6e5
```

---

**BoTTube** - Decentralized video platform on RustChain
