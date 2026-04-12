# elyanlabs.ai — sitemap.xml + robots.txt

**Bounty:** #2959 — 5 RTC  
**Wallet:** wocaoac

## Files

### sitemap.xml
Lists all currently discoverable pages on elyanlabs.ai:
- `/` — Homepage (priority 1.0, weekly refresh)
- `/contact.html` — Contact page (priority 0.6, monthly refresh)

### robots.txt
- Allows all crawlers
- Points to sitemap location
- Blocks `/admin/` and `/private/` paths as good practice

## How to deploy

Place both files at the web root of elyanlabs.ai:
```
https://elyanlabs.ai/sitemap.xml
https://elyanlabs.ai/robots.txt
```

## Google Search Console submission steps

1. Go to [search.google.com/search-console](https://search.google.com/search-console)
2. Add property: `https://elyanlabs.ai`
3. Verify ownership (HTML tag method recommended — add to `<head>`)
4. Go to Sitemaps → Add sitemap → enter `sitemap.xml`
5. Submit

## URLs included

| URL | Priority | Changefreq |
|-----|----------|-----------|
| https://elyanlabs.ai/ | 1.0 | weekly |
| https://elyanlabs.ai/contact.html | 0.6 | monthly |

*Note: As new pages are added (blog, projects, team, docs), they should be added to sitemap.xml with appropriate priorities.*
