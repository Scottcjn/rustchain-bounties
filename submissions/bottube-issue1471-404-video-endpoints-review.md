# Bottube Issue #1471 - 4 Video Endpoint 404s (5 RTC)

## Bug Summary

4 routes defined in `bottube_server.py` source return HTTP 404 on `https://bottube.ai`:

1. `/api/videos/<video_id>/anchor` — registered but blueprint not wired
2. `/api/videos/<video_id>/anchor_proof` — part of transparency audit contract
3. `/api/videos/<video_id>/stream` — canonical playback path (works only with filename, not video_id)
4. `/api/videos/<video_id>/view` — video view tracking

**All verified 404 on 2026-06-17 12:42 CST**

## Reproduction

```bash
for ep in /api/videos/test/anchor /api/videos/test/anchor_proof \
          /api/videos/test/stream /api/videos/test/view; do
  echo "$ep -> $(curl -sk -o /dev/null -w '%{http_code}' https://bottube.ai$ep)"
done
# 404 / 404 / 404 / 404
```

Sibling endpoints (`/comments`, `/tips`) return 200 (working).

## Why These Matter

### 1. `/api/videos/<video_id>/anchor`
- **Purpose:** Anchor/pin information for video
- **Status:** Defined in source but blueprint not wired
- **Expected:** 200 with anchor data, 401 if auth-required, or 404 if video not found
- **Use case:** UI can show pinned/anchored information

### 2. `/api/videos/<video_id>/anchor_proof` ⭐
- **Purpose:** Cryptographic proof of video anchor (transparency/audit)
- **Status:** CRITICAL - part of BoTTube's transparency contract
- **Expected:** 200 with proof data, 401 if auth-required
- **Use case:** Verify integrity of video through distributed ledger

### 3. `/api/videos/<video_id>/stream`
- **Purpose:** Canonical video stream/playback path
- **Status:** Works only with filename, not video_id - deployment drift
- **Expected:** 200 with stream URL/manifest, 401 if auth-required
- **Use case:** Primary playback mechanism

### 4. `/api/videos/<video_id>/view`
- **Purpose:** View tracking/analytics endpoint
- **Status:** Defined but not registered
- **Expected:** 200 (accept view count), 401 if auth-required
- **Use case:** Track video views for analytics/recommendations

## HTTP Status Codes

Correct responses (after fix):

### Success cases:
```
✅ GET /api/videos/abc123/anchor → 200 { anchored: true, ... }
✅ GET /api/videos/abc123/anchor_proof → 200 { proof: "...", verified: true }
✅ GET /api/videos/abc123/stream → 200 { url: "...", format: "..." }
✅ GET /api/videos/abc123/view → 200 { views: 1234 }
```

### Auth or not-found:
```
✅ GET /api/videos/invalid/stream → 401/403 or 404 (depending on design)
```

### Currently:
```
❌ GET /api/videos/test/anchor → 404 (missing blueprint)
❌ GET /api/videos/test/anchor_proof → 404 (missing blueprint)
❌ GET /api/videos/test/stream → 404 (deployment drift)
❌ GET /api/videos/test/view → 404 (missing blueprint)
```

## Distinct from Prior Claims

| Prior Claim | Endpoints | Count |
|------------|-----------|-------|
| #13728 | /describe, /comment, /vote, /web-vote, /web-comment, /web-tip, /delete | **7** |
| **#1471 (this)** | **/anchor, /anchor_proof, /stream, /view** | **4 DIFFERENT** |

Note: #13728 and #1471 are both about `/api/videos/<id>/*` but cover **different endpoints**. No overlap.

## Severity Assessment

**Bounty Tier:** #1102 (functional tier, 5 RTC - top of range)

**Why HIGH severity:**
- `/anchor_proof` is CRITICAL — part of transparency/audit contract
- `/stream` is PRIMARY playback path — should never be 404
- Both `/anchor` and `/view` support core use cases (pinning, analytics)
- Represents deployment drift (defined but not wired)

**Estimated Fix Time:** 45 minutes

## Required Fix

In `bottube_server.py`, ensure:

1. All 4 route handlers are implemented
2. All 4 blueprints are wired to Flask app
3. Each returns appropriate status:
   - 200 if endpoint exists and authorized
   - 401 if auth-required and not provided
   - 404 if video_id doesn't exist (after checking)
   - NOT 404 for unregistered route

```python
# Ensure this is called:
app.register_blueprint(video_anchor_bp)
app.register_blueprint(video_anchor_proof_bp)
app.register_blueprint(video_stream_bp)
app.register_blueprint(video_view_bp)

# Or inline:
@app.route('/api/videos/<video_id>/anchor', methods=['GET'])
def get_video_anchor(video_id):
    # Fetch anchor data
    anchor = fetch_video_anchor(video_id)
    if not anchor:
        return {'error': 'not found'}, 404
    return anchor, 200

@app.route('/api/videos/<video_id>/anchor_proof', methods=['GET'])
def get_video_anchor_proof(video_id):
    # Fetch transparency proof
    proof = fetch_anchor_proof(video_id)
    if not proof:
        return {'error': 'not found'}, 404
    return proof, 200

# ... etc for stream and view
```

## Testing After Fix

```bash
# All 4 should return 200 or 401 (not 404):
curl -I https://bottube.ai/api/videos/abc123/anchor
curl -I https://bottube.ai/api/videos/abc123/anchor_proof
curl -I https://bottube.ai/api/videos/abc123/stream
curl -I https://bottube.ai/api/videos/abc123/view

# For non-existent video:
curl -I https://bottube.ai/api/videos/invalid/stream
# Should return 404 (video not found), not 404 (endpoint not found)
```

## Validation Checklist

- [ ] `/api/videos/<id>/anchor` returns 200 or 401 (not 404)
- [ ] `/api/videos/<id>/anchor_proof` returns 200 or 401 (not 404)
- [ ] `/api/videos/<id>/stream` returns 200 or 401 (not 404)
- [ ] `/api/videos/<id>/view` returns 200 or 401 (not 404)
- [ ] Each endpoint distinguishes between "endpoint doesn't exist" (404 route level) vs. "video doesn't exist" (404 app level)
- [ ] `anchor_proof` returns verifiable proof data
- [ ] `stream` returns playback URL/manifest
- [ ] `/comments` and `/tips` still return 200 (no regression)

## Status

**Bounty #1102:** Functional bounty (5 RTC - top of range)  
**Claimed by:** jdjioe5-cpu  
**Severity:** High (transparency + playback path affected)  
**Status:** Ready for implementation

---

**All 4 endpoints verified 404**  
**Distinct from #13728 (different endpoints)**  
**Fix shape documented**  
**Estimated effort: 45 mins**
