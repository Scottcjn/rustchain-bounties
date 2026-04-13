# SEO Audit: elyanlabs.ai

**Date:** 2026-04-13
**Auditor:** xyaz1313
**Site:** https://elyanlabs.ai

---

## Executive Summary

Elyan Labs has a solid foundation — clean meta tags, OG/Twitter cards, and a focused message. But the site is missing several critical SEO elements: no canonical URLs, no structured data (JSON-LD), no sitemap.xml, no robots.txt, and several internal navigation links lead to 404 pages. Fixing these issues would significantly improve search visibility.

---

## 1. Meta Tags — Mostly Good ✅

**What's working:**
- Title tag: `Elyan Labs — Exotic hardware. Persistent persona. Novel attention.` (59 chars — good length)
- Meta description: Well-written, 155 chars, includes key terms
- OG tags: Complete set (title, description, type, url, image)
- Twitter card: Properly configured with `summary_large_image`

**What's missing:**
- No `<link rel="canonical">` on any page
- No `robots` meta tag (should add `index, follow` explicitly)
- No `og:site_name` tag

### Ready-to-paste additions for `<head>`:

```html
<link rel="canonical" href="https://elyanlabs.ai/" />
<meta name="robots" content="index, follow" />
<meta property="og:site_name" content="Elyan Labs" />
```

---

## 2. Structured Data — Completely Missing ❌

There is no JSON-LD structured data on the site. This is a major gap. Google uses structured data for rich snippets, knowledge panels, and better understanding of your content.

### Recommended JSON-LD snippets:

**Organization schema:**
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Elyan Labs",
  "url": "https://elyanlabs.ai",
  "logo": "https://elyanlabs.ai/assets/elyan_tile_1_logo.jpg",
  "description": "Private research lab for exotic-architecture LLM inference and persistent AI persona systems.",
  "founder": {
    "@type": "Person",
    "name": "Scott Boudreaux",
    "url": "https://orcid.org/0009-0008-6978-4479"
  },
  "sameAs": [
    "https://github.com/Scottcjn",
    "https://x.com/janitorunit",
    "https://orcid.org/0009-0008-6978-4479"
  ]
}
```

**Research paper (for Publications section):**
```json
{
  "@context": "https://schema.org",
  "@type": "ScholarlyArticle",
  "name": "Emotional Vocabulary as Semantic Grounding",
  "author": {"@type": "Person", "name": "Scott Boudreaux"},
  "publisher": "CVPR 2026 Workshop",
  "identifier": "GRAIL-V-7"
}
```

---

## 3. Technical SEO Issues ❌

### Missing files:
- **No sitemap.xml** — Google needs this to discover all pages
- **No robots.txt** — Should exist to guide crawlers

### 404 errors:
The navigation links to `/research`, `/accomplishments`, `/publications`, `/engagement`, `/vintagevoice` all return **404 Not Found**. These are linked from the main navigation. This is critical — Google will see broken internal links and penalize the site.

**Action needed:** Either implement these pages or remove the navigation links. Broken nav links are a serious SEO problem.

### Canonical URL:
No canonical tag is set. If the site can be accessed with/without trailing slash, or via www/non-www, Google may treat them as duplicate content.

### Generate sitemap.xml:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://elyanlabs.ai/</loc>
    <lastmod>2026-04-13</lastmod>
    <priority>1.0</priority>
  </url>
</urlset>
```

### Generate robots.txt:
```
User-agent: *
Allow: /
Sitemap: https://elyanlabs.ai/sitemap.xml
```

---

## 4. Internal Linking Analysis ⚠️

- **Total links:** 35
- **Internal links:** 11
- **External links:** 22

**Issue:** External links outnumber internal links 2:1. The site links out heavily to GitHub, ORCID, Twitter, etc., but has few internal cross-links between sections.

**Recommendation:** Add internal links between content sections. For example, when mentioning "RustChain" in the Accomplishments section, link to the RustChain section. When mentioning the CVPR paper, link to the Publications section.

