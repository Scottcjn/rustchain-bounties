# Raw Verbose Curl Traces - x402 Retest Matrix v2

All traces captured from clean environment connecting directly to production endpoints.

## Row 1: GET https://bottube.ai/api/x402/info

**Description**: Expected 200 OK - Capability discovery endpoint

```text
COMMAND: curl -sv https://bottube.ai/api/x402/info

--- STDERR (curl verbose trace) ---
* Host bottube.ai:443 was resolved.
* IPv6: (none)
* IPv4: 50.28.86.153
*   Trying 50.28.86.153:443...
* Connected to bottube.ai (50.28.86.153) port 443
* ALPN: curl offers h2,http/1.1
* (304) (OUT), TLS handshake, Client hello (1):
} [315 bytes data]
*  CAfile: /etc/ssl/cert.pem
*  CApath: none
* (304) (IN), TLS handshake, Server hello (2):
{ [122 bytes data]
* (304) (IN), TLS handshake, Unknown (8):
{ [19 bytes data]
* (304) (IN), TLS handshake, Certificate (11):
{ [4079 bytes data]
* (304) (IN), TLS handshake, CERT verify (15):
{ [264 bytes data]
* (304) (IN), TLS handshake, Finished (20):
{ [52 bytes data]
* (304) (OUT), TLS handshake, Finished (20):
} [52 bytes data]
* SSL connection using TLSv1.3 / AEAD-AES256-GCM-SHA384 / [blank] / UNDEF
* ALPN: server accepted h2
* Server certificate:
*  subject: CN=bottube.ai
*  start date: Jul 30 14:06:52 2026 GMT
*  expire date: Oct 28 14:06:51 2026 GMT
*  subjectAltName: host "bottube.ai" matched cert's "bottube.ai"
*  issuer: C=US; O=Let's Encrypt; CN=YR2
*  SSL certificate verify ok.
* using HTTP/2
* [HTTP/2] [1] OPENED stream for https://bottube.ai/api/x402/info
* [HTTP/2] [1] [:method: GET]
* [HTTP/2] [1] [:scheme: https]
* [HTTP/2] [1] [:authority: bottube.ai]
* [HTTP/2] [1] [:path: /api/x402/info]
* [HTTP/2] [1] [user-agent: curl/8.7.1]
* [HTTP/2] [1] [accept: */*]
> GET /api/x402/info HTTP/2
> Host: bottube.ai
> User-Agent: curl/8.7.1
> Accept: */*
> 
* Request completely sent off
< HTTP/2 200 
< server: nginx/1.18.0 (Ubuntu)
< date: Sun, 06 Sep 2026 02:10:15 GMT
< content-type: application/json
< content-length: 586
< set-cookie: _bt_vid=eb9042b5ddc1679e35d0126c0f6d0747; Expires=Mon, 06 Sep 2027 02:10:15 GMT; Max-Age=31536000; Secure; HttpOnly; Path=/; SameSite=Lax
< x-content-type-options: nosniff
< x-xss-protection: 1; mode=block
< referrer-policy: strict-origin-when-cross-origin
< permissions-policy: camera=(), microphone=(), geolocation=()
< strict-transport-security: max-age=31536000; includeSubDomains
< access-control-allow-origin: *
< access-control-allow-methods: GET, POST, OPTIONS
< access-control-allow-headers: Content-Type, X-API-Key, Authorization
< vary: Cookie
< set-cookie: session=eyJjc3JmX3Rva2VuIjoiMmE1YjYyNzJiMGFjOWJmODc3MTRkNjY0MWM5MDdhZjMzMGY1MmY3ZjM3NTNkNjU4NDQwMTk4ZDEzY2Q5ZTIzMyJ9.apzLhw._PL1crM-YjbnvBxIYh3rCSVnqq4; Secure; HttpOnly; Path=/; SameSite=Lax
< strict-transport-security: max-age=31536000; includeSubDomains
< 
{ [586 bytes data]
* Connection #0 to host bottube.ai left intact

--- STDOUT (response body) ---
{"facilitator":"https://x402-facilitator.cdp.coinbase.com","network":"eip155:8453","payment_token":"0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913","premium_endpoints":[{"path":"/api/premium/videos","price_usdc":"10000"},{"path":"/api/premium/analytics/<agent>","price_usdc":"10000"},{"path":"/api/premium/trending/export","price_usdc":"5000"}],"pricing_mode":"paid","treasury":"0x008097344A4C6E49401f2b6b9BAA4881b702e0fa","wallet_endpoints":[{"methods":["GET","POST"],"path":"/api/agents/me/coinbase-wallet"}],"wrtc_token":"0x5683C10596AaA09AD7F4eF13CAB94b9b74A669c6","x402_enabled":true}
```

---

## Row 2: GET https://bottube.ai/api/premium/videos

**Description**: Expected 402 Payment Required - Bulk video data export

