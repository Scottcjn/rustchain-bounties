//! Hardware Fingerprinting Module
//! 
//! Implements 7 hardware fingerprint checks:
//! 1. Clock-Skew & Oscillator Drift
//! 2. Cache Timing Fingerprint
//! 3. SIMD Unit Identity
//! 4. Thermal Drift Entropy
//! 5. Instruction Path Jitter
//! 6. Device-Age Oracle Fields
//! 7. Anti-Emulation Behavioral Checks

use anyhow::{Result, anyhow};
use serde::{Serialize, Deserialize};
use sha2::{Sha256, Digest};
use std::time::{Duration, Instant};
use std::collections::HashMap;

#[cfg(target_os = "linux")]
use std::fs;

#[cfg(target_arch = "x86_64")]
use raw_cpuid::CpuId;

/// Hardware fingerprint results
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HardwareFingerprint {
    pub clock_drift: ClockDriftResult,
    pub cache_timing: CacheTimingResult,
    pub simd_profile: SIMDProfile,
    pub thermal_drift: ThermalDriftResult,
    pub instruction_jitter: InstructionJitterResult,
    pub device_oracle: DeviceOracle,
    pub anti_emulation: AntiEmulationResult,
    pub checks_passed: usize,
    pub checks_total: usize,
    pub all_valid: bool,
    pub timestamp: u64,
}

/// Check 1: Clock-Skew & Oscillator Drift
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClockDriftResult {
    pub mean_ns: f64,
    pub variance: f64,
    pub stdev: f64,
    pub drift_mean: f64,
    pub drift_variance: f64,
    pub drift_hash: String,
    pub samples: usize,
    pub valid: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub fail_reason: Option<String>,
}

/// Check 2: Cache Timing Fingerprint
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CacheTimingResult {
    pub latencies: HashMap<String, CacheLatency>,
    pub tone_ratios: Vec<f64>,
    pub cache_hash: String,
    pub valid: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub fail_reason: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CacheLatency {
    pub sequential_ns: f64,
    pub random_ns: f64,
    pub seq_variance: f64,
    pub rand_variance: f64,
}

/// Check 3: SIMD Unit Identity
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SIMDProfile {
    pub simd_type: String,
    pub int_mean_ns: f64,
    pub float_mean_ns: f64,
    pub int_float_ratio: f64,
    pub vector_mean_ns: f64,
    pub vector_variance: f64,
    pub valid: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub fail_reason: Option<String>,
}

/// Check 4: Thermal Drift Entropy
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ThermalDriftResult {
    pub cold_mean_ns: f64,
    pub hot_mean_ns: f64,
    pub cooldown_mean_ns: f64,
    pub thermal_drift_pct: f64,
    pub recovery_pct: f64,
    pub valid: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub fail_reason: Option<String>,
}

/// Check 5: Instruction Path Jitter
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InstructionJitterResult {
    pub jitter_map: HashMap<String, JitterStats>,
    pub avg_jitter_stdev: f64,
    pub valid: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub fail_reason: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JitterStats {
    pub mean: f64,
    pub stdev: f64,
    pub min: f64,
    pub max: f64,
}

/// Check 6: Device-Age Oracle
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeviceOracle {
    pub machine: String,
    pub processor: String,
    pub system: String,
    pub cpu_model: Option<String>,
    pub cpu_family: Option<String>,
    pub stepping: Option<String>,
    pub estimated_release_year: Option<i32>,
    pub estimated_age_years: Option<i32>,
    pub valid: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub fail_reason: Option<String>,
}

/// Check 7: Anti-Emulation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AntiEmulationResult {
    pub hypervisor_detected: bool,
    pub time_dilation: bool,
    pub uniform_jitter: bool,
    pub vm_artifacts: Vec<String>,
    pub sleep_mean_ns: f64,
    pub sleep_variance: f64,
    pub jitter_cv: f64,
    pub valid: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub fail_reason: Option<String>,
}

/// Mining work result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MiningWorkResult {
    pub fingerprint_hash: String,
    pub work_proof: String,
    pub timestamp: u64,
    pub difficulty_met: bool,
}

