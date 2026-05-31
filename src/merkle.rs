use sha2::{Sha256, Digest};

pub fn verify_merkle_proof(leaf: &[u8], proof: &[Vec<u8>], root: &[u8]) -> bool {
    let mut hash = Sha256::digest(leaf).to_vec();
    for sibling in proof {
        let mut hasher = Sha256::new();
        hasher.update(&hash);
        hasher.update(sibling);
        hash = hasher.finalize().to_vec();
    }
    hash == root
}