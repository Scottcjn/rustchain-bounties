# Stage 3 Proof Pack

Issue: `#317`  
Audience: skeptical, non-technical humans with older hardware  
Date baseline used in this pack: `2026-03-28`

## Factual guardrails

Use these facts as-is unless you re-verify them:

- Official site: `https://rustchain.org`
- RustChain is a Proof-of-Antiquity blockchain where older hardware can earn higher multipliers
- Install path: `pip install clawrtc`
- Start path: `clawrtc install --wallet YOUR_MINER_ID` then `clawrtc start`
- Current documented defaults:
  - PowerPC G4: `2.5x`
  - PowerPC G5: `2.0x`
  - POWER8: `1.5x`
  - Apple Silicon: `1.2x`
  - Modern x86: `1.0x`
- Live network snapshot checked on `2026-03-28`:
  - `epoch`: `115`
  - `epoch_pot`: `1.5 RTC`
  - `enrolled_miners`: `28`
  - `total_miners`: `521`

Do not replace placeholders below with made-up earnings, fake screenshots, or nonexistent GUI flows.

## Deliverable 1: Testimonial-style post templates

These are templates, not fake testimonials. Replace only the bracketed fields with your own verified details.

### Template 1: The "I was going to recycle this" post

```text
I was one weekend away from recycling my old [machine model].

Instead, I tried RustChain. It is a Proof-of-Antiquity network that rewards older hardware more than newer hardware in some classes. A PowerPC G4 is documented at 2.5x. Modern x86 is 1.0x.

My setup was not a mystery box. I used:
pip install clawrtc
clawrtc install --wallet [your-miner-id]
clawrtc start

Proof:
- Miner ID: [your-miner-id]
- Screenshot: [terminal screenshot or photo]
- Network check: [link or pasted /api/miners entry]

If you have an old Mac or workstation in a closet, test it before you throw it out.
Start here: https://rustchain.org
```

Common objection response:
- "This sounds fake."  
  Response: include the exact command output, your miner ID, and a matching `/api/miners` entry.

### Template 2: The "old Mac beats new Mac" post

```text
The weird part about RustChain is that my older machine is the point.

This network is not "buy new hardware, burn more power, win." It documents higher multipliers for preserved machines:
- PowerPC G4: 2.5x
- PowerPC G5: 2.0x
- Apple Silicon: 1.2x
- Modern x86: 1.0x

I tested it on [machine model]. Setup was command-line simple:
clawrtc install --wallet [your-miner-id]
clawrtc start

If you want proof, ask me for:
- the terminal screenshot
- my miner ID
- the live miner list entry

That old Mac in your closet might be more interesting than your current laptop.
https://rustchain.org
```

Common objection response:
- "Will this only work on rare museum hardware?"  
  Response: no. Modern x86 and Apple Silicon can participate too, but the vintage bonus is the differentiator.

### Template 3: The "skeptical student / side machine" post

```text
I did not want another crypto app with fake promises.

RustChain only became interesting when I saw two things:
1. the install path was transparent
2. the multiplier table was public

What I actually ran:
- pip install clawrtc
- clawrtc install --wallet [your-miner-id] --dry-run
- clawrtc install --wallet [your-miner-id]
- clawrtc start

What I checked next:
- clawrtc status
- https://50.28.86.131/api/miners
- https://50.28.86.131/epoch

If you have an older backup machine, you can verify this yourself in minutes instead of trusting screenshots on the internet.
https://rustchain.org
```

Common objection response:
- "What if it wrecks my daily driver?"  
  Response: start on a spare or side machine first and use `clawrtc status` plus screenshots as your proof trail.

### Template 4: The "anti-e-waste" post

```text
Most tech products tell you to upgrade.
RustChain is one of the few telling you to test the hardware you already own.

That is why I paid attention.

The pitch is simple:
- older hardware can earn higher weight on the network
- fake VM claims are penalized
- setup starts with pip, not a mystery installer

My proof pack:
- machine: [model]
- miner ID: [your-miner-id]
- photo of the machine: [photo link]
- terminal proof: [screenshot link]
- miner list proof: [link or pasted entry]

If you care about e-waste, "try the old machine first" is a much better story than "buy a new one."
https://rustchain.org
```

Common objection response:
- "Is this only a greenwashing angle?"  
  Response: anchor the post in your own machine photo plus a live miner-list check, not in abstract claims.

### Template 5: The "repair shop / collector" post

```text
I keep old hardware because I hate throwing away machines that still work.

RustChain is the first project I have seen that treats that instinct like an advantage instead of a hobby.

Current documented multiplier examples:
- G4: 2.5x
- G5: 2.0x
- POWER8: 1.5x
- modern x86: 1.0x

My recommendation:
1. pick one working machine
2. install clawrtc
3. save terminal screenshots
4. check your miner ID in /api/miners

If your machine is still alive, test it before you retire it.
https://rustchain.org
```

