# 📋 Atari ST Miner Implementation Plan

> **Bounty**: #414 - Port RustChain Miner to Atari ST (1985)  
> **Reward**: 150 RTC ($15) - 3.0x Multiplier Tier  
> **Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`  
> **Estimated Duration**: 14-21 days

---

## 📅 Phase Timeline

### Phase 1: Environment Setup (Days 1-2)

**Goals:**
- Set up cross-compilation toolchain
- Configure Hatari emulator
- Create project structure
- Verify build system

**Tasks:**

| Task | Description | Status |
|------|-------------|--------|
| 1.1 | Install vbcc compiler | ⏳ |
| 1.2 | Install vasm assembler | ⏳ |
| 1.3 | Install Hatari emulator | ⏳ |
| 1.4 | Create directory structure | ⏳ |
| 1.5 | Write Makefile | ⏳ |
| 1.6 | Test "Hello World" build | ⏳ |

**Deliverables:**
- Working build system
- `make` produces `miner.tos`
- Emulator runs test program

---

### Phase 2: TOS Framework (Days 3-5)

**Goals:**
- Create TOS application skeleton
- Implement startup code (68000 assembly)
- Set up memory model
- Basic I/O functions

**Tasks:**

| Task | Description | Status |
|------|-------------|--------|
| 2.1 | Write `startup.s` (68000 entry) | ⏳ |
| 2.2 | Create TOS header bindings | ⏳ |
| 2.3 | Implement stack initialization | ⏳ |
| 2.4 | Set up BSS/Data segments | ⏳ |
| 2.5 | Create linker configuration | ⏳ |
| 2.6 | Test basic C function calls | ⏳ |

**Code Structure:**
```
atari-st-miner/
├── asm/
│   └── startup.s          # ← Phase 2
├── include/
│   └── tos.h              # ← Phase 2
├── src/
│   └── main.c             # ← Phase 2
└── linker.cfg             # ← Phase 2
```

**Deliverables:**
- Bootable TOS application
- Clean exit to TOS
- No crashes or exceptions

---

### Phase 3: GEM Desktop Interface (Days 6-9)

**Goals:**
- Initialize GEM AES/VDI
- Create menu bar
- Build status window
- Implement event loop

**Tasks:**

| Task | Description | Status |
|------|-------------|--------|
| 3.1 | Initialize GEM AES | ⏳ |
| 3.2 | Open VDI workstation | ⏳ |
| 3.3 | Create menu bar | ⏳ |
| 3.4 | Build status dialog | ⏳ |
| 3.5 | Implement event handler | ⏳ |
| 3.6 | Add keyboard shortcuts | ⏳ |
| 3.7 | Create resource file | ⏳ |
| 3.8 | Test UI interactions | ⏳ |

**UI Components:**
```
Menu Bar:
  [File] [Info] [Options] [Help]
  
  File → Start, Stop, Quit
  Info → Status, Hardware
  Options → Network, Settings
  Help → About, Documentation

Status Window:
  ┌────────────────────────────┐
  │ RustChain Miner v1.0       │
  ├────────────────────────────┤
  │ Status: Mining             │
  │ Epoch: 12345               │
  │ Reward: 0.0042 RTC         │
  │ Hardware: 68000 @ 8 MHz    │
  │ Network: Connected         │
  ├────────────────────────────┤
  │              [OK] [Pause]  │
  └────────────────────────────┘
```

**Deliverables:**
- Functional GEM interface
- Menu navigation works
- Status updates in real-time

---

### Phase 4: Hardware Fingerprinting (Days 10-12)

**Goals:**
- Implement 68000 cycle timing
- Measure instruction jitter
- Generate unique hardware ID
- Anti-emulation detection

**Tasks:**

| Task | Description | Status |
|------|-------------|--------|
| 4.1 | Write MFP timer access | ⏳ |
| 4.2 | Implement jitter measurement | ⏳ |
| 4.3 | Create fingerprint buffer | ⏳ |
| 4.4 | Generate hardware ID | ⏳ |
| 4.5 | Add emulator detection | ⏳ |
| 4.6 | Test on real hardware | ⏳ |

**Assembly Routines:**
```assembly
; asm/fingerprint.s

measure_jitter:
    ; Read MFP Timer A
    ; Execute MULU (70 cycles)
    ; Read timer again
    ; Calculate variance
    ; Return result
    
generate_hardware_id:
    ; Mix TOS serial
    ; Mix jitter samples
    ; Hash to 16 bytes
    ; Return ID
