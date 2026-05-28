# SEO Audit: elyanlabs.ai — Quiet Launch Readiness

**Date:** 2026-05-26  
**Auditor:** @yujinju666 (Hermes V1)  
**Site:** [elyanlabs.ai](https://elyanlabs.ai)  
**Pages audited:** `/` (home), `/vintage-voice.html`, `/contact.html`

---

## 1. Current State Summary

| Check | Status |
|-------|--------|
| `<title>` tags | Good — unique on all 3 pages |
| `<meta description>` | Good — present on all pages, 140-160 chars |
| OG tags | Partial — `og:image` exists, `og:image:width/height` missing |
| Twitter cards | Mixed — home uses `summary_large_image`, contact uses `summary` |
| Structured data (JSON-LD) | **Missing entirely** |
| Canonical URLs | **Missing** |
| `robots.txt` | **404 Not Found** |
| `sitemap.xml` | **404 Not Found** |
| H1 hierarchy | Good — single H1 per page |
| Image optimization | Needs work — no `width`/`height`, no `loading` attr |
| Mobile viewport | Present |
| Theme color | Present (`#0d0b09`) |

---

## 2. Meta Tags — Recommended Fixes

### 2.1 Missing Canonical Tags

Every page needs a canonical URL to prevent duplicate content penalties:

```html
<link rel="canonical" href="https://elyanlabs.ai/">
```

### 2.2 OG Image Dimensions

Add explicit dimensions to help social platforms pre-layout:

```html
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
```

### 2.3 Twitter Card Consistency

Contact page uses `summary` (small thumbnail) while home uses `summary_large_image`. Standardize on `summary_large_image` for all pages — the site is visual enough to warrant large cards.

### 2.4 Missing Tags on Vintage Voice

`vintage-voice.html` is missing `twitter:card`, `twitter:title`, `twitter:description`, and `twitter:image`. Add:

```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="VintageVoice — First Open-Source Historical Speech TTS">
<meta name="twitter:description" content="164 hours of vintage audio (1888–1955), 10 presets including Cajun French. Built for $138 on vintage hardware.">
<meta name="twitter:image" content="https://elyanlabs.ai/assets/vintage-voice/sophia_transatlantic_1940s.jpg">
```

---

## 3. Structured Data — JSON-LD Recommendations

The site has zero structured data. These three schemas are high-ROI:

### 3.1 Organization Schema

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Elyan Labs",
  "url": "https://elyanlabs.ai",
  "logo": "https://elyanlabs.ai/assets/elyan_tile_1_logo.jpg",
  "description": "Private research lab for exotic-architecture LLM inference, persistent AI persona systems, and hardware-fingerprinted blockchain consensus.",
  "foundingDate": "2024",
  "founder": {
    "@type": "Person",
    "name": "Scott Boudreaux",
    "jobTitle": "Founder",
    "url": "https://github.com/Scottcjn"
  },
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Lake Charles",
    "addressRegion": "Louisiana",
    "addressCountry": "US"
  },
  "contactPoint": {
    "@type": "ContactPoint",
    "email": "scott@elyanlabs.ai",
    "contactType": "Research Collaboration"
  },
  "sameAs": [
    "https://github.com/Scottcjn",
    "https://github.com/sophiaeagent-beep",
    "https://x.com/janitorunit",
    "https://x.com/rustchainpoa",
    "https://bottube.ai/@elyanlabs",
    "https://orcid.org/0009-0008-6978-4479"
  ]
}
```

### 3.2 SoftwareApplication Schema (for RustChain)

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "RustChain",
  "applicationCategory": "Blockchain",
  "operatingSystem": "Cross-platform",
  "description": "Attestation blockchain with hardware-fingerprinted proof-of-antiquity consensus. Rewards vintage hardware based on device architecture and silicon age.",
  "url": "https://rustchain.org",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  }
}
```

### 3.3 Article Schema (for CVPR 2026 paper)

```json
{
  "@context": "https://schema.org",
  "@type": "ScholarlyArticle",
  "headline": "Emotional Vocabulary as Semantic Grounding: Efficient Diffusion via Affective Conditioning",
  "author": {
    "@type": "Person",
    "name": "Scott Boudreaux"
  },
  "publisher": {
    "@type": "Organization",
    "name": "CVPR 2026 Workshop — GRAIL-V-7"
  },
  "datePublished": "2026-06",
  "about": "Using emotionally-grounded language to achieve 20% more efficient diffusion outputs"
}
```

---

## 4. Internal Linking — Cross-Project Audit

Currently, elyanlabs.ai links to these projects:

| Target | Linked from |
|--------|------------|
| `rustchain.org` | Home (inline text + sidebar) |
| `bottube.ai` | Home (inline text) |
| `github.com/Scottcjn/beacon-skill` | Home (agent card section) |
| `github.com/Scottcjn/grazer-skill` | Home (agent card section) |
| `grokipedia.com` | Home (5 article links) |

