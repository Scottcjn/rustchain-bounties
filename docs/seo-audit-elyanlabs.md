# SEO Audit — elyanlabs.ai

**Bounty:** #2957 — 10 RTC (20 RTC bonus with Lighthouse + meta HTML + JSON-LD)  
**Audited:** 2026-04-11  
**Wallet:** wocaoac

---

## Executive Summary

elyanlabs.ai has strong foundational meta tags (og/twitter cards present, correct image) but is missing several critical SEO elements: no sitemap, no robots.txt, no JSON-LD structured data, no canonical tags, minimal internal linking, and the site's most credibility-boosting content (44+ merged OSS PRs to OpenSSL, Ghidra, vLLM, LLVM) is buried in the page body without semantic markup.

**Overall estimated Lighthouse SEO score: ~65/100** (see detailed breakdown below).

---

## 1. Meta Tags Audit

### ✅ Present and correct

| Tag | Value | Status |
|-----|-------|--------|
| `<meta charset>` | UTF-8 | ✅ |
| `<meta viewport>` | width=device-width, initial-scale=1.0 | ✅ |
| `<meta name="description">` | "Elyan Labs — private research lab for exotic-architecture LLM inference, persistent AI persona systems, and novel attention mechanisms." | ✅ Good length (~155 chars) |
| `<meta name="author">` | Scott Boudreaux | ✅ |
| `og:title` | "Elyan Labs — Exotic hardware. Persistent persona. Novel attention." | ✅ |
| `og:description` | Present | ✅ |
| `og:type` | website | ✅ |
| `og:url` | https://elyanlabs.ai | ✅ |
| `og:image` | https://elyanlabs.ai/assets/elyan_tile_1_logo.jpg | ✅ |
| `twitter:card` | summary_large_image | ✅ |
| `twitter:title` | Present | ✅ |
| `twitter:image` | Present | ✅ |

### ❌ Missing

| Tag | Issue | Fix |
|-----|-------|-----|
| `<link rel="canonical">` | Not present on any page — causes duplicate content risk if pages are accessed via HTTP or www | Add `<link rel="canonical" href="https://elyanlabs.ai/">` to every page |
| `twitter:description` | May be truncated or absent | Add explicit `<meta name="twitter:description">` |
| `og:image:width` / `og:image:height` | Missing dimensions — some parsers won't load image | Add `<meta property="og:image:width" content="1200">` etc. |
| Per-page `og:url` | contact.html should have its own `og:url` | Set to `https://elyanlabs.ai/contact.html` |

### Ready-to-paste meta tag HTML

```html
<!-- Canonical (add to every page, update URL per page) -->
<link rel="canonical" href="https://elyanlabs.ai/">

<!-- Twitter description -->
<meta name="twitter:description" content="Private research lab building 9x faster LLM inference on POWER8, persistent AI persona systems, and novel attention mechanisms. 44+ merged upstream contributions to OpenSSL, Ghidra, vLLM, LLVM.">

<!-- OG image dimensions -->
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:type" content="image/jpeg">

<!-- For contact.html specifically -->
<link rel="canonical" href="https://elyanlabs.ai/contact.html">
<meta property="og:url" content="https://elyanlabs.ai/contact.html">
<meta property="og:title" content="Contact — Elyan Labs">
<meta name="description" content="Contact Elyan Labs — partnership inquiries, research collaboration, technology licensing, and consulting on exotic-architecture AI inference.">
```

---

## 2. Structured Data (JSON-LD)

### ❌ Current state: None

No JSON-LD found on any page. This is a significant missed opportunity — Google uses structured data for rich results, knowledge panels, and credibility signals.

### Ready-to-paste JSON-LD snippets

**Organization schema (add to `<head>` of every page):**

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Elyan Labs",
  "url": "https://elyanlabs.ai",
  "logo": "https://elyanlabs.ai/assets/elyan_tile_1_logo.jpg",
  "description": "Private research lab for exotic-architecture LLM inference, persistent AI persona systems, and novel attention mechanisms.",
  "founder": {
    "@type": "Person",
    "name": "Scott Boudreaux"
  },
  "sameAs": [
    "https://github.com/Scottcjn",
    "https://x.com/janitorunit",
    "https://rustchain.org"
  ]
}
</script>
```

**SoftwareApplication schema for RustChain (add to homepage):**

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "RustChain",
  "url": "https://rustchain.org",
  "applicationCategory": "BlockchainApplication",
  "operatingSystem": "Linux, macOS, Windows",
  "description": "Proof-of-Antiquity blockchain that rewards vintage hardware. Older computers earn more RTC tokens.",
  "author": {
    "@type": "Organization",
    "name": "Elyan Labs"
  }
}
</script>
```

