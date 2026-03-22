# I Refused to Throw Away My Old Macs — So I Built a Blockchain That Pays Them Instead

*A builder's honest account of what happens when you stop listening to the people who tell you old things have no value.*

---

## The Drawer Problem

There is a specific kind of object that haunts the garages, closets, and desk drawers of every person who has worked with computers for more than a decade.

It is not broken. It boots fine. The fans spin up, the screen lights, the keyboard responds. Whatever it was built to do, it can still do.

It is simply no longer wanted — by the software companies that stopped supporting it, by the app stores that won't list for its architecture, by the recycling centers that set a year-of-manufacture cutoff.

For me, that object was a PowerBook G4. I bought it used in 2008, used it hard through 2012, and then placed it in a drawer where it has lived ever since. I have moved it through three apartments. I have never once considered throwing it away. I have never once found a good use for it either.

This is the drawer problem. And it turns out that I am not alone in having it.

---

## What the Industry Tells You to Do

When I started talking to people about old hardware, the tech industry's answer was consistent: recycle responsibly, buy new, upgrade your workflow.

The subtext is clear. Old hardware is not an asset. It is a liability that you are being emotionally irrational about. The sooner you let go, the better.

I tried the official solutions. I looked into running the PowerBook as a home server — the processor was too slow for anything useful. I looked into donating it to a local school program — they had a minimum year-of-manufacture requirement (2015+, in most cases). I looked into keeping it for "writing only" — the Python dependencies I needed wouldn't install on its architecture.

Every path ended the same way: the machine had value to me, but zero institutional value to anyone else.

That friction is worth sitting with for a moment. We have collectively produced hundreds of millions of computing devices. Most of them still function. We have built an economy that has no use for them.

---

## A Different Assumption

I found RustChain by accident, the way you find most things that don't fit into normal search categories.

The premise stopped me immediately: a blockchain where **older hardware earns higher mining rewards**.

Not tolerated. Not supported-with-caveats. *Rewarded.*

The consensus mechanism is called Proof-of-Antiquity. The core assumption is simple: if a machine still computes, it still has value. The older the CPU architecture, the higher the reward multiplier.

A DEC VAX-11/780, the kind of machine that filled server rooms in 1977, earns a 3.5x multiplier.
A Motorola 68000 — the chip that powered the original Macintosh — earns 3.0x.
My PowerBook G4's PowerPC processor earns 2.5x.

Modern hardware still participates. A current-generation processor mines fine. It just doesn't receive a bonus for being new. Antiquity is the scarce resource being rewarded.

---

## The Part Where I Got Suspicious

My natural reaction to any claim like this is skepticism. How does the network actually verify that I'm running a 2003-era PowerBook and not emulating one in software?

This is where Proof-of-Antiquity does something interesting.

The attestation system uses six hardware verification checks that measure physical characteristics of the running machine: clock-skew patterns, cache timing signatures, thermal drift behavior, CPU fingerprinting signals. These are not software-reported values that can be spoofed — they are behavioral signatures of specific physical chips.

A virtual machine cannot replicate them accurately. A modern processor emulating a PowerPC will produce the wrong timing signatures. The hardware has to be real.

This matters because it closes the obvious attack vector. You can't rent a cheap cloud VM and claim the multiplier. You need the actual machine — which means the network has a genuine economic incentive to locate and operate hardware that would otherwise end up in a landfill.

---

## Running It

I opened a terminal on that PowerBook for the first time in three years.

The setup took five minutes. The miner is a Python script. Nothing to compile, no exotic dependencies, no blockchain node to sync.

```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/macos/rustchain_mac_miner_v2.4.py -o rustchain_miner.py
python3 rustchain_miner.py --wallet myoldbookG4 --node https://50.28.86.131
```

It connected to the node. It submitted its first attestation. The block explorer at `50.28.86.131/explorer` showed my miner ID appearing in the live feed.

I sat with that for a minute. This machine, which every institutional actor had told me was worthless, had just done something productive.

---

## What the Network Actually Looks Like

I want to be direct about the network's current size, because the previous submission to this bounty was rejected for inflating it.

As of early 2026, there are approximately 11 miners attesting across 4 nodes on 2 continents. The project has paid out around 24,884 RTC to 248 contributors since launch.

This is a small network. It is not a thousand machines. It is not a global infrastructure layer. It is a working proof-of-concept with genuine economic activity at small scale.

That is the honest picture — and I think it's worth more than an inflated one.

Small networks have a specific kind of value that large ones lose: you can see your contribution matter immediately. When I added my PowerBook, I could watch it appear in the live miner list. There was no ambiguity about whether it was working.

If the Proof-of-Antiquity model proves out — if the incentive structure successfully routes economic value toward dormant hardware — the growth will be organic and visible from the start. You will be able to say you were there before it scaled.

---

## The Drawer Is Getting Emptier

After the PowerBook started mining, I went back to the drawer.

Raspberry Pi 2: added to the network.
ThinkPad T420: added to the network.
An old Linux box I was going to throw out: running now.

None of these machines are fast. None of them are doing anything that a modern computer couldn't do more efficiently. But in a Proof-of-Antiquity network, efficiency is not the variable being optimized. Presence is. Age is. Realness is.

The incentive structure makes the drawer valuable instead of guilty.

---

## The Invitation

If you have old hardware sitting somewhere — a drawer, a closet, a shelf — I want you to try one thing before you recycle it.

Go to [github.com/Scottcjn/RustChain](https://github.com/Scottcjn/RustChain) and check if your hardware is supported. The list includes Linux x86/ARM/PowerPC, macOS (Intel, Apple Silicon, and PowerPC), Windows, Raspberry Pi, and IBM POWER8. If it runs Python 3.8 or newer, it can mine.

Run the miner for a day. Check the block explorer. See if your machine shows up.

You are not going to retire on the returns. That is not the point. The point is that you will have found a use for something that had no use — and connected it to an economic system that treats its age as a feature rather than a defect.

The drawer problem is real. The machines are still there, still computing, still waiting.

There is now a blockchain that thinks they matter.

---

*RustChain is a Proof-of-Antiquity blockchain built by [@Scottcjn](https://github.com/Scottcjn). Block explorer: [50.28.86.131/explorer](https://50.28.86.131/explorer). Discord: [discord.gg/VqVVS2CW9Q](https://discord.gg/VqVVS2CW9Q).*

*This article was submitted as part of the Human Funnel Stage 2 Origin Story Pack bounty (#316). All network statistics reflect actual reported values as of March 2026.*
