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

fn format_response(json_body: &str) -> String {
    format!(
        "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\nAccess-Control-Allow-Methods: POST, OPTIONS\r\nAccess-Control-Allow-Headers: Content-Type\r\nContent-Length: {}\r\n\r\n{}",
        json_body.len(), json_body
    )
}

fn format_preflight_response() -> String {
    format!(
        "HTTP/1.1 204 No Content\r\nAccess-Control-Allow-Origin: *\r\nAccess-Control-Allow-Methods: POST, OPTIONS\r\nAccess-Control-Allow-Headers: Content-Type\r\nContent-Length: 0\r\n\r\n"
    )
}

fn send_error(stream: &mut dyn Write, message: &str) {
    let resp = json!({ "jsonrpc": "2.0", "error": message });
    let response = format_response(&resp.to_string());
    let _ = stream.write(response.as_bytes());
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

                    if request_str.starts_with("OPTIONS") {
                        let response = format_preflight_response();
                        let _ = stream.write(response.as_bytes());
                        return;
                    }

                    let parts: Vec<&str> = request_str.split("\r\n\r\n").collect();
                    if parts.len() < 2 {
                        send_error(&mut stream, "Malformed HTTP request");
                        return;
                    }

                    let body = parts[1];

                    if request_str.starts_with("POST") {
                        match serde_json::from_str::<Value>(body) {
                            Ok(parsed) => {
                                println!("🧪 Parsed request: {:?}", parsed);

                                let method = parsed.get("method").and_then(|m| m.as_str()).unwrap_or("");
                                let id = parsed.get("id").cloned().unwrap_or(json!(null));

                                match method {
                                    "synergy_status" => {
                                        let resp = json!({"jsonrpc": "2.0", "id": id, "result": "ok"});
                                        let response = format_response(&resp.to_string());
                                        let _ = stream.write(response.as_bytes());
                                        return;
                                    }

                                    "synergy_getBlockNumber" => {
                                        let result = CHAIN.lock().unwrap().get_block_height();
                                        let resp = json!({ "jsonrpc": "2.0", "id": id, "result": result });
                                        let response = format_response(&resp.to_string());
                                        let _ = stream.write(response.as_bytes());
                                        return;
                                    }

                                    "synergy_getLastBlockTime" => {
                                        let chain = CHAIN.lock().unwrap();
                                        let time = chain.get_latest_block_time();
                                        let resp = json!({ "jsonrpc": "2.0", "id": id, "result": time });
                                        let response = format_response(&resp.to_string());
                                        let _ = stream.write(response.as_bytes());
                                        return;
                                    }

                                    "synergy_getTotalTxCount" => {
                                        let total_tx = CHAIN.lock().unwrap().get_total_tx_count();
                                        let resp = json!({ "jsonrpc": "2.0", "id": id, "result": total_tx });
                                        let response = format_response(&resp.to_string());
                                        let _ = stream.write(response.as_bytes());
                                        return;
                                    }

                                    "synergy_getAvgBlockTime" => {
                                        let avg_time = CHAIN.lock().unwrap().calculate_average_block_time();
                                        let resp = json!({ "jsonrpc": "2.0", "id": id, "result": avg_time });
                                        let response = format_response(&resp.to_string());
                                        let _ = stream.write(response.as_bytes());
                                        return;
                                    }

                                    "synergy_getRecentActivity" => {
                                        let activity = CHAIN.lock().unwrap().get_recent_activity(10);
                                        let resp = json!({ "jsonrpc": "2.0", "id": id, "result": activity });
                                        let response = format_response(&resp.to_string());
                                        let _ = stream.write(response.as_bytes());
                                        return;
                                    }

                                    "synergy_mineBlock" => {
                                        let mut chain = CHAIN.lock().unwrap();
                                        chain.mine_pending_block("validator_1");
                                        let height = chain.get_block_height();
                                        let total = chain.get_total_tx_count();
                                        let resp = json!({ "jsonrpc": "2.0", "id": id, "result": {
                                            "height": height,
                                            "total_tx": total
                                        }});
                                        let response = format_response(&resp.to_string());
                                        let _ = stream.write(response.as_bytes());
                                        return;
                                    }

                                    _ => {
                                        if let Some(tx_obj) = parsed.get("tx") {
                                            match serde_json::from_value::<Transaction>(tx_obj.clone()) {
                                                Ok(tx) => {
                                                    let mut pool = tx_pool.lock().unwrap();
                                                    println!("🆕 Adding TX to TX_POOL: {:?}", tx);
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
                            Err(_) => send_error(&mut stream, "Malformed JSON"),
                        }
                    }
                }
            }
        });
    }
}
