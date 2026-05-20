# RustChain Stage 3 Proof Pack

Factual proof assets for bounty [#317](https://github.com/Scottcjn/rustchain-bounties/issues/317).

This pack is written for skeptical non-developers. It avoids invented earnings, invented screenshots, and invented user stories. Every template below is meant to be filled with real wallet IDs, real terminal output, and real hardware photos.

## Source Basis

- RustChain quick start: `START_HERE.md`
- Installer flow: `INSTALL.md`
- Troubleshooting and balance checks: `TROUBLESHOOTING.md`
- Hardware multiplier table: `rustchain-miner/README.md`
- Live network snapshot taken on 2026-05-15:
  - `GET https://rustchain.org/health`
  - `GET https://rustchain.org/epoch`
  - `GET https://rustchain.org/api/miners`
  - `GET https://rustchain.org/wallet/balance?miner_id=power8-s824-sophia`
  - `GET https://rustchain.org/wallet/balance?miner_id=nox-ventures`

## How To Use This Pack

1. Pick one testimonial template that matches the operator.
2. Replace every placeholder with real proof.
3. Keep the command lines exactly reproducible.
4. Do not publish earnings claims without the matching balance output or miner logs.

## Deliverable 1: Five Testimonial-Style Post Templates

### Template 1: "I used an old machine instead of buying new hardware"

**Headline**
My old `[machine_name]` is finally useful again.

**Post**
I had a `[year] [machine_name]` sitting unused and assumed it was basically e-waste. I tried RustChain because it rewards older hardware instead of forcing an arms race for newer GPUs.

What I actually did:

- Installed from the official setup docs
- Used wallet ID: `[wallet_id]`
- Started the miner with: `[exact command]`
- Verified the node was up with: `[health or status command]`
- Checked balance with: `curl -sk "https://rustchain.org/wallet/balance?miner_id=[wallet_id]"`

What I can prove:

- Hardware photo: `[insert photo link]`
- First successful miner output: `[insert terminal screenshot or paste]`
- First balance check JSON: `[insert exact JSON]`
- 24-hour follow-up: `[insert later balance JSON]`

Why I found it credible:

- The miner flow is command-line based, not a fake "one-click passive income" widget
- The public node exposes health, epoch, and miner endpoints anyone can query
- The project publishes hardware multiplier docs instead of pretending all machines are equal

**Common objections**

- "Is this fake?"  
  Response: Post the exact `curl` balance output and miner logs, not a vague screenshot.
- "Did you have to buy anything?"  
  Response: State exactly what machine you already owned and whether you spent anything on setup.
- "How do I know the numbers are real?"  
  Response: Include raw JSON from the wallet balance endpoint.

### Template 2: "This is for thrift-store or attic hardware"

**Headline**
I tested RustChain on hardware most people would throw away.

**Post**
Instead of benchmarking a brand-new machine, I tried RustChain on `[hardware class]` because the project explicitly claims older hardware can earn better multipliers.

My proof format:

- Hardware: `[machine / CPU model]`
- Multiplier class from docs: `[multiplier from source]`
- Install path used: `[install-miner.sh or other verified path]`
- Miner ID / wallet: `[wallet_id]`
- First epoch snapshot: `[insert output]`
- Balance check after waiting: `[insert JSON]`

What stood out:

- The docs call out specific hardware families like G4/G5/Core 2 instead of hand-wavy "AI mining"
- The public miner list shows mixed hardware classes on the network
- The project is easier to trust when the proof is boring and reproducible

**Common objections**

- "This sounds like nostalgia cosplay."  
  Response: Show the multiplier table and your actual hardware model.
- "Is there a hidden dashboard?"  
  Response: No. Show the command line and endpoint output.
- "Can I copy your post?"  
  Response: Only if you replace the proof block with your own machine and logs.

### Template 3: "I am not a crypto person"

**Headline**
I only trust setups I can verify in plain text.

**Post**
I am not the target audience for most crypto projects. I tried RustChain only because the proof path is simple enough to inspect:

1. Install from the official docs
2. Start the miner with my own wallet ID
3. Query the public node directly
4. Compare my output against the published docs

My evidence pack:

- Wallet ID: `[wallet_id]`
- Start command: `[exact command]`
- Health check result: `[insert JSON or screenshot]`
- Balance query result: `[insert JSON]`
- Miner list snapshot showing my class of hardware: `[insert excerpt or screenshot]`

What I would tell another skeptic:

- Trust the raw command output, not the marketing copy
- If you cannot post a balance check, you have not proved anything yet
- Keep the first post small and factual; let the logs do the selling

**Common objections**

- "Where is the wallet UI?"  
  Response: This flow is CLI-first. That is a feature, not a bug, for a proof-based testimonial.
- "Why should I believe your result?"  
  Response: Because you can run the same balance query against the same public node.

### Template 4: "Vintage hardware hobbyist"

**Headline**
This is one of the few blockchain projects where the old machine is the point.

**Post**
I already keep `[machine_name]` alive because I like vintage hardware. RustChain is interesting because it turns that hobby into a measurable network role.

My post should include:

- A clear machine shot: `[photo]`
- CPU / architecture label: `[for example: PowerPC 7450 / G4]`
- Documented multiplier class: `[2.5x / 2.0x / 1.8x / etc.]`
- First miner run output: `[terminal proof]`
- Public balance check: `[JSON proof]`

What not to say:

- No made-up monthly earnings
- No claims about "thousands of users" unless linked to a source
- No pretending a GUI exists if your proof is from the shell

**Common objections**

- "Isn't this just a toy?"  
  Response: Treat it like a real proof artifact: show the logs, show the machine, show the balance endpoint.
- "Why not just say it earns X dollars a month?"  
  Response: Because repeatable proof beats a fabricated estimate.

### Template 5: "Operator proof update"

**Headline**
24-hour update from my first RustChain run.

**Post**
Yesterday I posted my setup proof for RustChain on `[machine_name]`. Here is the follow-up with actual output instead of guesses.

**Before**

- Balance at T0: `[JSON]`
- Start method: `[exact command]`
- Hardware class: `[doc-backed label]`

**After 24 hours**

- Balance at T+24h: `[JSON]`
- Service status / log line: `[paste output]`
- Any problems I hit: `[short honest note]`

**What changed**

- RTC delta: `[computed from the two balance checks]`
- Whether I stayed online the whole time: `[yes/no]`
- Whether the machine stayed usable: `[yes/no with note]`

**Common objections**

- "Maybe you edited the screenshot."  
  Response: Paste the raw JSON alongside the screenshot.
- "Maybe your machine class is fake."  
  Response: Add the hardware photo and CPU model text.

## Deliverable 2: "Zero to Mining in 5 Minutes" Guide

This version uses the official shell installer path because it is documented in `INSTALL.md`, `README.md`, and `TROUBLESHOOTING.md`.

### Goal

Get a new operator from zero to a verifiable first balance check in one sitting.

### Step 1: Pick a wallet ID

Choose one short RustChain wallet / miner ID and use it consistently.

```bash
export YOUR_WALLET=my-vintage-miner
```

**Screenshot placeholder:** Terminal showing the exported wallet name.

### Step 2: Run the official installer

```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet "$YOUR_WALLET"
```

What this should do according to `INSTALL.md`:

- Detect platform and architecture
- Create `~/.rustchain/venv`
- Download the miner files
- Configure the wallet name
- Offer service setup

**Screenshot placeholder:** Terminal output from the installer.

### Step 3: Confirm the service is running

Use the documented service commands.

```bash
systemctl --user status rustchain-miner
```

Or on macOS:

```bash
tail -f ~/.rustchain/miner.log
```

If you are using the newer wrapper flow documented in `START_HERE.md`, also capture:

```bash
clawrtc status
clawrtc logs
```

**Screenshot placeholder:** One successful status or log view.

### Step 4: Check the node and epoch

```bash
curl -sk https://rustchain.org/health
curl -sk https://rustchain.org/epoch
```

Expected proof format:

- `health` should return `ok: true`
- `epoch` should return the current epoch and `epoch_pot`

**Screenshot placeholder:** Health JSON and epoch JSON in the terminal.

### Step 5: Check your balance

```bash
curl -sk "https://rustchain.org/wallet/balance?miner_id=$YOUR_WALLET"
```

Post the full JSON exactly as returned.

**Screenshot placeholder:** First balance query.

### Step 6: Optional cross-check

See the active miner list:

```bash
curl -sk https://rustchain.org/api/miners
```

This is useful if you want to show that the public node is alive even before your own miner appears.

### Troubleshooting block

Use this verbatim if something fails:

- Re-check the wallet ID for typos
- Wait at least one epoch before assuming a balance issue
- Re-run the documented balance query with the same wallet ID
- Include exact log lines in any support request

### Repeatable proof bundle

Every valid beginner proof post should include:

1. The exact install command used
2. One status or log screenshot
3. `health` JSON
4. `epoch` JSON
5. `wallet/balance` JSON

## Deliverable 3: Old Hardware vs Modern Hardware Table

This comparison avoids speculative daily or monthly earnings. It focuses on the documented multiplier classes, which are the core user-facing claim.

| Hardware class | Example family | Multiplier source | Relative reward share vs modern x86 (1.0x) | Why a skeptical user might care |
|---|---|---:|---:|---|
| PowerPC G4 | 7450 / 7447 / 7455 | `rustchain-miner/README.md` | 2.5x | The headline claim is concrete: a G4 is worth 2.5 modern shares on RustChain. |
| PowerPC G5 | 970 | `rustchain-miner/README.md` | 2.0x | Vintage desktop hardware still receives a clear premium. |
| PowerPC G3 | 750 | `rustchain-miner/README.md` | 1.8x | Older, slower hardware is still directly recognized by the protocol. |
| Core 2 | Core 2 family | `rustchain-miner/README.md` | 1.3x | Even late-2000s x86 can sit above the generic modern baseline. |
| Apple Silicon | M1 / M2 / M3 | `rustchain-miner/README.md` | 1.2x | Modern Macs are supported, but not positioned as the top reward class. |
| Modern x86_64 | "Everything else" | `rustchain-miner/README.md` | 1.0x | Useful for baseline comparison and easy onboarding. |

### Dated live-network note

On 2026-05-15, the public miner list returned a mixed fleet including:

- `power8-s824-sophia` with `antiquity_multiplier: 2.0`
- multiple Apple Silicon miners with `antiquity_multiplier` values between `1.05` and `1.2`
- x86 / Windows miners with `antiquity_multiplier` values including `0.8`, `1.0`, and `1.1`

This matters because it shows the network is not hypothetical: both vintage and modern classes are visible on the public endpoint today.

## Common Objections And Responses

### "I do not trust made-up earning screenshots."

Correct. Only post:

- raw balance JSON
- the command that produced it
- the hardware photo that backs the machine claim

### "I am not technical enough for this."

The first proof does not need advanced skills. It needs:

- copy-paste of one installer command
- one balance query
- one screenshot of the machine and terminal

### "What if my machine is not vintage?"

That is still usable. The comparison table makes the pitch honest:

- vintage hardware is the differentiator
- modern hardware is the baseline
- your proof is still valuable if it is real

### "How do I avoid sounding like spam?"

Use this checklist:

- no invented dollar figures
- no generic praise
- no unverifiable user counts
- no GUI claims unless you show the GUI
- always include one machine-specific detail

## Simple Repeatable Proof Format

Copy this block into any public testimonial or bounty comment:

```md
Machine: [exact model / CPU]
Wallet ID: [wallet_id]
Install command:
`[exact command]`

Health check:
`[paste JSON]`

Epoch check:
`[paste JSON]`

Balance check:
`[paste JSON]`

Hardware proof:
- [photo link]
- [terminal screenshot link]

Notes:
- [what worked]
- [what was confusing]
```

## Why This Pack Is Safer Than A Typical Crypto Funnel

- It sells proof, not fantasies.
- It gives skeptical users a script they can reproduce.
- It uses public endpoints instead of invented dashboards.
- It treats old hardware as a verifiable differentiator, not a vague brand story.