**BreadcrumbList (add to contact.html):**

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://elyanlabs.ai"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Contact",
      "item": "https://elyanlabs.ai/contact.html"
    }
  ]
}
</script>
```

---

## 3. Internal Linking

### ❌ Critical gap

The homepage links to only one internal page (`/contact.html`). All other links go to external sites (GitHub, RustChain, BoTTube, Grokipedia).

**Missing internal pages that should exist:**

| Page | Why | Priority |
|------|-----|----------|
| `/projects.html` | Hub linking RustChain, BoTTube, Beacon, TrashClaw | HIGH |
| `/research.html` | OpenSSL/LLVM/vLLM contributions detail | HIGH |
| `/team.html` | Scott Boudreaux + Sophia Elya agent page | MEDIUM |
| `/blog/` | Regular content for crawlability | MEDIUM |
| `/docs/` | Technical documentation | MEDIUM |
| `/roadmap.html` | Investor/contributor signal | LOW |

**Internal link fix for homepage:**

Every section heading (Research, Accomplishments, Publications, Grokipedia Articles, Engagement, Team) should link to a dedicated subpage. Currently they're all anchors on the same page with no deep-linkable URLs.

---

## 4. Missing Pages Analysis

**elyanlabs.ai currently has 2 pages.** A lab with 44+ merged upstream OSS contributions, a blockchain project, an AI agent platform, and CVPR 2026 paper should have at minimum:

1. **`/research`** — Detail the OpenSSL AES-GCM fix, LLVM PowerPC patches, vLLM POWER8 backend. These are credibility signals that currently only appear as a list in the homepage body.
2. **`/projects`** — RustChain, BoTTube, Beacon, TrashClaw with descriptions, links, and status.
3. **`/blog`** — Even 3-4 posts about Proof-of-Antiquity, POWER8 LLM inference, or the CVPR paper would dramatically improve crawl depth and keyword coverage.
4. **`/about`** — Lab history, mission, hardware focus.

---

## 5. Performance (Estimated Lighthouse Breakdown)

*Full Lighthouse run requires a browser — scores below are estimates based on page structure analysis.*

| Category | Estimated Score | Notes |
|----------|----------------|-------|
| Performance | ~75 | Google Fonts external load, no lazy loading detected |
| Accessibility | ~85 | Semantic HTML present; alt text status unknown |
| Best Practices | ~90 | HTTPS, no obvious issues |
| SEO | ~65 | Missing canonical, JSON-LD, sitemap, robots.txt |

**Core Web Vitals estimated issues:**
- Google Fonts (`fonts.googleapis.com`) blocks render — preload or self-host
- No `<link rel="preload">` for hero image

**Quick performance wins:**
```html
<!-- Add to <head> before Google Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<!-- Preload hero image -->
<link rel="preload" as="image" href="/assets/elyan_tile_1_logo.jpg">
```

---

## 6. Backlink Opportunities

Sites that should link to elyanlabs.ai:

| Site | Why | How |
|------|-----|-----|
| GitHub awesome-depin | DePIN project | PR to add elyanlabs.ai/RustChain ✅ already submitted |
| awesome-mcp-servers | MCP server for RustChain | PR submitted ✅ |
| Hacker News | Security/OSS angle: "We fixed OpenSSL on PowerPC G4" | Show HN post |
| Dev.to | Technical article on POWER8 LLM inference | Publish article |
| arxiv.org | CVPR 2026 paper link back | Add homepage URL to paper |
| grokipedia.com | Already linked from homepage | Ensure backlinks from article footers |
| rustchain.org | Sister project | Prominent footer link to elyanlabs.ai |

---

## 7. Content Gaps — The Buried Credibility Signals

**This is the biggest SEO opportunity on the site.**

The homepage mentions "44+ merged upstream contributions" but lists them in a dense table with no individual pages, no dedicated URLs, and no searchable content per project. Google cannot rank elyanlabs.ai for "OpenSSL PowerPC fix", "LLVM PowerPC patch", "vLLM POWER8" etc. because there's no dedicated page.

**Recommended keyword targets the site should rank for:**

| Keyword | Monthly searches (est.) | Fix |
|---------|------------------------|-----|
| "Proof of Antiquity blockchain" | Low | Dedicated `/projects/rustchain` page |
| "vintage computing blockchain" | Low | Blog post + project page |
| "POWER8 LLM inference" | Low | Research page with benchmark data |
| "PowerPC OpenSSL fix" | Very low | Dedicated research post |
| "DePIN Proof of Antiquity" | Low | Add to projects page |
| "AI agent economy blockchain" | Low | Connect RustChain + elyanlabs narrative |

**Content fix (high impact, low effort):**

Create `/research/openssl-powerpc.html` that details the OpenSSL AES-GCM fix with code, before/after benchmarks, and links to the merged PRs. This alone would rank for several low-competition but credible security/OSS queries.

---

## 8. Summary — Priority Action List

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| 🔴 CRITICAL | Add sitemap.xml + robots.txt | 30 min | High |
| 🔴 CRITICAL | Add JSON-LD Organization schema | 15 min | High |
| 🔴 CRITICAL | Add `<link rel="canonical">` to all pages | 10 min | High |
| 🟠 HIGH | Create `/projects` hub page | 2 hours | High |
| 🟠 HIGH | Create `/research` page with OSS contributions | 3 hours | High |
| 🟡 MEDIUM | Add twitter:description meta tag | 5 min | Medium |
| 🟡 MEDIUM | Add og:image dimensions | 5 min | Medium |
| 🟡 MEDIUM | Self-host or preconnect Google Fonts | 30 min | Medium |
| 🟢 LOW | Add blog with 3-4 technical posts | 1 week | High (long-term) |
| 🟢 LOW | Add BreadcrumbList JSON-LD to inner pages | 30 min | Low |

---

*Audit by wocaoac — submitted for bounty #2957*