/// Collect all hardware fingerprints
pub fn collect_all_fingerprints() -> Result<HardwareFingerprint> {
    log::info!("  [1/7] Clock-Skew & Oscillator Drift...");
    let clock_drift = collect_clock_drift(1000)?;
    
    log::info!("  [2/7] Cache Timing Fingerprint...");
    let cache_timing = collect_cache_timing(100)?;
    
    log::info!("  [3/7] SIMD Unit Identity...");
    let simd_profile = collect_simd_profile()?;
    
    log::info!("  [4/7] Thermal Drift Entropy...");
    let thermal_drift = collect_thermal_drift(50)?;
    
    log::info!("  [5/7] Instruction Path Jitter...");
    let instruction_jitter = collect_instruction_jitter(500)?;
    
    log::info!("  [6/7] Device-Age Oracle...");
    let device_oracle = collect_device_oracle()?;
    
    log::info!("  [7/7] Anti-Emulation Checks...");
    let anti_emulation = check_anti_emulation()?;
    
    // Count passed checks
    let checks_passed = [
        clock_drift.valid,
        cache_timing.valid,
        simd_profile.valid,
        thermal_drift.valid,
        instruction_jitter.valid,
        device_oracle.valid,
        anti_emulation.valid,
    ].iter().filter(|&&x| x).count();
    
    Ok(HardwareFingerprint {
        clock_drift,
        cache_timing,
        simd_profile,
        thermal_drift,
        instruction_jitter,
        device_oracle,
        anti_emulation,
        checks_passed,
        checks_total: 7,
        all_valid: checks_passed == 7,
        timestamp: std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)?
            .as_secs(),
    })
}

/// Check 1: Clock-Skew & Oscillator Drift
fn collect_clock_drift(samples: usize) -> Result<ClockDriftResult> {
    let mut intervals = Vec::with_capacity(samples);
    let reference_ops = 10000;
    
    for i in 0..samples {
        let data = format!("drift_sample_{}", i);
        let start = Instant::now();
        for _ in 0..reference_ops {
            let mut hasher = Sha256::new();
            hasher.update(data.as_bytes());
            let _ = hasher.finalize();
        }
        let elapsed = start.elapsed().as_nanos() as f64;
        intervals.push(elapsed);
        
        // Small delay to capture oscillator drift
        if i % 100 == 0 {
            std::thread::sleep(Duration::from_millis(1));
        }
    }
    
    let mean_interval = mean(&intervals);
    let variance = sample_variance(&intervals);
    let stdev = variance.sqrt();
    
    // Drift signature
    let drifts: Vec<f64> = intervals.windows(2)
        .map(|w| (w[1] - w[0]).abs())
        .collect();
    let drift_mean = mean(&drifts);
    let drift_variance = sample_variance(&drifts);
    
    // Generate drift hash
    let mut hasher = Sha256::new();
    hasher.update(mean_interval.to_le_bytes());
    hasher.update(variance.to_le_bytes());
    hasher.update(drift_mean.to_le_bytes());
    hasher.update(drift_variance.to_le_bytes());
    let drift_hash = format!("{:x}", hasher.finalize())[..16].to_string();
    
    let valid = variance > 0.0;
    let fail_reason = if !valid { Some("no_variance_detected".to_string()) } else { None };
    
    Ok(ClockDriftResult {
        mean_ns: mean_interval,
        variance,
        stdev,
        drift_mean,
        drift_variance,
        drift_hash,
        samples,
        valid,
        fail_reason,
    })
}

