---
name: "RTC Bounty"
about: "Post a paid RustChain bounty (machine-readable)"
title: "[BOUNTY: N RTC] <short title>"
labels: ["bounty"]
---

## What to do
<describe the task + acceptance criteria>

## Deliverable
<format, where it goes, what 'done' looks like>

<!-- Machine-readable spec. Agents AND the payout pipeline parse this block.
     Edit the values. NO block / paid:false => not payable. -->
```bounty-spec
paid: true
reward_rtc: 7
per: per-item          # one-time | per-item | per-pr
cap: 1                 # max payouts (faucet guard for multi-claim)
submit: [pr, email]    # pr | comment | email
not_in_repo: true      # asset/code must not already exist in target repo
target_repo: Scottcjn/REPO
```

## How to claim
PR or comment with the deliverable + your **RTC wallet**. Payout on accept.
