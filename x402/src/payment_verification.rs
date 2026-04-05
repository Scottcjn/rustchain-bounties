pub fn verify_payment_proof(proof: &PaymentProof, expected_amount: u64, ledger_tx: &LedgerTransaction) -> Result<(), String> {
    let expected_sender = derive_sender_from_pubkey(&proof.pubkey);
    if expected_sender != ledger_tx.sender {
        return Err("Sender mismatch".into());
    }

    // Check if the signed amount matches the expected amount
    if proof.amount != expected_amount {
        return Err("Amount mismatch".into());
    }

    // Existing logic for nonce and tx_hash verification
    if !verify_nonce_and_tx_hash(&proof.nonce, &proof.tx_hash) {
        return Err("Invalid nonce or tx_hash".into());
    }
    Ok(())
}