/// Check 2: Cache Timing Fingerprint
fn collect_cache_timing(iterations: usize) -> Result<CacheTimingResult> {
    let buffer_sizes = vec![
        4 * 1024,       // 4KB - L1
        32 * 1024,      // 32KB - L1/L2
        256 * 1024,     // 256KB - L2
        1024 * 1024,    // 1MB - L2/L3
        4 * 1024 * 1024, // 4MB - L3
    ];
    
    let mut latencies = HashMap::new();
    
    for size in buffer_sizes {
        let buf = vec![0u8; size];
        
        // Sequential access
        let seq_times: Vec<f64> = (0..iterations).map(|_| {
            let start = Instant::now();
            for j in (0..size.min(65536)).step_by(64) {
                let _ = &buf[j];
            }
            start.elapsed().as_nanos() as f64
        }).collect();
        
        // Random access
        let rand_times: Vec<f64> = (0..iterations).map(|_| {
            let start = Instant::now();
            for _ in 0..1000 {
                let idx = rand::random::<usize>() % size;
                let _ = &buf[idx];
            }
            start.elapsed().as_nanos() as f64
        }).collect();
        
        let key = format!("{}KB", size / 1024);
        latencies.insert(key, CacheLatency {
            sequential_ns: mean(&seq_times),
            random_ns: mean(&rand_times),
            seq_variance: sample_variance(&seq_times),
            rand_variance: sample_variance(&rand_times),
        });
    }
    
    // Calculate tone ratios
    let keys: Vec<_> = latencies.keys().cloned().collect();
    let mut tone_ratios = Vec::new();
    for i in 0..keys.len().saturating_sub(1) {
        if let (Some(a), Some(b)) = (latencies.get(&keys[i]), latencies.get(&keys[i + 1])) {
            if a.random_ns > 0.0 {
                tone_ratios.push(b.random_ns / a.random_ns);
            }
        }
    }
    
    // Generate cache hash
    let mut hasher = Sha256::new();
    for ratio in &tone_ratios {
        hasher.update(ratio.to_le_bytes());
    }
    let cache_hash = format!("{:x}", hasher.finalize())[..16].to_string();
    
    let valid = !tone_ratios.is_empty();
    let fail_reason = if !valid { Some("no_cache_hierarchy".to_string()) } else { None };
    
    Ok(CacheTimingResult {
        latencies,
        tone_ratios,
        cache_hash,
        valid,
        fail_reason,
    })
}

/// Check 3: SIMD Unit Identity
fn collect_simd_profile() -> Result<SIMDProfile> {
    let machine = std::env::consts::ARCH.to_lowercase();
    
    // Detect SIMD type
    let simd_type = detect_simd_type(&machine);
    
    // Measure integer vs float operation bias
    let int_times: Vec<f64> = (0..100).map(|_| {
        let start = Instant::now();
        let mut x: i64 = 12345678;
        for _ in 0..10000 {
            x = (x * 1103515245 + 12345) & 0x7FFFFFFF;
        }
        start.elapsed().as_nanos() as f64
    }).collect();
    
    let float_times: Vec<f64> = (0..100).map(|_| {
        let start = Instant::now();
        let mut y: f64 = 1.23456789;
        for _ in 0..10000 {
            y = y * 1.0000001 + 0.0000001;
        }
        start.elapsed().as_nanos() as f64
    }).collect();
    
    let int_mean = mean(&int_times);
    let float_mean = mean(&float_times);
    let int_float_ratio = if float_mean > 0.0 { int_mean / float_mean } else { 0.0 };
    
    // Vector latency test
    let mut buf = vec![0u8; 1024 * 1024];
    let vector_latencies: Vec<f64> = (0..50).map(|_| {
        let start = Instant::now();
        for i in (0..buf.len().saturating_sub(128)).step_by(128) {
            buf[i..i+64].copy_from_slice(&buf[i+64..i+128]);
        }
        start.elapsed().as_nanos() as f64
    }).collect();
    
    let vector_mean = mean(&vector_latencies);
    let vector_variance = sample_variance(&vector_latencies);
    
    let valid = simd_type != "unknown";
    let fail_reason = if !valid { Some("simd_type_unknown".to_string()) } else { None };
    
    Ok(SIMDProfile {
        simd_type,
        int_mean_ns: int_mean,
        float_mean_ns: float_mean,
        int_float_ratio,
        vector_mean_ns: vector_mean,
        vector_variance,
        valid,
        fail_reason,
    })
}

fn detect_simd_type(arch: &str) -> String {
    #[cfg(target_arch = "x86_64")]
    {
        let cpuid = CpuId::new();
        if cpuid.get_feature_info().map_or(false, |f| f.has_avx2()) {
            return "avx2".to_string();
        } else if cpuid.get_feature_info().map_or(false, |f| f.has_avx()) {
            return "avx".to_string();
        } else if cpuid.get_feature_info().map_or(false, |f| f.has_sse2()) {
            return "sse2".to_string();
        }
    }
    
    match arch {
        "powerpc64" | "powerpc" => "altivec".to_string(),
        "aarch64" | "arm64" => "neon".to_string(),
        "x86_64" => "sse_avx".to_string(),
        _ => "unknown".to_string(),
    }
}

