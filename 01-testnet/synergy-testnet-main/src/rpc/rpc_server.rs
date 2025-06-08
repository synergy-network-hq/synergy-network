use std::net::TcpListener;
use std::io::{Read, Write};
use std::sync::{Arc, Mutex};
use std::thread;

use crate::transaction::Transaction;
use crate::block::BlockChain;
use lazy_static::lazy_static;
use serde_json::{Value, json};

lazy_static! {
    pub static ref TX_POOL: Arc<Mutex<Vec<Transaction>>> = Arc::new(Mutex::new(Vec::new()));
}

lazy_static! {
    pub static ref CHAIN: Arc<Mutex<BlockChain>> = Arc::new(Mutex::new(BlockChain::new()));
}

pub fn start_rpc_server() {
    let listener = TcpListener::bind("0.0.0.0:8545").expect("Failed to bind RPC server");
    println!("📡 RPC server running on 0.0.0.0:8545");

    for stream in listener.incoming() {
        let tx_pool = Arc::clone(&TX_POOL);
        let chain = Arc::clone(&CHAIN);

        thread::spawn(move || {
            if let Ok(mut stream) = stream {
                let mut buffer = [0; 8192];
                if let Ok(bytes_read) = stream.read(&mut buffer) {
                    let request_str = String::from_utf8_lossy(&buffer[..bytes_read]);
                    println!("📩 Received RPC request:\n{}", request_str);

                    // --- Split headers and body ---
                    let parts: Vec<&str> = request_str.split("\r\n\r\n").collect();
                    if parts.len() < 2 {
                        send_error(&mut stream, "Malformed HTTP request");
                        return;
                    }

                    let body = parts[1];

                    // --- Handle POST: JSON-RPC ---
                    if request_str.starts_with("POST") {
                        match serde_json::from_str::<Value>(body) {
                            Ok(parsed) => {
                                println!("🧪 Parsed request: {:?}", parsed);

                                let method = parsed.get("method").and_then(|m| m.as_str()).unwrap_or("");
                                let id = parsed.get("id").cloned().unwrap_or(json!(null));

                                match method {
                                    "synergy_status" => {
                                        let resp = json!({
                                            "jsonrpc": "2.0",
                                            "id": id,
                                            "result": "ok"
                                        });
                                        let response = format_response(&resp.to_string());
                                        let _ = stream.write(response.as_bytes());
                                        return;
                                    }

                                    _ => {
                                        // Legacy: check for "tx" param and treat as broadcast
                                        if let Some(tx_obj) = parsed.get("tx") {
                                            match serde_json::from_value::<Transaction>(tx_obj.clone()) {
                                                Ok(tx) => {
                                                    let mut pool = tx_pool.lock().unwrap();
                                                    pool.push(tx);
                                                    let response = "HTTP/1.1 200 OK\r\nContent-Length: 7\r\n\r\nSuccess";
                                                    let _ = stream.write(response.as_bytes());
                                                    return;
                                                }
                                                Err(_) => send_error(&mut stream, "Invalid transaction object"),
                                            }
                                        } else {
                                            send_error(&mut stream, "Unknown method or missing 'tx' field");
                                        }
                                    }
                                }
                            }
                            Err(_) => send_error(&mut stream, "Malformed JSON in body"),
                        }
                    }

                    // --- Handle GET endpoints ---
                    else if request_str.starts_with("GET") {
                        let response = if request_str.contains("GET /chain") {
                            let chain = chain.lock().unwrap();
                            let json = serde_json::to_string_pretty(&chain.chain).unwrap();
                            format_response(&json)
                        } else if request_str.contains("GET /block/latest") {
                            let chain = chain.lock().unwrap();
                            if let Some(latest) = chain.last() {
                                let json = serde_json::to_string_pretty(latest).unwrap();
                                format_response(&json)
                            } else {
                                format_response("No blocks available.")
                            }
                        } else if request_str.contains("GET /txpool") {
                            let pool = tx_pool.lock().unwrap();
                            let json = serde_json::to_string_pretty(&*pool).unwrap();
                            format_response(&json)
                        } else if let Some(block_index_start) = request_str.find("/block/") {
                            if let Some(line_end) = request_str[block_index_start..].find(" HTTP") {
                                let idx_str = &request_str[block_index_start + 7..block_index_start + line_end];
                                if let Ok(block_index) = idx_str.trim().parse::<u64>() {
                                    let chain = chain.lock().unwrap();
                                    if let Some(block) = chain.chain.iter().find(|b| b.block_index == block_index) {
                                        let json = serde_json::to_string_pretty(block).unwrap();
                                        format_response(&json)
                                    } else {
                                        format_response(&format!("No block at block_index {}", block_index))
                                    }
                                } else {
                                    format_response("Invalid block block_index")
                                }
                            } else {
                                format_response("Malformed /block/{block_index} request")
                            }
                        } else {
                            format_response("Unknown endpoint")
                        };

                        let _ = stream.write(response.as_bytes());
                    }
                }
            }
        });
    }
}

fn format_response(body: &str) -> String {
    format!(
        "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\n\r\n{}",
        body.len(),
        body
    )
}

fn send_error(stream: &mut std::net::TcpStream, msg: &str) {
    let body = format!("{{\"error\": \"{}\"}}", msg);
    let response = format_response(&body);
    let _ = stream.write(response.as_bytes());
}
