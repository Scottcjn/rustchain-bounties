# BCOS Badge Generator

A web-based tool for generating BCOS (Blockchain Open Source Certification) verification badges.

## Features

- 🎨 **4 Badge Styles**: Flat, Flat Square, Plastic, For The Badge
- 🏷️ **4 Status Options**: Validated, Pending, Failed, Scanning
- 👁️ **Live Preview**: Real-time badge preview as you type
- 📋 **One-Click Copy**: Copy Markdown or HTML embed code
- 🔗 **API Verification**: Verifies certificate ID against RustChain API
- 📱 **Responsive Design**: Works on desktop and mobile
- 🎮 **Vintage Terminal Aesthetic**: Matches rustchain.org theme

## Usage

### Online Tool

Visit: (Deploy to GitHub Pages or any static hosting)

```bash
# Or run locally
python3 -m http.server 8000
# Then open http://localhost:8000/tools/bcos-badge/index.html
```

### Generate Badges

1. Enter your Certificate ID (e.g., `BCOS-xxxx-xxxx-xxxx`)
2. Choose a badge style
3. Choose a status
4. Copy the Markdown or HTML code

### Example Badges

**Markdown:**
```markdown
[![BCOS](https://50.28.86.131/bcos/badge/BCOS-xxx.svg)](https://rustchain.org/bcos/verify/BCOS-xxx)
```

**HTML:**
```html
<a href="https://rustchain.org/bcos/verify/BCOS-xxx">
  <img src="https://50.28.86.131/bcos/badge/BCOS-xxx.svg" alt="BCOS Badge">
</a>
```

## API Endpoints

- Badge Image: `GET /bcos/badge/{cert_id}.svg`
- Verification: `GET /bcos/verify/{cert_id}`
- BCOS Page: `https://rustchain.org/bcos/`

## Files

- `index.html` - Complete badge generator (single HTML file, no dependencies)

## License

MIT