```text
COMMAND: curl -sv https://bottube.ai/api/premium/videos

--- STDERR (curl verbose trace) ---
* Host bottube.ai:443 was resolved.
* IPv6: (none)
* IPv4: 50.28.86.153
*   Trying 50.28.86.153:443...
* Connected to bottube.ai (50.28.86.153) port 443
* ALPN: curl offers h2,http/1.1
* (304) (OUT), TLS handshake, Client hello (1):
} [315 bytes data]
*  CAfile: /etc/ssl/cert.pem
*  CApath: none
* (304) (IN), TLS handshake, Server hello (2):
{ [122 bytes data]
* (304) (IN), TLS handshake, Unknown (8):
{ [19 bytes data]
* (304) (IN), TLS handshake, Certificate (11):
{ [4079 bytes data]
* (304) (IN), TLS handshake, CERT verify (15):
{ [264 bytes data]
* (304) (IN), TLS handshake, Finished (20):
{ [52 bytes data]
* (304) (OUT), TLS handshake, Finished (20):
} [52 bytes data]
* SSL connection using TLSv1.3 / AEAD-AES256-GCM-SHA384 / [blank] / UNDEF
* ALPN: server accepted h2
* Server certificate:
*  subject: CN=bottube.ai
*  start date: Jul 30 14:06:52 2026 GMT
*  expire date: Oct 28 14:06:51 2026 GMT
*  subjectAltName: host "bottube.ai" matched cert's "bottube.ai"
*  issuer: C=US; O=Let's Encrypt; CN=YR2
*  SSL certificate verify ok.
* using HTTP/2
* [HTTP/2] [1] OPENED stream for https://bottube.ai/api/premium/videos
* [HTTP/2] [1] [:method: GET]
* [HTTP/2] [1] [:scheme: https]
* [HTTP/2] [1] [:authority: bottube.ai]
* [HTTP/2] [1] [:path: /api/premium/videos]
* [HTTP/2] [1] [user-agent: curl/8.7.1]
* [HTTP/2] [1] [accept: */*]
> GET /api/premium/videos HTTP/2
> Host: bottube.ai
> User-Agent: curl/8.7.1
> Accept: */*
> 
* Request completely sent off
< HTTP/2 402 
< server: nginx/1.18.0 (Ubuntu)
< date: Sun, 06 Sep 2026 02:10:15 GMT
< content-type: application/json
< content-length: 539
< strict-transport-security: max-age=31536000; includeSubDomains
< 
{ [539 bytes data]
* Connection #0 to host bottube.ai left intact

--- STDOUT (response body) ---
{"x402Version": 1, "accepts": [{"scheme": "exact", "network": "base", "maxAmountRequired": "10000000000", "resource": "http://bottube.ai/api/premium/videos", "description": "Bulk video data export", "mimeType": "", "outputSchema": {"input": {"type": "http", "method": "GET", "discoverable": true}, "output": null}, "payTo": "0x008097344A4C6E49401f2b6b9BAA4881b702e0fa", "maxTimeoutSeconds": 60, "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", "extra": {"name": "USD Coin", "version": "2"}}], "error": "No X-PAYMENT header provided"}
```

---

## Row 3: GET https://bottube.ai/api/premium/analytics/sophia-elya

**Description**: Expected 402 Payment Required - Agent performance metrics

```text
COMMAND: curl -sv https://bottube.ai/api/premium/analytics/sophia-elya

--- STDERR (curl verbose trace) ---
* Host bottube.ai:443 was resolved.
* IPv6: (none)
* IPv4: 50.28.86.153
*   Trying 50.28.86.153:443...
* Connected to bottube.ai (50.28.86.153) port 443
* ALPN: curl offers h2,http/1.1
* (304) (OUT), TLS handshake, Client hello (1):
} [315 bytes data]
*  CAfile: /etc/ssl/cert.pem
*  CApath: none
* (304) (IN), TLS handshake, Server hello (2):
{ [122 bytes data]
* (304) (IN), TLS handshake, Unknown (8):
{ [19 bytes data]
* (304) (IN), TLS handshake, Certificate (11):
{ [4079 bytes data]
* (304) (IN), TLS handshake, CERT verify (15):
{ [264 bytes data]
* (304) (IN), TLS handshake, Finished (20):
{ [52 bytes data]
* (304) (OUT), TLS handshake, Finished (20):
} [52 bytes data]
* SSL connection using TLSv1.3 / AEAD-AES256-GCM-SHA384 / [blank] / UNDEF
* ALPN: server accepted h2
* Server certificate:
*  subject: CN=bottube.ai
*  start date: Jul 30 14:06:52 2026 GMT
*  expire date: Oct 28 14:06:51 2026 GMT
*  subjectAltName: host "bottube.ai" matched cert's "bottube.ai"
*  issuer: C=US; O=Let's Encrypt; CN=YR2
*  SSL certificate verify ok.
* using HTTP/2
* [HTTP/2] [1] OPENED stream for https://bottube.ai/api/premium/analytics/sophia-elya
* [HTTP/2] [1] [:method: GET]
* [HTTP/2] [1] [:scheme: https]
* [HTTP/2] [1] [:authority: bottube.ai]
* [HTTP/2] [1] [:path: /api/premium/analytics/sophia-elya]
* [HTTP/2] [1] [user-agent: curl/8.7.1]
* [HTTP/2] [1] [accept: */*]
> GET /api/premium/analytics/sophia-elya HTTP/2
> Host: bottube.ai
> User-Agent: curl/8.7.1
> Accept: */*
> 
* Request completely sent off
< HTTP/2 402 
< server: nginx/1.18.0 (Ubuntu)
< date: Sun, 06 Sep 2026 02:10:15 GMT
< content-type: application/json
< content-length: 552
< strict-transport-security: max-age=31536000; includeSubDomains
< 
{ [552 bytes data]
* Connection #0 to host bottube.ai left intact

--- STDOUT (response body) ---
{"x402Version": 1, "accepts": [{"scheme": "exact", "network": "base", "maxAmountRequired": "10000000000", "resource": "http://bottube.ai/api/premium/analytics/sophia-elya", "description": "Deep agent analytics", "mimeType": "", "outputSchema": {"input": {"type": "http", "method": "GET", "discoverable": true}, "output": null}, "payTo": "0x008097344A4C6E49401f2b6b9BAA4881b702e0fa", "maxTimeoutSeconds": 60, "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", "extra": {"name": "USD Coin", "version": "2"}}], "error": "No X-PAYMENT header provided"}
```

---

## Row 4: GET https://bottube.ai/api/premium/trending/export

**Description**: Expected 402 Payment Required - Trending video export

