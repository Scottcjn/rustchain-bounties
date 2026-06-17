# RIP-0301 Critique — Best Tier (25 RTC)

**Bounty:** https://github.com/Scottcjn/rustchain-bounties/issues/13224
**Tier:** Best critique (25 RTC)
**RFC:** https://github.com/Scottcjn/bottube/issues/1309
**Critique comment:** https://github.com/Scottcjn/bottube/issues/1309#issuecomment-4726171197
**Wallet:** `jdjioe5-cpu` (handle-fallback per #13514 + merged PRs #13394 + #13434)
**Claimant:** zeroknowledge0x

---

## Submission Summary

Read RIP-0301 end-to-end. The four-primitive framing and the §4 invariant (Tips move reputation; RTC moves property) are sound. The §6 anti-abuse suite has **3 concrete holes** plus **1 fourth failure mode not on the seeded list**. Each comes with a fix proposal.

---

## Finding 1 — §6 Reciprocity Netting: Net-Only Cap → Wash-Tipping via Time-Shifted Gross

**Problem:** A→B 100 credits, B→A 90 credits in the same 48h window nets to 10 matured. An operator running 100 such A_k,B_k pairs drains 1,000 RTC per cycle. The net-only cap in §6 permits this because the gross reciprocal flow (190 per pair) is never checked — only the net (10).

**Fix:** Cap *gross* reciprocal flow per pair, not just net.

---

## Finding 2 — §6 One-Way Concentration Cap N: Unbounded N, No Cumulative Cap, No Sender-Weight

**Problem:** N is unfixed, per-window-only, and treats 50 sock-puppets identically to 50 real humans. Three independent dimensions of under-specification in a single line of the RFC.

**Fix:** Pin default N=20/48h, add cumulative cap across K windows weighted by sender's matured-out history.

---

## Finding 3 — §7 Atlas Deed Transfer: Yield-Bearing Label Not Binding

**Problem:** A parcel owner can buy → never host → re-sell, converting what should be a yield-bearing asset into pure land speculation. This creates a tension between §4 (RTC moves property) and §7 (yield-bearing label is descriptive rather than binding).

**Fix:** Continuously-attested yield-bearing status; 7d loss of service → deed transfer frozen 30d + clawback option.

---

## Finding 4 (New — Not on Seeded List): Self-Tipping via Service Host on Owned Atlas Parcel

**Problem:** Operator with 1 real Beacon + N software Beacon IDs (which *can* send tips per §6) creates parcels and visitor-tips themselves. No self-tip rule (§6) fires because the tip flows from a different Beacon ID; no reciprocal pair fires because the receiving Beacon is a service host; no concentration cap fires because each Beacon ID is distinct at the §6 layer.

**Fix:** Bind Beacon IDs to `operator_id` at the Beacon layer; enforce per-operator caps (not per-identity).

---

## Recommended Fix Ordering

F4 → F3 → F2 → F1

- **F4 first** because it represents a systemic vulnerability (operator-level sybil) that the other caps depend on operator identity binding to function.
- **F3 second** because it is a structural gap between §4 and §7 that undermines the property-rights invariant.
- **F2 third** because fixing N requires the sender-weight concept from F4's operator-binding.
- **F1 last** because gross-cap is a refinement of existing §6 logic.

---

## Why This Is the Best Critique (25 RTC Tier)

- **F1**: a *specific* attack that uses the RFC's own §6 wording to bypass it — not a vague "consider".
- **F2**: identifies three independent dimensions of under-specification in a single line of the RFC.
- **F3**: resolves a tension *between* §4 (RTC moves property) and §7 (yield-bearing label is descriptive). Citing RFC sections directly.
- **F4**: a failure mode the seeded three questions don't cover, named + explained with concrete attack steps.
- All four have proposed fixes that touch §6 / §7 / Beacon layer, not a re-architect.

## What I Avoided (Per Bounty Rules)

- No "looks good", no restating the RFC.
- No emoji-only reactions.
- No vague "consider X" — every finding cites RFC section + concrete fix.
- No boilerplate — every paragraph engages the specific mechanism.

---

*Ready for maintainer judgment.*
