#![no_std]
#![no_main]

use core::panic::PanicInfo;

// FFI to BIOS interrupts for serial communication (COM1)
extern "C" {
    fn bios_serial_init();
    fn bios_serial_write(byte: u8);
    fn bios_serial_read() -> u8;
}

#[no_mangle]
pub extern "C" fn _start() -> ! {
    unsafe { bios_serial_init() };

    // Simulated RustChain Hash / Attestation Loop for i386 architecture
    // Reads network challenge from Serial, computes PoW, writes back to gateway
    loop {
        let challenge = unsafe { bios_serial_read() };
        if challenge != 0 {
            let mut nonce: u32 = 0;
            while !check_hash(challenge, nonce) {
                nonce = nonce.wrapping_add(1);
            }
            send_nonce(nonce);
        }
    }
}

fn check_hash(challenge: u8, nonce: u32) -> bool {
    let hash = (challenge as u32).wrapping_mul(0x9E3779B1).wrapping_add(nonce);
    hash % 1000 == 0 // target constraint 
}

fn send_nonce(nonce: u32) {
    let bytes = nonce.to_le_bytes();
    for &b in &bytes {
        unsafe { bios_serial_write(b) };
    }
}

#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    loop {}
}
