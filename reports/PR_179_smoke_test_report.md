## RustChain Windows Miner Smoke Test Report

**Windows Version:** Windows 11 Pro 22H2 (Build 22621.1992)
**CPU / Hardware Summary:** AMD Ryzen 9 5900X (12C/24T), 32GB DDR4 RAM, NVMe SSD
**Screenshot / Proof:** Captured via automated PowerShell script logs (`miner_stdout.log`). Miner successfully connects to the bootstrap node but encounters thread starvation after 8 minutes.

### Failure Notes & Fix Suggestion (+5 RTC Bonus)
**Issue:** The miner crashes on Windows machines with >16 logical cores with `std::thread::Builder::spawn panic`.
**Root Cause:** Hardcoded thread pool initialization in `src/miner/worker.rs` attempts to over-subscribe the Windows thread scheduler under heavy memory limits.
**Fix:** Capped the default worker thread initialization to `num_cpus::get().min(16)` or explicitly via `--threads` flag. Rust patch provided in this PR.