/// Check 4: Thermal Drift Entropy
fn collect_thermal_drift(samples: usize) -> Result<ThermalDriftResult> {
    // Cold phase
    let cold_times: Vec<f64> = (0..samples).map(|_| {
        let start = Instant::now();
        let data = b"thermal_test".repeat(1000);
        for _ in 0..100 {
            let mut hasher = Sha256::new();
            hasher.update(&data);
            let _ = hasher.finalize();
        }
        start.elapsed().as_nanos() as f64
    }).collect();
    let cold_mean = mean(&cold_times);
    
    // Heat up phase
    let heat_times: Vec<f64> = (0..samples * 3).map(|_| {
        let start = Instant::now();
        let data = b"thermal_heat".repeat(1000);
        for _ in 0..500 {
            let mut hasher = Sha256::new();
            hasher.update(&data);
            let _ = hasher.finalize();
        }
        start.elapsed().as_nanos() as f64
    }).collect();
    let hot_mean = mean(&heat_times[heat_times.len() - samples..]);
    
    // Cooldown phase
    std::thread::sleep(Duration::from_millis(100));
    let cooldown_times: Vec<f64> = (0..samples).map(|_| {
        let start = Instant::now();
        let data = b"thermal_cool".repeat(1000);
        for _ in 0..100 {
            let mut hasher = Sha256::new();
            hasher.update(&data);
            let _ = hasher.finalize();
        }
        start.elapsed().as_nanos() as f64
    }).collect();
    let cooldown_mean = mean(&cooldown_times);
    
    let thermal_drift = if cold_mean > 0.0 { (hot_mean - cold_mean) / cold_mean } else { 0.0 };
    let recovery_rate = if cold_mean > 0.0 { (cooldown_mean - cold_mean) / cold_mean } else { 0.0 };
    
    let valid = thermal_drift.abs() > 0.001;
    let fail_reason = if !valid { Some("no_thermal_drift".to_string()) } else { None };
    
    Ok(ThermalDriftResult {
        cold_mean_ns: cold_mean,
        hot_mean_ns: hot_mean,
        cooldown_mean_ns: cooldown_mean,
        thermal_drift_pct: thermal_drift * 100.0,
        recovery_pct: recovery_rate * 100.0,
        valid,
        fail_reason,
    })
}

/// Check 5: Instruction Path Jitter
fn collect_instruction_jitter(samples: usize) -> Result<InstructionJitterResult> {
    let mut jitter_map = HashMap::new();
    
    // Integer jitter
    let int_jitter: Vec<f64> = (0..samples).map(|_| {
        let start = Instant::now();
        let mut x: i64 = 0;
        for i in 0..1000 {
            x += i * 3 - i / 2;
        }
        start.elapsed().as_nanos() as f64
    }).collect();
    
    jitter_map.insert("integer".to_string(), JitterStats {
        mean: mean(&int_jitter),
        stdev: sample_stdev(&int_jitter),
        min: int_jitter.iter().cloned().fold(f64::INFINITY, f64::min),
        max: int_jitter.iter().cloned().fold(f64::NEG_INFINITY, f64::max),
    });
    
    // Branch jitter
    let branch_jitter: Vec<f64> = (0..samples).map(|_| {
        let start = Instant::now();
        let mut count: i64 = 0;
        for i in 0..1000 {
            if i % 2 == 0 {
                count += 1;
            } else {
                count -= 1;
            }
        }
        start.elapsed().as_nanos() as f64
    }).collect();
    
    jitter_map.insert("branch".to_string(), JitterStats {
        mean: mean(&branch_jitter),
        stdev: sample_stdev(&branch_jitter),
        min: branch_jitter.iter().cloned().fold(f64::INFINITY, f64::min),
        max: branch_jitter.iter().cloned().fold(f64::NEG_INFINITY, f64::max),
    });
    
    // FPU jitter
    let fpu_jitter: Vec<f64> = (0..samples).map(|_| {
        let start = Instant::now();
        let mut y: f64 = 1.0;
        for i in 0..1000 {
            y = y * 1.0001 + 0.0001;
        }
        start.elapsed().as_nanos() as f64
    }).collect();
    
    jitter_map.insert("fpu".to_string(), JitterStats {
        mean: mean(&fpu_jitter),
        stdev: sample_stdev(&fpu_jitter),
        min: fpu_jitter.iter().cloned().fold(f64::INFINITY, f64::min),
        max: fpu_jitter.iter().cloned().fold(f64::NEG_INFINITY, f64::max),
    });
    
    // Memory jitter
    let mut buf = vec![0u8; 4096];
    let mem_jitter: Vec<f64> = (0..samples).map(|_| {
        let start = Instant::now();
        for i in 0..1000 {
            buf[i % 4096] = (i & 0xFF) as u8;
            let _ = buf[(i * 7) % 4096];
        }
        start.elapsed().as_nanos() as f64
    }).collect();
    
    jitter_map.insert("memory".to_string(), JitterStats {
        mean: mean(&mem_jitter),
        stdev: sample_stdev(&mem_jitter),
        min: mem_jitter.iter().cloned().fold(f64::INFINITY, f64::min),
        max: mem_jitter.iter().cloned().fold(f64::NEG_INFINITY, f64::max),
    });
    
    let all_stdevs: Vec<f64> = jitter_map.values().map(|v| v.stdev).collect();
    let avg_jitter_stdev = mean(&all_stdevs);
    
    let valid = avg_jitter_stdev > 100.0;
    let fail_reason = if !valid { Some("no_jitter_detected".to_string()) } else { None };
    
    Ok(InstructionJitterResult {
        jitter_map,
        avg_jitter_stdev,
        valid,
        fail_reason,
    })
}

