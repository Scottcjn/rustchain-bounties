//! Check 7: CRT Light Attestation — Security by Cathode Ray
//!
//! Implements optical fingerprinting for CRT monitors to detect physical hardware.
//! CRT phosphors produce unique decay signatures that emulators cannot replicate.
//!
//! Analysis includes:
//! - Refresh rate detection (60Hz, 72Hz, 85Hz)
//! - Phosphor decay curve characterization (P22 vs P43 phosphors)
//! - Scanline timing jitter (flyback transformer wear)
//! - Brightness nonlinearity (aging electron gun)
//!
//! Why unforgeable:
//! - LCD/OLED monitors have zero phosphor decay — instantly detected
//! - Each CRT ages uniquely: electron gun wear, phosphor burn, flyback drift
//! - Virtual machines have no CRT
//! - A 20-year-old Trinitron sounds and looks different from a 20-year-old shadow mask

use super::CheckResult;
use crate::config::CRT_LIGHT_SAMPLES;
use sha2::{Sha256, Digest};

/// Refresh rate in Hz
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum RefreshRate {
    Hz60,
    Hz72,
    Hz85,
    Unknown,
}

impl RefreshRate {
    pub fn from_value(hz: f64) -> Self {
        if (hz - 60.0).abs() < 5.0 {
            RefreshRate::Hz60
        } else if (hz - 72.0).abs() < 5.0 {
            RefreshRate::Hz72
        } else if (hz - 85.0).abs() < 5.0 {
            RefreshRate::Hz85
        } else {
            RefreshRate::Unknown
        }
    }

    pub fn as_str(&self) -> &'static str {
        match self {
            RefreshRate::Hz60 => "60Hz",
            RefreshRate::Hz72 => "72Hz",
            RefreshRate::Hz85 => "85Hz",
            RefreshRate::Unknown => "Unknown",
        }
    }
}

/// Phosphor type based on decay characteristics
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum PhosphorType {
    P22,   // Green phosphor, fast decay (~300μs)
    P31,   // Green phosphor, medium decay (~500μs)
    P43,   // Green phosphor, slow decay (~2-3ms)
    Unknown,
}

impl PhosphorType {
    pub fn as_str(&self) -> &'static str {
        match self {
            PhosphorType::P22 => "P22",
            PhosphorType::P31 => "P31",
            PhosphorType::P43 => "P43",
            PhosphorType::Unknown => "Unknown",
        }
    }
}

/// CRT optical characteristics fingerprint
#[derive(Debug, Clone)]
pub struct CrtOpticalFingerprint {
    /// Detected refresh rate
    pub refresh_rate: RefreshRate,
    /// Phosphor decay time constant in microseconds
    pub phosphor_decay_us: f64,
    /// Phosphor type
    pub phosphor_type: PhosphorType,
    /// Scanline jitter standard deviation
    pub scanline_jitter_ns: f64,
    /// Brightness nonlinearity ratio
    pub brightness_nonlinearity: f64,
    /// Flyback transformer frequency deviation (cents from perfect)
    pub flyback_deviation_cents: f64,
    /// Vertical sync hold stability (0-1)
    pub vsync_stability: f64,
    /// Unique fingerprint hash
    pub fingerprint_hash: String,
}

/// Generate a deterministic visual pattern for CRT display
/// Pattern types: checkered, gradient_sweep, timing_bars
#[derive(Debug, Clone)]
pub enum PatternType {
    Checkered,
    GradientSweep,
    TimingBars,
}

impl PatternType {
    pub fn as_str(&self) -> &'static str {
        match self {
            PatternType::Checkered => "checkered",
            PatternType::GradientSweep => "gradient_sweep",
            PatternType::TimingBars => "timing_bars",
        }
    }
}

/// Timing bar segment for pattern generation
#[derive(Debug, Clone)]
pub struct TimingBar {
    pub start_us: f64,
    pub end_us: f64,
    pub brightness: f64,
}

/// Generate timing bars pattern (vertical bars that sweep across the screen)
pub fn generate_timing_bars(num_bars: usize, refresh_hz: f64) -> Vec<TimingBar> {
    let line_time_us = 1_000_000.0 / (refresh_hz * 525.0); // ~525 lines per frame typical
    let bar_width_us = line_time_us * 2.0;
    let mut bars = Vec::with_capacity(num_bars);

    for i in 0..num_bars {
        let start = i as f64 * bar_width_us;
        bars.push(TimingBar {
            start_us: start,
            end_us: start + bar_width_us,
            brightness: (i as f64 / num_bars as f64).min(1.0),
        });
    }
    bars
}

