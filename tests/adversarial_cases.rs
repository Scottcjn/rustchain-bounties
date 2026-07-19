use rustchain::node::classification::derive_verified_device;
use rustchain::node::device_payload::DevicePayload;

#[test]
fn test_adversarial_cases() {
    let adversarial_cases = vec![
        // Empty CPU brand + no `machine` field
        (DevicePayload { brand: "".to_string(), machine: "".to_string(), /* other fields */ }, "unknown"),
        
        // ARM `platform.machine()` with x86 brand claim
        (DevicePayload { brand: "Intel(R) Core(TM) i7-9700K CPU @ 3.60GHz".to_string(), machine: "aarch64".to_string(), /* other fields */ }, "unknown"),
        
        // Family-6 modern chip with "Pentium III" injected into the brand string
        (DevicePayload { brand: "Intel(R) Core(TM) i7-9700K CPU @ 3.60GHz (Pentium III)".to_string(), machine: "x86_64".to_string(), /* other fields */ }, "modern"),
        
        // Mixed legacy/new field names
        (DevicePayload { brand: "Intel(R) Pentium(R) III CPU 933 @ 933MHz".to_string(), machine: "x86_64".to_string(), /* other fields */ }, "vintage"),
        
        // Unicode/oversized/null-byte fields
        (DevicePayload { brand: "Intel\x00(R) Core(TM) i7-9700K CPU @ 3.60GHz".to_string(), machine: "x86_64".to_string(), /* other fields */ }, "unknown"),
    ];

    for (payload, expected) in adversarial_cases {
        let classification = derive_verified_device(&payload);
        assert_eq!(classification, expected, "Failed to classify {:?}", payload);
    }
}
