#![no_main]

use libfuzzer_sys::fuzz_target;
use rustchain::attestation::{Attestation, AttestationData};
use std::io::Cursor;

fuzz_target!(|data: &[u8]| {
    // Try to parse the input as an attestation
    let mut cursor = Cursor::new(data);
    
    // Test parsing
    let _ = Attestation::parse(&mut cursor);
    
    // Test validation
    if let Ok(attestation) = Attestation::parse(&mut cursor) {
        let _ = attestation.validate();
        
        // Test serialization
        let _ = bincode::serialize(&attestation);
        
        // Test specific components
        if let Some(data) = &attestation.data {
            // Test data validation
            let _ = data.verify_signature();
            
            // Test data fields
            let _ = data.version;
            let _ = data.timestamp;
            let _ = data.payload;
        }
    }
});
