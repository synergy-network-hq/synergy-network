use std::io::{Read, Write};
use std::net::TcpStream;
use crate::transaction::Transaction;

/// Broadcasts a fully signed and validated transaction to the local Synergy Testnet RPC server.
pub fn broadcast_transaction(tx: Transaction) -> Result<String, String> {
    let tx_data = tx.to_json();
    println!("\n📡 Broadcasting transaction:\n{}", tx_data);

    let mut stream = TcpStream::connect("127.0.0.1:8545")
        .map_err(|e| format!("❌ Could not connect to Synergy RPC at 127.0.0.1:8545 — {}", e))?;

    stream
        .write_all(tx_data.as_bytes())
        .map_err(|e| format!("❌ Failed to send transaction data: {}", e))?;

    stream
        .flush()
        .map_err(|e| format!("❌ Failed to flush stream: {}", e))?;

    let mut response = String::new();
    stream
        .read_to_string(&mut response)
        .map_err(|e| format!("⚠️ Failed to read response from node: {}", e))?;

    println!("✅ Response from node:\n{}", response);
    Ok(response)
}
