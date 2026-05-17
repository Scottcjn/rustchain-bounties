# Human Funnel Stage 4-5 Conversion Pack

Bounty: [#318](https://github.com/Scottcjn/rustchain-bounties/issues/318)
Contributor: `@kekehanshujun`
RTC wallet: `RTC02811ff5e2bb4bb4b95eee44c5429cd9525496e7`

This submission includes an implementation-ready static start-flow page plus the conversion copy and engineering notes requested by the bounty. The page is intentionally drop-in: plain HTML/CSS/JavaScript, no build step, no CDN dependencies, no analytics, and no private-key collection.

## Files

- `start-flow.html` - static conversion page with:
  - hero and low-friction CTA
  - three-step start flow
  - start-mining button copy and command generator
  - three non-technical micro-bounties
  - referral/invite loop copy
  - brag card preview using browser canvas
  - weekly hall-of-fame rules and prize structure
  - engineering handoff notes

## How to Review

Open `start-flow.html` directly in a browser. It does not need a server.

Suggested review checklist:

1. Enter an RTC wallet or miner ID in the command generator.
2. Confirm the dry-run/install/status commands update safely.
3. Try the copy buttons.
4. Enter a machine label in the brag card form and generate the preview.
5. Confirm no private key, seed phrase, password, or wallet-file content is requested.

## Deliverables Covered

| Requirement | Where implemented |
|---|---|
| Landing page copy for start flow | Hero and 3-step flow in `start-flow.html` |
| "Start Mining" button copy and click flow | CTA panel, command generator, and state notes |
| 3 micro-bounties for non-technical users | Micro-bounty section |
| Referral mechanics copy | Invite loop section |
| Brag card generator spec | Spec section and working canvas preview |
| Weekly hall-of-fame rules and prizes | Hall-of-fame section |
| Engineering notes | Implementation handoff section |

## Design and Safety Notes

- The first CTA is `Run Safe Dry-Run`, not "earn now", because first-time users should test before mining.
- Copy avoids guaranteed earning claims.
- All proof flows use public wallet/miner IDs only.
- The page warns users not to paste private keys, seed phrases, passwords, wallet JSON, or full environment dumps.
- The brag card is generated locally in the browser and can be wired to server-side rendering later.

## RTC Wallet

`RTC02811ff5e2bb4bb4b95eee44c5429cd9525496e7`
