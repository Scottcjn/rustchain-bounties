# Pac-Man Miner Porting Strategy

## Overview

This document describes the technical approach for porting the RustChain miner to Pac-Man arcade hardware (1980).

## Architecture Design

### Minimal Viable Miner

```
┌─────────────────────────────────────────────────────────────┐
│                    Pac-Man Miner Stack                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 5: RustChain Node Communication (External)           │
│            └─> ESP8266 WiFi co-processor                    │
│                                                              │
│  Layer 4: Network Protocol (UART Serial)                    │
│            └─> Simple text-based protocol                   │
│                                                              │
│  Layer 3: Attestation Engine (Z80 Assembly)                 │
│            └─> Hardware fingerprinting                      │
│                                                              │
│  Layer 2: Timing Measurement (Z80 Native)                   │
│            └─> Cycle-accurate benchmarks                    │
│                                                              │
│  Layer 1: Hardware Access (Bare Metal)                      │
│            └─> Direct Z80 I/O operations                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Code Size Budget

| Component | Budget (bytes) | Priority |
|-----------|----------------|----------|
| Bootloader | 256 | Critical |
| Attestation Core | 512 | Critical |
| Timing Engine | 256 | High |
| UART Driver | 256 | High |
| Network Protocol | 512 | Medium |
| **Total** | **1,792 bytes** | |

Available ROM: 48 KB ✅ (plenty of space!)
Available RAM: 4 KB ✅ (minimal state needed)

## Implementation Phases

### Phase 1: Hardware Attestation (Core)

**Goal**: Prove the hardware is authentic Pac-Man arcade board

**Steps**:
1. Read CPU timing signature
2. Calculate ROM checksum
3. Generate hardware ID
4. Sign attestation (external co-processor)

**Z80 Assembly Example**:
```asm
; Measure CPU timing
measure_timing:
    LD HL, 0x0000      ; Counter
    LD B, 100          ; Iterations
    
timing_loop:
    NOP                ; 4 cycles
    NOP
    NOP
    NOP
    DJNZ timing_loop   ; Decrement B, jump if not zero
    
    ; Read timer value
    IN A, (0x00)       ; Read from timer port
    RET
```

### Phase 2: Network Interface

**Goal**: Connect to RustChain node

**Hardware Addition**:
- Add UART interface to Z80 I/O space
- Connect to ESP8266 WiFi module
- 5V ↔ 3.3V level shifting

**Protocol**:
```
Attestation Request:
  ATTEST|{hardware_id}|{timestamp}

Attestation Response:
  OK|{epoch}|{reward}|{signature}
```

### Phase 3: Mining Loop

**Goal**: Periodic attestation submission

**Algorithm**:
```
1. Wait for epoch boundary (10 minutes)
2. Perform hardware attestation
3. Send to RustChain node via UART
4. Receive reward confirmation
5. Update display (optional: show on Pac-Man screen!)
6. Repeat
```

## Memory Layout

```
┌─────────────────────────────────────────────────────────────┐
│ RAM Usage (4 KB Total)                                      │
├─────────────────────────────────────────────────────────────┤
│ 0x8000 - 0x80FF : Stack (256 bytes)                         │
│ 0x8100 - 0x81FF : Attestation Buffer (256 bytes)            │
│ 0x8200 - 0x82FF : Network Buffer (256 bytes)                │
│ 0x8300 - 0x83FF : Game State (preserve original!)           │
│ 0x8400 - 0x87FF : Free / Working Memory                     │
└─────────────────────────────────────────────────────────────┘
```

## Interrupt Handling

Pac-Man uses interrupts for:
- Video refresh (VBLANK)
- Sound generation

Miner must preserve these!

```asm
; Custom interrupt handler
miner_interrupt:
    PUSH AF            ; Save registers
    PUSH BC
    PUSH DE
    PUSH HL
    
    ; Run miner logic (if epoch boundary)
    CALL check_epoch
    
    ; Restore registers
    POP HL
    POP DE
    POP BC
    POP AF
    
    ; Jump to original interrupt handler
    JP 0x0038          ; Original Z80 interrupt vector
```

## Power Management

**Challenge**: Pac-Man runs 24/7 in arcade environment

**Solution**:
- Miner runs at low priority
- No performance impact on game
- Can be disabled during gameplay (coin-operated mode)

## Testing Strategy

### Unit Tests (Python Simulator)
- [x] Hardware attestation logic
- [x] Timing measurement
- [x] Network protocol

### Integration Tests (Hardware)
- [ ] Z80 assembly execution
- [ ] UART communication
- [ ] WiFi connectivity

### Field Tests (Real Arcade)
- [ ] Long-term stability (24+ hours)
- [ ] Temperature effects
- [ ] Power consumption

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hardware damage | High | Non-invasive modifications only |
| Game functionality | High | Preserve original code |
| Network reliability | Medium | Retry logic, offline mode |
| Reward calculation | Medium | Server-side verification |

## Success Criteria

- [ ] Attestation proves hardware authenticity
- [ ] Network connection stable
- [ ] No impact on original game
- [ ] Receives RustChain rewards
- [ ] Documentation complete

## Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Research | 1 week | None |
| Simulator | 1 week | Research |
| Assembly Core | 2 weeks | Simulator |
| Hardware Mods | 2 weeks | Assembly Core |
| Integration | 1 week | Hardware Mods |
| Testing | 1 week | Integration |
| **Total** | **8 weeks** | |

## Budget

| Item | Cost |
|------|------|
| ESP8266 Module | $5 |
| Level Shifters | $2 |
| Prototyping | $10 |
| **Total** | **$17** |

Bounty Reward: 200 RTC ($20) ✅ **Profitable!**

## Future Enhancements

1. **Display Integration**: Show mining stats on Pac-Man screen
2. **Sound Effects**: "Waka waka" on successful attestation
3. **Multi-Board**: Network multiple Pac-Man miners
4. **Leaderboard**: Compare with other vintage miners

---

**Note**: This is a conceptual demonstration. Actual hardware modification requires expertise in vintage arcade hardware and should only be attempted by qualified technicians.