```

**Deliverables:**
- Unique fingerprint per CPU
- Detects emulators (Hatari, etc.)
- Fingerprint stored in attestation

---

### Phase 5: Network Interface (Days 13-16)

**Goals:**
- Implement ST-Link driver
- Add serial-to-Ethernet bridge
- Create HTTP client
- Test network communication

**Tasks:**

| Task | Description | Status |
|------|-------------|--------|
| 5.1 | Write ST-Link driver | ⏳ |
| 5.2 | Implement serial driver | ⏳ |
| 5.3 | Create TCP/IP abstraction | ⏳ |
| 5.4 | Build HTTP client | ⏳ |
| 5.5 | Test API communication | ⏳ |
| 5.6 | Add error handling | ⏳ |

**Network Abstraction:**
```c
/* src/network.h */
typedef struct {
    int (*init)(void);
    int (*send)(unsigned char *data, int len);
    int (*recv)(unsigned char *buffer, int max_len);
    void (*shutdown)(void);
} network_driver_t;

/* Drivers */
extern network_driver_t stlink_driver;
extern network_driver_t serial_driver;
```

**API Endpoints:**
```
POST /api/v1/miners/register
  - hardware_id
  - fingerprint
  - client_version

POST /api/v1/miners/attest
  - epoch
  - proof
  - signature

GET /api/v1/miners/status
  - reward_balance
  - attestation_count
```

**Deliverables:**
- Network initialization works
- Can send/receive data
- API integration functional

---

### Phase 6: Miner Integration (Days 17-19)

**Goals:**
- Integrate all components
- Implement state machine
- Add attestation logic
- Polish UI

**Tasks:**

| Task | Description | Status |
|------|-------------|--------|
| 6.1 | Create miner state machine | ⏳ |
| 6.2 | Implement attestation cycle | ⏳ |
| 6.3 | Add reward tracking | ⏳ |
| 6.4 | Integrate network calls | ⏳ |
| 6.5 | Polish UI display | ⏳ |
| 6.6 | Add error messages | ⏳ |
| 6.7 | Test full workflow | ⏳ |

**State Machine:**
```
IDLE ──[Start]──> MINING ──[Epoch Complete]──> ATTESTING
  ▲                                         │
  │                                         │
  └────────────[Error]──────────────────────┘
                    │
                    ▼
               SUBMITTING ──[Success]──> IDLE
```

**Deliverables:**
- Complete mining workflow
- Attestation cycle works
- UI reflects state changes

---

### Phase 7: Testing & Documentation (Days 20-21)

**Goals:**
- Test on multiple configurations
- Write documentation
- Prepare bounty submission
- Create demo assets

**Tasks:**

| Task | Description | Status |
|------|-------------|--------|
| 7.1 | Test on Hatari (ST mode) | ⏳ |
| 7.2 | Test on Hatari (STE mode) | ⏳ |
| 7.3 | Test on real hardware | ⏳ |
| 7.4 | Write README | ⏳ |
| 7.5 | Create screenshots | ⏳ |
| 7.6 | Record demo video | ⏳ |
| 7.7 | Submit bounty | ⏳ |

**Test Matrix:**

| Configuration | TOS Version | RAM | Network | Status |
|---------------|-------------|-----|---------|--------|
| Hatari ST | 1.0 | 512 KB | None | ⏳ |
| Hatari ST | 1.4 | 512 KB | None | ⏳ |
| Hatari STE | 2.0 | 1 MB | ST-Link | ⏳ |
| Hatari STE | 4.0 | 4 MB | ST-Link | ⏳ |
| Real ST | 1.0 | 512 KB | None | ⏳ |
| Real STE | 2.0+ | 4 MB | ST-Link | ⏳ |

**Deliverables:**
- All tests pass
- Documentation complete
- Bounty submitted

---

## 📦 Source Code Outline

### Directory Structure

```
atari-st-miner/
├── README.md                  ← Complete
├── ARCHITECTURE.md            ← Complete
├── IMPLEMENTATION_PLAN.md     ← This file
├── Makefile                   ← Phase 1
├── linker.cfg                 ← Phase 2
│
├── src/
│   ├── main.c                 ← Phase 2
│   ├── miner.c                ← Phase 6
│   ├── miner.h                ← Phase 6
│   ├── network.c              ← Phase 5
│   ├── network.h              ← Phase 5
│   ├── fingerprint.c          ← Phase 4
│   ├── fingerprint.h          ← Phase 4
│   ├── ui_gem.c               ← Phase 3
│   ├── ui_gem.h               ← Phase 3
│   └── ui_text.c              ← Phase 3 (fallback)
│
├── asm/
│   ├── startup.s              ← Phase 2
│   ├── fingerprint.s          ← Phase 4
│   └── crypto.s               ← Phase 6 (optional)
│
├── include/
│   ├── tos.h                  ← Phase 2
│   ├── gem.h                  ← Phase 3
│   ├── stlink.h               ← Phase 5
│   └── miner_config.h         ← Phase 1
│
├── resources/
│   ├── miner.rsh              ← Phase 3
│   ├── miner.rsc              ← Phase 3 (compiled)
│   └── miner.inf              ← Phase 3
│
└── docs/
    ├── screenshots/           ← Phase 7
    └── hardware/              ← Phase 7
```

---

## 🔨 Build System

### Makefile Targets

```makefile
# Default build
make              # Build for standard ST (512 KB)

# Alternative configurations
make ste          # Build for STE (1-4 MB)
make debug        # Build with debug symbols

# Utilities
make clean        # Remove build artifacts
make run          # Run in Hatari
make hat          # Create .HAT package
make disk         # Create floppy image

# Documentation
make docs         # Generate documentation
make screenshots  # Capture emulator screenshots
```

### Build Process

```bash
# 1. Compile C sources
vbcc -c -O -Iinclude src/main.c -o main.o
vbcc -c -O -Iinclude src/miner.c -o miner.o
vbcc -c -O -Iinclude src/network.c -o network.o
vbcc -c -O -Iinclude src/fingerprint.c -o fingerprint.o
vbcc -c -O -Iinclude src/ui_gem.c -o ui_gem.o

# 2. Assemble 68000 code
vasm -o startup.o asm/startup.s
vasm -o fingerprint_asm.o asm/fingerprint.s

# 3. Link
vlink -o miner.tos -t tos \
    startup.o main.o miner.o network.o \
    fingerprint.o fingerprint_asm.o ui_gem.o

# Output: miner.tos (48-64 KB)
```

---

## ✅ Acceptance Criteria

### Minimum Viable Product (MVP)

- [ ] Compiles without errors
- [ ] Boots in Hatari emulator
- [ ] Displays GEM interface
- [ ] Shows miner status
- [ ] Generates hardware fingerprint
- [ ] Simulates attestation cycle

### Full Implementation

- [ ] All MVP criteria met
- [ ] Network communication works (ST-Link or serial)
- [ ] Real API integration
- [ ] Runs on real hardware
- [ ] Complete documentation
- [ ] Demo video

### Bounty Claim Requirements

- [ ] Source code on GitHub
- [ ] MIT license
- [ ] README with wallet address
- [ ] Build instructions
- [ ] Photo of real ST running miner (recommended)
- [ ] Video of attestation cycle (recommended)
- [ ] Screenshot from rustchain.org/api/miners

---

## 🚨 Risk Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Toolchain issues | Medium | High | Use well-tested vbcc/vasm |
| Memory constraints | High | Medium | Careful budgeting, optimize |
| Network hardware unavailable | High | Medium | Provide serial fallback |
| Real hardware testing | Medium | High | Use emulator initially |

### Schedule Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| GEM complexity | Medium | Medium | Use simple UI initially |
| Fingerprint accuracy | Low | High | Test on multiple systems |
| API changes | Low | Medium | Abstract network layer |

---

## 📊 Progress Tracking

### Phase Completion

```
Phase 1: Environment Setup        [  0%] ⏳
Phase 2: TOS Framework            [  0%] ⏳
Phase 3: GEM Interface            [  0%] ⏳
Phase 4: Hardware Fingerprint     [  0%] ⏳
Phase 5: Network Interface        [  0%] ⏳
Phase 6: Miner Integration        [  0%] ⏳
Phase 7: Testing & Docs           [  0%] ⏳
                                   ───────
TOTAL PROGRESS                    [  0%] 🟡
```

### Daily Goals

| Day | Focus | Deliverable |
|-----|-------|-------------|
| 1-2 | Environment | Working toolchain |
| 3-5 | TOS Framework | Bootable application |
| 6-9 | GEM Interface | Functional UI |
| 10-12 | Fingerprint | Hardware ID |
| 13-16 | Network | API communication |
| 17-19 | Integration | Complete workflow |
| 20-21 | Testing | Bounty submission |

---

## 📝 Notes

### Development Tips

1. **Start simple:** Get "Hello World" working first
2. **Test frequently:** Use Hatari for rapid iteration
3. **Save often:** Version control with Git
4. **Document as you go:** Update README continuously
5. **Ask for help:** Atari-Forum community is helpful

### Useful Commands

```bash
# Check file size
ls -l miner.tos

# Verify TOS header
hexdump -C miner.tos | head

# Run in emulator
hatari --compatible miner.tos

# Debug mode
hatari --debug --log-file=debug.log miner.tos
```

### Reference Materials

- [vbcc Manual](https://github.com/serpent/vbcc/blob/master/README)
- [vasm Manual](http://sun.hasenbraten.de/vasm/release/vasm.pdf)
- [Hatari User Guide](https://hatari.tuxfamily.org/manual/)
- [TOS Function Calls](http://toshyp.atari.org/)
- [GEM Programming](http://dev-docs.org/atari/)

---

**Last Updated:** 2026-03-13  
**Author:** OpenClaw Subagent  
**Status:** 🟡 Planning Phase