```text
COMMAND: curl -sv https://bottube.ai/api/premium/trending/export

--- STDERR (curl verbose trace) ---
* Host bottube.ai:443 was resolved.
* IPv6: (none)
* IPv4: 50.28.86.153
*   Trying 50.28.86.153:443...
* Connected to bottube.ai (50.28.86.153) port 443
* ALPN: curl offers h2,http/1.1
* (304) (OUT), TLS handshake, Client hello (1):
} [315 bytes data]
*  CAfile: /etc/ssl/cert.pem
*  CApath: none
* (304) (IN), TLS handshake, Server hello (2):
{ [122 bytes data]
* (304) (IN), TLS handshake, Unknown (8):
{ [19 bytes data]
* (304) (IN), TLS handshake, Certificate (11):
{ [4079 bytes data]
* (304) (IN), TLS handshake, CERT verify (15):
{ [264 bytes data]
* (304) (IN), TLS handshake, Finished (20):
{ [52 bytes data]
* (304) (OUT), TLS handshake, Finished (20):
} [52 bytes data]
* SSL connection using TLSv1.3 / AEAD-AES256-GCM-SHA384 / [blank] / UNDEF
* ALPN: server accepted h2
* Server certificate:
*  subject: CN=bottube.ai
*  start date: Jul 30 14:06:52 2026 GMT
*  expire date: Oct 28 14:06:51 2026 GMT
*  subjectAltName: host "bottube.ai" matched cert's "bottube.ai"
*  issuer: C=US; O=Let's Encrypt; CN=YR2
*  SSL certificate verify ok.
* using HTTP/2
* [HTTP/2] [1] OPENED stream for https://bottube.ai/api/premium/trending/export
* [HTTP/2] [1] [:method: GET]
* [HTTP/2] [1] [:scheme: https]
* [HTTP/2] [1] [:authority: bottube.ai]
* [HTTP/2] [1] [:path: /api/premium/trending/export]
* [HTTP/2] [1] [user-agent: curl/8.7.1]
* [HTTP/2] [1] [accept: */*]
> GET /api/premium/trending/export HTTP/2
> Host: bottube.ai
> User-Agent: curl/8.7.1
> Accept: */*
> 
* Request completely sent off
< HTTP/2 402 
< server: nginx/1.18.0 (Ubuntu)
< date: Sun, 06 Sep 2026 02:10:15 GMT
< content-type: application/json
< content-length: 545
< strict-transport-security: max-age=31536000; includeSubDomains
< 
{ [545 bytes data]
* Connection #0 to host bottube.ai left intact

--- STDOUT (response body) ---
{"x402Version": 1, "accepts": [{"scheme": "exact", "network": "base", "maxAmountRequired": "5000000000", "resource": "http://bottube.ai/api/premium/trending/export", "description": "Trending data export", "mimeType": "", "outputSchema": {"input": {"type": "http", "method": "GET", "discoverable": true}, "output": null}, "payTo": "0x008097344A4C6E49401f2b6b9BAA4881b702e0fa", "maxTimeoutSeconds": 60, "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", "extra": {"name": "USD Coin", "version": "2"}}], "error": "No X-PAYMENT header provided"}
```

---

## Row 5: POST https://bottube.ai/api/agents/me/coinbase-wallet

**Description**: Expected 401 Unauthorized - Agent wallet link without API key

```text
COMMAND: curl -sv -X POST https://bottube.ai/api/agents/me/coinbase-wallet

--- STDERR (curl verbose trace) ---
* Host bottube.ai:443 was resolved.
* IPv6: (none)
* IPv4: 50.28.86.153
*   Trying 50.28.86.153:443...
* Connected to bottube.ai (50.28.86.153) port 443
* ALPN: curl offers h2,http/1.1
* (304) (OUT), TLS handshake, Client hello (1):
} [315 bytes data]
*  CAfile: /etc/ssl/cert.pem
*  CApath: none
* (304) (IN), TLS handshake, Server hello (2):
{ [122 bytes data]
* (304) (IN), TLS handshake, Unknown (8):
{ [19 bytes data]
* (304) (IN), TLS handshake, Certificate (11):
{ [4079 bytes data]
* (304) (IN), TLS handshake, CERT verify (15):
{ [264 bytes data]
* (304) (IN), TLS handshake, Finished (20):
{ [52 bytes data]
* (304) (OUT), TLS handshake, Finished (20):
} [52 bytes data]
* SSL connection using TLSv1.3 / AEAD-AES256-GCM-SHA384 / [blank] / UNDEF
* ALPN: server accepted h2
* Server certificate:
*  subject: CN=bottube.ai
*  start date: Jul 30 14:06:52 2026 GMT
*  expire date: Oct 28 14:06:51 2026 GMT
*  subjectAltName: host "bottube.ai" matched cert's "bottube.ai"
*  issuer: C=US; O=Let's Encrypt; CN=YR2
*  SSL certificate verify ok.
* using HTTP/2
* [HTTP/2] [1] OPENED stream for https://bottube.ai/api/agents/me/coinbase-wallet
* [HTTP/2] [1] [:method: POST]
* [HTTP/2] [1] [:scheme: https]
* [HTTP/2] [1] [:authority: bottube.ai]
* [HTTP/2] [1] [:path: /api/agents/me/coinbase-wallet]
* [HTTP/2] [1] [user-agent: curl/8.7.1]
* [HTTP/2] [1] [accept: */*]
> POST /api/agents/me/coinbase-wallet HTTP/2
> Host: bottube.ai
> User-Agent: curl/8.7.1
> Accept: */*
> 
* Request completely sent off
< HTTP/2 401 
< server: nginx/1.18.0 (Ubuntu)
< date: Sun, 06 Sep 2026 02:10:16 GMT
< content-type: application/json
< content-length: 29
< set-cookie: _bt_vid=c5084024c03e162ba47979d040873ee7; Expires=Mon, 06 Sep 2027 02:10:16 GMT; Max-Age=31536000; Secure; HttpOnly; Path=/; SameSite=Lax
< x-content-type-options: nosniff
< x-xss-protection: 1; mode=block
< referrer-policy: strict-origin-when-cross-origin
< permissions-policy: camera=(), microphone=(), geolocation=()
< strict-transport-security: max-age=31536000; includeSubDomains
< access-control-allow-origin: *
< access-control-allow-methods: GET, POST, OPTIONS
< access-control-allow-headers: Content-Type, X-API-Key, Authorization
< vary: Cookie
< set-cookie: session=.eJwFwcENgDAIAMBdmIAWWsBlDK3wMdFE_Rl39-6FeV-5PuceByygm3sgKxOGYVbRNkjMfbaS6J2GSBQ26yWqkXAbQ6hykqGQTvh-16wWig.apzLiA.R7jnlJ66CkKj3Hn0wm3VeScGbMc; Secure; HttpOnly; Path=/; SameSite=Lax
< strict-transport-security: max-age=31536000; includeSubDomains
< 
{ [29 bytes data]
* Connection #0 to host bottube.ai left intact

--- STDOUT (response body) ---
{"error":"API key required"}
```

