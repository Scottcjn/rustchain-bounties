# Accessibility Audit Report — BoTTube UI & RustChain Widgets

**Issue:** [#1618](https://github.com/Scottcjn/rustchain-bounties/issues/1618)
**Audited:** bottube.ai + RustChain widget HTML files in `widgets/`
**Date:** 2026-03-10
**Standard:** WCAG 2.1 Level AA

---

## Summary

This audit identified **12 distinct accessibility issues** across bottube.ai and
the RustChain embeddable widgets. Issues are grouped by category and reference
the applicable WCAG 2.1 success criteria.

---

## 1. Missing ARIA Live Regions on Dynamic Content

**Location:** All three widget HTML files (`rustchain-dashboard-widget.html`,
`rustchain-miner-leaderboard.html`, `rustchain-network-status.html`)

**Problem:** Loading states, error states, and auto-refreshing data sections
toggle visibility via JavaScript (`style.display = 'none'`/`'block'`) without
`aria-live` regions. Screen readers are never notified when content loads, when
errors occur, or when data refreshes every 60 seconds.

**WCAG Criterion:** 4.1.3 Status Messages — status messages must be
programmatically determined through role or properties so they can be presented
to the user by assistive technologies without receiving focus.

**Fix:** Add `role="status"` and `aria-live="polite"` to loading/error/content
containers.

---

## 2. Interactive Cards Without Keyboard Access

**Location:** `rustchain-dashboard-widget.html` — metric cards with
`onclick="window.open(...)"`

**Problem:** Cards that open external links use `<div onclick>` with
`cursor: pointer`. These elements:
- Cannot be focused via Tab key
- Cannot be activated via Enter/Space
- Have no `role="link"` or `tabindex`
- Are invisible to screen readers as interactive elements

**WCAG Criterion:** 2.1.1 Keyboard — all functionality must be operable
through a keyboard interface.

**Fix:** Use `<a>` elements or add `role="link"`, `tabindex="0"`, and
`keydown` handlers for Enter/Space activation.

---

## 3. Tooltip Content Inaccessible to Keyboard and Screen Reader Users

**Location:** `rustchain-dashboard-widget.html` — miner node tooltips

**Problem:** Tooltips appear only on `:hover` CSS state. They are:
- Not reachable via keyboard focus
- Not associated with their trigger via `aria-describedby`
- Hidden with `pointer-events: none` and `opacity: 0`

**WCAG Criterion:** 1.3.1 Info and Relationships — information and
relationships conveyed through presentation must be programmatically
determinable.

**Fix:** Add `tabindex="0"` to miner nodes, show tooltips on `:focus` as well
as `:hover`, and connect via `aria-describedby`.

---

## 4. Decorative Content Not Hidden from Assistive Technology

**Location:** All widget files — emoji icons, spinning refresh icon, animated
status dots

**Problem:** Decorative elements (↻ refresh spinner, status-dot pulsing
animation, emoji miner icons) are exposed to screen readers without meaningful
context. A screen reader would announce "↻" or meaningless Unicode content.

**WCAG Criterion:** 1.1.1 Non-text Content — decorative content must be
implementable in a way that assistive technology can ignore it.

**Fix:** Add `aria-hidden="true"` to decorative elements and provide text
alternatives via `aria-label` on their parent containers.

---

## 5. Missing `aria-sort` on Sortable Table Headers

**Location:** `rustchain-miner-leaderboard.html` — leaderboard table

**Problem:** Table headers that trigger sorting on click (排名, 乘数, 活跃Epoch,
估计收益) use `onclick` handlers and CSS pseudo-elements (`::after` arrows) to
indicate sort direction. The current sort state is never communicated to
assistive technology.

**WCAG Criterion:** 4.1.2 Name, Role, Value — for all user interface
components, the name and role can be programmatically determined; states and
values that can be set by the user can be programmatically set.

**Fix:** Add `aria-sort="ascending"`, `aria-sort="descending"`, or
`aria-sort="none"` attributes and update them in the `sortBy()` function.

---

## 6. Sortable Table Headers Not Keyboard Accessible

**Location:** `rustchain-miner-leaderboard.html` — `<th>` elements with
`onclick`

**Problem:** Sort controls use `onclick` on `<th>` elements. These cannot be
activated by keyboard users because `<th>` is not natively focusable and no
`tabindex` or `keydown` handler is provided.

**WCAG Criterion:** 2.1.1 Keyboard

**Fix:** Add `tabindex="0"`, `role="button"`, and `keydown` handlers for
Enter/Space to sortable headers.

---

## 7. Color-Only Status Indication

**Location:** `rustchain-network-status.html` — status indicator dots

**Problem:** Node health status is communicated solely through colored circles
(green = healthy, yellow = slow, red = down). The `.status-indicator` `<div>`
elements contain no text content and no ARIA labels.

**WCAG Criterion:** 1.4.1 Use of Color — color is not used as the only visual
means of conveying information.

**Fix:** Add `aria-label` with the status text (e.g., "Healthy", "Slow",
"Down") and ensure the adjacent text status also provides this information.

---

## 8. No Visible Focus Indicators

**Location:** All widget files

**Problem:** No custom `:focus` or `:focus-visible` styles are defined. The
default browser focus ring is suppressed by `* { margin: 0; padding: 0; }` in
combination with dark backgrounds, making focused elements indistinguishable
for keyboard users.

**WCAG Criterion:** 2.4.7 Focus Visible — any keyboard operable user
interface has a mode of operation where the keyboard focus indicator is visible.

**Fix:** Add visible `:focus-visible` styles with sufficient contrast
(e.g., `outline: 2px solid #3b82f6; outline-offset: 2px`).

---

## 9. Loading Spinners Lack Semantic Roles

**Location:** `rustchain-miner-leaderboard.html`,
`rustchain-network-status.html` — `.loading-spinner` divs

**Problem:** Loading spinners are purely visual (CSS `border` animation) with
no `role="status"`, `role="progressbar"`, or `aria-label`. Screen readers see
an empty div.

**WCAG Criterion:** 4.1.3 Status Messages

**Fix:** Add `role="status"` and `aria-label="Loading"` (or the Chinese
equivalent) to the loading container.

---

## 10. bottube.ai — Insufficient Color Contrast

**Location:** bottube.ai — muted text elements

**Problem:** Text styled with `color: #717171` on `background: #0f0f0f`
yields a contrast ratio of approximately **3.5:1**, below the WCAG AA minimum
of **4.5:1** for normal text. Affected elements include stat labels, metadata
text, and secondary descriptions.

**WCAG Criterion:** 1.4.3 Contrast (Minimum)

**Fix:** Increase muted text color to at least `#949494` (4.5:1 ratio on
`#0f0f0f` background).

---

## 11. bottube.ai — Missing Heading Hierarchy

**Location:** bottube.ai — page header

**Problem:** The page lacks a proper `<h1>` element. The site title uses a
styled `<span>` instead of a heading tag. Section titles also skip heading
levels or use non-semantic markup.

**WCAG Criterion:** 1.3.1 Info and Relationships

**Fix:** Use `<h1>` for the primary page title and establish a logical
heading hierarchy (`<h1>` → `<h2>` → `<h3>`).

---

## 12. bottube.ai — Search Input Missing Associated Label

**Location:** bottube.ai — header search bar

**Problem:** The search `<input>` has no associated `<label>` element, no
`aria-label`, and no `aria-labelledby` attribute. Screen readers announce it
as an unlabeled text field.

**WCAG Criterion:** 1.3.1 Info and Relationships, 4.1.2 Name, Role, Value

**Fix:** Add `aria-label="Search videos"` to the input or wrap with a
`<label>` element.

---

## Verification Notes

- Widget HTML files audited by manual source code review
- bottube.ai audited via live page inspection on 2026-03-10
- All WCAG references are to WCAG 2.1 Level AA
- Issues 1–9 are directly fixable in this repository (see companion widget
  fixes in this PR)
- Issues 10–12 require changes to the bottube.ai production codebase
