# Canonical Payout Wallets

Registry mapping a contributor's GitHub handle to their **canonical native RTC
wallet** (`RTC` + 40 hex). The bounty payout resolver (`scripts/bounty_payout.py`)
consults this table **first** — so once a contributor is listed here, *every*
payout goes to their registered wallet regardless of what an individual claim
body happens to say. This prevents payouts fragmenting across a contributor's
GitHub handle and their native wallet.

To register: open a `[WALLET]` issue with your handle + native `RTC…` wallet, or
PR a row into the table below. Only native `RTC[0-9a-fA-F]{40}` addresses are
honored here (no off-chain/handle entries — those fall back to per-claim
resolution).

| GitHub handle | Canonical RTC wallet |
| --- | --- |
| qingfeng312 | RTC69a97c336ad63f4904a311997a0429fb6104ed32 |
