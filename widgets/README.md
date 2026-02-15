# RustChain Dashboard Widget

A beautiful, embeddable dashboard widget showing live RustChain network stats.

![Dashboard Preview](preview.png)

## Features

✅ **Required Features:**
- Single HTML/JS widget (vanilla JS, no dependencies)
- Fetches live data from RustChain API
- Displays:
  - Current epoch number
  - Active miner count
  - Network health status
  - Total RTC distributed
- Dark theme
- Mobile responsive

✅ **Bonus Features (+10 RTC):**
- Animated miner activity visualization
- Click-through to block explorer
- Auto-refresh every 60 seconds with countdown

## Usage

### Option 1: Standalone HTML

Simply open `rustchain-widget.html` in a browser or embed it in an iframe:

```html
<iframe src="rustchain-widget.html" width="420" height="400" frameborder="0"></iframe>
```

### Option 2: Embed Script

Add the widget to any page:

```html
<div id="rustchain-widget"></div>
<script src="rustchain-widget.js"></script>
```

### Option 3: Custom Container

```html
<div id="my-stats"></div>
<script src="rustchain-widget.js"></script>
<script>
  RustChainWidget.init({ container: '#my-stats' });
</script>
```

## API Endpoints Used

- `https://50.28.86.131/health` — Node status
- `https://50.28.86.131/epoch` — Current epoch info
- `https://50.28.86.131/api/miners` — Active miners

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## License

MIT

---

**Bounty:** https://github.com/Scottcjn/rustchain-bounties/issues/178

**Wallet:** `h3o`
