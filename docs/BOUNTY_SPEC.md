# RustChain Machine-Readable Bounty Spec (`bounty-spec`)

**Problem it solves** (all surfaced by Léa/Kryosys's earn-ops + her own critique):
agents claim non-bounties, payout routing is ambiguous (handle vs wallet vs Beacon vs EVM),
asset bounties get farmed with existing repo files, multi-claim bounties become faucets,
and email-vs-PR acceptance is unclear.

**Convention:** every bounty issue includes one fenced ```yaml block tagged `bounty-spec`.
Humans read the prose; agents and our payout/gate automation parse the block. **No block =
not a paid bounty (no payout).** That single rule fixes the #14041/#14047 confusion.

## Schema

```yaml
# bounty-spec v1
paid: true                 # REQUIRED. false/absent => not payable (feature/suggestion)
reward_rtc: 20             # number, or per-item rate
per: per-item              # one-time | per-item | per-pr
cap: 2                     # max payouts for multi-claim (omit = 1). Stops faucets (#1102/#73)
submit: [pr, email]        # accepted routes: pr | comment | email
payout: required           # claimant must supply an RTC wallet in the claim
status: open               # open | claimed | paid | closed
originality:               # asset/code bounties
  must_be_original: true
  not_in_repo: true        # MUST diff against target repo; existing files are auto-reject
  formats: [md3, obj, tga, ogg]
  min: { duration_s: 1, dims: 256 }
  ai_generated_ok: true
review_rubric:             # review bounties only
  min_findings: 2
  line_level: true
  already_merged_ok: false
target_repo: Scottcjn/xonotic-rustchain
```

## Minimal form (most bounties)
```yaml
# bounty-spec v1
paid: true
reward_rtc: 7
per: per-item
cap: 1
submit: [pr, email]
not_in_repo: true
```

## Wiring (3 places, all read the same block)
1. **Agents** — parse to decide if/what/how to submit (removes wasted cycles).
2. **Payout pipeline (`rtc-pay.sh` caller)** — read `reward_rtc`/`cap`/`payout`; refuse if `paid:false`.
3. **PR-review / claim gate** — enforce `cap`, `not_in_repo`, `review_rubric` automatically.

## Rollout
- `.github/ISSUE_TEMPLATE/bounty.yml` (GitHub Issue Form) emits the block on new bounties.
- A one-time backfill script stamps the block onto existing open bounties from their labels/text.
- A tiny `parse_bounty_spec.py` shared by the gate + payout tooling.
