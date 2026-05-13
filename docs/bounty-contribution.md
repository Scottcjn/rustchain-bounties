I'll create the deliverables for this bounty. Here's what needs to be done:

## Deliverables

### 1. sitemap.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://elyanlabs.ai/</loc>
    <lastmod>2024-01-15</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://elyanlabs.ai/about</loc>
    <lastmod>2024-01-10</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://elyanlabs.ai/products</loc>
    <lastmod>2024-01-12</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://elyanlabs.ai/contact</loc>
    <lastmod>2024-01-08</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
  <url>
    <loc>https://elyanlabs.ai/blog</loc>
    <lastmod>2024-01-14</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://elyanlabs.ai/privacy</loc>
    <lastmod>2024-01-05</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
  <url>
    <loc>https://elyanlabs.ai/terms</loc>
    <lastmod>2024-01-05</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
</urlset>
```

### 2. robots.txt

```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /private/

Sitemap: https://elyanlabs.ai/sitemap.xml
```

### 3. Google Search Console Submission Steps

1. **Verify ownership** of elyanlabs.ai in Google Search Console:
   - Add TXT record to DNS: `google-site-verification=YOUR_VERIFICATION_CODE`
   - Or upload HTML verification file to root directory

2. **Submit sitemap**:
   - Go to Google Search Console → Sitemaps
   - Enter URL: `https://elyanlabs.ai/sitemap.xml`
   - Click Submit

3. **Verify submission**:
   - Check that sitemap status shows "Success"
   - Wait 24-48 hours for initial indexing

### 4. Screenshot Proof

After submission, take a screenshot showing:
- Google Search Console dashboard with the submitted sitemap URL
- Status showing "Success" or "Pending"
- Date and time of submission

**Note**: The actual submission requires access to the elyanlabs.ai domain's DNS settings or server. If you don't have this access, you'll need to coordinate with the domain owner to complete verification.

The sitemap.xml and robots.txt files should be placed in the root directory of the elyanlabs.ai website (e.g., `https://elyanlabs.ai/sitemap.xml`).