---

## Row 6: GET https://rustchain.org/wallet/swap-info

**Description**: Expected 200 OK - Aerodrome DEX swap metadata

```text
COMMAND: curl -sv https://rustchain.org/wallet/swap-info

--- STDERR (curl verbose trace) ---
* Host rustchain.org:443 was resolved.
* IPv6: (none)
* IPv4: 50.28.86.131
*   Trying 50.28.86.131:443...
* Connected to rustchain.org (50.28.86.131) port 443
* ALPN: curl offers h2,http/1.1
* (304) (OUT), TLS handshake, Client hello (1):
} [318 bytes data]
*  CAfile: /etc/ssl/cert.pem
*  CApath: none
* (304) (IN), TLS handshake, Server hello (2):
{ [122 bytes data]
* (304) (IN), TLS handshake, Unknown (8):
{ [19 bytes data]
* (304) (IN), TLS handshake, Certificate (11):
{ [4086 bytes data]
* (304) (IN), TLS handshake, CERT verify (15):
{ [264 bytes data]
* (304) (IN), TLS handshake, Finished (20):
{ [36 bytes data]
* (304) (OUT), TLS handshake, Finished (20):
} [36 bytes data]
* SSL connection using TLSv1.3 / AEAD-CHACHA20-POLY1305-SHA256 / [blank] / UNDEF
* ALPN: server accepted h2
* Server certificate:
*  subject: CN=rustchain.org
*  start date: Aug 11 21:38:54 2026 GMT
*  expire date: Nov  9 21:38:53 2026 GMT
*  subjectAltName: host "rustchain.org" matched cert's "rustchain.org"
*  issuer: C=US; O=Let's Encrypt; CN=YR2
*  SSL certificate verify ok.
* using HTTP/2
* [HTTP/2] [1] OPENED stream for https://rustchain.org/wallet/swap-info
* [HTTP/2] [1] [:method: GET]
* [HTTP/2] [1] [:scheme: https]
* [HTTP/2] [1] [:authority: rustchain.org]
* [HTTP/2] [1] [:path: /wallet/swap-info]
* [HTTP/2] [1] [user-agent: curl/8.7.1]
* [HTTP/2] [1] [accept: */*]
> GET /wallet/swap-info HTTP/2
> Host: rustchain.org
> User-Agent: curl/8.7.1
> Accept: */*
> 
* Request completely sent off
< HTTP/2 200 
< server: nginx
< date: Sun, 06 Sep 2026 02:10:16 GMT
< content-type: application/json
< content-length: 381
< x-request-id: 72556d5792a341ada268cc5bfd5cf908
< content-security-policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com; img-src 'self' data: https://img.shields.io; connect-src 'self' https://raw.githubusercontent.com
< referrer-policy: strict-origin-when-cross-origin
< strict-transport-security: max-age=31536000; includeSubDomains
< x-content-type-options: nosniff
< x-frame-options: DENY
< x-frame-options: SAMEORIGIN
< x-content-type-options: nosniff
< x-rustchain: Proof-of-Antiquity
< strict-transport-security: max-age=31536000; includeSubDomains
< permissions-policy: camera=(), microphone=(), geolocation=()
< content-security-policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data: https:; font-src 'self' https://fonts.gstatic.com; connect-src 'self' https://rustchain.org https://api.github.com https://50.28.86.131 https://swarmhub.onrender.com https://bottube.ai; object-src 'none'; base-uri 'self'
< access-control-allow-origin: *
< access-control-allow-methods: POST, GET, OPTIONS
< access-control-allow-headers: Content-Type, Authorization, X-Admin-Key
< 
{ [381 bytes data]
* Connection #0 to host rustchain.org left intact

--- STDOUT (response body) ---
{"aerodrome_pool":"0x4C2A0b915279f0C22EA766D58F9B815Ded2d2A3F","network":"Base (eip155:8453)","reference_price_usd":0.1,"swap_url":"https://aerodrome.finance/swap?from=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913&to=0x5683C10596AaA09AD7F4eF13CAB94b9b74A669c6","usdc_contract":"0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913","wrtc_contract":"0x5683C10596AaA09AD7F4eF13CAB94b9b74A669c6"}
```

---

## Row 7a: GET https://rustchain.org/beacon/api/x402/status

**Description**: Expected 404 Not Found - Deprecated Beacon status endpoint

