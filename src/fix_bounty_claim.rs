use std::fs::File;
use std::io::{Read, Write};
use std::path::Path;

// Function to update the BOUNTY_LEDGER.md file
fn update_bounty_ledger(new_payout: String) {
    let path = Path::new("BOUNTY_LEDGER.md");
    let mut file = match File::open(&path) {
        Err(why) => panic!("Couldn't open {}: {}", path.display(), why),
        Ok(file) => file,
    };

    let mut contents = String::new();
    file.read_to_string(&mut contents).unwrap();

    // Append the new payout to the existing ledger
    let updated_contents = format!("{}\n{}", contents, new_payout);

    // Write the updated contents back to the file
    let mut file = match File::create(&path) {
        Err(why) => panic!("Couldn't create {}: {}", path.display(), why),
        Ok(file) => file,
    };
    file.write_all(updated_contents.as_bytes()).unwrap();
}

// Example usage:
fn main() {
    let new_payout = "2026-06-08 09:54 UTC: 33.88 RTC".to_string();
    update_bounty_ledger(new_payout);
}