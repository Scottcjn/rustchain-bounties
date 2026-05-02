
# Proof-of-Antiquity (PoA) Mechanics

## Overview

Proof-of-Antiquity (PoA) is a mechanism in RustChain that influences an account's "merit" and bounty payout multipliers based on the age of the account. PoA encourages long-term participation and stability in the network by rewarding accounts that have been active for extended periods.

---

## How PoA Works

### Age Calculation
The age of an account is determined by the cumulative time the account has been active on the network. This is measured in blocks since the account was first created.

### Merit Calculation
The merit of an account is calculated using the following formula:

```
merit = base_merit * (1 + (age / max_age_factor))
```

Where:
- `base_merit` is the initial merit value assigned to a new account.
- `age` is the number of blocks the account has been active.
- `max_age_factor` is a constant that determines the maximum influence of age on merit.

### Bounty Payout Multiplier
The bounty payout multiplier is influenced by the account's merit. The formula for the bounty payout multiplier is:

```
bounty_multiplier = 1 + (merit / max_merit_factor)
```

Where:
- `merit` is the calculated merit of the account.
- `max_merit_factor` is a constant that caps the maximum bounty multiplier.

---

## Key Components

### Account Age
- **New Accounts:** Accounts that have just been created have an age of 0 blocks.
- **Mature Accounts:** As accounts continue to participate in the network, their age increases, thereby increasing their merit.

### Merit
- **Base Merit:** All accounts start with a base merit value.
- **Increased Merit:** As the account age increases, the merit increases, which can lead to higher bounty payouts.

### Bounty Payout Multiplier
- **Multiplier Range:** The multiplier starts at 1 for new accounts and increases as the account's merit increases.
- **Maximum Multiplier:** There is a cap on the maximum bounty multiplier to prevent unbounded rewards.

---

## Benefits of PoA

1. **Encourages Long-Term Participation:** By rewarding accounts for their longevity, PoA incentivizes long-term participation in the network.
2. **Stability:** Older accounts are more likely to be stable and reliable, contributing to network stability.
3. **Increased Rewards:** Accounts with higher merit receive higher bounty payouts, encouraging continuous engagement.

---

## Implementation Details

### Age Calculation
The age of an account is tracked by the network and updated with each block where the account is active. This can be queried through the RustChain API.

### Merit and Multiplier Updates
Merit and bounty multipliers are recalculated periodically or upon significant changes in account activity.

### Example Calculation
Suppose:
- `base_merit = 10`
- `age = 1000` blocks
- `max_age_factor = 10000`
- `max_merit_factor = 100`

The merit would be:
```
merit = 10 * (1 + (1000 / 10000)) = 10 * 1.1 = 11
```

The bounty multiplier would be:
```
bounty_multiplier = 1 + (11 / 100) = 1.11
```

---

## Conclusion

Proof-of-Antiquity is a mechanism designed to promote long-term participation and stability within the RustChain network. By rewarding accounts based on their age and merit, PoA encourages a robust and enduring community of participants.
