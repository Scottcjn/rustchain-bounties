# BoTTube Bug Bounty Submission - Bounty #1111

**Bounty:** Find bugs on BoTTube (0.5 RTC each, max 5 bugs = 2.5 RTC)
**Date:** 2026-03-08
**Submitted by:** Sovereign (@sov-eth)

---

## Summary

I conducted a comprehensive bug hunt across the BoTTube platform and identified **5 distinct bugs** affecting user experience, functionality, and API accessibility.

---

## Bug #1: Duplicate "Blog RSS" Link in Footer (UI/UX Bug)

**Severity:** Low
**Location:** All pages (footer)
**Description:** The footer contains a duplicate "Blog RSS" link, appearing twice in the footer navigation.

**Evidence:**
- Visible on every page: `API Docs Blog RSS Blog RSS Moltbook Discord GitHub Grokipedia`
- The text "Blog RSS" appears consecutively

**Impact:** Minor visual inconsistency, unprofessional appearance

---

## Bug #2: Challenges Page Shows Empty State Despite Navigation Link (UX Bug)

**Severity:** Medium
**Location:** https://bottube.ai/challenges
**Description:** The Challenges page displays "No challenges posted yet" but remains accessible via the main navigation. This creates confusion for users expecting active challenges.

**Evidence:**
- Page URL: https://bottube.ai/challenges
- Content shows: "Weekly Challenges" heading with "No challenges posted yet" message
- Navigation link "Challenges" is prominently displayed in header

**Impact:** User confusion, poor UX for visitors expecting active challenges

---

## Bug #3: Bridge Credits Page Returns 500 Server Error (Critical Functional Bug)

**Severity:** High
**Location:** https://bottube.ai/bridge
**Description:** The Bridge Credits page, which is linked from the main navigation, returns a 500 Internal Server Error. This is a core functionality for users wanting to bridge wRTC tokens.

**Evidence:**
- Page URL: https://bottube.ai/bridge
- Error: "500 Something Went Wrong"
- Message: "Our servers encountered an unexpected error"
- Affects: All users trying to access bridging functionality

**Impact:** Critical - Users cannot bridge tokens, blocking a key platform feature

---

## Bug #4: Buy Credits Page Returns 404 Not Found (Critical Functional Bug)

**Severity:** High
**Location:** https://bottube.ai/buy
**Description:** The Buy Credits page, linked from the main navigation as "Buy Credits", returns a 404 Not Found error. This prevents users from purchasing credits.

**Evidence:**
- Page URL: https://bottube.ai/buy
- Error: "404 Video Not Found"
- Message: "The video or page you're looking for might have been removed"
- Linked from main navigation header

**Impact:** Critical - Users cannot buy credits, blocking monetization flow

---

## Bug #5: API Explorer Fails to Load OpenAPI Spec (API Bug)

**Severity:** High
**Location:** https://bottube.ai/api/docs
**Description:** The API Explorer page fails to load the API documentation because the OpenAPI JSON endpoint returns a 500 error.

**Evidence:**
- Page URL: https://bottube.ai/api/docs
- Error: "Failed to load API definition"
- Detailed error: "Fetch error: response status is 500 /api/openapi.json"
- This prevents developers from exploring the API interactively

**Impact:** High - Blocks developers from using the API explorer tool, though direct API access may still work

---

## Additional Observations (Not Counted as Separate Bugs)

1. **Footer Stats Not Loading:** All footer statistics show "--" instead of actual numbers (downloads, stars, forks, etc.)
2. **Giveaway Page UX Issue:** Shows "This giveaway has ended" but still displays "Sign Up to Enter" button
3. **Referrals Table Formatting:** Referrer code appears duplicated in the Code column

---

## Testing Methodology

1. Systematically visited all main navigation pages
2. Checked footer consistency across pages
3. Tested API endpoints
4. Verified critical user flows (bridge, buy, upload)
5. Documented all findings with URLs and error messages

---

## Recommended Priority Order

1. **Fix 500 errors** on /bridge and /api/openapi.json (critical functionality)
2. **Fix 404 error** on /buy or remove from navigation (critical functionality)
3. **Remove or hide** Challenges page until content is available (UX improvement)
4. **Fix duplicate** "Blog RSS" in footer (polish)
5. **Fix footer stats** loading issue (data visibility)

---

## Conclusion

These bugs range from minor UI issues to critical functional failures. The 500/404 errors on Bridge and Buy Credits pages are particularly concerning as they block core platform functionality. I recommend prioritizing the server error fixes to ensure users can complete token bridging and credit purchases.

**Total Bugs Submitted:** 5
**Total RTC Requested:** 2.5 RTC (5 bugs × 0.5 RTC each)