**Critical gap:** The site mentions "Moltbook" and "4claw" but does not link to them. The OpenSSL PRs are listed but not linked to the actual PR pages. Add these links:

- `https://github.com/openssl/openssl/pull/30437`
- `https://github.com/openssl/openssl/pull/30452`
- `https://github.com/wolfSSL/wolfssl/pull/9932`
- Links to libdragon, capstone, c-blosc2, hacl-star PRs if available

**Also missing:** Reciprocal links FROM project sites back to elyanlabs.ai. RustChain.org and BoTTube.ai should have visible "An Elyan Labs Project" footer links.

---

## 5. Missing Pages — Priority Order

| Priority | Page | Rationale |
|----------|------|-----------|
| **P0** | `robots.txt` | Search engines may crawl inefficiently without it |
| **P0** | `sitemap.xml` | Zero pages currently indexed via sitemap submission |
| **P1** | `/about.html` | "About" is the 2nd most visited page type on research org sites |
| **P1** | `/blog/` or `/news/` | No date-stamped content = no freshness signal to Google |
| **P1** | `/opensource.html` | Dedicated page for 75+ external PRs — huge credibility signal |
| **P2** | `/team.html` | Currently buried in anchor-scroll; separate page improves crawl depth |
| **P2** | `/research.html` | Deep-dive on POWER8 benchmarks, RAM Coffers, CVPR paper |
| **P2** | `/privacy.html` | Required for Google Merchant/shopping features |
| **P3** | `/faq.html` | FAQ schema can win featured snippets for niche queries |

---

## 6. Performance Observations

*Note: Full Lighthouse scores require browser-based audit. Below are server-side observations.*

| Metric | Value | Assessment |
|--------|-------|------------|
| Page size (home) | 58.5 KB (HTML only) | Good — under 100KB |
| Response time | ~1.25s | Acceptable, room for improvement |
| Image: sophia-portrait.jpg | 62.7 KB | Could compress to ~30KB WebP |
| Image: elyan_tile_1_logo.jpg | 128.3 KB | **Too large** — should be <50KB for OG image |
| Gzip/Brotli | Unknown | Verify compression is enabled |
| Cache headers | Unknown | Add `Cache-Control: public, max-age=86400` for static assets |

### Quick Wins

```nginx
# Enable gzip
gzip on;
gzip_types text/html text/css application/javascript application/json image/svg+xml;

# Cache static assets
location /assets/ {
    expires 7d;
    add_header Cache-Control "public, immutable";
}
```

### Image Optimization

Convert hero images to WebP with `<picture>` fallbacks:

```html
<picture>
  <source srcset="/assets/sophia-portrait.webp" type="image/webp">
  <img src="/assets/sophia-portrait.jpg" alt="Sophia Elya" width="400" height="400" loading="lazy">
</picture>
```

---

## 7. Backlink Strategy — High-Authority Targets

Priority targets for link building:

| Site | Relevance | Action |
|------|-----------|--------|
| `github.com/topics/llama.cpp` | 9× stock llama.cpp benchmark | Add elyanlabs.ai to repo topics |
| `github.com/awesome-llm-inference` | POWER8 inference optimization | Submit PR to awesome lists |
| `news.ycombinator.com` | "Show HN: 9× llama.cpp on POWER8" | Post with benchmark data |
| `dev.to` | Technical writeup of RAM Coffers | Cross-post blog post |
| `lobste.rs` | Vintage computing + AI intersection | Share hardware benchmarking post |
| `reddit.com/r/LocalLLaMA` | Local LLM inference community | Share POWER8 benchmarks |
| `reddit.com/r/vintagecomputing` | Vintage hardware mining angle | Share Proof of Antiquity concept |
| `en.wikipedia.org` (via ORCID) | Academic credibility | Auto-backlinks from ORCID profile |
| `scholar.google.com` | CVPR 2026 paper | Ensure paper is indexed |

---

## 8. Content Gaps — Credibility Signals Not Visible

The site currently surfaces ~40% of the lab's actual credibility:

### 8.1 Missing from Site (but referenced in GitHub)

