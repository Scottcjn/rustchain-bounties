# RustChain vs Helium / DePIN Networks: Proof of Antiquity as a Distinct DePIN Model

DePIN networks all prove one thing: that a participant controls a real physical resource. They differ in *what* they prove. Helium proves radio coverage; Hivemapper proves fresh road imagery; Render proves GPU render capacity; IoTeX proves device data streams. RustChain proves something the others do not — that the machine itself is real, old, and physically unique.

## Consensus mechanism

Helium's Proof of Coverage asks whether a hotspot plausibly provides RF coverage at a claimed location, via challenge-response between hotspots. Hivemapper scores map contributions against freshness and area novelty. Render verifies job-completion receipts. All of these verify *output* or *location* — what the hardware did.

RustChain's Proof of Antiquity verifies the *substrate*: six checks (cache timing, clock drift, SIMD identity traits, thermal drift, instruction jitter, anti-emulation) combine into a hardware fingerprint. The claim is not "this device did work" but "this device is a distinct, aged physical object." Age is the scarce resource, and age cannot be rushed.

## Hardware model

Helium requires purpose-built LoRaWAN hotspots, Hivemapper semi-purpose-built dashcams, Render high-end GPUs. Capital intensity is the entry gate, and identical commodity hardware is exactly what Sybil farms buy in bulk.

RustChain inverts it: existing vintage and consumer hardware — old ThinkPads, PowerBooks, Mac minis, SBCs. The trade-off is honest. RustChain gets near-zero marginal hardware cost, e-waste reuse, and long-lived device identities; it gives up throughput, geographic coverage guarantees, and the ability to bootstrap supply by simply shipping more units.

## Token model + emissions

Helium's HNT went through halvings and a migration to a burn-and-mint equilibrium; Render uses a work-priced marketplace with ongoing payouts; many DePINs emit continuously to subsidize supply growth. RustChain ties reward to antiquity multipliers under a capped supply: older, well-attested hardware earns more per unit of work. That is an emissions policy pointed at *retention of real devices* rather than *acquisition of new ones*.

## Anti-spoof model

Helium's 2023 hotspot Sybil episode showed RF proofs degrade once clone hardware costs less than the reward. RustChain's fingerprinting attacks the same failure from a different angle: cache timing, clock drift and thermal drift are analog, device-specific, and expensive to reproduce en masse. A container can fake a CPU model string, but not fifteen years of oscillator aging. It is not unbounded — a patient attacker with physical access to many old machines is the real threat model, which is why attestation history over time matters more than any single check.

## What each does better

Helium, Hivemapper and Render do things RustChain does not: they coordinate geographically meaningful coverage, fresh real-world data, and heavy compute at scale. Their purpose-built model gives clear, measurable utility and a proven growth playbook. RustChain's advantage is identity and cost: it turns already-owned hardware into verifiable infrastructure, resists bulk forgery by design, and defines a DePIN niche — vintage hardware — that the purpose-built narrative leaves empty. The honest read: DePIN does not need one model, it needs proof that survives the incentive to fake it.

---

Wallet: RTCfd7c2116f64c876c4281241abea73617f3bfacd6