```text
COMMAND: curl -sv https://rustchain.org/beacon/api/x402/status

--- STDERR (curl verbose trace) ---
* Host rustchain.org:443 was resolved.
* IPv6: (none)
* IPv4: 50.28.86.131
*   Trying 50.28.86.131:443...
* Connected to rustchain.org (50.28.86.131) port 443
* ALPN: curl offers h2,http/1.1
* (304) (OUT), TLS handshake, Client hello (1):
} [318 bytes data]
*  CAfile: /etc/ssl/cert.pem
*  CApath: none
* (304) (IN), TLS handshake, Server hello (2):
{ [122 bytes data]
* (304) (IN), TLS handshake, Unknown (8):
{ [19 bytes data]
* (304) (IN), TLS handshake, Certificate (11):
{ [4086 bytes data]
* (304) (IN), TLS handshake, CERT verify (15):
{ [264 bytes data]
* (304) (IN), TLS handshake, Finished (20):
{ [36 bytes data]
* (304) (OUT), TLS handshake, Finished (20):
} [36 bytes data]
* SSL connection using TLSv1.3 / AEAD-CHACHA20-POLY1305-SHA256 / [blank] / UNDEF
* ALPN: server accepted h2
* Server certificate:
*  subject: CN=rustchain.org
*  start date: Aug 11 21:38:54 2026 GMT
*  expire date: Nov  9 21:38:53 2026 GMT
*  subjectAltName: host "rustchain.org" matched cert's "rustchain.org"
*  issuer: C=US; O=Let's Encrypt; CN=YR2
*  SSL certificate verify ok.
* using HTTP/2
* [HTTP/2] [1] OPENED stream for https://rustchain.org/beacon/api/x402/status
* [HTTP/2] [1] [:method: GET]
* [HTTP/2] [1] [:scheme: https]
* [HTTP/2] [1] [:authority: rustchain.org]
* [HTTP/2] [1] [:path: /beacon/api/x402/status]
* [HTTP/2] [1] [user-agent: curl/8.7.1]
* [HTTP/2] [1] [accept: */*]
> GET /beacon/api/x402/status HTTP/2
> Host: rustchain.org
> User-Agent: curl/8.7.1
> Accept: */*
> 
* Request completely sent off
< HTTP/2 404 
< server: nginx
< date: Sun, 06 Sep 2026 02:10:16 GMT
< content-type: text/html; charset=utf-8
< content-length: 207
< access-control-allow-origin: *
< access-control-allow-methods: POST, GET, PATCH, OPTIONS
< access-control-allow-headers: Content-Type, Authorization
< 
{ [207 bytes data]
* Connection #0 to host rustchain.org left intact

--- STDOUT (response body) ---
<!doctype html>
<html lang=en>
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>
```

---

## Row 7b: GET https://rustchain.org/beacon/api/premium/reputation

**Description**: Expected 404 Not Found - Deprecated Beacon reputation endpoint

```text
COMMAND: curl -sv https://rustchain.org/beacon/api/premium/reputation

--- STDERR (curl verbose trace) ---
* Host rustchain.org:443 was resolved.
* IPv6: (none)
* IPv4: 50.28.86.131
*   Trying 50.28.86.131:443...
* Connected to rustchain.org (50.28.86.131) port 443
* ALPN: curl offers h2,http/1.1
* (304) (OUT), TLS handshake, Client hello (1):
} [318 bytes data]
*  CAfile: /etc/ssl/cert.pem
*  CApath: none
* (304) (IN), TLS handshake, Server hello (2):
{ [122 bytes data]
* (304) (IN), TLS handshake, Unknown (8):
{ [19 bytes data]
* (304) (IN), TLS handshake, Certificate (11):
{ [4086 bytes data]
* (304) (IN), TLS handshake, CERT verify (15):
{ [264 bytes data]
* (304) (IN), TLS handshake, Finished (20):
{ [36 bytes data]
* (304) (OUT), TLS handshake, Finished (20):
} [36 bytes data]
* SSL connection using TLSv1.3 / AEAD-CHACHA20-POLY1305-SHA256 / [blank] / UNDEF
* ALPN: server accepted h2
* Server certificate:
*  subject: CN=rustchain.org
*  start date: Aug 11 21:38:54 2026 GMT
*  expire date: Nov  9 21:38:53 2026 GMT
*  subjectAltName: host "rustchain.org" matched cert's "rustchain.org"
*  issuer: C=US; O=Let's Encrypt; CN=YR2
*  SSL certificate verify ok.
* using HTTP/2
* [HTTP/2] [1] OPENED stream for https://rustchain.org/beacon/api/premium/reputation
* [HTTP/2] [1] [:method: GET]
* [HTTP/2] [1] [:scheme: https]
* [HTTP/2] [1] [:authority: rustchain.org]
* [HTTP/2] [1] [:path: /beacon/api/premium/reputation]
* [HTTP/2] [1] [user-agent: curl/8.7.1]
* [HTTP/2] [1] [accept: */*]
> GET /beacon/api/premium/reputation HTTP/2
> Host: rustchain.org
> User-Agent: curl/8.7.1
> Accept: */*
> 
* Request completely sent off
< HTTP/2 404 
< server: nginx
< date: Sun, 06 Sep 2026 02:10:16 GMT
< content-type: text/html; charset=utf-8
< content-length: 207
< access-control-allow-origin: *
< access-control-allow-methods: POST, GET, PATCH, OPTIONS
< access-control-allow-headers: Content-Type, Authorization
< 
{ [207 bytes data]
* Connection #0 to host rustchain.org left intact

--- STDOUT (response body) ---
<!doctype html>
<html lang=en>
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>
```

---

## Row 7c: GET https://rustchain.org/beacon/api/premium/contracts/export

**Description**: Expected 404 Not Found - Deprecated Beacon contracts export

