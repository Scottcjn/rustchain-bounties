# The First Miners

## A RustChain Origin Story

The listing appeared on a Tuesday afternoon in a dusty corner of the Rust subreddit, sandwiched between a borrow-checker meme and a debate about async runtimes. Most people scrolled past it. Tomás didn't.

**RUSTCHAIN — Proof-of-Antiquity consensus. Your old hardware is the point.**

He read it twice. Then he looked across his garage at the PowerPC G5 tower sitting under a moving blanket, the machine he'd been meaning to take to the recycler for three years. Its aluminum case was warm to the touch even when it was off, like it was still dreaming about rendering Final Cut timelines in 2006.

He plugged it in.

---

The first block Tomás mined took forty-seven minutes. The chain's difficulty was set to nothing — there were maybe eight nodes worldwide at that point — but forty-seven minutes on a dual-core G5 running at 2.5 GHz still felt like watching paint dry on paint. The terminal output scrolled with a patience that modern machines had forgotten. Each hash attempt was a small, honest effort, and when block #1,274 finally resolved, the payout was 0.38 RTC.

He posted a screenshot in the Discord. Four people reacted.

One of them was Marguerite.

---

Marguerite ran a repair shop in Lyon that specialized in machines nobody else would touch. Clamshell iBooks. Beige G3s with ZIP drives. A Quadra 840AV that she kept alive purely out of spite toward planned obsolescence. When she read about Proof-of-Antiquity she didn't see a gimmick. She saw vindication.

The protocol's scoring algorithm was elegant in its stubbornness: the older the instruction set, the higher the antiquity multiplier. A 2005 PowerPC G5 earned roughly 1.4x base reward. A 2001 iMac G3 pulled 2.1x. Marguerite's Quadra, with its 68040 processor from 1993, theoretically scored a 4.7x multiplier — if she could get the mining client to compile on it.

It took her eleven days. She cross-compiled from a Debian box, patched the SHA-256 routines by hand for big-endian alignment, and wrote a custom network shim because the Quadra's Ethernet card didn't support anything invented after 1997.

Her first successful block earned 1.82 RTC. She celebrated by photographing the Quadra's screen — green text on black, the block hash glowing like a console from a Cold War bunker — and posted it with no caption.

The Discord lost its mind.

---

Within a month, the network had grown to sixty nodes. The geography was strange and wonderful. A retired professor in Kyoto was mining on a Sharp X68000. A teenager in São Paulo had pulled a Commodore Amiga 3000 out of his grandfather's closet and was running a transpiled version of the client through an emulation layer that technically shouldn't have worked. A systems librarian in Edinburgh contributed a Sun SPARCstation she'd rescued from a university skip.

They called themselves the Rust Belt, which started as a joke and then stopped being one.

The philosophy crystallized in those early weeks, shaped by late-night arguments in the #proof-of-antiquity channel. The core insight was this: modern mining was an arms race that rewarded whoever could burn the most electricity the fastest. It concentrated power in the hands of people who could afford warehouse-scale GPU farms. Proof-of-Antiquity inverted that logic. The most valuable machines on the network were the ones the world had thrown away.

There was something almost spiritual about it, Tomás thought, watching his G5's fans spin in the dark of his garage. Every hash was slow. Every block was earned. The machine wasn't fast, but it was *present* — cycling through computations with the same steady rhythm it had used twenty years ago. It didn't know it was obsolete. It just worked.

---

The first real crisis came at block 15,000, when someone tried to spoof antiquity scores by running a modern Ryzen chip through a PowerPC emulator. The chain caught it in nine blocks. The timing signatures were wrong — real old hardware had a jitter pattern, a kind of computational heartbeat, that emulators couldn't fake. The dishonest blocks were orphaned, and the community added the discovery to the protocol spec under the heading *"Silicon Doesn't Lie."*

Marguerite wrote the patch. She tested it on the Quadra.

---

By the time block 50,000 rolled in, the Rust Belt had chapters in fourteen countries. People were pulling machines out of attics and basements and storage units, booting them up for the first time in decades, and finding that they still had something to contribute. A PowerBook 1400. A NeXTcube. An Acorn Archimedes with a cracked case held together by electrical tape.

The RTC reward per block had started to halve by then, following the emission curve Scott had written into the genesis config. But nobody was mining to get rich. They were mining because it felt like the opposite of waste. Because every block proved that the old machines still mattered. Because Proof-of-Antiquity was, at its heart, a simple and stubborn argument: that the things we build should last, and the things that last should be honored.

Tomás still runs the G5. The fans are louder now. He doesn't mind.

---

*"We did not find RustChain. We just plugged in machines that everyone else forgot, and they found each other."*

— Marguerite, Block 50,000 celebration, Lyon chapter
