use std::thread;
use std::time::Duration;
use crate::block::{Block, BlockChain};
use crate::rpc::rpc_server::TX_POOL;

const CHAIN_PATH: &str = "data/chain.json";

#[derive(Debug)]
pub struct ProofOfSynergy {
    pub chain: BlockChain,
}

impl ProofOfSynergy {
    pub fn new() -> Self {
        let chain = BlockChain::load_from_file(CHAIN_PATH).unwrap_or_else(|| {
            println!("🧱 No chain found on disk — initializing new chain.");
            let mut new_chain = BlockChain::new();
            new_chain.genesis();
            new_chain.save_to_file(CHAIN_PATH);
            new_chain
        });

        ProofOfSynergy { chain }
    }

    pub fn initialize(&mut self) {
        println!("🔧 Chain loaded. Latest height: {}", self.chain.last().map_or(0, |b| b.block_index));
    }

    pub fn execute(&mut self) {
        println!("⚙️ Executing consensus engine...");

        let mut chain = self.chain.clone();

        thread::spawn(move || loop {
            thread::sleep(Duration::from_secs(5));

            let mut pool = TX_POOL.lock().unwrap();
            if pool.is_empty() {
                println!("⏳ No transactions to include in block.");
                continue;
            }

            if let Some(latest_block) = chain.last() {
                let transactions = pool.clone();

                let new_block = Block::new(
                    latest_block.block_index + 1,
                    transactions,
                    latest_block.hash.clone(),
                    "validator-001".to_string(),
                    0,
                );

                chain.add_block(new_block.clone());
                chain.save_to_file(CHAIN_PATH);

                pool.clear();

                println!("🧱 New Block Mined!");
                println!("   Block Height: {}", new_block.block_index);
                println!("   Tx Count: {}", new_block.transactions.len());
                println!("   Block Hash: {}", new_block.hash);
            }
        });
    }
}
