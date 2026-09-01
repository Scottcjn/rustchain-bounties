use sysinfo::System;

/// Get total RAM in gigabytes.
pub fn get_ram_gb() -> u64 {
    let sys = System::new_all();
    sys.total_memory() / (1024 * 1024 * 1024)
}

/// Get OS name and version string.
pub fn get_os_string() -> String {
    let name = System::name().unwrap_or_else(|| "Unknown".to_string());
    let version = System::os_version().unwrap_or_else(|| "".to_string());
    let kernel = System::kernel_version().unwrap_or_else(|| "".to_string());

    if !kernel.is_empty() {
        format!("{} {}", name, kernel)
    } else if !version.is_empty() {
        format!("{} {}", name, version)
    } else {
        name
    }
}

/// Get system uptime in seconds.
pub fn get_uptime_secs() -> u64 {
    System::uptime()
}

/// Get all available MAC addresses as hex strings.
pub fn get_mac_addresses() -> Vec<String> {
    let mut macs = Vec::new();

    // Try the mac_address crate first
    match mac_address::mac_address_by_name("eth0") {
        Ok(Some(addr)) => macs.push(addr.to_string().to_lowercase()),
        _ => {}
    }
    match mac_address::mac_address_by_name("wlan0") {
        Ok(Some(addr)) => macs.push(addr.to_string().to_lowercase()),
        _ => {}
    }
    match mac_address::mac_address_by_name("en0") {
        Ok(Some(addr)) => macs.push(addr.to_string().to_lowercase()),
        _ => {}
    }
    // Windows interfaces
    match mac_address::mac_address_by_name("Ethernet") {
        Ok(Some(addr)) => macs.push(addr.to_string().to_lowercase()),
        _ => {}
    }
    match mac_address::mac_address_by_name("Wi-Fi") {
        Ok(Some(addr)) => macs.push(addr.to_string().to_lowercase()),
        _ => {}
    }

    // If we could not enumerate any MAC from the well-known interfaces and
    // the default fallback also failed, return an empty vector instead of
    // synthesizing a placeholder value.
    //
    // Returning a hard-coded "00:00:00:00:00:00" would (a) collide the
    // identities of every sandbox / container / restricted node that
    // can't read its own NIC, and (b) silently bypass the VM-OUI check
    // because that placeholder is not in any VM vendor prefix list.
    // Callers (fingerprint/anti_emulation.rs and the attestation
    // payload) treat an empty list as "no MAC available".

    // Deduplicate
    macs.sort();
    macs.dedup();
    macs
}
