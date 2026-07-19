use rustchain::node::classification::derive_verified_device;
use rustchain::node::device_payload::DevicePayload;

#[test]
fn test_real_world_corpus() {
    let corpus = vec![
        // Vintage x86
        (DevicePayload { brand: "Intel(R) Pentium(R) III CPU 933 @ 933MHz".to_string(), machine: "x86_64".to_string(), /* other fields */ }, "vintage"),
        (DevicePayload { brand: "AMD-K6(tm)-III Processor".to_string(), machine: "x86_64".to_string(), /* other fields */ }, "vintage"),
        (DevicePayload { brand: "Pentium Pro".to_string(), machine: "x86_64".to_string(), /* other fields */ }, "vintage"),
        
        // Modern Intel/AMD
        (DevicePayload { brand: "Intel(R) Core(TM) i7-9700K CPU @ 3.60GHz".to_string(), machine: "x86_64".to_string(), /* other fields */ }, "modern"),
        (DevicePayload { brand: "AMD Ryzen 5 3600 6-Core Processor".to_string(), machine: "x86_64".to_string(), /* other fields */ }, "modern"),
        
        // Modern ARM SBCs claiming x86
        (DevicePayload { brand: "ARMv8 Processor rev 1 (v8l)".to_string(), machine: "x86_64".to_string(), /* other fields */ }, "modern"),
        
        // PowerPC
        (DevicePayload { brand: "PowerPC G4".to_string(), machine: "ppc".to_string(), /* other fields */ }, "vintage"),
        (DevicePayload { brand: "PowerPC G5".to_string(), machine: "ppc".to_string(), /* other fields */ }, "vintage"),
        
        // VM/QEMU strings
        (DevicePayload { brand: "QEMU Virtual CPU version 2.5.0".to_string(), machine: "x86_64".to_string(), /* other fields */ }, "modern"),
    ];

    for (payload, expected) in corpus {
        let classification = derive_verified_device(&payload);
        assert_eq!(classification, expected, "Failed to classify {:?}", payload);
    }
}
