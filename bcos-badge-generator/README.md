# BCOS Badge Generator

> Bounty #2292 — Static badge generator for BCOS (Beacon Certified Open Source) attestations.

Live at: `rustchain.org/bcos/badge-generator`

## Features

- Enter a **GitHub repo URL** or **cert ID** (`BCOS-xxx`) to look up the attestation
- Live **badge preview** with instant style switching
- One-click **copy** for Markdown and HTML embed codes
- Supports all three badge styles: `flat`, `flat-square`, `for-the-badge`
- Vintage terminal aesthetic matching rustchain.org
- Pure static HTML/JS — no backend required

## Usage

Open `index.html` in any browser. No build step, no dependencies.

```bash
# Serve locally (optional)
python -m http.server 8080
# open http://localhost:8080
```

## Badge URL Format

```
https://50.28.86.131/bcos/badge/{cert_id}.svg?style=flat
```

## API Endpoints Used

| Endpoint | Description |
|----------|-------------|
| `GET /bcos/verify/{cert_id}` | Look up cert by ID |
| `GET /bcos/repo/{owner/repo}` | Look up cert by repo slug |
| `GET /bcos/badge/{cert_id}.svg?style=flat` | SVG badge |

## Example Output

**Markdown:**
```markdown
[![BCOS](https://50.28.86.131/bcos/badge/BCOS-abc1234.svg)](https://rustchain.org/bcos/verify/BCOS-abc1234)
```

**HTML:**
```html
<a href="https://rustchain.org/bcos/verify/BCOS-abc1234">
  <img src="https://50.28.86.131/bcos/badge/BCOS-abc1234.svg" alt="BCOS">
</a>
```

## License

MIT
