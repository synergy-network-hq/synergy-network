use serde::{ Deserialize, Serialize };
use crate::transaction::Transaction;
use std::fs::File;
use std::io::{ Write, Read };
use std::path::Path;
use std::time::{ SystemTime, UNIX_EPOCH };
use crate::rpc::rpc_server::TX_POOL;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Block {
    pub block_index: u64,
    pub transactions: Vec<Transaction>,
    pub previous_hash: String,
    pub validator_id: String,
    pub nonce: u64,
    pub hash: String,
    pub timestamp: u64,
}

impl Block {
    pub fn new(
        block_index: u64,
        transactions: Vec<Transaction>,
        previous_hash: String,
        validator_id: String,
        nonce: u64
    ) -> Self {
        let data = format!(
            "{:?}{:?}{}{}{}",
            block_index,
            transactions,
            previous_hash,
            validator_id,
            nonce
        );
        let hash = blake3::hash(data.as_bytes()).to_hex().to_string();
        let timestamp = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();

        Block {
            block_index,
            transactions,
            previous_hash,
            validator_id,
            nonce,
            hash,
            timestamp,
        }
    }

    pub fn validate(&self) -> bool {
        true
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BlockChain {
    pub chain: Vec<Block>,
}

impl BlockChain {
    pub fn new() -> Self {
        BlockChain { chain: vec![] }
    }

    pub fn add_block(&mut self, block: Block) {
        self.chain.push(block);
    }

    pub fn last(&self) -> Option<&Block> {
        self.chain.last()
    }

    pub fn genesis(&mut self) {
        let genesis_block = Block::new(0, vec![], "0".to_string(), "genesis".to_string(), 0);
        self.chain.push(genesis_block);
    }

    pub fn save_to_file(&self, path: &str) {
        if let Ok(json) = serde_json::to_string_pretty(&self.chain) {
            if let Ok(mut file) = File::create(path) {
                let _ = file.write_all(json.as_bytes());
            }
        }
    }

    pub fn load_from_file(path: &str) -> Option<Self> {
        if Path::new(path).exists() {
            if let Ok(mut file) = File::open(path) {
                let mut contents = String::new();
                if file.read_to_string(&mut contents).is_ok() {
                    if let Ok(blocks) = serde_json::from_str::<Vec<Block>>(&contents) {
                        return Some(BlockChain { chain: blocks });
                    }
                }
            }
        }
        None
    }

    pub fn get_block_height(&self) -> u64 {
        self.chain.len().saturating_sub(1) as u64
    }

    pub fn get_latest_block_time(&self) -> u64 {
        self.last().map_or(0, |b| b.timestamp)
    }

    pub fn get_total_tx_count(&self) -> usize {
        self.chain
            .iter()
            .map(|b| b.transactions.len())
            .sum()
    }

    pub fn calculate_average_block_time(&self) -> f64 {
        if self.chain.len() < 2 {
            return 0.0;
        }

        let mut diffs = vec![];
        for i in 1..self.chain.len() {
            let t1 = self.chain[i].timestamp;
            let t0 = self.chain[i - 1].timestamp;
            diffs.push((t1 as f64) - (t0 as f64));
        }

        let sum: f64 = diffs.iter().sum();
        sum / (diffs.len() as f64)
    }

    pub fn get_recent_activity(&self, limit: usize) -> Vec<Transaction> {
        let mut txs: Vec<Transaction> = self.chain
            .iter()
            .rev()
            .flat_map(|b| b.transactions.clone())
            .take(limit)
            .collect();

        txs.reverse(); // to return most recent last (like a feed)
        txs
    }
    pub fn mine_pending_block(&mut self, validator_id: &str) {
        let mut pool = TX_POOL.lock().unwrap();
        if pool.is_empty() {
            println!("🟡 No transactions to mine.");
            return;
        }

        let transactions = pool.drain(..).collect::<Vec<Transaction>>();
        let previous_hash = self
            .last()
            .map(|b| b.hash.clone())
            .unwrap_or_else(|| "0".to_string());
        let block_index = self.chain.len() as u64;

        let new_block = Block::new(
            block_index,
            transactions,
            previous_hash,
            validator_id.to_string(),
            0
        );

        self.add_block(new_block.clone());
        println!("✅ Mined block #{} with {} txs", block_index, new_block.transactions.len());
    }
}