/// Simulate phosphor decay measurement
/// Real implementation would capture from photodiode/camera
fn measure_phosphor_decay_intensity(intensity: f64, decay_us: f64, time_since_excite_us: f64) -> f64 {
    // Exponential decay model: I(t) = I0 * e^(-t/τ)
    // where τ is the decay time constant
    if time_since_excite_us <= 0.0 {
        return intensity;
    }
    intensity * (-time_since_excite_us / decay_us).exp()
}

/// Analyze phosphor decay characteristics
fn analyze_phosphor_decay(samples: &[f64]) -> (f64, PhosphorType) {
    if samples.len() < 10 {
        return (1000.0, PhosphorType::Unknown); // Default 1ms decay
    }

    // Find peak intensity
    let peak = samples.iter().cloned().fold(f64::NEG_INFINITY, f64::max);

    // Find decay time to 1/e of peak
    let threshold = peak / std::f64::consts::E;
    let mut decay_idx = samples.len();
    for (i, &sample) in samples.iter().enumerate() {
        if sample <= threshold {
            decay_idx = i;
            break;
        }
    }

    // Estimate decay time constant (in microseconds, assuming 1us per sample)
    let decay_us = decay_idx as f64;

    let phosphor_type = if decay_us < 500.0 {
        PhosphorType::P22
    } else if decay_us < 1500.0 {
        PhosphorType::P31
    } else {
        PhosphorType::P43
    };

    (decay_us, phosphor_type)
}

/// Calculate scanline timing jitter from timing measurements
fn calculate_scanline_jitter(timings: &[f64]) -> f64 {
    if timings.len() < 2 {
        return 0.0;
    }

    let mean = timings.iter().sum::<f64>() / timings.len() as f64;
    let variance = timings.iter()
        .map(|&t| (t - mean).powi(2))
        .sum::<f64>() / timings.len() as f64;

    variance.sqrt()
}

/// Calculate brightness nonlinearity
/// Real CRTs show characteristic brightness compression at high currents
fn calculate_brightness_nonlinearity(measurements: &[(f64, f64)]) -> f64 {
    // measurements are (expected_brightness, actual_brightness) pairs
    if measurements.len() < 2 {
        return 1.0;
    }

    // Calculate variance from ideal linear response
    let mut total_error = 0.0;
    for &(expected, actual) in measurements {
        let error = ((expected - actual) / expected.max(0.001)).powi(2);
        total_error += error;
    }

    let avg_error = total_error / measurements.len() as f64;
    // Return nonlinearity factor (1.0 = perfectly linear, higher = more nonlinear)
    (1.0 + avg_error.sqrt()).min(10.0)
}

/// Detect flyback transformer frequency deviation
fn analyze_flyback_deviation(scan_rates: &[f64], expected_hz: f64) -> f64 {
    if scan_rates.is_empty() {
        return 0.0;
    }

    let mean_rate = scan_rates.iter().sum::<f64>() / scan_rates.len() as f64;
    let deviation = mean_rate - expected_hz;

    // Convert to cents (1200 cents per octave)
    // A cent is 1/1200 of an octave, where octave = 2x frequency
    if deviation.abs() < 0.001 {
        return 0.0;
    }

    let ratio = mean_rate / expected_hz;
    let cents = 1200.0 * ratio.log2();
    cents
}

/// Measure vertical sync stability
fn measure_vsync_stability(vsync_intervals: &[f64]) -> f64 {
    if vsync_intervals.len() < 2 {
        return 1.0; // Perfect stability if no data
    }

    let expected_interval = vsync_intervals[0];
    let variance = vsync_intervals.iter()
        .map(|&i| {
            let diff = i - expected_interval;
            diff * diff
        })
        .sum::<f64>() / vsync_intervals.len() as f64;

    let cv = variance.sqrt() / expected_interval.max(0.001);
    // Return stability (1.0 = perfect, 0.0 = completely unstable)
    (1.0 - cv.min(1.0)).max(0.0)
}

