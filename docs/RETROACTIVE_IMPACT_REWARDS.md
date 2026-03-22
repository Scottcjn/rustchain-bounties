# Retroactive Impact Rewards — Surprise Bonuses for Real Impact

> **Program Status:** Active
> **Monthly Pool:** 100 RTC
> **Recipients per Cycle:** 3–5 contributors
> **Review Window:** 1st–14th of each month

---

## Overview

The Retroactive Impact Rewards program recognises contributions that delivered real value to the RustChain ecosystem — even when that value was not anticipated by a formal bounty. Rewards are distributed monthly after a council review and are not pre-announced or guaranteed.

---

## Pool Structure

| Recipients | Min per Recipient | Max per Recipient | Total Pool |
|:-----------:|:-----------------:|:-----------------:|:----------:|
| 3           | 20 RTC            | 60 RTC            | 100 RTC    |
| 4           | 15 RTC            | 40 RTC            | 100 RTC    |
| 5           | 10 RTC            | 30 RTC            | 100 RTC    |

The council determines the exact split each cycle based on relative impact. Remaining RTC after distribution rolls over to the next month's pool.

---

## What Qualifies as Impact

Eligible contributions include (but are not limited to):

- **Bug fixes** that resolved production incidents or prevented data loss
- **Documentation** that is actively referenced by community members
- **Security reports** that prevented attacks or vulnerabilities from being exploited
- **Community mentorship** that helped onboard or unblock other contributors
- **Content or marketing** that drove measurable user or developer growth
- **Unexpected valuable contributions** that did not fit an existing bounty category

---

## What Does Not Qualify

The following will not be considered for retroactive rewards:

- High volume of low-value work (e.g., multiple minor typo fixes with no other contribution)
- Self-promotional activity without a demonstrated benefit to the project
- Work that was **already fully compensated** through an existing bounty (see Double-Dipping Policy)

---

## Double-Dipping Policy

A contributor who received a partial or reduced bounty payout for a high-impact piece of work **may** still be considered for a top-up retroactive award if the council determines the original compensation did not adequately reflect the impact delivered. The council must document its reasoning in the public award record.

Contributors who received a full bounty payout at the standard rate are **not eligible** for additional retroactive compensation for the same work.

---

## Review Council

### Composition

The review council consists of **3–5 active maintainers**, updated quarterly. Current council members are listed in [`MAINTAINERS.md`](../MAINTAINERS.md).

### Quorum

A minimum of **3 council members** must participate in each monthly review. Decisions require a simple majority of participating members.

### Conflict-of-Interest Rules

Any council member who is themselves a candidate for a retroactive award in a given cycle **must recuse themselves** from that cycle's deliberations entirely. Recusal must be declared publicly in the review thread before voting begins. A recused member's vote does not count toward quorum.

---

## Monthly Review Schedule

| Dates          | Activity                                              |
|----------------|-------------------------------------------------------|
| 1st–7th        | Council collects nominations and reviews contributions |
| 8th–10th       | Council deliberation and voting                       |
| 11th–14th      | Award announcement published                          |
| 15th–28th      | **Dispute window** (14-day challenge period)          |
| End of month   | Community nominations open for next cycle             |

---

## Nomination Process

Anyone in the community may nominate a contributor (including themselves — see FAQ). Nominations must be submitted using the [`NOMINATION_FORM.md`](../NOMINATION_FORM.md) template and posted as a comment on the active monthly review issue before the last day of the month.

The council also performs its own proactive discovery of impactful contributions; a formal nomination is not required for a contributor to receive an award.

---

## Dispute Resolution

Following each monthly announcement, a **14-day dispute window** opens during which any community member may formally challenge an award decision. To file a dispute:

1. Open a new GitHub issue titled `[DISPUTE] Retroactive Award – <Month Year>`
2. Clearly state the grounds for the dispute (e.g., conflict of interest, missed nomination, factual inaccuracy)
3. The council will respond within 7 days of the dispute being filed
4. A final decision will be issued before the close of the dispute window

Disputes cannot increase the total pool size or carry awards across cycles.

---

## Award Record

All retroactive awards are logged publicly in [`BOUNTY_LEDGER.md`](../BOUNTY_LEDGER.md) with the following fields:

| Cycle     | Recipient | Contribution Summary | RTC Awarded | Council Notes |
|-----------|-----------|----------------------|:-----------:|---------------|
| *(To be populated after first cycle)* | | | | |

---

## Compliance Notice

RustChain does not provide tax or legal advice. Recipients are solely responsible for understanding and fulfilling any tax obligations arising from RTC rewards in their jurisdiction. KYC requirements may apply for large payouts as determined by applicable law. Distribution method (on-chain wallet transfer) will be confirmed with each recipient before payout.

---

## Frequently Asked Questions

**Can I nominate myself?**
Yes. Self-nominations are accepted but must clearly describe the impact delivered and avoid promotional language. The council gives equal weight to self-nominations and external nominations.

**Is there a guaranteed payout each month?**
No. If the council determines that no contributions in a given cycle meet the impact threshold, no awards will be distributed and the pool rolls over.

**What if I contributed but no one nominated me?**
The council proactively reviews commit history, closed issues, community threads, and Discord activity. You do not need a formal nomination to be considered.

**What counts as "production-ready" impact?**
Work that demonstrably improved the experience of real users or the stability/security of the live system. Proof of impact (e.g., before/after metrics, user testimonials, incident reports) strengthens a nomination.

**How are award amounts decided?**
The council scores each candidate's contribution on breadth of impact, severity of the problem addressed, and quality of execution, then distributes the pool proportionally, subject to the min/max bounds in the Pool Structure table above.

---

*This document was established in response to [Issue #401](https://github.com/Scottcjn/rustchain-bounties/issues/401). For questions, open a GitHub issue tagged `[RETROACTIVE-REWARDS]`.*
