## Bounty Submission

**Bounty**: Closes #ISSUE_NUMBER

**RTC Wallet**: YOUR_WALLET_NAME

> **RTC wallets are string names** (e.g. `my-wallet`, `alice`, `builder-fred`).
> Do NOT use ETH/SOL/ERG addresses. Pick any name and start mining:
> `pip install clawrtc && clawrtc --wallet your-name`
>
> RustChain is a long-term project. Bounties grow the ecosystem — not for quick cash-outs.
> If you won't support what you build, don't build it.

## BCOS Checklist (Required For Non-Doc PRs)

- [ ] Add a tier label: `BCOS-L1` or `BCOS-L2` (also accepted: `bcos:l1`, `bcos:l2`)
- [ ] If adding new code files, include SPDX header near the top (example: `# SPDX-License-Identifier: MIT`)
- [ ] Provide test evidence (commands + output or screenshots)

## Changes

- ...

## Testing

- [ ] `npm test` / `python -m pytest` / manual verification passes
- [ ] Demo or reproduction steps provided

## Evidence

- Proof links (screenshots/logs/metrics):
- Before vs after summary:
- Validation method:

## Quality Gate Self-Score (0-5)

| Dimension | Score | Notes |
|---|---:|---|
| Impact |  |  |
| Correctness |  |  |
| Evidence |  |  |
| Craft |  |  |

Suggested gate for maintainers: >=13/20 total and Correctness > 0.

## Checklist

- [ ] All acceptance criteria from the bounty issue are met
- [ ] Code is tested
- [ ] No secrets or credentials committed
- [ ] Submission does not match any global disqualifier


## Supply-Chain Proof (Required if changed)

Complete this if your PR changes dependencies, install docs, CI tooling, or external artifacts.

- [ ] Dependency versions are pinned (or intentionally ranged with reason)
- [ ] External repo references include commit SHA
- [ ] Artifact checksum/container digest provided
- [ ] No `curl | bash` or equivalent blind install steps

Proof details:
- Dependency diff summary:
- SHA/checksum/digest:
- Repro command used by reviewer:

