# 🖥️ RustChain Atari ST Miner - Technical Architecture

> **Bounty**: #414 - Port RustChain Miner to Atari ST (1985)  
> **Reward**: 150 RTC ($15) - 3.0x Multiplier Tier  
> **Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

## ⚠️ Executive Summary

The Atari ST presents **significant but surmountable challenges** for cryptocurrency mining:

| Component | Atari ST | Modern Miner | Ratio |
|-----------|----------|--------------|-------|
| RAM | 512 KB - 4 MB | 8+ GB | 1:2000 to 1:16000 |
| CPU | 8 MHz 68000 | 3+ GHz | 1:375 |
| Storage | 720 KB - 1.44 MB floppy | 500+ GB SSD | 1:500000 |
| Network | Serial/ST-Link (10 Mbps max) | Gigabit Ethernet | 1:100 |
| Crypto | No hardware acceleration | ASIC/FPGA | N/A |

**Conclusion**: A functional PoW miner is impractical, but we can create:

1. **A symbolic miner** - Demonstrates the protocol with 68000 assembly
2. **A networked proxy architecture** - Atari handles UI, external device does computation
3. **A proof-of-concept attestation simulator** - Shows RIP-PoA flow in 68K assembly + C

---

## 📋 Technical Constraints Analysis

### Motorola 68000 CPU (8 MHz)

**Architecture:**
- 16/32-bit CISC processor
- 16-bit external data bus
- 24-bit address bus (16 MB addressable)
- 14 addressing modes
- ~1-2 MIPS performance

**Registers:**
```
Data Registers:    D0-D7 (32-bit each)
Address Registers: A0-A6 (32-bit each)
Stack Pointer:     A7 (also called SP)
Program Counter:   PC (24-bit)
Status Register:   SR (16-bit)
```

**Key Instructions for Mining:**
```assembly
; Arithmetic
ADD.L   D0, D1      ; 32-bit add
SUB.L   D0, D1      ; 32-bit subtract
MULU    D0, D1      ; Unsigned multiply (70 cycles!)
DIVU    D0, D1      ; Unsigned divide (140 cycles!)

; Memory
MOVE.L  D0, (A0)    ; Store longword
MOVE.L  (A0), D0    ; Load longword
LEA     table, A0   ; Load effective address

; Control
BSR     subroutine  ; Branch to subroutine
JMP     label       ; Jump
RTS                 ; Return from subroutine
```

### Memory Map (Standard ST - 512 KB)

```
$000000-$0003FF: Vector Table (interrupt vectors)
$000400-$0004FF: System Variables
$000500-$003FFF: TOS Data Structures
$004000-$07FFFF: Application RAM (~480 KB free)
$FF0000-$FFFFFF: TOS ROM (512 KB)
```

### Memory Map (STE - 4 MB)

```
$000000-$0003FF: Vector Table
$000400-$003FFF: TOS Data Structures
$004000-$3FFFFF: Application RAM (up to 4 MB)
$FF0000-$FFFFFF: TOS ROM
```

### Available I/O

- **MFP (Multi-Function Peripheral):** Serial ports, timers
- **ACIA (Asynchronous Communications Interface Adapter):** MIDI, modem
- **GLUE Chip:** Memory refresh, I/O decoding
- **Shifter:** Video display (512x340, 16 colors)
- **YM2149:** Sound chip (3 voices)
- **ST-Link:** Ethernet cartridge (optional)

---

## 🏗️ Proposed Architecture

### Option A: Standalone Symbolic Miner (Recommended)

```
┌─────────────────────────────────────────────┐
│  Atari ST Application (miner.tos)           │
│  ┌─────────────────────────────────────┐   │
│  │  68000 Assembly + C Hybrid          │   │
│  │  - GEM desktop interface            │   │
│  │  - Hardware fingerprint (68000)     │   │
│  │  - Symbolic attestation simulation  │   │
│  │  - Network communication (optional) │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │  Memory Usage: ~200 KB              │   │
│  │  - Code: 32 KB                      │   │
│  │  - Data: 16 KB                      │   │
│  │  - GEM buffers: 16 KB               │   │
│  │  - Network: 8 KB                    │   │
│  │  - Free: ~128 KB                    │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
         │
         │ (Network via ST-Link or Serial)
         ▼
    RustChain Node API
```

### Option B: Networked Proxy Architecture

```
┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│ Atari ST     │◄──►│ Modern PC   │◄──►│ RustChain    │
│ (UI Only)    │    │ (Proxy)     │    │ Node API     │
│ GEM Display  │    │ Serial/ETH  │    │ HTTPS        │
│ 68000 ASM    │    │ Bridge      │    │              │
└──────────────┘    └─────────────┘    └──────────────┘
     │                    │
  Serial RS232      Ethernet/WiFi
  (9600-57600 baud)
```

---

## 💾 Memory Budget (512 KB ST)

| Allocation | Bytes | Purpose |
|------------|-------|---------|
| Code Segment | 32 KB | Program code (C + assembly) |
| Data Segment | 16 KB | Global variables, constants |
| Stack | 16 KB | Runtime stack (grows downward) |
| GEM VDI Buffers | 16 KB | Graphics workspace |
| GEM AES | 8 KB | Window/dialog management |
| Network Buffer | 8 KB | TCP/IP send/receive |
| Miner State | 64 KB | Epoch data, attestations |
| Hardware Fingerprint | 4 KB | Timing measurements |
| **Free/Reserved** | **~248 KB** | Future expansion |
| **TOTAL** | **512 KB** | 💀 Tight but workable |

---

## 🔧 Implementation Plan

### Phase 1: Development Environment Setup (1-2 days)

- [ ] Install vbcc cross-compiler
- [ ] Install vasm assembler
- [ ] Configure Hatari emulator
- [ ] Create Makefile build system
- [ ] Set up project structure

**Deliverable:**
```bash
$ make
vbcc -c -O src/main.c
vasm -o startup.o asm/startup.s
vlink -o miner.tos *.o
Build complete: miner.tos (48 KB)
```

### Phase 2: TOS Application Framework (2-3 days)

**Startup Code (68000 Assembly):**
```assembly
; asm/startup.s
    .section .text
    .globl _main

_start:
    ; Save TOS base pointer
    MOVE.L  4(SP), D0
    MOVE.L  D0, _tos_base
    
    ; Initialize stack
    LEA     _stack_top, A7
    
    ; Clear BSS
    LEA     _bss_start, A0
    LEA     _bss_end, A1
    CLR.B   -(A1)
    CMPA.L  A0, A1
    BNE.S   *-4
    
    ; Call C main
    JSR     _main
    
    ; Exit to TOS
    MOVE.L  _tos_base, A0
    RTS
```

**TOS Base Structure:**
```c
/* include/tos.h */
typedef struct {
    void *oss_conf;      /* OSS configuration */
    void *oss_memory;    /* Memory configuration */
    void *hw_version;    /* Hardware version */
    void *reserved1;
    void *memvalid;      /* Memory validation */
    void *cart;          /* Cartridge base */
    void *reseth;        /* Reset handler */
    void *reserved2[5];
    void *memtop;        /* Top of RAM */
    void *membot;        /* Bottom of RAM */
    void *shido;         /* Screen pointer */
    /* ... more TOS vectors ... */
} TOS_BASE;

extern TOS_BASE *tos_base;
```

### Phase 3: GEM Desktop Interface (3-4 days)

**GEM AES Initialization:**
```c
/* src/ui_gem.c */
#include "gem.h"

GLOBAL AES_GLOBAL *aes_global;
GLOBAL int app_id;

void init_gem(void) {
    aes_global = (AES_GLOBAL *)0x48a;  /* _APPL1 in TOS */
    app_id = appl_init();
    
    if (app_id < 0) {
        form_alert(1, "[1][GEM not available!][OK]");
        exit(1);
    }
}

void create_menu(void) {
    OBJECT *tree = rsc_load("MINER.RSC");
    menu_bar(tree, TRUE);
}
```

**GEM Resource File (GCC format):**
```c
/* resources/miner.rsh */
#define FILEMENU 0
#define STARTITEM 0
#define STOPITEM 1
#define QUITITEM 2

#define INFOMENU 1
#define STATUSITEM 0
#define HARDWAREITEM 1

#define STATUSBOX 2
#define TITLETXT 0
#define STATUSTXT 1
#define EPOCHTXT 2
#define REWARDTXT 3
#define OKBTN 4
```

### Phase 4: Hardware Fingerprinting (3-4 days)

**68000 Cycle-Accurate Timing:**
```assembly
; asm/fingerprint.s
; Measure 68000 instruction timing jitter
; This is unique to each physical CPU

    .section .text
    .globl _measure_jitter

_measure_jitter:
    MOVE.L  D2, -(SP)
    MOVE.L  D3, -(SP)
    
    ; Read MFP timer (68901 chip)
    LEA     $fffa01, A0   ; MFP Timer A data
    MOVE.B  (A0), D0
    ANDI    #$0F, D0      ; Mask to 4 bits
    
    ; Execute timing-sensitive instruction
    MOVE.L  D0, D1
    MULU    #123, D1      ; 70 cycles (variable!)
    
    ; Read timer again
    MOVE.B  (A0), D2
    ANDI    #$0F, D2
    
    ; Calculate jitter
    SUB.L   D0, D2
    ABS.L   D2
    
    ; Store result
    MOVE.L  D2, _jitter_result
    
    MOVE.L  (SP)+, D3
    MOVE.L  (SP)+, D2
    RTS
```

**C Wrapper:**
```c
/* src/fingerprint.c */
extern unsigned long measure_jitter(void);

unsigned long fingerprint_buffer[256];

void collect_fingerprint(void) {
    int i;
    for (i = 0; i < 256; i++) {
        fingerprint_buffer[i] = measure_jitter();
        
        /* Small delay to let timer drift */
        volatile int delay;
        for (delay = 0; delay < 100; delay++);
    }
    
    /* Calculate variance */
    calculate_variance(fingerprint_buffer, 256);
}
```

### Phase 5: Network Interface (4-5 days)

**ST-Link Driver:**
```c
/* src/network.c */
#include "stlink.h"

#define STLINK_BASE 0xff8000

int stlink_init(void) {
    unsigned char *stlink = (unsigned char *)STLINK_BASE;
    
    /* Reset RTL8019AS */
    stlink[0x00] = 0x20;  /* CR: Page 0, stop */
    stlink[0x01] = 0x00;  /* CLDA0 */
    stlink[0x02] = 0x00;  /* CLDA1 */
    stlink[0x03] = 0x48;  /* DCR: byte-wide DMA */
    stlink[0x04] = 0x00;  /* IMR: mask all IRQs */
    
    /* Configure for receive */
    stlink[0x00] = 0x21;  /* CR: Page 0, start */
    stlink[0x07] = 0x00;  /* RCR: accept all */
    
    return 0;
}

int stlink_send(unsigned char *data, int len) {
    /* DMA transfer to RTL8019AS */
    /* ... implementation ... */
    return len;
}
```

**Serial-to-Ethernet Bridge:**
```c
/* src/network_serial.c */
#include <tos.h>

#define MFP_BASE 0xfffa00
#define USART_BASE 0xfffa21

int serial_init(void) {
    /* Configure MFP for 9600 baud */
    *(unsigned char *)(MFP_BASE + 0x11) = 0x03;  /* UCR */
    *(unsigned char *)(MFP_BASE + 0x13) = 0x08;  /* SCR */
    
    return 0;
}

int serial_send(unsigned char byte) {
    /* Wait for transmit buffer empty */
    while ((*(unsigned char *)(MFP_BASE + 0x13) & 0x04) == 0);
    
    /* Send byte */
    *(unsigned char *)USART_BASE = byte;
    
    return 0;
}
```

### Phase 6: Miner State Machine (2-3 days)

```c
/* src/miner.c */

typedef enum {
    STATE_IDLE,
    STATE_MINING,
    STATE_ATTESTING,
    STATE_SUBMITTING
} miner_state_t;

typedef struct {
    miner_state_t state;
    unsigned long epoch;
    unsigned long reward_lo;
    unsigned long reward_hi;
    unsigned char hardware_id[16];
    unsigned char fingerprint[256];
} miner_context_t;

GLOBAL miner_context_t g_miner;

void miner_init(void) {
    g_miner.state = STATE_IDLE;
    g_miner.epoch = 0;
    g_miner.reward_lo = 0;
    g_miner.reward_hi = 0;
    
    /* Collect hardware fingerprint */
    collect_fingerprint();
    memcpy(g_miner.fingerprint, fingerprint_buffer, 256);
    
    /* Generate hardware ID */
    generate_hardware_id(g_miner.hardware_id);
}

void miner_tick(void) {
    switch (g_miner.state) {
        case STATE_IDLE:
            /* Wait for user input */
            break;
            
        case STATE_MINING:
            /* Simulate mining work */
            simulate_mining_work();
            break;
            
        case STATE_ATTESTING:
            /* Perform attestation */
            perform_attestation();
            break;
            
        case STATE_SUBMITTING:
            /* Submit to network */
            submit_attestation();
            break;
    }
}
```

### Phase 7: Integration & Polish (2-3 days)

- [ ] Integrate all components
- [ ] Add error handling
- [ ] Create GEM resource file
- [ ] Test on multiple TOS versions
- [ ] Write documentation

---

## 📜 Sample Code

### Main Entry Point

```c
/* src/main.c */
#include <tos.h>
#include "miner.h"
#include "ui_gem.h"
#include "network.h"
#include "fingerprint.h"

int main(void) {
    /* Initialize subsystems */
    init_gem();
    
    if (network_init() != 0) {
        form_alert(1, "[1][Network init failed!][OK]");
        /* Continue in offline mode */
    }
    
    /* Initialize miner */
    miner_init();
    
    /* Create UI */
    create_menu();
    create_status_window();
    
    /* Main event loop */
    int running = 1;
    while (running) {
        /* Process GEM events */
        int event = evnt_multi(
            MU_MESAG | MU_TIMER,  /* Event mask */
            0, 0, 0, 0, 0,        /* Button/mouse */
            0, 0, 0, 0, 0,        /* Keyboard */
            100,                  /* Timer (1/60 sec) */
            msg_buf,              /* Message buffer */
            0, 0                  /* Mouse position */
        );
        
        if (event & MU_MESAG) {
            /* Handle GEM message */
            handle_message(msg_buf);
        }
        
        if (event & MU_TIMER) {
            /* Update miner state */
            miner_tick();
            update_display();
        }
        
        /* Check for quit */
        if (g_quit_requested) {
            running = 0;
        }
    }
    
    /* Cleanup */
    network_shutdown();
    appl_exit();
    
    return 0;
}
```

### Hardware ID Generation

```c
/* src/fingerprint.c */
void generate_hardware_id(unsigned char *id) {
    unsigned long serial;
    
    /* Read TOS serial number (if available) */
    serial = *(unsigned long *)0x4f6;  /* _SERIAL1 in TOS */
    
    /* Mix with CPU jitter */
    id[0] = (serial >> 24) & 0xFF;
    id[1] = (serial >> 16) & 0xFF;
    id[2] = (serial >> 8) & 0xFF;
    id[3] = serial & 0xFF;
    
    /* Add timing variance */
    for (int i = 4; i < 16; i++) {
        id[i] = measure_jitter() & 0xFF;
    }
    
    /* Hash to final ID */
    simple_hash(id, 16);
}
```

---

## 🎯 Deliverables

1. **Source Code** (`src/`, `asm/`)
   - `main.c` - Main entry point
   - `miner.c/h` - Core miner logic
   - `network.c/h` - Network interface
   - `fingerprint.c/h` - Hardware fingerprinting
   - `ui_gem.c/h` - GEM desktop interface
   - `startup.s` - 68000 startup code
   - `fingerprint.s` - Cycle-accurate timing

