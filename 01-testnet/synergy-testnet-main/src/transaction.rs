use serde::{Deserialize, Serialize};
use blake3::Hasher;
use bincode::{encode_to_vec, decode_from_slice};
use bincode::config::standard;
use bincode::{Decode, Encode};

#[derive(Debug, Clone, Serialize, Deserialize, Encode, Decode)]
pub struct Transaction {
    pub sender: String,
    pub receiver: String,
    pub amount: u64,
    pub nonce: u64,
    pub signature: String,
}

impl Transaction {
    pub fn new(sender: String, receiver: String, amount: u64, nonce: u64, signature: String) -> Self {
        Transaction {
            sender,
            receiver,
            amount,
            nonce,
            signature,
        }
    }

    pub fn hash(&self) -> String {
        let mut hasher = Hasher::new();
        hasher.update(self.sender.as_bytes());
        hasher.update(self.receiver.as_bytes());
        hasher.update(&self.amount.to_le_bytes());
        hasher.update(&self.nonce.to_le_bytes());
        hasher.update(self.signature.as_bytes());
        hasher.finalize().to_hex().to_string()
    }

    pub fn validate(&self) -> bool {
        !self.sender.is_empty()
            && !self.receiver.is_empty()
            && self.amount > 0
            && self.nonce > 0
    }

    pub fn to_json(&self) -> String {
        serde_json::to_string_pretty(self).unwrap()
    }

    pub fn from_json(data: &str) -> Result<Self, serde_json::Error> {
        serde_json::from_str(data)
    }

    pub fn to_yaml(&self) -> String {
        serde_yaml::to_string(self).unwrap()
    }

    pub fn from_yaml(data: &str) -> Result<Self, serde_yaml::Error> {
        serde_yaml::from_str(data)
    }

    pub fn to_bytes(&self) -> Vec<u8> {
        let config = standard();
        encode_to_vec(self, config).unwrap()
    }

    pub fn from_bytes(data: &[u8]) -> Self {
        let config = standard();
        decode_from_slice(data, config).unwrap().0
    }
}
