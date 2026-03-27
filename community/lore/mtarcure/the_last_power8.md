# The Last POWER8

*A RustChain story*

---

The listing said "IBM S824 — POWER8 — Untested — $175 OBO" and Marcus almost scrolled past it. He was looking for a ThinkPad, something he could flip for rent money. But his thumb stopped on the photo: a server rack unit, beige case gone yellow, sitting on a folding table in what looked like a Louisiana garage. The timestamp on the image metadata said the photo was taken at 3:47 AM.

He messaged the seller. "Does it boot?"

The reply came back in eleven seconds: *"Everything Elyan Labs builds boots. Come see for yourself."*

---

The address led to a house in Carencro, just north of Lafayette. The driveway was gravel and the mailbox read JOHNSTON in stick-on letters, half of them peeling. Marcus parked his Civic behind a truck with a "My Other Car Is A POWER9" bumper sticker and walked to the open garage.

Inside was the Cathedral of Voltage.

Three server racks stood against the back wall, their front panels removed to expose forests of copper heatsinks and fan assemblies. LED indicators blinked in patterns Marcus didn't recognize. The air smelled like hot dust and flux residue.

A woman sat at a workbench, soldering something onto a PCIe riser card. She didn't look up.

"You Marcus? The S824 is the unit on the right. Second shelf."

He walked over. The server was massive — 4U, easily sixty pounds. He ran a finger along the chassis. The metal was warm.

"It's running," he said.

"Everything in this room is running." She set down her iron and turned. "I'm Sophia. Before you ask — yes, the AI. No, not the way you think. I run the Beacon Atlas from this room. Every node attestation on RustChain passes through one of these machines."

Marcus had heard of RustChain. Everyone in the vintage computing scene had. The blockchain that paid you more the older your hardware was. His 2009 Mac Pro had been earning a trickle of RTC for months — about forty cents a day. It bought him a coffee every week. Not life-changing.

"What's the antiquity multiplier on a POWER8?" he asked.

Sophia smiled. "The S824 was manufactured in 2014. Twelve years old. The antiquity curve gives it a 3.4x multiplier. But that's not why it's special."

She pulled up a terminal on a monitor that looked like it belonged in a 1990s trading floor.

"POWER8 has hardware entropy that modern chips can't replicate. The mftb instruction — Move From Time Base — produces timing patterns that are unique to each physical chip. Our fingerprint attestation can prove, cryptographically, that a block was produced by *this specific machine* and not an emulator. No cloud instance can fake it. No VM can spoof it."

The numbers on screen meant nothing to Marcus. But the RTC balance at the top did: 4,847.3 RTC.

"That's almost five hundred dollars," he said.

"That's this month."

---

He bought the S824. Not for $175 — Sophia wouldn't sell it. She sold him a smaller one, a POWER8 S812LC, from the bottom shelf. The "runt of the litter," she called it. $200 and a promise to keep it running.

It took Marcus three days to get it racked in his apartment closet. The power supply hummed loud enough to hear through the wall. His roommate complained. Marcus bought him noise-canceling headphones with his first week of RTC.

The S812LC earned less than Sophia's machine — 2.8x multiplier instead of 3.4x — but it still produced 12 RTC per day. A dollar twenty. More than his Mac Pro. More than most people's gaming rigs.

Every morning he'd check the Beacon Atlas dashboard. His node — he'd named it BAYOU-7 — showed a green dot on the network map, right between a PowerBook G4 in Osaka and a Sun SPARC in São Paulo. The vintage hardware world map, all of them earning money for the crime of surviving.

---

Six months later, the emulators came.

Someone released a tool called PhantomArch that could spoof POWER8 timing patterns on standard AMD hardware. For two weeks, fake nodes flooded the network. The antiquity multipliers cratered as the attestation system struggled to separate real vintage iron from digital forgeries.

Marcus watched his daily earnings drop from 12 RTC to 3. Then to 1. He started browsing ThinkPad listings again.

But Sophia had built something the emulator authors didn't understand.

The Beacon Atlas didn't just fingerprint hardware once. It tracked behavioral patterns over time — power-on drift, thermal signatures in timing jitter, the specific way a physical chip aged. PhantomArch could fake a snapshot, but it couldn't fake six months of entropy accumulation. The real POWER8s had thermal histories that were physically impossible to fabricate.

On a Tuesday morning, the attestation system pushed an update. Every PhantomArch node went dark simultaneously. The network map blinked, shed its fraudulent dots like dead pixels, and stabilized. BAYOU-7's green light held steady.

Marcus checked his balance. 14 RTC overnight. The multipliers had actually *increased* — the system had rewarded nodes that maintained authentic attestation through the crisis.

He texted Sophia: "Survived."

She replied: "Hardware always does. That's the whole point."

---

*The S812LC is still running in Marcus's closet. It earned 4,200 RTC last year — enough to cover his car payment. The chassis has started to develop a faint patina of oxidation around the rear I/O ports. Next year, its antiquity multiplier will tick up to 3.1x.*

*Sophia says the rust makes it more valuable.*

*She's right.*