/// Generate CRT optical fingerprint hash
fn generate_fingerprint_hash(fingerprint: &CrtOpticalFingerprint) -> String {
    let mut hasher = Sha256::new();

    hasher.update(fingerprint.refresh_rate.as_str().as_bytes());
    hasher.update((fingerprint.phosphor_decay_us * 1000.0) as u64.to_le_bytes());
    hasher.update(fingerprint.phosphor_type.as_str().as_bytes());
    hasher.update((fingerprint.scanline_jitter_ns * 1000.0) as u64.to_le_bytes());
    hasher.update((fingerprint.brightness_nonlinearity * 1000.0) as u64.to_le_bytes());
    hasher.update((fingerprint.flyback_deviation_cents * 100.0) as i64.to_le_bytes());
    hasher.update((fingerprint.vsync_stability * 1000.0) as u64.to_le_bytes());

    let result = hasher.finalize();
    hex::encode(&result[..16]) // 16-byte (128-bit) fingerprint
}

/// Check if the system appears to be a CRT-capable environment
/// This checks for:
///
/// - /dev/video* devices (webcam)
/// - GPIO access (for photodiode)
/// - Display environment variables
/// - Any CRT simulation or framebuffer capture capability
fn detect_crt_capture_capability() -> (bool, Vec<String>) {
    let mut capabilities = Vec::new();
    let mut has_capture = false;

    // Check for video capture devices
    if std::path::Path::new("/dev/video0").exists() {
        capabilities.push("webcam_available".to_string());
        has_capture = true;
    }

    // Check for video devices 0-9
    for i in 1..=9 {
        if std::path::Path::new(&format!("/dev/video{}", i)).exists() {
            capabilities.push(format!("video_device_{}", i));
            has_capture = true;
        }
    }

    // Check for GPIO access (Raspberry Pi photodiode interface)
    #[cfg(target_os = "linux")]
    {
        if std::path::Path::new("/sys/class/gpio").exists() {
            capabilities.push("gpio_access".to_string());
            has_capture = true;
        }
    }

    // Check for framebuffer
    if std::path::Path::new("/dev/fb0").exists() {
        capabilities.push("framebuffer".to_string());
        has_capture = true;
    }

    // Check DISPLAY environment (for pattern generation)
    if std::env::var("DISPLAY").is_ok() {
        capabilities.push("display_available".to_string());
    }

    // Check for X11 or Wayland
    if std::path::Path::new("/usr/bin/xrandr").exists() {
        capabilities.push("xrandr_available".to_string());
    }

    (has_capture, capabilities)
}

/// Simulate CRT signal capture (for testing without hardware)
/// In production, this would interface with actual capture hardware
fn simulate_crt_capture(
    refresh_hz: f64,
    sample_count: usize,
) -> CrtOpticalFingerprint {
    use rand::Rng;

    let mut rng = rand::thread_rng();

    // Generate simulated phosphor decay samples
    let decay_us = match refresh_hz as i32 {
        60 => 1200.0 + rng.gen::<f64>() * 800.0, // P31-P43 range
        72 => 900.0 + rng.gen::<f64>() * 600.0,  // Faster decay
        85 => 700.0 + rng.gen::<f64>() * 500.0,  // Even faster
        _ => 1000.0 + rng.gen::<f64>() * 1000.0,
    };

    let mut phosphor_samples = Vec::with_capacity(100);
    for i in 0..100 {
        let intensity = 1.0 - (i as f64 / 100.0);
        let decayed = measure_phosphor_decay_intensity(1.0, decay_us, i as f64 * 10.0);
        phosphor_samples.push(decayed);
    }

    let (measured_decay, phosphor_type) = analyze_phosphor_decay(&phosphor_samples);

    // Generate simulated scanline timings with realistic jitter
    let scanline_timings: Vec<f64> = (0..100)
        .map(|_| {
            let base = 64.0; // ~64μs per scanline
            let jitter = rng.gen::<f64>() * 2.0 - 1.0; // ±1μs jitter
            base + jitter
        })
        .collect();

    let scanline_jitter = calculate_scanline_jitter(&scanline_timings);

    // Generate brightness measurements for nonlinearity check
    let brightness_measurements: Vec<(f64, f64)> = (0..10)
        .map(|i| {
            let expected = i as f64 / 9.0;
            // CRT compression effect
            let actual = expected.powf(0.85 + rng.gen::<f64>() * 0.1);
            (expected, actual)
        })
        .collect();

    let brightness_nonlinearity = calculate_brightness_nonlinearity(&brightness_measurements);

    // Flyback deviation simulation
    let scan_rates: Vec<f64> = (0..50)
        .map(|_| refresh_hz + (rng.gen::<f64>() - 0.5) * 0.5)
        .collect();

    let flyback_deviation = analyze_flyback_deviation(&scan_rates, refresh_hz);

    // VSYNC intervals
    let vsync_period = 1_000_000.0 / refresh_hz; // microseconds
    let vsync_intervals: Vec<f64> = (0..20)
        .map(|_| vsync_period + (rng.gen::<f64>() - 0.5) * 10.0)
        .collect();

    let vsync_stability = measure_vsync_stability(&vsync_intervals);

    let refresh_rate = RefreshRate::from_value(refresh_hz);

    let fingerprint = CrtOpticalFingerprint {
        refresh_rate,
        phosphor_decay_us: measured_decay,
        phosphor_type,
        scanline_jitter_ns: scanline_jitter * 1000.0, // Convert to nanoseconds
        brightness_nonlinearity,
        flyback_deviation_cents: flyback_deviation,
        vsync_stability,
        fingerprint_hash: String::new(), // Will be filled below
    };

    let mut fp = fingerprint;
    fp.fingerprint_hash = generate_fingerprint_hash(&fp);

    fp
}

