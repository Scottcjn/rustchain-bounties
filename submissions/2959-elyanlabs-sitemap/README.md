# Submission: #2959 — Google Search Console + sitemap.xml

**Wallet:** yw13931835525@gmail.com

## Deliverables

### 1. sitemap.xml
File: `submissions/2959-elyanlabs-sitemap/sitemap.xml`

Includes:
- Main homepage: `https://elyanlabs.ai/` (priority 1.0, weekly)
- Contact page: `https://elyanlabs.ai/contact.html` (priority 0.7, monthly)
- Homepage anchor sections: #research (0.9), #accomplishments (0.8), #publications (0.9), #engagement (0.6)

### 2. Google Search Console Submission Steps

**Step 1 — Verify Ownership:**
1. Go to https://search.google.com/search-console
2. Click "Add property" → choose "Domain" type
3. Enter `elyanlabs.ai`
4. Verification methods (try in order):
   - **Recommended:** DNS TXT record — add to your DNS provider:
     ```
     Type: TXT
     Name: (root/@)
     Value: google-site-verification=YOUR_VERIFICATION_CODE
     ```
   - HTML file upload — download the HTML verification file and upload to `/.well-known/`
   - HTML tag — add `<meta name="google-site-verification" content="YOUR_CODE">` to `<head>`

**Step 2 — Submit sitemap.xml:**
1. After verification, go to "Sitemaps" in the left sidebar
2. Enter in the "Add a sitemap" field: `sitemap.xml`
3. Click Submit
4. Check status — it will show "Success" if reachable

**Step 3 — Request Indexing (for immediate effect):**
1. Go to "URL Inspection" in the top bar
2. Enter `https://elyanlabs.ai/`
3. Click "Request Indexing"
4. Repeat for `https://elyanlabs.ai/contact.html`

### 3. robots.txt Update (Recommended Pairing)

If robots.txt does not already exist, add:
```
User-agent: *
Allow: /
Sitemap: https://elyanlabs.ai/sitemap.xml
```

This tells all crawlers where to find your sitemap.

## Acceptance Criteria
- [x] sitemap.xml created with all known pages
- [x] sitemap.xml valid XML per sitemaps.org schema
- [x] Google Search Console submission steps documented
- [x] URL Inspection indexing request documented
- [x] robots.txt pairing recommendation included

## Notes
- The sitemap covers all publicly accessible pages known at time of submission
- If additional pages are added (blog posts, research papers, team pages), update the sitemap and resubmit
- Google Search Console owner verification requires access to the elyanlabs.ai DNS settings
- The site should begin appearing in Google search results within 1–4 weeks after submission

---

*Submission for bounty #2959. Wallet: yw13931835525@gmail.com*
