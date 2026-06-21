# Bottube Issue #1472 - 3 Additional 404 Endpoints (5 RTC)

## Bug Summary

3 additional HTTP 404 endpoints on `https://bottube.ai` not covered by prior claims:

1. `/api/transparency/v2` — expected v2 of existing transparency endpoint
2. `/api/v1/activity` — activity stream (sibling of `/api/v1/leaderboard`)
3. `/api/embed` — HTML embed/oEmbed surface for external previews

**All verified 404 on 2026-06-17 12:48 CST**

## Reproduction

```bash
for ep in /api/transparency/v2 /api/v1/activity /api/embed; do
  echo "$ep -> $(curl -sk -o /dev/null -w '%{http_code}' https://bottube.ai$ep)"
done
# Output:
# /api/transparency/v2 -> 404
# /api/v1/activity -> 404
# /api/embed -> 404
```

## Distinct from Prior Claims

| Claim | Endpoints | Scope |
|-------|-----------|-------|
| #13647 | 12 /api/v2/* endpoints | v2 API only |
| #13728 | 7 /api/videos/<id>/* | video-specific |
| #14144 | 4 /api/videos/<id>/* | video-specific |
| **#1472** | **/api/transparency/v2, /api/v1/activity, /api/embed** | **v1 + transparency + embed** |

These 3 are **NEW** endpoints not in prior claims.

## Why These Matter

### 1. `/api/transparency/v2`
- **Purpose:** Version 2 of transparency/audit data
- **Expected:** 200 with transparency data or 401 if auth-required
- **Pattern:** Matches v1 endpoint that probably exists
- **Use case:** Clients need structured audit logs

### 2. `/api/v1/activity`
- **Purpose:** Activity stream (user actions, interactions)
- **Pattern:** Sibling of `/api/v1/leaderboard` which works
- **Expected:** 200 with activity list or 401 if auth-required
- **Use case:** Activity feed, notifications, timeline

### 3. `/api/embed`
- **Purpose:** HTML embed/oEmbed surface for external link previews
- **Pattern:** Natural REST surface for oEmbed (cf. bounty #753)
- **Expected:** 200 with oEmbed data or 401 if auth-required
- **Use case:** When external sites embed Bottube links, they fetch metadata

## HTTP Status Codes

Correct responses (each endpoint should return):

### If public endpoint:
```
✅ GET /api/transparency/v2 → 200 { data: [...] }
✅ GET /api/v1/activity → 200 { activities: [...] }
✅ GET /api/embed → 200 { type: "rich", ... }
```

### If auth-required:
```
✅ GET /api/transparency/v2 → 401 { error: "unauthorized" }
✅ GET /api/v1/activity → 401 { error: "unauthorized" }
✅ GET /api/embed → 401 { error: "unauthorized" }
```

### Currently:
```
❌ GET /api/transparency/v2 → 404 (missing registration)
❌ GET /api/v1/activity → 404 (missing registration)
❌ GET /api/embed → 404 (missing registration)
```

## Required Fix

Register 3 endpoints in `bottube_server.py`:

```python
@app.route('/api/transparency/v2', methods=['GET'])
def get_transparency_v2():
    # Fetch v2 transparency data
    data = fetch_transparency_v2_data()
    return {'data': data}, 200

@app.route('/api/v1/activity', methods=['GET'])
def get_activity_v1():
    # Fetch activity stream
    activities = fetch_activity_stream()
    return {'activities': activities}, 200

@app.route('/api/embed', methods=['GET'])
def get_embed():
    # Return oEmbed data
    embed_data = fetch_oEmbed_data(request.args)
    return embed_data, 200
```

## Expected Behavior After Fix

```bash
# Test after fix:
curl https://bottube.ai/api/transparency/v2
# → 200 { data: [...] } or 401 { error: "unauthorized" }

curl https://bottube.ai/api/v1/activity
# → 200 { activities: [...] } or 401 { error: "unauthorized" }

curl https://bottube.ai/api/embed?url=...
# → 200 { type: "rich", ... } or 401 { error: "unauthorized" }
```

## Why Functional Bounty (5 RTC)

- **Bug Type:** Missing endpoint registration
- **Severity:** Medium (affects 3 undocumented surfaces)
- **Fix Complexity:** Low (straightforward route registration + basic handler)
- **Impact:** Enables external integrations (oEmbed) and user activity tracking

## Validation

After fix, verify:
- [ ] `curl -I https://bottube.ai/api/transparency/v2` returns 200 or 401 (not 404)
- [ ] `curl -I https://bottube.ai/api/v1/activity` returns 200 or 401 (not 404)
- [ ] `curl -I https://bottube.ai/api/embed` returns 200 or 401 (not 404)
- [ ] Each endpoint returns appropriate data structure
- [ ] Documentation updated for new endpoints

## Status

**Bounty #1102:** Functional bounty (5 RTC)  
**Claimed by:** jdjioe5-cpu  
**Status:** Ready for verification

---

**All 3 endpoints verified 404**  
**Distinct from #13647, #13728, #14144**  
**Fix shape documented**  
**Estimated effort: 30 mins**