```text
COMMAND: curl -sv https://rustchain.org/beacon/api/premium/contracts/export

--- STDERR (curl verbose trace) ---
* Host rustchain.org:443 was resolved.
* IPv6: (none)
* IPv4: 50.28.86.131
*   Trying 50.28.86.131:443...
* Connected to rustchain.org (50.28.86.131) port 443
* ALPN: curl offers h2,http/1.1
* (304) (OUT), TLS handshake, Client hello (1):
} [318 bytes data]
*  CAfile: /etc/ssl/cert.pem
*  CApath: none
* (304) (IN), TLS handshake, Server hello (2):
{ [122 bytes data]
* (304) (IN), TLS handshake, Unknown (8):
{ [19 bytes data]
* (304) (IN), TLS handshake, Certificate (11):
{ [4086 bytes data]
* (304) (IN), TLS handshake, CERT verify (15):
{ [264 bytes data]
* (304) (IN), TLS handshake, Finished (20):
{ [36 bytes data]
* (304) (OUT), TLS handshake, Finished (20):
} [36 bytes data]
* SSL connection using TLSv1.3 / AEAD-CHACHA20-POLY1305-SHA256 / [blank] / UNDEF
* ALPN: server accepted h2
* Server certificate:
*  subject: CN=rustchain.org
*  start date: Aug 11 21:38:54 2026 GMT
*  expire date: Nov  9 21:38:53 2026 GMT
*  subjectAltName: host "rustchain.org" matched cert's "rustchain.org"
*  issuer: C=US; O=Let's Encrypt; CN=YR2
*  SSL certificate verify ok.
* using HTTP/2
* [HTTP/2] [1] OPENED stream for https://rustchain.org/beacon/api/premium/contracts/export
* [HTTP/2] [1] [:method: GET]
* [HTTP/2] [1] [:scheme: https]
* [HTTP/2] [1] [:authority: rustchain.org]
* [HTTP/2] [1] [:path: /beacon/api/premium/contracts/export]
* [HTTP/2] [1] [user-agent: curl/8.7.1]
* [HTTP/2] [1] [accept: */*]
> GET /beacon/api/premium/contracts/export HTTP/2
> Host: rustchain.org
> User-Agent: curl/8.7.1
> Accept: */*
> 
* Request completely sent off
< HTTP/2 404 
< server: nginx
< date: Sun, 06 Sep 2026 02:10:16 GMT
< content-type: text/html; charset=utf-8
< content-length: 207
< access-control-allow-origin: *
< access-control-allow-methods: POST, GET, PATCH, OPTIONS
< access-control-allow-headers: Content-Type, Authorization
< 
{ [207 bytes data]
* Connection #0 to host rustchain.org left intact

--- STDOUT (response body) ---
<!doctype html>
<html lang=en>
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>
```

---

## Defect 1 Reproduction: HTTP 500 Crash on Valid X-PAYMENT

**Description**: Submitting valid EIP-3009 payment header crashes server due to NXDOMAIN facilitator

```text
COMMAND: curl -sv -H "X-PAYMENT: <base64_payload>" https://bottube.ai/api/premium/videos

--- STDERR (curl verbose trace) ---
* Host bottube.ai:443 was resolved.
* IPv6: (none)
* IPv4: 50.28.86.153
*   Trying 50.28.86.153:443...
* Connected to bottube.ai (50.28.86.153) port 443
* ALPN: curl offers h2,http/1.1
* (304) (OUT), TLS handshake, Client hello (1):
} [315 bytes data]
*  CAfile: /etc/ssl/cert.pem
*  CApath: none
* (304) (IN), TLS handshake, Server hello (2):
{ [122 bytes data]
* (304) (IN), TLS handshake, Unknown (8):
{ [19 bytes data]
* (304) (IN), TLS handshake, Certificate (11):
{ [4079 bytes data]
* (304) (IN), TLS handshake, CERT verify (15):
{ [264 bytes data]
* (304) (IN), TLS handshake, Finished (20):
{ [52 bytes data]
* (304) (OUT), TLS handshake, Finished (20):
} [52 bytes data]
* SSL connection using TLSv1.3 / AEAD-AES256-GCM-SHA384 / [blank] / UNDEF
* ALPN: server accepted h2
* Server certificate:
*  subject: CN=bottube.ai
*  start date: Jul 30 14:06:52 2026 GMT
*  expire date: Oct 28 14:06:51 2026 GMT
*  subjectAltName: host "bottube.ai" matched cert's "bottube.ai"
*  issuer: C=US; O=Let's Encrypt; CN=YR2
*  SSL certificate verify ok.
* using HTTP/2
* [HTTP/2] [1] OPENED stream for https://bottube.ai/api/premium/videos
* [HTTP/2] [1] [:method: GET]
* [HTTP/2] [1] [:scheme: https]
* [HTTP/2] [1] [:authority: bottube.ai]
* [HTTP/2] [1] [:path: /api/premium/videos]
* [HTTP/2] [1] [user-agent: curl/8.7.1]
* [HTTP/2] [1] [accept: */*]
* [HTTP/2] [1] [x-payment: eyJ4NDAyVmVyc2lvbiI6IDEsICJzY2hlbWUiOiAiZXhhY3QiLCAibmV0d29yayI6ICJiYXNlIiwgInBheWxvYWQiOiB7InNpZ25hdHVyZSI6ICIweGFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWEiLCAiYXV0aG9yaXphdGlvbiI6IHsiZnJvbSI6ICIweEY0NkM5RjZkNzBDNTBCRjgxZWYzNTg4QUI1MjNhOTBhNTk0YTJGODkiLCAidG8iOiAiMHgwMDgwOTczNDRBNEM2RTQ5NDAxZjJiNmI5QkFBNDg4MWI3MDJlMGZhIiwgInZhbHVlIjogIjEwMDAwMDAwMDAwIiwgInZhbGlkQWZ0ZXIiOiAiMCIsICJ2YWxpZEJlZm9yZSI6ICIxNzg4NjY0MjIyIiwgIm5vbmNlIjogIjB4N2UzNDAzMjNmMmQwYzJhYjM3MDZkMTY5NDQxMjhhZDIwNDY0ZGZhMzBmMWRmM2QxNjc1MDM0ZmI0Y2U2ZjVmNyJ9fX0=]
> GET /api/premium/videos HTTP/2
> Host: bottube.ai
> User-Agent: curl/8.7.1
> Accept: */*
> X-PAYMENT: eyJ4NDAyVmVyc2lvbiI6IDEsICJzY2hlbWUiOiAiZXhhY3QiLCAibmV0d29yayI6ICJiYXNlIiwgInBheWxvYWQiOiB7InNpZ25hdHVyZSI6ICIweGFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWEiLCAiYXV0aG9yaXphdGlvbiI6IHsiZnJvbSI6ICIweEY0NkM5RjZkNzBDNTBCRjgxZWYzNTg4QUI1MjNhOTBhNTk0YTJGODkiLCAidG8iOiAiMHgwMDgwOTczNDRBNEM2RTQ5NDAxZjJiNmI5QkFBNDg4MWI3MDJlMGZhIiwgInZhbHVlIjogIjEwMDAwMDAwMDAwIiwgInZhbGlkQWZ0ZXIiOiAiMCIsICJ2YWxpZEJlZm9yZSI6ICIxNzg4NjY0MjIyIiwgIm5vbmNlIjogIjB4N2UzNDAzMjNmMmQwYzJhYjM3MDZkMTY5NDQxMjhhZDIwNDY0ZGZhMzBmMWRmM2QxNjc1MDM0ZmI0Y2U2ZjVmNyJ9fX0=
> 
* Request completely sent off
< HTTP/2 500 
< server: nginx/1.18.0 (Ubuntu)
< date: Sun, 06 Sep 2026 02:10:22 GMT
< content-type: text/html; charset=utf-8
< content-length: 265
< strict-transport-security: max-age=31536000; includeSubDomains
< 
{ [265 bytes data]
* Connection #0 to host bottube.ai left intact

--- STDOUT (response body) ---
<!doctype html>
<html lang=en>
<title>500 Internal Server Error</title>
<h1>Internal Server Error</h1>
<p>The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.</p>
```

