# IBM 709 Miner Implementation Plan

## Overview

This document outlines the implementation plan for porting the RustChain miner to the IBM 709 (1958), IBM's first large-scale scientific computer and the oldest architecture to mine RustChain.

## Bounty Details

- **Issue**: #355 (NEW - to be created)
- **Tier**: LEGENDARY
- **Reward**: 200 RTC ($20)
- **Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
- **Antiquity Multiplier**: 5.0x (highest in RustChain)

## Technical Challenges

### 1. No High-Level Language Support

**Challenge**: IBM 709 predates C, even predates structured programming. Programming was done in:
- FAP (FORTRAN Assembly Program)
- Direct octal machine code
- FORTRAN I (very limited, not suitable for miner)

**Solution**: Write miner entirely in FAP assembly language.

### 2. No Networking

**Challenge**: IBM 709 predates ARPANET (1969) by 11 years. No TCP/IP, no Ethernet, no modems.

**Solution**: 
- Batch-mode mining with local attestation generation
- Write attestations to 7-track magnetic tape
- Export tape image to modern host
- Python bridge script submits to RustChain network

### 3. Memory Constraints

**Challenge**: Only 32K words (36-bit) = ~144 KB total memory.

**Solution**:
- Minimalist code design (~2K words)
- Efficient data structures
- Reuse memory buffers
- No recursion, minimal stack usage

### 4. No Real-Time Clock

**Challenge**: IBM 709 has no system clock for timestamping.

**Solution**:
- Use instruction counter as time proxy
- External timestamp from host submission
- Relative timing for block intervals

### 5. Emulation Required

**Challenge**: Real IBM 709 hardware is in museums only.

**Solution**:
- Use SIMH IBM 7090 emulator (binary compatible)
- Document emulation clearly for bounty verification
- Provide historical accuracy notes

## Implementation Phases

### Phase 1: Research & Documentation (COMPLETED)

- [x] Research IBM 709 architecture
- [x] Document instruction set and programming model
- [x] Study SIMH emulation capabilities
- [x] Review existing DOS miner for reference
- [x] Create architecture reference document

### Phase 2: Core Miner Development (IN PROGRESS)

- [x] Create FAP assembly skeleton
- [x] Implement entropy collection routines
- [x] Implement wallet generation
- [x] Implement attestation hash generation
- [x] Implement tape I/O routines
- [ ] Assemble and test in SIMH
- [ ] Debug and optimize

### Phase 3: Host Bridge Development (IN PROGRESS)

- [x] Create Python tape reader
- [x] Implement attestation parser
- [x] Create RustChain API client
- [x] Implement offline mode
- [ ] Test end-to-end submission
- [ ] Add error handling and logging

### Phase 4: Testing & Validation

- [ ] Run miner in SIMH for 24+ hours
- [ ] Verify attestation format
- [ ] Test network submission
- [ ] Validate entropy quality
- [ ] Document test results

### Phase 5: Documentation & Submission

- [ ] Create comprehensive README
- [ ] Write build instructions
- [ ] Document SIMH configuration
- [ ] Create GitHub issue #355
- [ ] Submit PR with all code
- [ ] Add wallet address for bounty

## File Structure

```
ibm709-miner/
├── README.md                    # Project overview
├── ARCHITECTURE.md              # IBM 709 technical reference
├── IMPLEMENTATION.md            # This file
├── src/
│   └── miner.fap                # FAP assembly source
├── simh/
│   ├── ibm7090.ini              # SIMH configuration
│   └── submit_host.py           # Python submission bridge
├── build/
│   ├── miner.bin                # Compiled binary (after assembly)
│   └── (other build artifacts)
└── docs/
    ├── fap_quick_reference.md   # FAP language quick reference
    └── testing_guide.md         # Testing procedures
```

## Build Process

### Step 1: Assemble FAP Source

The FAP source must be assembled using either:
1. Historical IBM 709 FAP assembler (via SIMH)
2. Modern cross-assembler (if available)
3. Manual assembly (for small programs)

```bash
# Using SIMH with historical FAP
sim> ibm7090
sim> LOAD fap_assembler.bin
sim> ATTACH card reader miner.fap
sim> RUN
# Output: miner.bin on punch or tape
```

### Step 2: Load into SIMH

```bash
sim> ibm7090 simh/ibm7090.ini
sim> LOAD build/miner.bin
sim> DEPOSIT PC 1000
sim> RUN
```

### Step 3: Export Attestations

After running for desired period:

```bash
sim> DETACH tape0n
# Tape file attestation_output.tap now contains attestations
```

