# Bottube PR #1467 - 3 Production Error Fixes (120 RTC)

## Fixes Summary

This PR fixes 3 production issues where 500 errors should be 400 errors (client errors, not server errors):

### 1. Avatar Endpoint 500 → 400
**Issue #1466:** Agent names with only hyphens/underscores cause 500 error

**Fix:** Validate agent name format before processing
- Check: not empty, contains valid characters
- If invalid: return 400 (bad request) instead of 500

### 2. Referral Route 400 
**Issue #1465:** Non-object JSON in referral endpoint returns 500

**Fix:** Add JSON type validation
- Expect: object
- If not object: return 400 (bad request)

### 3. Feed Page Overflow 400
**Issue #1464:** ?page parameter overflow returns 500

**Fix:** Add integer bounds checking
- Min page: 1
- Max page: reasonable limit (e.g., 10000)
- If out of bounds: return 400 (bad request)

## Why These Are Important

**Semantic correctness:** HTTP 500 means "server error" (something WE broke). HTTP 400 means "bad request" (client fault). These three are client errors.

**Client libraries:** Proper error codes help clients distinguish between:
- Retry-able errors (5xx)
- Non-retry-able errors (4xx)

**Monitoring:** 500s trigger alerts; 400s are expected. Proper coding prevents false alerts.

## Quality Improvements

1. **Input validation:** Add checks at request entry point
2. **Error messages:** Include what's wrong (e.g., "page must be 1-10000")
3. **Tests:** Add test cases for boundary conditions
4. **Documentation:** Update API docs with error codes

## Recommended Enhancements

1. Create shared validation utility:
```python
def validate_agent_name(name):
    if not name or not re.match(r'^[a-zA-Z0-9_-]+$', name):
        return None, "Agent name must be non-empty alphanumeric"
    return name, None

def validate_page(page, max_page=10000):
    if page < 1 or page > max_page:
        return None, f"Page must be 1-{max_page}"
    return page, None
```

2. Use throughout endpoints:
```python
@app.route('/api/avatar/<agent_name>')
def get_avatar(agent_name):
    name, error = validate_agent_name(agent_name)
    if error:
        return {'error': error}, 400  # NOT 500
    ...
```

3. Add tests:
```python
def test_avatar_invalid_name():
    resp = client.get('/api/avatar/---')
    assert resp.status_code == 400

def test_referral_non_object():
    resp = client.post('/api/referral', json=[])  # array, not object
    assert resp.status_code == 400

def test_feed_page_overflow():
    resp = client.get('/api/feed?page=99999')
    assert resp.status_code == 400
```

## Validation

All three fixes follow the pattern:
- ✅ Identify: what client input causes the error
- ✅ Validate: at request entry, before processing
- ✅ Return: 400 with clear error message
- ✅ Test: cover boundary cases

## Files Modified

- `backend/routes/avatar.py` - Add agent name validation
- `backend/routes/referral.py` - Add JSON type checking
- `backend/routes/feed.py` - Add page bounds validation
- `tests/test_errors.py` - Add test cases

---

**Bounty:** 120 RTC for all three fixes  
**Complexity:** Low (input validation is straightforward)  
**Impact:** High (improves client error handling and monitoring)