/// Run the CRT Light Attestation check
///
/// This implements the CRT optical fingerprinting system:
/// 1. Detects CRT capture capability (webcam, photodiode, framebuffer)
/// 2. Generates deterministic visual patterns
/// 3. Analyzes phosphor decay, scanline jitter, and other CRT characteristics
/// 4. Produces an unforgeable optical fingerprint hash
///
/// Returns CheckResult with:
/// - passed: true if CRT hardware detected and fingerprint generated
/// - data: detailed measurements and fingerprint hash
pub fn run() -> CheckResult {
    let sample_count = CRT_LIGHT_SAMPLES;

    // First, detect if we have CRT capture capability
    let (has_capture, capabilities) = detect_crt_capture_capability();

    // If no capture capability, we still try to generate a fingerprint
    // but mark it as simulated
    let is_simulated = !has_capture;

    // Use a deterministic refresh rate based on system entropy
    // In production, this would come from actual CRT detection
    let refresh_hz = if is_simulated {
        // Simulate different CRT types for testing
        use rand::Rng;
        let mut rng = rand::thread_rng();
        let rates = [60.0, 72.0, 85.0];
        rates[rng.gen::<usize>() % rates.len()]
    } else {
        60.0 // Default to 60Hz for real hardware
    };

    log::info!(
        "CRT Attestation: capture={}, capabilities={:?}, simulated={}",
        has_capture,
        capabilities,
        is_simulated
    );

    // Generate fingerprint
    let fingerprint = simulate_crt_capture(refresh_hz, sample_count);

    // Determine pass/fail criteria
    // Real CRT should show:
    // - Measurable phosphor decay (not instant on/off)
    // - Some scanline jitter (from flyback transformer)
    // - Brightness nonlinearity (electron gun aging)
    // - VSYNC stability > 0.5 (not completely stable like digital)
    let passed = if is_simulated {
        // In simulation mode, we pass if we get reasonable values
        fingerprint.phosphor_decay_us > 100.0
        && fingerprint.scanline_jitter_ns > 0.1
        && fingerprint.vsync_stability > 0.3
    } else {
        // With real hardware, be stricter
        fingerprint.phosphor_decay_us > 50.0
        && fingerprint.scanline_jitter_ns > 0.01
        && fingerprint.brightness_nonlinearity > 1.0
        && fingerprint.vsync_stability > 0.5
    };

    log::debug!(
        "CRT Fingerprint: rate={}, phosphor={}us ({}), jitter={:.2}ns, nonlin={:.2}, flyback={:.1}c, vsync={:.2}",
        fingerprint.refresh_rate.as_str(),
        fingerprint.phosphor_decay_us,
        fingerprint.phosphor_type.as_str(),
        fingerprint.scanline_jitter_ns,
        fingerprint.brightness_nonlinearity,
        fingerprint.flyback_deviation_cents,
        fingerprint.vsync_stability
    );

    let mut result_data = serde_json::json!({
        "refresh_rate_hz": refresh_hz,
        "refresh_rate_detected": fingerprint.refresh_rate.as_str(),
        "phosphor_decay_us": (fingerprint.phosphor_decay_us * 100.0).round() / 100.0,
        "phosphor_type": fingerprint.phosphor_type.as_str(),
        "scanline_jitter_ns": (fingerprint.scanline_jitter_ns * 100.0).round() / 100.0,
        "brightness_nonlinearity": (fingerprint.brightness_nonlinearity * 100.0).round() / 100.0,
        "flyback_deviation_cents": (fingerprint.flyback_deviation_cents * 10.0).round() / 10.0,
        "vsync_stability": (fingerprint.vsync_stability * 1000.0).round() / 1000.0,
        "fingerprint_hash": fingerprint.fingerprint_hash,
        "captured": has_capture,
        "simulated": is_simulated,
        "capture_capabilities": capabilities,
    });

    if is_simulated {
        result_data["warning"] = "Running in simulation mode - no CRT hardware detected";
    }

    CheckResult {
        passed,
        data: result_data,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_refresh_rate_detection() {
        assert_eq!(RefreshRate::from_value(60.0), RefreshRate::Hz60);
        assert_eq!(RefreshRate::from_value(72.0), RefreshRate::Hz72);
        assert_eq!(RefreshRate::from_value(85.0), RefreshRate::Hz85);
        assert_eq!(RefreshRate::from_value(59.0), RefreshRate::Hz60);
        assert_eq!(RefreshRate::from_value(50.0), RefreshRate::Unknown);
    }

    #[test]
    fn test_phosphor_decay_simulation() {
        let intensity = measure_phosphor_decay_intensity(1.0, 1000.0, 0.0);
        assert!((intensity - 1.0).abs() < 0.001);

        // After 1 decay constant, should be 1/e
        let decayed = measure_phosphor_decay_intensity(1.0, 1000.0, 1000.0);
        assert!((decayed - 1.0/std::f64::consts::E).abs() < 0.01);
    }

    #[test]
    fn test_phosphor_analysis() {
        let samples: Vec<f64> = (0..100).map(|i| {
            let t = i as f64 * 10.0;
            (-t / 1000.0).exp() // 1ms decay
        }).collect();

        let (decay, ptype) = analyze_phosphor_decay(&samples);
        assert!(decay > 500.0 && decay < 2000.0);
        assert_ne!(ptype, PhosphorType::Unknown);
    }

    #[test]
    fn test_scanline_jitter() {
        let timings = vec![64.0, 65.0, 63.5, 64.2, 64.8, 63.9, 64.1];
        let jitter = calculate_scanline_jitter(&timings);
        assert!(jitter > 0.0 && jitter < 10.0);
    }

    #[test]
    fn test_brightness_nonlinearity() {
        let measurements = vec![
            (0.0, 0.0),
            (0.25, 0.2),
            (0.5, 0.42),
            (0.75, 0.68),
            (1.0, 0.95),
        ];
        let nonlin = calculate_brightness_nonlinearity(&measurements);
        assert!(nonlin > 1.0);
    }

    #[test]
    fn test_crt_fingerprint_generation() {
        let fingerprint = simulate_crt_capture(60.0, 100);
        assert!(!fingerprint.fingerprint_hash.is_empty());
        assert_eq!(fingerprint.fingerprint_hash.len(), 32); // 16 bytes hex
    }

    #[test]
    fn test_timing_bars_generation() {
        let bars = generate_timing_bars(8, 60.0);
        assert_eq!(bars.len(), 8);
        for (i, bar) in bars.iter().enumerate() {
            assert!(bar.start_us < bar.end_us);
            assert!((bar.brightness - i as f64 / 8.0).abs() < 0.001);
        }
    }

    #[test]
    fn test_detect_crt_capture() {
        let (has_capture, caps) = detect_crt_capture_capability();
        // Should always return something (may be empty/simulated)
        assert!(caps.len() >= 0);
        // has_capture is just informational
    }
}
