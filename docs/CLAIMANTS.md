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
| 0oAstro | RTC5268f16391bcdff87c43cd8694fca3be9d995359 |
| 508704820 | RTC9d7caca3039130d3b26d41f7343d8f4ef4592360 |
| Asti1982 | RTCda4841be5b2d109da5d995fb864c09676bb5b7c7 |
| Vyacheslav-Tomashevskiy | RTCd1554f0f35576faf01d386a6be1c947f560dd0b7 |
| kryosys-lea | RTC31ede8c0133d0af78ab557d1be7568523b619a84 |
