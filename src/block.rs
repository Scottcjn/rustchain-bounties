// Validate the coinbase transaction in a block
pub fn validate_block(block: &Block) -> bool {
    // Validate the coinbase transaction
    if !validate_coinbase(block.coinbase, block.epoch, block.total_supply) {
        return false;
    }

    true
}