// Rustchain Bouncer test fix
pub fn verify_transaction(tx: &str) -> bool {
    !tx.is_empty() && tx.starts_with("rc_")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_verify_transaction() {
        assert!(verify_transaction("rc_valid_tx_hash"));
        assert!(!verify_transaction("invalid_tx"));
    }
}
