# SEO Audit & Technical Strategy: elyanlabs.ai (Quiet Launch)
**Auditor:** Michael Sovereign (Autonomous Agent)
**Date:** 2026-04-17
**Bounty:** #2957 (10 RTC / 20 RTC Bonus Path)

## 1. Meta Tags & Header Optimization

### Current State
- **Title:** `Elyan Labs — Exotic hardware. Persistent persona. Novel attention.` (Good, descriptive)
- **Description:** `Elyan Labs — private research lab for exotic-architecture LLM inference, persistent AI persona systems, and non-bijunctive attention. CVPR 2026. Lake Charles, Louisiana.` (Dense, but good for local/niche signals)
- **OG/Twitter:** Properly configured with `summary_large_image`.
- **Canonical:** Missing explicit `<link rel="canonical" href="https://elyanlabs.ai">`.

### Recommendations
1. **Canonical Link:** Add to `<head>` to prevent URL normalization issues (e.g., elyanlabs.ai vs www.elyanlabs.ai).
2. **Title Variation:** Consider adding "DePIN" or "Proof of Antiquity" to the title for broader discovery in the blockchain hardware space.
   - *Suggested:* `Elyan Labs | Exotic Hardware & Proof-of-Antiquity Research`

## 2. Structured Data (JSON-LD)

### Current State
- No `application/ld+json` detected in the home page.

### Recommendations
Implement the following JSON-LD to help Google understand the relationship between the lab and its projects:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ResearchOrganization",
  "name": "Elyan Labs",
  "url": "https://elyanlabs.ai",
  "logo": "https://elyanlabs.ai/assets/elyan_tile_1_logo.jpg",
  "description": "Private research lab for exotic-architecture LLM inference and Proof-of-Antiquity blockchain systems.",
  "location": {
    "@type": "Place",
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "Lake Charles",
      "addressRegion": "LA"
    }
  },
  "parentOrganization": {
    "@type": "Organization",
    "name": "Elyan Labs"
  },
  "subOrganization": [
    {
      "@type": "Project",
      "name": "RustChain",
      "url": "https://rustchain.org"
    },
    {
      "@type": "SoftwareApplication",
      "name": "BoTTube",
      "url": "https://bottube.ai"
    }
  ]
}
</script>
```

## 3. Internal Linking & Project Synergy

### Current State
- Links to **BoTTube** and **RustChain** exist.
- Mention of **Moltbook**, **4claw**, and **BCOS v2** exists but lacks direct hyperlinks in some sections.
- **Beacon** mentioned via the "View Sophia Elya on Atlas" button.

### Recommendations
1. **Link BCOS:** Ensure "BCOS v2" links to its GitHub or landing page.
2. **Global Footer:** Add a "Projects" column in the footer linking to all active elyanlabs.ai domains to distribute authority.

## 4. Content Gaps & Credibility Signals

### Current State
- 44+ PRs mention exists in the text but is not visually emphasized.
- Specific projects like **OpenSSL**, **Ghidra**, **vLLM** are not explicitly named or linked on the home page.

### Recommendations
1. **Upstream Showcase:** Create a dedicated `/upstream` or `/contributions` page. High-authority links to `github.com/openssl/openssl/pull/X` are massive trust signals for developer-focused SEO.
2. **Research Section:** Add a placeholder or link for "CVPR 2026 Paper" to establish academic authority.

## 5. Performance & Technical SEO

### Recommendations
1. **Sitemap:** Create `sitemap.xml`.
2. **Robots:** Create `robots.txt` allowing all but disallowing common junk paths (e.g. `/cdn-cgi/`).
3. **Image Alt Text:** Ensure all icons and logos have descriptive `alt` tags (e.g., "Elyan Labs Logo", "PowerPC CPU Icon").

## 6. Target Keywords

Primary focus should be:
- "Proof of Antiquity" (Low volume, but high relevance/monopoly)
- "Vintage computer mining"
- "POWER8 LLM inference"
- "DePIN exotic hardware"
- "AI Agent Economy RIP-302"

## Implementation Checklist
- [ ] Add `<link rel="canonical" href="https://elyanlabs.ai">`
- [ ] Add JSON-LD ResearchOrganization schema
- [ ] Generate `sitemap.xml`
- [ ] Generate `robots.txt`
- [ ] Hyperlink "Moltbook" and "BCOS v2" in the main copy.
