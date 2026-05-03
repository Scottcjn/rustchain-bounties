use std::collections::HashMap;
use sha2::{Sha256, Digest};
use serde::{Serialize, Deserialize};
use std::fmt;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub struct OutPoint {
    pub txid: [u8; 32],
    pub index: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TxOutput {
    pub value: u64,
    pub script_pubkey: Vec<u8>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TxInput {
    pub previous_output: OutPoint,
    pub script_sig: Vec<u8>,
    pub sequence: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Transaction {
    pub version: u32,
    pub inputs: Vec<TxInput>,
    pub outputs: Vec<TxOutput>,
    pub lock_time: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UTXO {
    pub outpoint: OutPoint,
    pub output: TxOutput,
    pub height: u64,
    pub coinbase: bool,
}

#[derive(Debug, Clone)]
pub struct UTXOSet {
    utxos: HashMap<OutPoint, UTXO>,
    total_value: u64,
}

impl UTXOSet {
    pub fn new() -> Self {
        UTXOSet {
            utxos: HashMap::new(),
            total_value: 0,
        }
    }

    pub fn add_utxo(&mut self, utxo: UTXO) {
        self.total_value += utxo.output.value;
        self.utxos.insert(utxo.outpoint.clone(), utxo);
    }

    pub fn remove_utxo(&mut self, outpoint: &OutPoint) -> Option<UTXO> {
        if let Some(utxo) = self.utxos.remove(outpoint) {
            self.total_value -= utxo.output.value;
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

    pub fn total_value(&self) -> u64 {
        self.total_value
    }

    pub fn len(&self) -> usize {
        self.utxos.len()
    }

    pub fn is_empty(&self) -> bool {
        self.utxos.is_empty()
    }

    pub fn iter(&self) -> impl Iterator<Item = &UTXO> {
        self.utxos.values()
    }
}

impl Transaction {
    pub fn txid(&self) -> [u8; 32] {
        let serialized = bincode::serialize(self).unwrap();
        let mut hasher = Sha256::new();
        hasher.update(&serialized);
        let result = hasher.finalize();
        let mut txid = [0u8; 32];
        txid.copy_from_slice(&result);
        txid
    }

    pub fn is_coinbase(&self) -> bool {
        self.inputs.len() == 1 && self.inputs[0].previous_output.txid == [0u8; 32] && self.inputs[0].previous_output.index == u32::MAX
    }

    pub fn total_input_value(&self, utxo_set: &UTXOSet) -> Result<u64, String> {
        let mut total = 0u64;
        for input in &self.inputs {
            if let Some(utxo) = utxo_set.get_utxo(&input.previous_output) {
                total = total.checked_add(utxo.output.value).ok_or("Overflow in input value")?;
            } else {
                return Err(format!("UTXO not found: {:?}", input.previous_output));
            }
        }
        Ok(total)
    }

    pub fn total_output_value(&self) -> u64 {
        self.outputs.iter().map(|o| o.value).sum()
    }

    pub fn verify(&self, utxo_set: &UTXOSet) -> Result<(), String> {
        if self.is_coinbase() {
            return Ok(());
        }

        if self.inputs.is_empty() {
            return Err("Transaction has no inputs".to_string());
        }

        if self.outputs.is_empty() {
            return Err("Transaction has no outputs".to_string());
        }

        let input_value = self.total_input_value(utxo_set)?;
        let output_value = self.total_output_value();

        if output_value > input_value {
            return Err("Output value exceeds input value".to_string());
        }

        // Check for duplicate inputs
        let mut seen_inputs = std::collections::HashSet::new();
        for input in &self.inputs {
            if !seen_inputs.insert(input.previous_output.clone()) {
                return Err("Duplicate input".to_string());
            }
        }

        Ok(())
    }
}

impl fmt::Display for OutPoint {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}:{}", hex::encode(self.txid), self.index)
    }
}

impl fmt::Display for UTXO {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "UTXO({}, value={}, height={})", self.outpoint, self.output.value, self.height)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn create_test_utxo(value: u64, index: u32) -> UTXO {
        UTXO {
            outpoint: OutPoint {
                txid: [0u8; 32],
                index,
            },
            output: TxOutput {
                value,
                script_pubkey: vec![],
            },
            height: 0,
            coinbase: false,
        }
    }

    #[test]
    fn test_utxo_set_basic_operations() {
        let mut utxo_set = UTXOSet::new();
        assert!(utxo_set.is_empty());
        assert_eq!(utxo_set.total_value(), 0);

        let utxo = create_test_utxo(100, 0);
        utxo_set.add_utxo(utxo.clone());
        assert_eq!(utxo_set.len(), 1);
        assert_eq!(utxo_set.total_value(), 100);

        let removed = utxo_set.remove_utxo(&utxo.outpoint);
        assert!(removed.is_some());
        assert_eq!(utxo_set.len(), 0);
        assert_eq!(utxo_set.total_value(), 0);
    }

    #[test]
    fn test_transaction_verification_valid() {
        let mut utxo_set = UTXOSet::new();
        let utxo = create_test_utxo(100, 0);
        utxo_set.add_utxo(utxo);

        let tx = Transaction {
            version: 1,
            inputs: vec![TxInput {
                previous_output: OutPoint { txid: [0u8; 32], index: 0 },
                script_sig: vec![],
                sequence: 0xFFFFFFFF,
            }],
            outputs: vec![TxOutput {
                value: 50,
                script_pubkey: vec![],
            }],
            lock_time: 0,
        };

        assert!(tx.verify(&utxo_set).is_ok());
    }

    #[test]
    fn test_transaction_verification_overspend() {
        let mut utxo_set = UTXOSet::new();
        let utxo = create_test_utxo(100, 0);
        utxo_set.add_utxo(utxo);

        let tx = Transaction {
            version: 1,
            inputs: vec![TxInput {
                previous_output: OutPoint { txid: [0u8; 32], index: 0 },
                script_sig: vec![],
                sequence: 0xFFFFFFFF,
            }],
            outputs: vec![TxOutput {
                value: 150,
                script_pubkey: vec![],
            }],
            lock_time: 0,
        };

        assert!(tx.verify(&utxo_set).is_err());
    }

    #[test]
    fn test_transaction_verification_duplicate_inputs() {
        let mut utxo_set = UTXOSet::new();
        let utxo1 = create_test_utxo(100, 0);
        let utxo2 = create_test_utxo(100, 0);
        utxo_set.add_utxo(utxo1);
        utxo_set.add_utxo(utxo2);

        let tx = Transaction {
            version: 1,
            inputs: vec![
                TxInput {
                    previous_output: OutPoint { txid: [0u8; 32], index: 0 },
                    script_sig: vec![],
                    sequence: 0xFFFFFFFF,
                },
                TxInput {
                    previous_output: OutPoint { txid: [0u8; 32], index: 0 },
                    script_sig: vec![],
                    sequence: 0xFFFFFFFF,
                },
            ],
            outputs: vec![TxOutput {
                value: 200,
                script_pubkey: vec![],
            }],
            lock_time: 0,
        };

        assert!(tx.verify(&utxo_set).is_err());
    }

    #[test]
    fn test_coinbase_transaction() {
        let utxo_set = UTXOSet::new();
        let coinbase = Transaction {
            version: 1,
            inputs: vec![TxInput {
                previous_output: OutPoint { txid: [0u8; 32], index: u32::MAX },
                script_sig: vec![],
                sequence: 0xFFFFFFFF,
            }],
            outputs: vec![TxOutput {
                value: 50,
                script_pubkey: vec![],
            }],
            lock_time: 0,
        };

        assert!(coinbase.is_coinbase());
        assert!(coinbase.verify(&utxo_set).is_ok());
    }

    #[test]
    fn test_txid_generation() {
        let tx = Transaction {
            version: 1,
            inputs: vec![],
            outputs: vec![],
            lock_time: 0,
        };
        let txid = tx.txid();
        assert_ne!(txid, [0u8; 32]);
    }
}