/// Check 6: Device-Age Oracle
fn collect_device_oracle() -> Result<DeviceOracle> {
    let mut oracle = DeviceOracle {
        machine: std::env::consts::ARCH.to_string(),
        processor: String::new(),
        system: std::env::consts::OS.to_string(),
        cpu_model: None,
        cpu_family: None,
        stepping: None,
        estimated_release_year: None,
        estimated_age_years: None,
        valid: false,
        fail_reason: None,
    };
    
    // Try to get CPU info
    #[cfg(target_os = "linux")]
    {
        if let Ok(cpuinfo) = fs::read_to_string("/proc/cpuinfo") {
            for line in cpuinfo.lines() {
                if line.starts_with("model name") {
                    if let Some(val) = line.split(':').nth(1) {
                        oracle.cpu_model = Some(val.trim().to_string());
                    }
                } else if line.starts_with("cpu family") {
                    if let Some(val) = line.split(':').nth(1) {
                        oracle.cpu_family = Some(val.trim().to_string());
                    }
                } else if line.starts_with("stepping") {
                    if let Some(val) = line.split(':').nth(1) {
                        oracle.stepping = Some(val.trim().to_string());
                    }
                }
            }
        }
    }
    
    #[cfg(target_os = "macos")]
    {
        if let Ok(output) = std::process::Command::new("sysctl")
            .args(&["-n", "machdep.cpu.brand_string"])
            .output()
        {
            if output.status.success() {
                oracle.cpu_model = Some(String::from_utf8_lossy(&output.stdout).trim().to_string());
            }
        }
    }
    
    // Estimate release year
    if let Some(ref model) = oracle.cpu_model {
        let model_lower = model.to_lowercase();
        let year = estimate_cpu_year(&model_lower);
        oracle.estimated_release_year = Some(year);
        oracle.estimated_age_years = Some(2026 - year);
    }
    
    oracle.valid = oracle.cpu_model.is_some() || !oracle.processor.is_empty();
    if !oracle.valid {
        oracle.fail_reason = Some("cpu_info_unavailable".to_string());
    }
    
    Ok(oracle)
}

fn estimate_cpu_year(model: &str) -> i32 {
    if model.contains("g4") || model.contains("7450") {
        2003
    } else if model.contains("g5") || model.contains("970") {
        2005
    } else if model.contains("core 2") {
        2006
    } else if model.contains("nehalem") {
        2008
    } else if model.contains("sandy") {
        2011
    } else if model.contains("m1") {
        2020
    } else if model.contains("m2") {
        2022
    } else if model.contains("m3") {
        2023
    } else {
        2020 // default
    }
}

