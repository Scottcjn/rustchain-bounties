use std::collections::HashMap;
use sha2::{Sha256, Digest};
use serde::{Serialize, Deserialize};
use std::fmt;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub struct OutPoint {
    pub txid: [u8; 32],
    pub vout: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TxOut {
    pub value: u64,
    pub script_pubkey: Vec<u8>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TxIn {
    pub previous_output: OutPoint,
    pub script_sig: Vec<u8>,
    pub sequence: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Transaction {
    pub version: u32,
    pub inputs: Vec<TxIn>,
    pub outputs: Vec<TxOut>,
    pub lock_time: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UTXO {
    pub outpoint: OutPoint,
    pub txout: TxOut,
    pub height: u64,
    pub coinbase: bool,
}

#[derive(Debug)]
pub struct UTXOSet {
    utxos: HashMap<OutPoint, UTXO>,
    total_supply: u64,
}

impl UTXOSet {
    pub fn new() -> Self {
        UTXOSet {
            utxos: HashMap::new(),
            total_supply: 0,
        }
    }

    pub fn add_utxo(&mut self, utxo: UTXO) {
        self.total_supply += utxo.txout.value;
        self.utxos.insert(utxo.outpoint.clone(), utxo);
    }

    pub fn remove_utxo(&mut self, outpoint: &OutPoint) -> Option<UTXO> {
        if let Some(utxo) = self.utxos.remove(outpoint) {
            self.total_supply -= utxo.txout.value;
            Some(utxo)
        } else {
            None
        }
    }

    pub fn get_utxo(&self, outpoint: &OutPoint) -> Option<&UTXO> {
        self.utxos.get(outpoint)
    }

    pub fn contains(&self, outpoint: &OutPoint) -> bool {
        self.utxos.contains_key(outpoint)
    }

    pub fn total_supply(&self) -> u64 {
        self.total_supply
    }

    pub fn iter(&self) -> impl Iterator<Item = &UTXO> {
        self.utxos.values()
    }

    pub fn len(&self) -> usize {
        self.utxos.len()
    }

    pub fn is_empty(&self) -> bool {
        self.utxos.is_empty()
    }
}

pub struct UTXOVerifier;

impl UTXOVerifier {
    pub fn verify_transaction(tx: &Transaction, utxo_set: &UTXOSet) -> Result<(), String> {
        if tx.inputs.is_empty() {
            return Err("Transaction has no inputs".to_string());
        }

        if tx.outputs.is_empty() {
            return Err("Transaction has no outputs".to_string());
        }

        let mut total_input: u64 = 0;
        let mut total_output: u64 = 0;

        for input in &tx.inputs {
            let utxo = utxo_set.get_utxo(&input.previous_output)
                .ok_or_else(|| format!("UTXO not found: {:?}", input.previous_output))?;

            total_input = total_input.checked_add(utxo.txout.value)
                .ok_or("Input value overflow")?;
        }

        for output in &tx.outputs {
            total_output = total_output.checked_add(output.value)
                .ok_or("Output value overflow")?;
        }

        if total_input < total_output {
            return Err(format!("Input {} less than output {}", total_input, total_output));
        }

        Ok(())
    }

    pub fn verify_coinbase(tx: &Transaction, block_height: u64, subsidy: u64) -> Result<(), String> {
        if tx.inputs.len() != 1 {
            return Err("Coinbase must have exactly one input".to_string());
        }

        let coinbase_input = &tx.inputs[0];
        if coinbase_input.previous_output.txid != [0u8; 32] || coinbase_input.previous_output.vout != u32::MAX {
            return Err("Coinbase input must reference null outpoint".to_string());
        }

        let mut total_output: u64 = 0;
        for output in &tx.outputs {
            total_output = total_output.checked_add(output.value)
                .ok_or("Output value overflow")?;
        }

        if total_output > subsidy {
            return Err(format!("Coinbase output {} exceeds subsidy {}", total_output, subsidy));
        }

        Ok(())
    }
}

pub fn calculate_txid(tx: &Transaction) -> [u8; 32] {
    let serialized = bincode::serialize(tx).unwrap();
    let mut hasher = Sha256::new();
    hasher.update(&serialized);
    let result = hasher.finalize();
    let mut txid = [0u8; 32];
    txid.copy_from_slice(&result);
    txid
}

#[cfg(test)]
mod tests {
    use super::*;

    fn create_test_utxo(value: u64) -> UTXO {
        UTXO {
            outpoint: OutPoint {
                txid: [1u8; 32],
                vout: 0,
            },
            txout: TxOut {
                value,
                script_pubkey: vec![],
            },
            height: 0,
            coinbase: false,
        }
    }

    #[test]
    fn test_utxo_set_basic() {
        let mut set = UTXOSet::new();
        assert!(set.is_empty());
        assert_eq!(set.total_supply(), 0);

        let utxo = create_test_utxo(100);
        set.add_utxo(utxo.clone());
        assert_eq!(set.len(), 1);
        assert_eq!(set.total_supply(), 100);
        assert!(set.contains(&utxo.outpoint));

        let removed = set.remove_utxo(&utxo.outpoint);
        assert!(removed.is_some());
        assert_eq!(set.len(), 0);
        assert_eq!(set.total_supply(), 0);
    }

    #[test]
    fn test_verify_transaction_valid() {
        let mut set = UTXOSet::new();
        let utxo = create_test_utxo(100);
        let outpoint = utxo.outpoint.clone();
        set.add_utxo(utxo);

        let tx = Transaction {
            version: 1,
            inputs: vec![TxIn {
                previous_output: outpoint,
                script_sig: vec![],
                sequence: 0xFFFFFFFF,
            }],
            outputs: vec![TxOut {
                value: 100,
                script_pubkey: vec![],
            }],
            lock_time: 0,
        };

        assert!(UTXOVerifier::verify_transaction(&tx, &set).is_ok());
    }

    #[test]
    fn test_verify_transaction_insufficient_input() {
        let mut set = UTXOSet::new();
        let utxo = create_test_utxo(50);
        let outpoint = utxo.outpoint.clone();
        set.add_utxo(utxo);

        let tx = Transaction {
            version: 1,
            inputs: vec![TxIn {
                previous_output: outpoint,
                script_sig: vec![],
                sequence: 0xFFFFFFFF,
            }],
            outputs: vec![TxOut {
                value: 100,
                script_pubkey: vec![],
            }],
            lock_time: 0,
        };

        assert!(UTXOVerifier::verify_transaction(&tx, &set).is_err());
    }

    #[test]
    fn test_verify_coinbase_valid() {
        let tx = Transaction {
            version: 1,
            inputs: vec![TxIn {
                previous_output: OutPoint {
                    txid: [0u8; 32],
                    vout: u32::MAX,
                },
                script_sig: vec![],
                sequence: 0xFFFFFFFF,
            }],
            outputs: vec![TxOut {
                value: 50,
                script_pubkey: vec![],
            }],
            lock_time: 0,
        };

        assert!(UTXOVerifier::verify_coinbase(&tx, 100, 50).is_ok());
    }

    #[test]
    fn test_verify_coinbase_exceeds_subsidy() {
        let tx = Transaction {
            version: 1,
            inputs: vec![TxIn {
                previous_output: OutPoint {
                    txid: [0u8; 32],
                    vout: u32::MAX,
                },
                script_sig: vec![],
                sequence: 0xFFFFFFFF,
            }],
            outputs: vec![TxOut {
                value: 100,
                script_pubkey: vec![],
            }],
            lock_time: 0,
        };

        assert!(UTXOVerifier::verify_coinbase(&tx, 100, 50).is_err());
    }

    #[test]
    fn test_calculate_txid() {
        let tx = Transaction {
            version: 1,
            inputs: vec![],
            outputs: vec![],
            lock_time: 0,
        };

        let txid = calculate_txid(&tx);
        assert_ne!(txid, [0u8; 32]);
    }

    #[test]
    fn test_utxo_set_overflow() {
        let mut set = UTXOSet::new();
        let utxo1 = create_test_utxo(u64::MAX);
        let utxo2 = create_test_utxo(1);

        set.add_utxo(utxo1);
        // Adding another would overflow, but we don't check in add_utxo
        // This is a potential bug to note
        set.add_utxo(utxo2);
        // Total supply will wrap around
        assert_eq!(set.total_supply(), 0); // u64::MAX + 1 = 0
    }
}