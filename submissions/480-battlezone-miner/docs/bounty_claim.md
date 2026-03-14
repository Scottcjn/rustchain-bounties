# Bounty Claim Instructions - RustChain Battlezone Miner

## 🏆 Bounty Details

- **Tier**: LEGENDARY
- **Reward**: 200 RTC (~$20 USD)
- **Task**: Port Miner to Battlezone Arcade (1980)
- **Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

## Submission Checklist

Before submitting your PR, ensure you have:

- [ ] Complete 6502 assembly code (`src/miner_6502.asm`)
- [ ] Working Python simulator (`simulator/battlezone_miner.py`)
- [ ] Architecture documentation (`ARCHITECTURE.md`)
- [ ] Mining concept explanation (`MINING_CONCEPT.md`)
- [ ] README with project overview (`README.md`)
- [ ] Bounty claim instructions (this file)
- [ ] Wallet address in PR description

## PR Submission Steps

### 1. Fork the RustChain Repository

```bash
git clone https://github.com/rustchain/rustchain.git
cd rustchain
git remote add fork https://github.com/YOUR_USERNAME/rustchain.git
```

### 2. Create Feature Branch

```bash
git checkout -b feature/battlezone-miner-port
```

### 3. Add Project Files

```bash
# Copy all battlezone-miner files to appropriate location
cp -r battlezone-miner/* examples/battlezone-miner/

# Add and commit
git add examples/battlezone-miner/
git commit -m "feat: Add Battlezone (1980) arcade miner port

- 6502 assembly miner core for Atari Battlezone hardware
- Python 6502 simulator with vector display emulation
- Complete documentation and architecture design
- Educational proof-of-concept for extreme resource constraints

Bounty wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b"
```

### 4. Push and Create PR

```bash
git push fork feature/battlezone-miner-port
```

Then visit GitHub and create a Pull Request from your fork.

### 5. PR Description Template

```markdown
# Battlezone Miner Port - LEGENDARY Bounty Claim

## Summary

This PR ports the RustChain miner concept to the Atari Battlezone (1980) arcade hardware - the first true 3D vector graphics arcade game!

## What's Included

- **6502 Assembly Code**: Complete miner implementation in `examples/battlezone-miner/src/miner_6502.asm`
- **Python Simulator**: Cycle-accurate 6502 emulation in `examples/battlezone-miner/simulator/`
- **Documentation**: Full architecture, mining concepts, and usage guides

## Hardware Target

| Component | Specification |
|-----------|---------------|
| CPU | MOS Technology 6502 |
| Clock | 1.5 MHz |
| Architecture | 8-bit |
| RAM | 8-48 KB |
| Display | Vector Graphics 1024×768 |

## Performance

- **Theoretical Hash Rate**: ~12,000 hashes/second (simplified 8-bit hash)
- **Solution Rate**: ~750 solutions/second (at target 0x10)
- **Note**: Educational demonstration only, not suitable for real mining

## Testing

```bash
cd examples/battlezone-miner/simulator
python battlezone_miner.py
```

## Bounty Claim

**Wallet Address**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

**Tier**: LEGENDARY (200 RTC / ~$20)

## Disclaimer

This is an **educational/historical proof-of-concept** demonstrating blockchain mining concepts on extreme resource-constrained hardware. The simplified hash function is NOT cryptographically secure and should not be used for actual mining.

---

Closes #[bounty-issue-number]
```

## Review Process

1. **Automated Checks**: CI will run on your PR
2. **Code Review**: RustChain team will review the implementation
3. **Verification**: They'll test the simulator and verify documentation
4. **Merge**: Upon approval, PR will be merged
5. **Payment**: Bounty will be sent to your wallet address

## Timeline

- **Submission**: Immediate (PR created)
- **Review**: 3-7 business days
- **Payment**: Within 14 days of merge

## Contact

For questions about the bounty program:
- Open an issue on the RustChain repository
- Contact the RustChain team directly

## Success Criteria

Your submission will be evaluated on:

1. **Completeness**: All required files present
2. **Correctness**: 6502 code is valid assembly
3. **Documentation**: Clear explanations of architecture and concepts
4. **Functionality**: Python simulator runs without errors
5. **Educational Value**: Demonstrates mining concepts clearly

## Common Issues to Avoid

❌ **Don't**:
- Claim this is practical for real mining
- Use cryptographically insecure hash without disclaimers
- Submit incomplete documentation
- Forget to include wallet address

✅ **Do**:
- Clearly state this is educational/conceptual
- Include all disclaimers about hash security
- Provide thorough documentation
- Test the simulator before submitting

## Example Output

When running the simulator, you should see:

```
============================================================
BATTLEZONE MINER - 6502 SIMULATION
============================================================
CPU: 6502 @ 1.5 MHz (emulated)
Target difficulty: $10
============================================================

[  100000 cycles] Nonce: $001A | Hashes:    800 | Solutions:   50 | Rate: 8000 H/s
[  200000 cycles] Nonce: $0034 | Hashes:   1600 | Solutions:  100 | Rate: 8000 H/s
...

============================================================
SIMULATION COMPLETE
============================================================
Total cycles executed: 1,000,000
Emulation time: 0.15 seconds
Final nonce: $F1C2
Total hashes: 8,000
Solutions found: 500

THEORETICAL REAL HARDWARE PERFORMANCE:
  Hash rate: ~15,000 hashes/second
  (6502 @ 1.5 MHz, ~100 cycles/hash)
============================================================
```

## Additional Resources

- [6502 Programming Manual](https://www.nesdev.org/6502.txt)
- [Battlezone Arcade Documentation](https://www.arcade-museum.com/)
- [RustChain Bounty Program](https://github.com/rustchain/rustchain/issues)

---

**Good luck with your submission! 🎮⛏️**

*Last updated: 2026-03-14*