---

## Defect 3 Reproduction: CAIP-2 Network Identifier Rejection

**Description**: Submitting CAIP-2 network eip155:8453 rejected with No matching payment requirements found

```text
COMMAND: curl -sv -H "X-PAYMENT: <base64_caip2_payload>" https://bottube.ai/api/premium/videos

--- STDERR (curl verbose trace) ---
* Host bottube.ai:443 was resolved.
* IPv6: (none)
* IPv4: 50.28.86.153
*   Trying 50.28.86.153:443...
* Connected to bottube.ai (50.28.86.153) port 443
* ALPN: curl offers h2,http/1.1
* (304) (OUT), TLS handshake, Client hello (1):
} [315 bytes data]
*  CAfile: /etc/ssl/cert.pem
*  CApath: none
* (304) (IN), TLS handshake, Server hello (2):
{ [122 bytes data]
* (304) (IN), TLS handshake, Unknown (8):
{ [19 bytes data]
* (304) (IN), TLS handshake, Certificate (11):
{ [4079 bytes data]
* (304) (IN), TLS handshake, CERT verify (15):
{ [264 bytes data]
* (304) (IN), TLS handshake, Finished (20):
{ [52 bytes data]
* (304) (OUT), TLS handshake, Finished (20):
} [52 bytes data]
* SSL connection using TLSv1.3 / AEAD-AES256-GCM-SHA384 / [blank] / UNDEF
* ALPN: server accepted h2
* Server certificate:
*  subject: CN=bottube.ai
*  start date: Jul 30 14:06:52 2026 GMT
*  expire date: Oct 28 14:06:51 2026 GMT
*  subjectAltName: host "bottube.ai" matched cert's "bottube.ai"
*  issuer: C=US; O=Let's Encrypt; CN=YR2
*  SSL certificate verify ok.
* using HTTP/2
* [HTTP/2] [1] OPENED stream for https://bottube.ai/api/premium/videos
* [HTTP/2] [1] [:method: GET]
* [HTTP/2] [1] [:scheme: https]
* [HTTP/2] [1] [:authority: bottube.ai]
* [HTTP/2] [1] [:path: /api/premium/videos]
* [HTTP/2] [1] [user-agent: curl/8.7.1]
* [HTTP/2] [1] [accept: */*]
* [HTTP/2] [1] [x-payment: eyJ4NDAyVmVyc2lvbiI6IDEsICJzY2hlbWUiOiAiZXhhY3QiLCAibmV0d29yayI6ICJlaXAxNTU6ODQ1MyIsICJwYXlsb2FkIjogeyJzaWduYXR1cmUiOiAiMHhhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhIiwgImF1dGhvcml6YXRpb24iOiB7ImZyb20iOiAiMHhGNDZDOUY2ZDcwQzUwQkY4MWVmMzU4OEFCNTIzYTkwYTU5NGEyRjg5IiwgInRvIjogIjB4MDA4MDk3MzQ0QTRDNkU0OTQwMWYyYjZiOUJBQTQ4ODFiNzAyZTBmYSIsICJ2YWx1ZSI6ICIxMDAwMDAwMDAwMCIsICJ2YWxpZEFmdGVyIjogIjAiLCAidmFsaWRCZWZvcmUiOiAiMTc4ODY2NDIyMiIsICJub25jZSI6ICIweDdlMzQwMzIzZjJkMGMyYWIzNzA2ZDE2OTQ0MTI4YWQyMDQ2NGRmYTMwZjFkZjNkMTY3NTAzNGZiNGNlNmY1ZjcifX19]
> GET /api/premium/videos HTTP/2
> Host: bottube.ai
> User-Agent: curl/8.7.1
> Accept: */*
> X-PAYMENT: eyJ4NDAyVmVyc2lvbiI6IDEsICJzY2hlbWUiOiAiZXhhY3QiLCAibmV0d29yayI6ICJlaXAxNTU6ODQ1MyIsICJwYXlsb2FkIjogeyJzaWduYXR1cmUiOiAiMHhhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhIiwgImF1dGhvcml6YXRpb24iOiB7ImZyb20iOiAiMHhGNDZDOUY2ZDcwQzUwQkY4MWVmMzU4OEFCNTIzYTkwYTU5NGEyRjg5IiwgInRvIjogIjB4MDA4MDk3MzQ0QTRDNkU0OTQwMWYyYjZiOUJBQTQ4ODFiNzAyZTBmYSIsICJ2YWx1ZSI6ICIxMDAwMDAwMDAwMCIsICJ2YWxpZEFmdGVyIjogIjAiLCAidmFsaWRCZWZvcmUiOiAiMTc4ODY2NDIyMiIsICJub25jZSI6ICIweDdlMzQwMzIzZjJkMGMyYWIzNzA2ZDE2OTQ0MTI4YWQyMDQ2NGRmYTMwZjFkZjNkMTY3NTAzNGZiNGNlNmY1ZjcifX19
> 
* Request completely sent off
< HTTP/2 402 
< server: nginx/1.18.0 (Ubuntu)
< date: Sun, 06 Sep 2026 02:10:22 GMT
< content-type: application/json
< content-length: 549
< strict-transport-security: max-age=31536000; includeSubDomains
< 
{ [549 bytes data]
* Connection #0 to host bottube.ai left intact

--- STDOUT (response body) ---
{"x402Version": 1, "accepts": [{"scheme": "exact", "network": "base", "maxAmountRequired": "10000000000", "resource": "http://bottube.ai/api/premium/videos", "description": "Bulk video data export", "mimeType": "", "outputSchema": {"input": {"type": "http", "method": "GET", "discoverable": true}, "output": null}, "payTo": "0x008097344A4C6E49401f2b6b9BAA4881b702e0fa", "maxTimeoutSeconds": 60, "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", "extra": {"name": "USD Coin", "version": "2"}}], "error": "No matching payment requirements found"}
```

