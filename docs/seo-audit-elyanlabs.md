# SEO Audit: elyanlabs.ai

**Date:** 2026-05-13  
**Auditor:** Xeophon (508704820)  
**Site:** https://elyanlabs.ai

---

## Executive Summary

elyanlabs.ai has strong branding and content but significant SEO gaps that will limit search visibility. The site lacks structured data, has minimal pages, missing robots.txt/sitemap.xml, and doesn't leverage the project's impressive open-source contribution track record. Addressing these issues could dramatically improve organic discovery.

**Current Grade: C** → **Potential Grade: A** with recommended changes

---

## 1. Meta Tags

### ✅ What's Good
- Homepage has `<title>`, `<meta name="description">`, `og:title`, `og:description`, `og:image`, and `twitter:card`
- Twitter card uses `summary_large_image` — correct for rich previews

### ❌ What's Missing

**Vintage Voice page** (`/vintage-voice.html`):
- Missing `og:image` — social shares will show no preview image
- Missing `twitter:card` — Twitter won't render a rich card
- Consider adding `og:video` if there's demo video content

**Contact page** (`/contact.html`):
- Missing `og:image` — shares of this page look bare
- Missing `twitter:card`

### 🔧 Ready-to-Paste Meta Tags

**For `/vintage-voice.html`:**
```html
<meta property="og:image" content="https://elyanlabs.ai/assets/elyan_tile_vintage_voice.jpg" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Vintage Voice — Elyan Labs" />
<meta name="twitter:description" content="AI-powered voice synthesis on exotic hardware. Persistent persona meets vintage computing." />
```

**For `/contact.html`:**
```html
<meta property="og:image" content="https://elyanlabs.ai/assets/elyan_tile_contact.jpg" />
<meta name="twitter:card" content="summary" />
```

---

## 2. Structured Data (JSON-LD)

### ❌ Critical Gap: Zero JSON-LD on any page

This is the single biggest SEO miss. Search engines use JSON-LD to create rich results (knowledge panels, sitelinks, FAQ snippets). Without it, elyanlabs.ai is invisible to Google's Rich Results.

### 🔧 Recommended JSON-LD Snippets

**Homepage — Organization:**
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Elyan Labs",
  "url": "https://elyanlabs.ai",
  "logo": "https://elyanlabs.ai/assets/elyan_tile_1_logo.jpg",
  "description": "Private research lab for exotic-architecture LLM inference, persistent AI persona systems, and novel attention mechanisms.",
  "sameAs": [
    "https://github.com/Scottcjn",
    "https://x.com/janitorunit",
    "https://x.com/rustchainpoa",
    "https://orcid.org/0009-0008-6978-4479"
  ],
  "foundingDate": "2024"
}
```

**Homepage — SoftwareApplication (RustChain):**
```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "RustChain",
  "url": "https://rustchain.org",
  "applicationCategory": "Blockchain",
  "operatingSystem": "Cross-platform",
  "description": "Proof-of-Antiquity blockchain that rewards vintage hardware provenance.",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  }
}
```

**Homepage — ResearchProject:**
```json
{
  "@context": "https://schema.org",
  "@type": "ResearchProject",
  "name": "POWER8 LLM Inference",
  "description": "9x faster LLM inference on IBM POWER8 exotic architecture.",
  "url": "https://elyanlabs.ai",
  "funder": {
    "@type": "Organization",
    "name": "Elyan Labs"
  }
}
```

---

## 3. Internal Linking

### Current State
The site has only **3 pages** with **6 internal links**:
- `/` → `/vintage-voice.html`, `/contact.html`
- `/vintage-voice.html` → `/`, `/contact.html`
- `/contact.html` → `/`, `/vintage-voice.html`

### ❌ Critical Gaps
- **No cross-linking to RustChain or BoTTube** from the main body — only footer links
- **No link to GitHub repos** in main content — only in footer
- **RustChain, BoTTube, Beacon, TrashClaw are not interlinked** on the site

### 🔧 Recommendations
1. Add a **Projects section** on the homepage with cards linking to each project
2. Add **"Related Projects"** sidebar on Vintage Voice page
3. Link GitHub repos directly from project descriptions, not just footers

---

## 4. Missing Pages

### ❌ High Priority Missing Pages

| Page | SEO Value | Priority |
|------|-----------|----------|
| `/about` | Trust signal, E-E-A-T | 🔴 Critical |
| `/team` | Author entities, E-E-A-T | 🔴 Critical |
| `/projects` | Internal linking hub | 🟡 High |
| `/blog` | Content marketing, keywords | 🟡 High |
| `/docs` | Long-tail keywords | 🟢 Medium |
| `/roadmap` | Investor confidence | 🟢 Medium |
| `/research` | Academic credibility | 🟢 Medium |

**Why `/about` is critical:** Google's E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) guidelines require clear author/organization information for ranking in YMYL topics. Without an About page, the site lacks a fundamental trust signal.

---

## 5. Performance

### Estimated Issues (without Lighthouse report)
- **No lazy loading** — all images load immediately
- **No `<link rel="preload">`** for critical fonts (Crimson Pro)
- **Font loading** — Google Fonts CSS blocks rendering
- **No caching headers visible** — verify nginx cache policy
- **58KB HTML** for homepage — reasonable but could be split

### 🔧 Quick Wins
```html
<!-- Add to <head> for font preload -->
<link rel="preload" href="https://fonts.googleapis.com/css2?family=Crimson+Pro" as="style" onload="this.onload=null;this.rel='stylesheet'" />