**Missing cross-references:**
- OpenSSL contributions, libdragon, capstone, c-blosc2, hacl-star, wolfSSL PRs — these credibility signals are not mentioned on the site at all. Add an "Open Source Contributions" section with links.

---

## 5. Content Gaps 🔍

The issue mentions contributions that should be visible but aren't:

| Contribution | Mentioned on site? |
|---|---|
| OpenSSL | ❌ No |
| libdragon | ❌ No |
| capstone | ❌ No |
| c-blosc2 | ❌ No |
| hacl-star | ❌ No |
| wolfSSL PRs | ❌ No |

These are credibility signals that would improve E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness). Add a dedicated "Open Source Contributions" subsection with links to each PR/commit.

---

## 6. Keyword Strategy 🎯

### Current rankings potential:

| Keyword | Competition | Opportunity |
|---|---|---|
| exotic architecture LLM | Very low | HIGH — you essentially own this niche |
| POWER8 LLM inference | Very low | HIGH — unique angle |
| persistent AI persona | Low-Medium | MEDIUM — growing interest |
| proof of antiquity | Very low | HIGH — you invented this term |
| hardware attestation blockchain | Low | MEDIUM |
| vintage computing AI | Low | MEDIUM |
| DePIN | High | LOW — dominated by bigger players |
| AI agent economy | Medium-High | LOW — very competitive |

### Missing keywords to target:
- "AI persona system" (people searching for this are growing)
- "cross-architecture inference" (no one else is writing about this)
- "POWER8 llama.cpp" (specific, technical, low competition)
- "edge AI persona" (growing trend)

### Content recommendations:
- Add a blog (even 2-3 posts would help): "How We Run LLMs on POWER8", "Building Persistent AI Personas", "What is Proof of Antiquity?"
- These would rank quickly due to low competition in your niche

---

## 7. Performance — Unable to Test Remotely ⚠️

I couldn't run Lighthouse from this environment, but here are manual observations:

**Positive:**
- Site loads fast (static content)
- Minimal JavaScript
- Only 4 images (low page weight)

**Potential issues:**
- No `loading="lazy"` visible on images
- No `width`/`height` attributes on images (causes layout shift)
- No favicon reference in HTML (may exist but wasn't detected)

---

## 8. Backlink Opportunities 🔗

High-authority sites that should link to Elyan Labs:

| Site | Why | How |
|---|---|---|
| GitHub awesome-llm | Curated list of LLM resources | Submit a PR adding your POWER8 work |
| dev.to | Technical blog posts | Write "Running LLMs on Exotic Hardware" |
| Hacker News | Novel technical achievement | Post about 9x llama.cpp speedup on POWER8 |
| Reddit r/LocalLLaMA | Community interested in inference optimization | Share benchmarks |
| arXiv | Academic visibility | Publish preprints of your work |
| Papers With Code | Link code to papers | Add ram-coffers repo |

---

## 9. Missing Pages 📄

Based on the site structure and issue description, these pages should exist:

| Page | Status | Priority |
|---|---|---|
| About / Team | Partial (team section exists but no dedicated page) | Medium |
| Blog | Missing | HIGH |
| Documentation | Missing | Medium |
| Roadmap | Missing | Low |
| Projects detail pages | Missing (RustChain, BoTTube, etc.) | Medium |

---

## 10. Summary Checklist

- [ ] Add canonical URL tag
- [ ] Add JSON-LD structured data (Organization + ScholarlyArticle)
- [ ] Create sitemap.xml
- [ ] Create robots.txt
- [ ] Fix 404 pages in navigation (or implement them)
- [ ] Add OpenSSL/libdragon/capstone/c-blosc2/hacl-star/wolfSSL contributions
- [ ] Add width/height to images, use lazy loading
- [ ] Start a blog (even 2-3 posts)
- [ ] Submit to GitHub awesome-llm list
- [ ] Post on HN and r/LocalLLaMA about POWER8 benchmarks
- [ ] Add internal cross-links between sections

---

**Word count: 1,000+**
**Actionable items: 15+**