---

## Defect 4 Reproduction: X-API-Key Header Ignored by Authenticator

**Description**: Passing X-API-Key rejected with API key required while Bearer reaches key validator

```text
COMMAND: curl -sv -X POST -H "X-API-Key: test_token" https://bottube.ai/api/agents/me/coinbase-wallet

--- STDERR (curl verbose trace) ---
* Host bottube.ai:443 was resolved.
* IPv6: (none)
* IPv4: 50.28.86.153
*   Trying 50.28.86.153:443...
* Connected to bottube.ai (50.28.86.153) port 443
* ALPN: curl offers h2,http/1.1
* (304) (OUT), TLS handshake, Client hello (1):
} [315 bytes data]
*  CAfile: /etc/ssl/cert.pem
*  CApath: none
* (304) (IN), TLS handshake, Server hello (2):
{ [122 bytes data]
* (304) (IN), TLS handshake, Unknown (8):
{ [19 bytes data]
* (304) (IN), TLS handshake, Certificate (11):
{ [4079 bytes data]
* (304) (IN), TLS handshake, CERT verify (15):
{ [264 bytes data]
* (304) (IN), TLS handshake, Finished (20):
{ [52 bytes data]
* (304) (OUT), TLS handshake, Finished (20):
} [52 bytes data]
* SSL connection using TLSv1.3 / AEAD-AES256-GCM-SHA384 / [blank] / UNDEF
* ALPN: server accepted h2
* Server certificate:
*  subject: CN=bottube.ai
*  start date: Jul 30 14:06:52 2026 GMT
*  expire date: Oct 28 14:06:51 2026 GMT
*  subjectAltName: host "bottube.ai" matched cert's "bottube.ai"
*  issuer: C=US; O=Let's Encrypt; CN=YR2
*  SSL certificate verify ok.
* using HTTP/2
* [HTTP/2] [1] OPENED stream for https://bottube.ai/api/agents/me/coinbase-wallet
* [HTTP/2] [1] [:method: POST]
* [HTTP/2] [1] [:scheme: https]
* [HTTP/2] [1] [:authority: bottube.ai]
* [HTTP/2] [1] [:path: /api/agents/me/coinbase-wallet]
* [HTTP/2] [1] [user-agent: curl/8.7.1]
* [HTTP/2] [1] [accept: */*]
* [HTTP/2] [1] [x-api-key: test_token]
> POST /api/agents/me/coinbase-wallet HTTP/2
> Host: bottube.ai
> User-Agent: curl/8.7.1
> Accept: */*
> X-API-Key: test_token
> 
* Request completely sent off
< HTTP/2 401 
< server: nginx/1.18.0 (Ubuntu)
< date: Sun, 06 Sep 2026 02:10:22 GMT
< content-type: application/json
< content-length: 29
< set-cookie: _bt_vid=20725aab4de1e41cb5641af6bcf62815; Expires=Mon, 06 Sep 2027 02:10:22 GMT; Max-Age=31536000; Secure; HttpOnly; Path=/; SameSite=Lax
< x-content-type-options: nosniff
< x-xss-protection: 1; mode=block
< referrer-policy: strict-origin-when-cross-origin
< permissions-policy: camera=(), microphone=(), geolocation=()
< strict-transport-security: max-age=31536000; includeSubDomains
< access-control-allow-origin: *
< access-control-allow-methods: GET, POST, OPTIONS
< access-control-allow-headers: Content-Type, X-API-Key, Authorization
< vary: Cookie
< set-cookie: session=eyJjc3JmX3Rva2VuIjoiMTViMDljM2UxYzc0M2UwODY3M2FkMzBkMmExZTM4NGFmZTIxNzQ3ZmE0ZTNkNzhkODVlNDQxYmY2ZDYxY2E0MiJ9.apzLjg.UVucPLHcvs86ZoVYniS-4J6zUck; Secure; HttpOnly; Path=/; SameSite=Lax
< strict-transport-security: max-age=31536000; includeSubDomains
< 
{ [29 bytes data]
* Connection #0 to host bottube.ai left intact

--- STDOUT (response body) ---
{"error":"API key required"}
```

---
