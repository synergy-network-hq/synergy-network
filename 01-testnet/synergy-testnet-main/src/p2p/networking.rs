use std::sync::{Arc, Mutex};
use std::net::{TcpListener, TcpStream, IpAddr};
use std::io::{Read, Write};
use std::thread;
use crate::block::Block;
use crate::p2p::identity::generate_enode;

/// Start a basic P2P network server that listens for incoming peer connections.
pub fn start_p2p_network(blockchain: Arc<Mutex<Vec<Block>>>, listen_address: &str) {
    println!("🔌 Starting P2P network on {}", listen_address);

    // Hardcoded local IP + port (replace as needed)
    let local_ip: IpAddr = "192.168.1.68".parse().unwrap();
    let local_port = 30303;

    // Generate and print enode ID
    let enode = generate_enode(local_ip, local_port);
    println!("🔑 Local enode ID: {}", enode);

    let listener = TcpListener::bind(listen_address).expect("Failed to bind P2P port");

    for stream in listener.incoming() {
        match stream {
            Ok(mut socket) => {
                let blockchain = Arc::clone(&blockchain);
                thread::spawn(move || handle_peer_connection(socket, blockchain));
            }
            Err(e) => {
                eprintln!("❌ Connection failed: {}", e);
            }
        }
    }
}

/// Handles a connection from a peer (very basic echo/block height response)
fn handle_peer_connection(mut stream: TcpStream, blockchain: Arc<Mutex<Vec<Block>>>) {
    let mut buffer = [0; 512];
    match stream.read(&mut buffer) {
        Ok(_) => {
            let chain = blockchain.lock().unwrap();
            let height = chain.len();
            let response = format!("Node height: {}\n", height);
            let _ = stream.write_all(response.as_bytes());
        }
        Err(e) => {
            eprintln!("⚠️ Failed to read from peer: {}", e);
        }
    }
}
