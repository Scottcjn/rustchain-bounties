// 在 node/src/validation.rs 中增强奖励验证逻辑

/// 安全硬件验证函数，防止 arch 字符串欺骗
fn validate_arch_against_cpu_features(arch: &str, cpu_features: &CpuFeatures) -> Result<f64, ValidationError> {
    // 使用 CPUID 指令检测真实特性，而非信任 self-reported arch
    match arch {
        "486" => {
            // 486 不支持 CPUID 指令，如果检测到 CPUID 则拒绝
            if cpu_features.has_cpuid() {
                return Err(ValidationError::SpoofDetected("Modern CPU cannot be 486"));
            }
            // 进一步检查：486 无 FPU、无 MMX、无 CMOV
            if cpu_features.has_fpu() || cpu_features.has_mmx() || cpu_features.has_cmov() {
                return Err(ValidationError::SpoofDetected("486 lacks FPU/MMX/CMOV"));
            }
            Ok(2.5)
        },
        "386" => {
            // 386 甚至不支持 32-bit 保护模式扩展（如 486 的 CX8）
            if cpu_features.has_cx8() {
                return Err(ValidationError::SpoofDetected("386 lacks CMPXCHG8B"));
            }
            Ok(3.0)
        },
        "pentium" | "pentium-mmx" | "pentium-pro" | "pentium-ii" | "pentium-iii" => {
            // 这些架构必须支持 CPUID，且 family/model 需匹配
            if !cpu_features.has_cpuid() {
                return Err(ValidationError::SpoofDetected("Pentium requires CPUID"));
            }
            let family = cpu_features.family();
            let model = cpu_features.model();
            match arch {
                "pentium" if family == 5 && model < 4 => {},
                "pentium-mmx" if family == 5 && model >= 4 => {},
                "pentium-pro" if family == 6 && model == 1 => {},
                "pentium-ii" if family == 6 && model >= 3 && model <= 5 => {},
                "pentium-iii" if family == 6 && model >= 7 && model <= 11 => {},
                _ => return Err(ValidationError::SpoofDetected("CPU family/model mismatch")),
            }
            Ok(2.0)
        },
        // 对于现代架构（如 x86_64），不应用复古乘数
        _ => Ok(1.0),
    }
}

// 在奖励计算函数中调用此验证
fn compute_block_reward(arch: &str, cpu_features: &CpuFeatures, base_reward: f64) -> Result<f64, ValidationError> {
    let multiplier = validate_arch_against_cpu_features(arch, cpu_features)?;
    Ok(base_reward * multiplier)
}