Common objection response:
- "Do I need to understand blockchain internals?"  
  Response: no. For the first proof post you only need install, start, status, and one miner-list check.

## Deliverable 2: "Zero to Mining in 5 Minutes" guide

This is the non-developer flow. The screenshots are placeholders for maintainers or creators to fill with real captures.

### Step 1: Pick a miner ID

Choose a simple wallet / miner name you can remember, for example `old-g4-lab` or `basement-imac`.

Optional command:

```bash
clawrtc wallet create
```

Screenshot placeholder:
- `[Screenshot Placeholder: clawrtc wallet create output or saved wallet note]`

### Step 2: Install the miner in preview mode first

Run a dry-run before making changes:

```bash
clawrtc install --wallet YOUR_MINER_ID --dry-run
```

What this proves:
- you have the correct CLI
- the machine can see the installer path
- you are not relying on a fake GUI walkthrough

Screenshot placeholder:
- `[Screenshot Placeholder: terminal showing clawrtc install --dry-run]`

### Step 3: Install for real

```bash
clawrtc install --wallet YOUR_MINER_ID --no-service -y
```

If you want background startup later, add service setup after the first successful run.

Screenshot placeholder:
- `[Screenshot Placeholder: successful install output]`

### Step 4: Start mining

```bash
clawrtc start
```

What to say in plain English:
- "I started the miner."
- "The machine is now attempting real hardware attestation."
- "This is the point where I wait for it to appear in the live miner list."

Screenshot placeholder:
- `[Screenshot Placeholder: clawrtc start output]`

### Step 5: Check local status

```bash
clawrtc status
```

What to look for:
- miner process running
- network reachability
- hardware / status summary

Screenshot placeholder:
- `[Screenshot Placeholder: clawrtc status output]`

### Step 6: Check live network proof

Open the live endpoints:

```bash
curl -sk https://50.28.86.131/api/miners
curl -sk https://50.28.86.131/epoch
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_MINER_ID"
```

Repeatable proof format:
- machine photo
- terminal showing `clawrtc start`
- terminal showing `clawrtc status`
- `/api/miners` entry containing your miner ID
- optional balance check after rewards accrue

Screenshot placeholder:
- `[Screenshot Placeholder: browser or terminal showing YOUR_MINER_ID in /api/miners]`

### Common objections and direct answers

- "Do I need a GPU?"  
  No. RustChain is built around hardware attestation and antiquity, not GPU arms races.

- "Do I need the newest machine?"  
  No. The documented multiplier table explicitly rewards some older machines more highly than newer ones.

- "Is this a fake dashboard trick?"  
  No. The proof format uses the CLI plus live endpoints, not mock screenshots.

- "What if I only have modern hardware?"  
  Modern x86 still participates. It just does not get the same multiplier as a G4 or G5 class machine.

## Deliverable 3: Old hardware vs modern hardware comparison table

This table is designed for skeptical newcomers. It compares network weight and onboarding angle, not fabricated earnings.

| Hardware class | Example machine | Current documented multiplier | What to say to a skeptical newcomer | Best proof artifact |
|---|---|---:|---|---|
| PowerPC G4 | Power Mac G4, iBook G4 | 2.5x | "This is the headline case. The old machine is not a fallback. It is the premium lane." | Photo of the machine + miner entry |
| PowerPC G5 | Power Mac G5 | 2.0x | "Still a vintage bonus machine, but easier to explain as a serious desktop tower." | Photo + `clawrtc status` + miner entry |
| POWER8 | IBM POWER8 S824 | 1.5x | "Good for the 'enterprise hardware still matters' pitch." | Rack photo or chassis photo + status output |
| Apple Silicon | M1/M2/M3 Mac | 1.2x | "For users who want a modern Mac test run before trying older hardware." | Terminal install/start screenshots |
| Modern x86 | ThinkPad, Intel/AMD desktop | 1.0x | "Useful for proving the flow works, but not the nostalgia angle." | CLI proof + miner list entry |

## Recommended usage notes

- For founder posts, lead with G4/G5 because that is the memorable Proof-of-Antiquity hook.
- For skeptical users, never publish exact revenue claims unless you have your own screenshot and miner history.
- For onboarding threads, link to `https://rustchain.org` and keep the first proof pack reproducible with commands.
- If you want one line that captures the whole project, use this:

```text
That old Mac in your closet? On RustChain, it can be more valuable than a newer one.
```

## Source notes

This pack was built from:
- live checks against `/api/miners`, `/epoch`, and `/api/stats` on `2026-03-28`
- `clawrtc 1.8.0` CLI verification on the local system
- multiplier references from:
  - `docs/MINERS_SETUP_GUIDE.md`
  - `rustchain-miner/README.md`
  - `docs/protocol/TOKENOMICS.md`