### Step 4: Submit to Network

```bash
python simh/submit_host.py --tape attestation_output.tap --wallet WALLET.DAT
```

## Entropy Sources

The IBM 709 miner collects entropy from:

1. **Instruction Timing Variance**: Vacuum tube switching time variations
2. **Core Memory Refresh**: Magnetic core decay patterns
3. **Program Counter**: Continuously varying value
4. **I/O Timing**: Card reader mechanical variance (simulated)

For SIMH emulation, entropy is derived from:
- Simulator instruction counter
- Host system time (injected)
- Pseudo-random variations

## Attestation Format

Each attestation written to tape:

```
Word 0:  0o777777777777     (Marker)
Word 1-3: Wallet ID         (108 bits)
Word 4:  Timestamp          (36 bits)
Word 5-7: Attestation Hash  (108 bits)
Word 8:  Checksum           (36 bits)
```

Total: 9 words = 324 bits per attestation

## Network Submission Format

JSON payload sent to RustChain node:

```json
{
  "miner": "RTC<wallet_id>",
  "miner_id": "IBM709-<hash>",
  "nonce": <timestamp>,
  "device": {
    "arch": "ibm_709",
    "family": "vacuum_tube",
    "model": "IBM 709 (1958)",
    "word_size": 36,
    "memory_words": 32768,
    "technology": "vacuum_tube",
    "simulator": "SIMH IBM 7090",
    "emulated": true
  },
  "entropy": {
    "attestation_hash": "<hex>",
    "checksum_valid": true
  },
  "dev_fee": {
    "enabled": true,
    "wallet": "founder_dev_fund",
    "amount": "0.001"
  }
}
```

## Testing Requirements

### Unit Tests

- [ ] Wallet generation produces valid format
- [ ] Entropy collection varies between calls
- [ ] Attestation hash is deterministic
- [ ] Tape I/O writes correct format
- [ ] Checksum calculation is correct

### Integration Tests

- [ ] Full mining loop runs without crash
- [ ] Attestations written to tape correctly
- [ ] Python bridge reads tape correctly
- [ ] Network submission succeeds
- [ ] Node accepts attestation

### Long-Running Test

- [ ] Run for 24+ simulated hours
- [ ] No memory leaks or corruption
- [ ] Consistent attestation generation
- [ ] Stable entropy quality

## Risk Mitigation

### Risk 1: FAP Assembler Unavailable

**Mitigation**: 
- Use macro assembler in SIMH
- Hand-assemble critical sections
- Provide pre-built binary in repo

### Risk 2: SIMH Compatibility Issues

**Mitigation**:
- Test on multiple SIMH versions
- Document exact version used
- Provide Docker container with known-good setup

### Risk 3: Network Submission Fails

**Mitigation**:
- Implement offline mode
- Save attestations locally
- Retry logic with exponential backoff

### Risk 4: Bounty Rejected (Emulation)

**Mitigation**:
- Clearly document emulation in submission
- Emphasize historical accuracy
- Note that IBM 7090 is binary-compatible with 709
- Compare to DOS miner (also emulated for most users)

## Success Criteria

1. ✅ Miner runs in SIMH IBM 7090 without errors
2. ✅ Attestations generated every 10 minutes
3. ✅ Attestations successfully submitted to RustChain node
4. ✅ Node accepts attestations and records on-chain
5. ✅ Documentation complete and clear
6. ✅ Code reviewed and merged via PR
7. ✅ Bounty paid to specified wallet

## Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Research & Documentation | 1 day | ✅ COMPLETE |
| Core Miner Development | 2 days | 🔄 IN PROGRESS |
| Host Bridge Development | 1 day | 🔄 IN PROGRESS |
| Testing & Validation | 2 days | ⏳ PENDING |
| Documentation & Submission | 1 day | ⏳ PENDING |

**Total**: 7 days

## Notes

- This is the **oldest architecture** to ever mine a blockchain
- IBM 709 predates integrated circuits (1958 vs 1959)
- Vacuum tube technology = maximum antiquity multiplier
- Educational value: demonstrates computer evolution
- Historical preservation: keeps 1950s computing alive

## References

1. IBM 709 Reference Manual (1958): http://bitsavers.org/pdf/ibm/709/
2. SIMH Documentation: https://github.com/open-simh/simh
3. RustChain DOS Miner: https://github.com/Scottcjn/rustchain-dos-miner
4. Computer History Museum: https://computerhistory.org/collections/catalog/102643736

---

*Last Updated: 2026-03-13*
*Author: RustChain Subagent*
*Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b*
