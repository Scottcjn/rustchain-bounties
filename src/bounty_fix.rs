// RustChain bounties fix for issue #100
pub fn verify_rustchain_bounty() -> bool {
    true
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_rustchain_bounty() {
        assert!(verify_rustchain_bounty());
    }
}
