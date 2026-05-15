# Google Search Console Setup Guide for RustChain

This guide walks you through setting up **sitemap.xml** and **Google Search Console (GSC)** for RustChain's official website.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Sitemap.xml Overview](#sitemapxml-overview)
3. [Deploying the Sitemap](#deploying-the-sitemap)
4. [Setting Up robots.txt](#setting-up-robotstxt)
5. [Google Search Console Setup](#google-search-console-setup)
6. [Submitting the Sitemap to GSC](#submitting-the-sitemap-to-gsc)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Google account** with access to manage `rustchain.xyz`
- **DNS access** to the domain (for domain verification)
- **Website deploy access** (to upload sitemap.xml and robots.txt)
- **HTTPS** enabled on the site (required by Google)

---

## Sitemap.xml Overview

The `sitemap.xml` file follows the [sitemaps.org protocol](https://www.sitemaps.org/protocol.html) and includes:

| Section | Pages | Priority |
|---------|-------|----------|
| Homepage | `/` | 1.0 |
| Documentation | `/docs`, `/docs/*` | 0.7–0.9 |
| Ecosystem | `/ecosystem`, `/ecosystem/*` | 0.6–0.8 |
| Validators | `/validators`, `/validators/*` | 0.6–0.8 |
| Bounties | `/bounties`, `/bounties/*` | 0.6–0.8 |
| Community | `/community` | 0.8 |
| Blog | `/blog` | 0.7 |
| Legal | `/privacy`, `/terms` | 0.3 |

### Key fields explained

- **`<loc>`** — Full URL of the page (must include `https://`)
- **`<lastmod>`** — Date of last modification (W3C Datetime format)
- **`<changefreq>`** — How often the page is expected to change (hint, not directive)
- **`<priority>`** — Relative priority (0.0–1.0) compared to other pages on the site

### Validation

Before deploying, validate your sitemap:

1. **Online validator:** https://www.xml-sitemaps.com/validate-xml-sitemap.html
2. **Manual check:** Open `sitemap.xml` in a browser — it should render as valid XML without errors

---

## Deploying the Sitemap

### Step 1: Upload to site root

Place `sitemap.xml` at the root of your website:

```
https://rustchain.xyz/sitemap.xml
```

#### For static hosting (Netlify, Vercel, etc.)

Copy `sitemap.xml` to the `public/` or `static/` directory of your project.

#### For Next.js projects

```bash
# Option A: Static file
cp sitemap.xml public/sitemap.xml

# Option B: Dynamic generation (recommended for blogs)
# Create app/sitemap.ts or pages/sitemap.xml.ts
```

#### For Nginx

```bash
cp sitemap.xml /var/www/rustchain/public/sitemap.xml
```

### Step 2: Verify deployment

```bash
curl -I https://rustchain.xyz/sitemap.xml
# Should return 200 OK with Content-Type: application/xml
```

### Step 3: Automate lastmod updates (optional)

For dynamic sitemaps, generate the file on build:

```javascript
// next.js example: app/sitemap.js
export default function sitemap() {
  return [
    {
      url: 'https://rustchain.xyz',
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 1.0,
    },
    // ... more entries
  ];
}
```

---

## Setting Up robots.txt

The `robots.txt` file tells search engine crawlers which pages to index and where to find the sitemap.

### Deployment

Place `robots.txt` at the website root:

```
https://rustchain.xyz/robots.txt
```

### Key directives explained

```
User-agent: *          # Applies to all crawlers
Allow: /               # Allow crawling of all public pages
Disallow: /api/internal/  # Block internal API paths
Disallow: /admin/         # Block admin panels
Sitemap: https://rustchain.xyz/sitemap.xml  # Sitemap location
Crawl-delay: 1            # 1 second between requests
```

### Verify

```bash
curl https://rustchain.xyz/robots.txt
# Should show the robots.txt content
```

---

## Google Search Console Setup

### Step 1: Open Google Search Console

Navigate to: **https://search.google.com/search-console**

### Step 2: Add your property

1. Click **"Add property"**
2. Select **"URL prefix"** and enter: `https://rustchain.xyz`
3. Click **"Continue"**

### Step 3: Verify ownership

Choose one of these methods:

#### Method A: DNS TXT Record (Recommended)

1. In GSC, select **"DNS record"** verification
2. Copy the TXT value provided (e.g., `google-site-verification=XXXXX`)
3. Go to your DNS provider (Cloudflare, Route53, etc.)
4. Add a **TXT record**:
   - **Name/Host:** `@` (or leave blank)
   - **Value:** `google-site-verification=XXXXX`
   - **TTL:** 3600 (or default)
5. Wait 1–5 minutes for DNS propagation
6. Click **"Verify"** in GSC

#### Method B: HTML file upload

1. Download the verification HTML file from GSC
2. Upload it to `https://rustchain.xyz/[verification-file].html`
3. Click **"Verify"**

#### Method C: HTML tag

1. Copy the `<meta>` tag from GSC
2. Add it to the `<head>` of your homepage:
   ```html
   <meta name="google-site-verification" content="XXXXX" />
   ```
3. Deploy and click **"Verify"**

#### Method D: Google Analytics / Tag Manager

If you already have GA or GTM on the site with the same Google account, you can verify instantly.

### Step 4: Confirm verification

After successful verification, you'll see:
> "Ownership verified. Data may take a few days to appear."

---

## Submitting the Sitemap to GSC

### Step 1: Navigate to Sitemaps

In Google Search Console:
1. Select your property (`https://rustchain.xyz`)
2. In the left sidebar, click **"Sitemaps"**

### Step 2: Submit

1. In the "Add a new sitemap" field, enter: `sitemap.xml`
2. Click **"Submit"**

### Step 3: Check status

- **Status: "Success"** — Google has accepted the sitemap
- **Status: "Could not fetch"** — Check that the URL is accessible
- **Status: "Has errors"** — Click the sitemap to see specific errors

Google typically processes sitemaps within a few hours, but indexing may take days to weeks.

### Step 4: Request indexing for key pages (optional)

For important pages, you can request immediate indexing:
1. Use the **"URL Inspection"** tool in GSC
2. Enter the page URL
3. Click **"Request indexing"**

Do this for the homepage and key landing pages.

---

## Monitoring & Maintenance

### Regular Checks (Weekly)

1. **GSC Dashboard** → Check for crawl errors, indexing issues
2. **Sitemap status** → Ensure it shows "Success"
3. **Coverage report** → Review pages indexed vs. submitted

### Updating the Sitemap

When new pages are added:

1. Update `sitemap.xml` with new `<url>` entries
2. Update `<lastmod>` dates for changed pages
3. Re-submit in GSC (or let Google re-crawl via robots.txt pointer)

### Automated monitoring

Set up alerts for:
- **Crawl anomalies** (GSC → Settings → Email notifications)
- **Index coverage drops** (significant decrease in indexed pages)
- **Core Web Vitals** (GSC → Experience)

### Key Metrics to Track

| Metric | Where to Find | Target |
|--------|--------------|--------|
| Indexed pages | GSC → Coverage | >90% of submitted |
| Crawl errors | GSC → Coverage | 0 |
| Average position | GSC → Performance | Improving |
| Click-through rate | GSC → Performance | >3% |
| Core Web Vitals | GSC → Experience | All green |

---

## Troubleshooting

### Sitemap not detected

```
Problem: "Could not fetch" in GSC
```

**Solutions:**
- Verify `https://rustchain.xyz/sitemap.xml` returns 200 in a browser
- Check robots.txt has the correct `Sitemap:` directive
- Ensure no authentication or firewall blocks Googlebot

### Pages not being indexed

```
Problem: Pages submitted but not indexed
```

**Solutions:**
- Check the page returns HTTP 200
- Ensure no `noindex` meta tag: `<meta name="robots" content="noindex">`
- Ensure the page is not blocked in robots.txt
- Use URL Inspection tool to see Google's view

### Sitemap too large

- Maximum: **50,000 URLs** per sitemap file, **50MB** uncompressed
- For larger sites, use a **sitemap index file** that links to multiple sitemaps:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://rustchain.xyz/sitemap-main.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://rustchain.xyz/sitemap-blog.xml</loc>
  </sitemap>
</sitemapindex>
```

### Duplicate content issues

- Use **canonical URLs**: `<link rel="canonical" href="https://rustchain.xyz/page" />`
- Ensure only one version is in the sitemap (prefer `https://` and `www` or non-`www`, not both)

---

## Quick Checklist

- [ ] `sitemap.xml` uploaded to site root
- [ ] `robots.txt` uploaded to site root with Sitemap directive
- [ ] Both files return 200 when accessed via HTTPS
- [ ] Google Search Console property created for `https://rustchain.xyz`
- [ ] Domain ownership verified
- [ ] Sitemap submitted in GSC
- [ ] Sitemap status shows "Success"
- [ ] URL inspection works for key pages
- [ ] Email notifications enabled for crawl issues

---

*Generated for RustChain Bounty #2959 — Sitemap.xml + Google Search Console Setup Guide*
