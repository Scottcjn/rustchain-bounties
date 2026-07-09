## Badge Generator Web Tool

Built a web tool for generating BCOS v2 badges.

**Platform:** GitHub / Web
**Features:**
- Generate custom badge images based on repo URL or Certificate ID
- Support multiple badge styles (`flat`, `flat-square`, `for-the-badge`)
- Live preview using `/bcos/badge/{cert_id}.svg` endpoint
- Direct copy buttons for Markdown and HTML embed codes
- Integrated verification status check against BCOS `/verify` API
- Vintage retro-terminal theme matching the RustChain design system
- Fully responsive layout

**Tech stack:** HTML, CSS, JavaScript
**Source Code:** [index.html](./bounty-2292-badge-generator/index.html)
**Working Demo:** [https://lequangsang01.github.io/rustchain-bounties/submissions/bounty-2292-badge-generator/index.html](https://lequangsang01.github.io/rustchain-bounties/submissions/bounty-2292-badge-generator/index.html)

### Verification
- Enter `BCOS-001` or `https://github.com/lequangsang01/bottube` in the input field.
- Select a badge style.
- Click **Generate Badge** to preview the badge and get the Markdown/HTML code blocks instantly.
- The tool automatically queries the verify API to display status checks.

---

**Wallet:** RTCfe13452d122263caf633ab1876bd9631133b68b1