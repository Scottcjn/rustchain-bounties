# Human Funnel Stage 3 Proof Pack

Bounty: [#317](https://github.com/Scottcjn/rustchain-bounties/issues/317)
Contributor: `@kekehanshujun`
RTC wallet: `RTC02811ff5e2bb4bb4b95eee44c5429cd9525496e7`

This proof pack is written for skeptical non-developer users. It uses proof placeholders instead of fabricated testimonials or fake earnings. Every balance, uptime, and device detail is designed to be filled with the user's actual command output.

## Deliverable 1: Five Testimonial-Style Post Templates

### Template 1: The Skeptical Old-Laptop Owner

```text
I thought my old laptop was done.

It still booted, but I only kept it because throwing it away felt wasteful. When I saw RustChain, I was skeptical because "mine crypto on old hardware" sounds like the kind of phrase that usually hides a catch.

So I tried the safe path first:

- Machine: [device model / year]
- OS: [operating system]
- Setup command tested: clawrtc install --dry-run
- Wallet command tested: clawrtc wallet show
- Mining command tested: clawrtc start
- Current status: [paste short status result]

What changed my mind was not a huge balance. It was seeing a real wallet address and a real machine status from a computer I almost ignored.

If you have an old computer that still boots, do the dry-run before you recycle it.

Start: https://rustchain.org
```

Objection handled: "This sounds too good to be true."
Response: frames the first step as a dry-run and asks for actual proof, not trust.

### Template 2: The Windows User Blocked by Current Install Support

```text
I am not a command-line person.

My first RustChain attempt was on Windows, and the current published `clawrtc==1.8.0` install path is not beginner-ready on Windows yet. The honest proof is the blocker itself: `clawrtc install --dry-run` reports that Windows is unsupported and recommends Linux or macOS.

My proof:

- Machine: [device model]
- Windows version: [version]
- Wallet: [public RTC address only, if already created elsewhere]
- Command tested: `clawrtc install --dry-run`
- Result: `[ERROR] Unsupported platform: Windows. Use Linux or macOS.`
- Safe next step: try the Linux/macOS path on a supported machine or wait for documented Windows support

This is not "one click and rich." It is a small open-source mining experiment that rewards real hardware, and the current Windows proof should be framed as a clear support gap rather than a successful beginner install.

Do not paste private keys anywhere.
```

Objection handled: "I am not technical enough."
Response: normalizes setup friction while giving a safe proof format.

### Template 3: The Retro Hardware Person

```text
Most crypto projects make old hardware feel useless.

RustChain is the first one I tried where the age of the machine is part of the point. Proof-of-Antiquity gives older real hardware a reason to show up.

My proof:

- Machine: [PowerPC / old Intel / ARM / other]
- Approximate year: [year]
- Public wallet: [RTC address]
- Miner status: [online / testing / dry-run only]
- Antiquity note: [multiplier shown or expected class]

I am not claiming this is passive income. I am claiming it is a better fate for old hardware than sitting in a closet.

If it still computes, test it.

https://rustchain.org
```

Objection handled: "Why would old hardware matter?"
Response: explains the Proof-of-Antiquity angle in plain language.

### Template 4: The Sustainability-Minded User

```text
I do not like pretending every old device is automatically e-waste.

My [device] still runs. It is not fast. It is not modern. But it can still perform real work, and RustChain gave me a simple way to test that.

Proof snapshot:

- Device: [model]
- Still boots: [yes/no]
- Setup attempt: [successful / error with note]
- Public wallet: [RTC address]
- Status command: [short output summary]

The point is not guaranteed income. The point is extending the life of useful machines and making the proof public enough that others can check it.

Before you recycle a working computer, test it once.
```

Objection handled: "Crypto is wasteful."
Response: positions RustChain as reuse-first, without overstating environmental impact.

### Template 5: The Small Workshop / Family Computer User

```text
We had an older computer sitting around because nobody wanted to be the person who threw it away.

RustChain turned that into a simple experiment:

1. Can the machine still boot?
2. Can it install the miner?
3. Can it show a public wallet?
4. Can it report status without exposing secrets?

Our result:

- Machine: [model]
- Public wallet: [RTC address]
- First command tried: clawrtc install --dry-run
- Current state: [dry-run complete / mining started / blocked by error]
- Next step: [leave running / fix setup / improve docs]

Even an error is useful if it helps the next beginner.

Try it: https://rustchain.org
```

Objection handled: "What if it fails?"
Response: makes failed setup evidence useful for onboarding feedback.

## Deliverable 2: Zero to Mining in 5 Minutes Guide

Audience: first-time user with an old laptop or desktop running Linux or macOS. Windows users should use the blocked-status template above until the published CLI supports Windows install/mining.

Safety rule: never share `C:\Users\...\default.json`, seed phrases, private keys, passwords, or full logs containing secrets. Only share public RTC addresses and redacted command output.

### Step 1: Check Python and Install the Miner

Open a terminal and run:

```bash
python --version
pip install clawrtc
```

If `python` is not found, install Python 3 first from your operating system's normal package manager or `python.org`.

Screenshot placeholder: terminal showing Python version and a successful `pip install clawrtc`.

### Step 2: Preview Before Changing Anything

Run the dry-run:

```bash
clawrtc install --dry-run
```

This is the safest first command on Linux/macOS because it previews the install path. On Windows with `clawrtc==1.8.0`, this currently exits with an unsupported-platform error; treat that as a blocker report, not as a beginner-ready install proof. If any command fails, copy only the public error message and redact usernames if desired.

Screenshot placeholder: dry-run output showing target paths and no private key material.

### Step 3: Create or View Your Wallet

If you already have a wallet, view it:

```bash
clawrtc wallet show
```

If you need a new wallet:

```bash
clawrtc wallet create
```

Record only the public RTC address. Back up the wallet file privately. Anyone with the private key file can spend your RTC.

Screenshot placeholder: wallet output with private path visible only to the user; public address can be shown.

### Step 4: Start Mining

Start the miner:

```bash
clawrtc start
```

or use the alias:

```bash
clawrtc mine
```

For a background service where supported:

```bash
clawrtc start --service
```

Screenshot placeholder: command output showing the miner attempting to connect or start.

### Step 5: Check Status and Balance

Check local miner and network status:

```bash
clawrtc status
```

Show your wallet again:

```bash
clawrtc wallet show
```

If the local wallet command cannot reach the network, you can check the public balance endpoint with your RTC address:

```bash
curl -k "https://50.28.86.131/wallet/balance?miner_id=YOUR_RTC_ADDRESS"
```

Screenshot placeholder: status output and a public balance response. Redact private paths if posting publicly.

### Common Objections and Responses

| Objection | Plain response | Proof to show |
|---|---|---|
| "Is this a scam?" | Do not deposit money. Start with a Linux/macOS dry-run and a public wallet check; on Windows, show the unsupported-platform output honestly. | `clawrtc install --dry-run` output or Windows unsupported-platform output |
| "Will it make me rich?" | No guarantee. Rewards are modest and depend on network rules and uptime. | Actual balance endpoint after a real run |
| "Will it damage my computer?" | Treat it like any sustained compute workload. Watch heat, fans, and stability. Stop if the machine struggles. | `clawrtc status`, OS temperature tools if available |
| "I am not technical." | The first useful step is only a dry-run. Errors can be shared safely if secrets are removed. | Short redacted command output |
| "Why old hardware?" | Proof-of-Antiquity gives older real hardware a reason to participate instead of being discarded. | Hardware model/year plus public status |

### Repeatable Proof Format

Use this format when posting a claim, testimonial, or help request:

```text
RustChain proof snapshot

Machine: [model and approximate year]
OS: [Windows/macOS/Linux/version]
Public RTC wallet: [RTC address only]
Command tested: [Linux/macOS dry-run / wallet show / start / status / Windows unsupported-platform check]
Result: [worked / failed with short error]
Current balance if available: [actual RTC value from wallet or balance endpoint]
Private material removed: yes
Next step: [keep mining / ask for help / improve docs]
```

## Deliverable 3: Old Hardware vs Modern Hardware on RustChain

This table is written for onboarding. It avoids made-up earnings and focuses on differences that users can verify.

| Category | Old hardware path | Modern hardware path |
|---|---|---|
| Network story | "This machine still works." | "This machine can participate too." |
| Main appeal | Reuse, nostalgia, Proof-of-Antiquity multiplier | Convenience, speed, stable setup |
| Example hardware | PowerPC G4, G5, older Intel Macs, old ThinkPads, spare desktops | Current x86 laptops, Apple Silicon, recent ARM devices |
| Multiplier framing | Vintage hardware can receive bonus multipliers; PowerPC is the clearest public example and can reach up to 2.5x in project docs/tooling. | Modern x86/ARM generally starts around the base class shown by `clawrtc --help`. |
| Setup expectation | May need more patience because old operating systems, Python versions, and paths can vary. | More likely to install cleanly with current Python and OS packages. |
| Best proof | Photo/model/year plus `clawrtc status` and public wallet balance. | Clean command output, status, and balance endpoint. |
| User risk | Heat, fan noise, old batteries, unsupported OS quirks. | Less vintage bonus, but smoother setup and better stability. |
| What not to claim | Do not invent earnings, uptime, or multiplier. | Do not claim a modern machine is vintage. |
| Best CTA | "Before you recycle it, run a dry-run." | "Try the miner and help test the network." |

### Simple Comparison Copy

```text
Old hardware is not automatically better because it is slow. It is better for RustChain when it is real, verifiable, and part of the Proof-of-Antiquity story. Modern machines are useful for testing and network growth, but vintage machines carry the emotional hook: the network values computers the upgrade cycle forgot.
```

## Acceptance Checklist

- Five testimonial-style templates included.
- Zero to Mining in 5 Minutes guide included with screenshot placeholders.
- Old hardware vs modern hardware comparison table included.
- Includes common objections and responses.
- Includes a simple repeatable proof format.
- Uses actual `clawrtc` commands verified from local CLI help.
- Does not fabricate users, earnings, GUI buttons, or payout guarantees.