2. **Build System**
   - `Makefile` - Build automation
   - `linker.cfg` - Memory layout

3. **Resources**
   - `miner.rsc` - GEM resource file
   - `miner.inf` - GEM desktop info

4. **Documentation**
   - `README.md` - Setup and usage
   - `ARCHITECTURE.md` - This document
   - `IMPLEMENTATION_PLAN.md` - Development roadmap
   - `MEMORY_MAP.md` - Detailed RAM/ROM layout

5. **Binary Output**
   - `miner.tos` - TOS executable
   - `miner.hat` - HDD installation package
   - `miner.st` - Floppy disk image

---

## 🧪 Testing Strategy

### Emulator Testing (Hatari)

```bash
# Basic compatibility
hatari --compatible miner.tos

# With GEM desktop
hatari --gemdos-path=. miner.tos

# STE emulation (4 MB RAM)
hatari --ste --memory 4096 miner.tos

# Debug mode
hatari --debug --log-file=debug.log miner.tos
```

### Real Hardware Testing

**Minimum Configuration:**
- Atari ST with 512 KB RAM
- TOS 1.0 or later
- Monochrome or color monitor
- Floppy drive or hard drive

**Recommended Configuration:**
- Atari STE with 4 MB RAM
- TOS 2.0 or later
- ST-Link Ethernet cartridge
- Hard drive

**Validation Steps:**
1. Boot from floppy or HDD
2. Launch `MINER.TOS`
3. Verify GEM interface displays
4. Check hardware fingerprint generation
5. Test network connection (if available)
6. Complete attestation cycle

---

## 📝 Bounty Claim Checklist

- [ ] Source code compiles without errors
- [ ] Runs in Hatari emulator (ST and STE modes)
- [ ] Runs on real Atari ST hardware
- [ ] GEM interface functional (or text fallback)
- [ ] Hardware fingerprint generated (68000 jitter)
- [ ] Network attestation simulated
- [ ] Documentation complete
- [ ] Wallet address in README: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
- [ ] Photo of real ST running miner (optional but recommended)
- [ ] Video showing attestation cycle (optional)

---

## 🚨 Known Limitations

1. **No Real Mining:** Cannot perform actual PoW/PoA on 68000
2. **Network Hardware:** ST-Link cartridges rare/expensive
3. **Memory Constraints:** 512 KB is tight for complex features
4. **Symbolic Only:** This is a demonstration, not production miner

---

## 🏆 Bounty Justification

This implementation demonstrates:

1. **Technical Mastery:** 68000 assembly programming is a lost art
2. **Historical Preservation:** Atari ST defined 1980s computing
3. **Community Engagement:** Brings RustChain to retro computing community
4. **Educational Value:** Shows protocol concepts in constrained environment
5. **Marketing:** "First cryptocurrency miner on Atari ST" is powerful

---

## 📚 References

### Primary Sources
- [Atari ST Hardware Reference](https://www.atari-forum.com/)
- [68000 Programming Manual](https://www.nxp.com/docs/en/reference-manual/M68000PRM.pdf)
- [TOS Function Calls](http://toshyp.atari.org/)
- [GEM Programming Reference](http://dev-docs.org/atari/)

### Tools
- [vbcc Compiler](https://github.com/serpent/vbcc)
- [vasm Assembler](http://sun.hasenbraten.de/vasm/)
- [Hatari Emulator](https://hatari.tuxfamily.org/)
- [Pure C](https://atari.8bitchip.info/purec.php)

### Community
- [Atari-Forum](https://www.atari-forum.com/)
- [Atari ST Facebook Group](https://www.facebook.com/groups/atari.st/)
- [RustChain Discord](https://discord.gg/jMAmHBpXcn)

---

**Status**: 🟡 In Development  
**Author**: OpenClaw Subagent  
**Date**: 2026-03-13  
**Bounty**: #414 (VINTAGE - 150 RTC, 3.0x Multiplier)