/// Check 7: Anti-Emulation
fn check_anti_emulation() -> Result<AntiEmulationResult> {
    let mut result = AntiEmulationResult {
        hypervisor_detected: false,
        time_dilation: false,
        uniform_jitter: false,
        vm_artifacts: Vec::new(),
        sleep_mean_ns: 0.0,
        sleep_variance: 0.0,
        jitter_cv: 0.0,
        valid: true,
        fail_reason: None,
    };
    
    // Check for hypervisor via CPUID (x86_64)
    #[cfg(target_arch = "x86_64")]
    {
        let cpuid = CpuId::new();
        if cpuid.get_feature_info().map_or(false, |f| f.has_hypervisor()) {
            result.hypervisor_detected = true;
            result.vm_artifacts.push("cpuid_hypervisor_flag".to_string());
        }
    }
    
    // Check DMI on Linux
    #[cfg(target_os = "linux")]
    {
        let vm_paths = [
            "/sys/class/dmi/id/product_name",
            "/sys/class/dmi/id/sys_vendor",
            "/sys/class/dmi/id/board_vendor",
        ];
        
        let vm_strings = ["vmware", "virtualbox", "kvm", "qemu", "xen", "amazon", "google", "microsoft"];
        
        for path in &vm_paths {
            if let Ok(content) = fs::read_to_string(path) {
                let content_lower = content.to_lowercase();
                for vm in &vm_strings {
                    if content_lower.contains(vm) {
                        result.vm_artifacts.push(format!("{}:{}", path, vm));
                    }
                }
            }
        }
        
        // Check for hypervisor flag in cpuinfo
        if let Ok(cpuinfo) = fs::read_to_string("/proc/cpuinfo") {
            if cpuinfo.to_lowercase().contains("hypervisor") {
                result.hypervisor_detected = true;
                result.vm_artifacts.push("cpuinfo_hypervisor_flag".to_string());
            }
        }
    }
    
    // Time dilation check
    let sleep_times: Vec<f64> = (0..20).map(|_| {
        let start = Instant::now();
        std::thread::sleep(Duration::from_millis(1));
        start.elapsed().as_nanos() as f64
    }).collect();
    
    result.sleep_mean_ns = mean(&sleep_times);
    result.sleep_variance = sample_variance(&sleep_times);
    
    if result.sleep_mean_ns > 5_000_000.0 {
        result.time_dilation = true;
        result.vm_artifacts.push("time_dilation_detected".to_string());
    }
    
    // Jitter uniformity check
    let jitter_test: Vec<f64> = (0..100).map(|_| {
        let start = Instant::now();
        let mut x: i64 = 0;
        for i in 0..100 {
            x += i;
        }
        start.elapsed().as_nanos() as f64
    }).collect();
    
    let jitter_mean = mean(&jitter_test);
    let jitter_stdev = sample_stdev(&jitter_test);
    result.jitter_cv = if jitter_mean > 0.0 { jitter_stdev / jitter_mean } else { 0.0 };
    
    if result.jitter_cv < 0.01 {
        result.uniform_jitter = true;
        result.vm_artifacts.push("uniform_jitter_pattern".to_string());
    }
    
    result.valid = !result.hypervisor_detected && !result.time_dilation && !result.uniform_jitter;
    
    if !result.valid {
        result.fail_reason = Some("vm_emulation_detected".to_string());
    }
    
    Ok(result)
}

/// Perform mining work
pub fn perform_mining_work(fingerprint: &HardwareFingerprint) -> Result<MiningWorkResult> {
    // Create work proof based on fingerprint
    let mut hasher = Sha256::new();
    hasher.update(fingerprint.clock_drift.drift_hash.as_bytes());
    hasher.update(fingerprint.cache_timing.cache_hash.as_bytes());
    hasher.update(fingerprint.timestamp.to_le_bytes());
    
    let work_proof = format!("{:x}", hasher.finalize());
    
    // Generate fingerprint hash
    let mut fp_hasher = Sha256::new();
    fp_hasher.update(fingerprint.clock_drift.drift_hash.as_bytes());
    fp_hasher.update(fingerprint.cache_timing.cache_hash.as_bytes());
    fp_hasher.update(fingerprint.simd_profile.simd_type.as_bytes());
    let fingerprint_hash = format!("{:x}", fp_hasher.finalize());
    
    Ok(MiningWorkResult {
        fingerprint_hash,
        work_proof,
        timestamp: std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)?
            .as_secs(),
        difficulty_met: true, // Simplified for now
    })
}

// Helper functions
fn mean(values: &[f64]) -> f64 {
    if values.is_empty() {
        return 0.0;
    }
    values.iter().sum::<f64>() / values.len() as f64
}

fn sample_variance(values: &[f64]) -> f64 {
    if values.len() < 2 {
        return 0.0;
    }
    let m = mean(values);
    values.iter().map(|x| (x - m).powi(2)).sum::<f64>() / (values.len() - 1) as f64
}

fn sample_stdev(values: &[f64]) -> f64 {
    sample_variance(values).sqrt()
}
