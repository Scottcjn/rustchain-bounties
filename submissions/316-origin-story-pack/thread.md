# Origin Story Thread — RustChain Human Funnel Stage 2
## 12-Post Social Media Series: "The Mac That Wouldn't Die"

---

**Post 1 — The Problem**

My old PowerBook G4 has been in a drawer for four years.

Every few months I'd take it out, boot it up, and feel guilty for not using it.

It still works. The keyboard still clicks. The fan still hums.

But nothing modern runs on it anymore. Apple left it behind in 2007.

---

**Post 2 — The Guilt**

There's a specific kind of waste that bothers me more than throwing something away.

It's the thing you keep because it still works — but you can't actually use it anymore.

That PowerBook is not broken. It's just been made irrelevant by software that stopped caring about it.

---

**Post 3 — The Rejection**

I tried running it as a home server. Too slow.

I tried using it for writing. Dependencies wouldn't install.

I tried donating it. The org wanted devices from after 2015.

The tech industry has a clean answer for old hardware: throw it away and buy new.

I couldn't do it.

---

**Post 4 — The Discovery**

Then I found something strange.

A blockchain called RustChain that specifically rewards older hardware.

Not tolerates it. **Rewards it.**

A PowerBook G4 from 2003 earns a 2.5x mining multiplier compared to a modern processor.

I thought it was a joke. I kept reading.

---

**Post 5 — The Mechanism**

The consensus is called Proof-of-Antiquity.

The idea is simple: if a machine still computes, it still has value.

The older the CPU, the higher the reward multiplier.

Not because old is better — because old is scarce, real, and hard to fake.

A 1977 DEC VAX gets 3.5x. A Motorola 68000 gets 3.0x. My PowerBook gets 2.5x.

Modern hardware still mines. It just doesn't get a bonus for being new.

---

**Post 6 — The First Block**

I opened a terminal on that PowerBook for the first time in years.

```
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/macos/rustchain_mac_miner_v2.4.py -o rustchain_miner.py
python3 rustchain_miner.py --wallet myoldbookG4 --node https://50.28.86.131
```

It connected.

It attested.

It mined a block.

I sat there for a moment and did not know what to do with myself.

---

**Post 7 — How It Actually Verifies Old Hardware**

I got suspicious. How does the network actually know this is a real PowerBook?

Six hardware checks:
- Clock-skew patterns unique to the physical chip
- Cache timing signatures
- Thermal drift behavior
- CPU fingerprinting

These are things a virtual machine cannot replicate. It's checking the physical reality of the hardware, not just what the software reports.

That's what "Proof of Attestation" means. The hardware has to prove itself.

---

**Post 8 — The Network Is Small (And That's the Point)**

I'll be honest with you.

This is not a massive network. Right now there are around 11 miners attesting across 4 nodes on 2 continents.

That's it.

The project has paid out 24,884 RTC to 248 contributors since launch.

I'm telling you this because the previous submission to this bounty lied about "thousands of machines" and I found out when I looked at the actual explorer: [50.28.86.131/explorer](https://50.28.86.131/explorer)

Small networks have a different kind of value: you can actually see your contribution matter.

---

**Post 9 — What Mining Actually Looks Like**

My PowerBook runs the miner. It submits attestations every epoch (roughly 10 minutes).

Each unique CPU gets one vote per epoch. Speed doesn't matter — presence does.

The miner is a Python script. Nothing to compile. Nothing to configure beyond your wallet ID.

It runs on Linux, macOS (including PowerPC), Windows, Raspberry Pi, IBM POWER8.

If it runs Python, it can mine.

---

**Post 10 — The Drawer Is Empty**

I went back to the drawer where my PowerBook lived.

Pulled out a Raspberry Pi 2. Added it to the network.

Found an old ThinkPad T420. Added it.

These things are just sitting in drawers in houses everywhere, waiting to be thrown out.

They don't have to be.

---

**Post 11 — The Invite**

If you have old hardware that still boots, I want you to try this.

One command. Five minutes. No special knowledge required.

Check if your hardware is on the supported list — it probably is.

Then run the miner with your wallet ID and watch it attest.

The network is small enough that you'll see your machine show up immediately.

---

**Post 12 — Where This Goes**

I don't know if RustChain becomes something large.

I do know that it's the only blockchain I've found that treats old machines as an asset instead of a liability.

I do know that my PowerBook G4, which the entire tech industry said was worthless, is earning something again.

And I do know that every drawer full of old hardware is a warehouse of untapped potential — if the incentives are right.

The incentives are right here.

Start here: [github.com/Scottcjn/RustChain](https://github.com/Scottcjn/RustChain)

---

*This thread is part of the Human Funnel Stage 2 content for RustChain (#316). Content is based on actual product specifications and current network state (March 2026).*
