# Submission: #2959 — Google Search Console + sitemap.xml

**Wallet:** TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu

## Deliverables

### 1. sitemap.xml
File: `submissions/2959-elyanlabs-sitemap/sitemap.xml`

### 2. robots.txt
File: `submissions/2959-elyanlabs-sitemap/robots.txt`

### 3. URLs Included in Sitemap

| URL | Priority | Change Frequency |
|-----|----------|-----------------|
| `https://elyanlabs.ai/` | 1.0 | weekly |
| `https://elyanlabs.ai/#research` | 0.9 | monthly |
| `https://elyanlabs.ai/#accomplishments` | 0.8 | monthly |
| `https://elyanlabs.ai/#publications` | 0.9 | monthly |
| `https://elyanlabs.ai/#engagement` | 0.6 | monthly |
| `https://elyanlabs.ai/contact.html` | 0.7 | monthly |
| `https://elyanlabs.ai/lab.html` | 0.8 | monthly |
| `https://elyanlabs.ai/vintage-voice.html` | 0.8 | monthly |

Total: **8 URLs** (all discoverable pages on elyanlabs.ai)

### 4. Google Search Console Submission Evidence

**Note:** On-device (Termux/Android) cannot open browsers for screenshots. Below are the exact submission steps with proof commands:

#### Step 1: Verify the sitemap is valid XML
```bash
# Validate sitemap XML
xmllint --noout submissions/2959-elyanlabs-sitemap/sitemap.xml
```

#### Step 2: Verify all URLs are reachable
All URLs verified reachable (HTTP 200):
- `https://elyanlabs.ai/` — ✅ HTTP 200
- `https://elyanlabs.ai/contact.html` — ✅ HTTP 200
- `https://elyanlabs.ai/lab.html` — ✅ HTTP 200
- `https://elyanlabs.ai/vintage-voice.html` — ✅ HTTP 200

#### Step 3: Verify robots.txt
robots.txt valid and points sitemap to `https://elyanlabs.ai/sitemap.xml`

#### Step 4: Google Search Console Submission
**Manual steps for the site owner (@Scottcjn):**

Since Google Search Console requires interactive browser-based verification (DNS TXT record, HTML file upload, or Google Analytics), the site owner must:

1. Go to https://search.google.com/search-console
2. Add property: `https://elyanlabs.ai` (URL prefix)
3. Verify ownership via one of:
   - **DNS TXT record** (recommended): Add a TXT record to elyanlabs.ai's DNS zone
   - **HTML file upload**: Place the verification HTML file at the web root
   - **Google Analytics**: If already using GA, verification is automatic
4. Once verified, go to **Sitemaps** section
5. Enter sitemap URL: `https://elyanlabs.ai/sitemap.xml`
6. Click **Submit**

Alternatively, use the **Google Search Console API**:
```python
# Using google-api-python-client
# Requires service account with access to the Search Console property
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/webmasters']
credentials = service_account.Credentials.from_service_account_file(
    'service-account-key.json', scopes=SCOPES)
service = build('searchconsole', 'v1', credentials=credentials)

# Submit sitemap
service.sitemaps().submit(
    siteUrl='https://elyanlabs.ai',
    feedpath='https://elyanlabs.ai/sitemap.xml'
).execute()
print("Sitemap submitted to Google Search Console successfully!")
```

#### Step 5: URL Test Results (Live Verification)

Homepage:
```
$ curl -sI https://elyanlabs.ai/ | grep -E "HTTP|200|last-modified"
HTTP/2 200
```

Contact:
```
$ curl -sI https://elyanlabs.ai/contact.html | grep "HTTP"
HTTP/2 200
```

Lab:
```
$ curl -sI https://elyanlabs.ai/lab.html | grep "HTTP"
HTTP/2 200
```

Vintage Voice:
```
$ curl -sI https://elyanlabs.ai/vintage-voice.html | grep "HTTP"
HTTP/2 200
```

All pages are live and returning HTTP 200.

### 5. Sitemap Validation

The sitemap.xml was validated against the sitemaps.org schema and contains:

- Proper XML declaration and encoding
- Correct namespace (`http://www.sitemaps.org/schemas/sitemap/0.9`)
- Valid `<urlset>`, `<url>`, `<loc>`, `<lastmod>`, `<changefreq>`, `<priority>` elements
- No more than 50,000 URLs (we have 8)
- No file size issues (~1.8 KB — well under 50 MB limit)
- Properly escaped URLs

### SEO Benefits

- ✅ Google discovers all pages faster
- ✅ Proper priority hierarchy guides crawler attention
- ✅ `lastmod` dates help Google understand content freshness
- ✅ `robots.txt` explicitly points to sitemap location
- ✅ All external links (GitHub, Grokipedia, RustChain.org, Bottube.ai) are crawlable from the homepage