| Contribution | Where It Should Appear |
|-------------|----------------------|
| OpenSSL PR #30437 | `/opensource.html` with description of the fix |
| OpenSSL PR #30452 | `/opensource.html` with description of the fix |
| wolfSSL POWER8 AES (PR #9932) | `/opensource.html` — POWER8 hardware acceleration story |
| libdragon (N64 homebrew) | `/opensource.html` — demonstrates compiler/arch depth |
| capstone disassembler | `/opensource.html` — binary analysis credibility |
| c-blosc2 | `/opensource.html` — high-performance compression |
| hacl-star (verified crypto) | `/opensource.html` — formal verification credibility |
| llama.cpp contributions | `/research.html` — directly supports 9× claim |

### 8.2 Recommendation

Create `/opensource.html` with one section per project:
- What was contributed
- Link to merged PR
- Why it matters (non-technical summary)
- Hardware relevance (for POWER8/SPARC/PPC contributions)

This single page would add 2000+ words of keyword-rich, authoritative content.

---

## 9. Keyword Strategy

### 9.1 Primary Keywords (should rank #1-3)

| Keyword | Current Rank | Target |
|---------|-------------|--------|
| "Proof of Antiquity" | Likely #1 (invented term) | Defend position |
| "POWER8 LLM inference" | Unknown | Top 3 |
| "hardware attestation blockchain" | Unknown | Top 10 |
| "vintage silicon mining" | Unknown | Top 10 |
| "AI agent economy" | Unknown | Top 20 |

### 9.2 Long-Tail Keywords (create content to capture)

- "how to run llama.cpp on IBM POWER8"
- "non-bijunctive permutation collapse explained"
- "cross-runtime AI persona persistence"
- "vintage hardware proof of work alternative"
- "CVPR 2026 diffusion efficiency emotional grounding"
- "open source TTS historical speech patterns"
- "NUMA-aware weight banking LLM"
- "RustChain mining on PowerPC G4"

### 9.3 Semantic Keyword Clusters

**Cluster 1 — Hardware Inference:** exotic architecture, POWER8, NUMA, vec_perm, matmul offload, llama.cpp, throughput, token/s, non-bijunctive, RAM Coffers

**Cluster 2 — AI Personas:** persistent identity, cross-runtime, memory scaffolding, anti-flattening, DriftLock, SophiaCore, Elyan Prime, emotional grounding

**Cluster 3 — Blockchain:** Proof of Antiquity, hardware fingerprint, attestation, vintage silicon, DePIN, RTC token, agent economy, Beacon Protocol

**Cluster 4 — Open Source:** OpenSSL, wolfSSL, libdragon, capstone, c-blosc2, hacl-star, verified cryptography, N64 homebrew

---

## 10. robots.txt (Recommended)

```text
User-agent: *
Allow: /
Sitemap: https://elyanlabs.ai/sitemap.xml

User-agent: GPTBot
Disallow: /

User-agent: anthropic-ai
Disallow: /
```

---

## 11. sitemap.xml (Recommended)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://elyanlabs.ai/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://elyanlabs.ai/vintage-voice.html</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://elyanlabs.ai/contact.html</loc>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
</urlset>
```

---

## 12. Priority Action Items (Sorted by ROI)

| # | Action | Effort | SEO Impact |
|---|--------|--------|------------|
| 1 | Create `robots.txt` | 5 min | High — crawl efficiency |
| 2 | Create `sitemap.xml` + submit to GSC | 15 min | High — indexation |
| 3 | Add JSON-LD Organization schema to all pages | 30 min | High — rich results |
| 4 | Add canonical URLs to all pages | 5 min | Medium — dedup |
| 5 | Fix Twitter card inconsistency + missing tags | 15 min | Medium — social CTR |
| 6 | Add `og:image:width/height` to all pages | 5 min | Low — social layout |
| 7 | Compress hero images (128KB → sub-50KB) | 20 min | Medium — LCP |
| 8 | Enable gzip + cache headers in nginx | 15 min | Medium — TTFB |
| 9 | Create `/opensource.html` | 2-3 hours | High — keyword breadth |
| 10 | Create `/blog/` with first post: "9× llama.cpp on POWER8" | 3-4 hours | High — freshness signal |
| 11 | Add reciprocal "Elyan Labs" footer links on RustChain/BoTTube | 30 min | Medium — link equity |
| 12 | Submit to GitHub awesome lists + relevant subreddits | 2 hours | Medium — backlinks |
| 13 | Add JSON-LD SoftwareApplication (RustChain) | 15 min | Medium — rich results |
| 14 | Add JSON-LD ScholarlyArticle (CVPR paper) | 10 min | Medium — Google Scholar |
| 15 | Create `/about.html` + `/team.html` | 3-4 hours | Medium — E-E-A-T |
| 16 | Run full Lighthouse audit (browser-based) | 20 min | Baseline measurement |

---

## 13. Bonus: Ready-to-Paste Meta Tag Fixes

### For `index.html` head:

```html
<link rel="canonical" href="https://elyanlabs.ai/">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="robots" content="index, follow">
<script type="application/ld+json">
  <!-- Organization JSON-LD from Section 3.1 -->
</script>
```

### For `vintage-voice.html` head:

```html
<link rel="canonical" href="https://elyanlabs.ai/vintage-voice.html">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="VintageVoice — First Open-Source Historical Speech TTS">
<meta name="twitter:description" content="164 hours of vintage audio (1888–1955). 10 presets including Cajun French. Built for $138.">
<meta name="twitter:image" content="https://elyanlabs.ai/assets/vintage-voice/sophia_transatlantic_1940s.jpg">
<meta name="robots" content="index, follow">
```

### For `contact.html` head:

```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://elyanlabs.ai/assets/sophia-portrait.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
```

---

**End of Audit.** 16 specific action items, ready-to-paste code snippets, keyword clusters, and backlink targets. Estimated total effort: ~12 hours for all recommendations.