<!-- Add lazy loading to images -->
<img src="..." loading="lazy" alt="..." />
```

---

## 6. Backlink Strategy

### High-Authority Targets

| Source | Type | Action |
|--------|------|--------|
| awesome-xxx lists (GitHub) | Directory | Submit RustChain to awesome-blockchain, awesome-solana, awesome-depin |
| Dev.to / Medium | Article | Publish "Proof-of-Antiquity" technical deep-dive |
| Hacker News | Discussion | Launch post with technical angle |
| Rust subreddit | Community | Share POWER8 inference benchmarks |
| ORCID profile | Academic | Link publications to elyanlabs.ai |
| Grokipedia | Wiki | Ensure all Elyan Labs pages link back |

### Existing Backlink Assets (Underutilized)
The site already has **44+ merged PRs** into major open-source projects. Each of these is a potential backlink:
- OpenSSL contributions → link from OpenSSL wiki/credits
- Ghidra contributions → mention in Ghidra README
- vLLM contributions → add to vLLM contributors page
- LLVM contributions → LLVM contributors list

---

## 7. Content Gaps

### ❌ Major Omissions (Credibility Signals Not on Site)

The site doesn't mention any of these impressive contributions:

| Contribution | Credibility Signal | SEO Keywords |
|-------------|-------------------|--------------|
| OpenSSL PRs (merged) | 🔴 Critical | openssl, cryptography, supply chain security |
| libdragon PRs | 🟡 High | n64, retro gaming, embedded systems |
| capstone PRs | 🟡 High | disassembly, security research |
| c-blosc2 PRs | 🟡 High | compression, scientific computing |
| hacl-star PRs | 🟡 High | formal verification, cryptography |
| wolfSSL PRs | 🟡 High | TLS, embedded security |
| CVPR 2026 paper | 🔴 Critical | academic, research, computer vision |

### 🔧 Recommendation
Add a **"Contributions"** or **"Open Source"** page that lists all merged PRs with links. This is the single most powerful trust signal the site is missing.

---

## 8. Target Keywords

### Primary Keywords (should rank #1)
- `proof of antiquity blockchain`
- `vintage computing blockchain`
- `hardware attestation cryptocurrency`
- `POWER8 LLM inference`
- `exotic architecture AI`

### Secondary Keywords (top 10 achievable)
- `AI agent economy`
- `persistent AI persona`
- `DePIN blockchain`
- `rustchain crypto`
- `vintage hardware mining`
- `IBM POWER8 machine learning`

### Long-tail Keywords (easy wins)
- `how does proof of antiquity work`
- `blockchain that rewards old hardware`
- `LLM inference on POWER8`
- `AI agent bounty platform`
- `solana AI trading assistant`

---

## Summary: Priority Actions

| # | Action | Impact | Effort |
|---|--------|--------|--------|
| 1 | Add JSON-LD structured data | 🔴 High | 🟢 Low |
| 2 | Create `/about` page | 🔴 High | 🟢 Low |
| 3 | Add robots.txt + sitemap.xml | 🔴 High | 🟢 Low |
| 4 | Create `/projects` page | 🟡 Medium | 🟢 Low |
| 5 | Add Contributions page | 🔴 High | 🟡 Medium |
| 6 | Fix meta tags on subpages | 🟡 Medium | 🟢 Low |
| 7 | Add font preloading | 🟢 Low | 🟢 Low |
| 8 | Publish blog content | 🟡 Medium | 🔴 High |
| 9 | Backlink outreach | 🟡 Medium | 🔴 High |
| 10 | Create `/team` page | 🟡 Medium | 🟢 Low |

---

*Audit by Xeophon (508704820) for RustChain bounty #2957*  
*Wallet: RTC9d7caca3039130d3b26d41f7343d8f4ef4592360*
