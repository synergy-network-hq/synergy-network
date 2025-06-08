use std::io::{Read, Write};
use std::net::{TcpStream};
use std::thread;
use std::time::Duration;
use synergy_testnet::rpc::rpc_server;

#[test]
fn test_rpc_server_response() {
    // Launch the RPC server in a background thread (assumes 127.0.0.1:8545 is free)
    thread::spawn(|| {
        rpc_server::start_rpc_server();
    });

    // Wait for the server to start up
    thread::sleep(Duration::from_secs(2));

    // Prepare a basic JSON-RPC request
    let payload = r#"{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}"#;

    // Attempt to connect and send the request
    let mut stream = TcpStream::connect("127.0.0.1:8545").expect("Failed to connect to RPC server on 127.0.0.1:8545");
    stream.write_all(payload.as_bytes()).expect("Failed to send JSON-RPC request");

    // Read and verify response
    let mut buffer = [0; 1024];
    let size = stream.read(&mut buffer).expect("Failed to read response from server");
    let response = String::from_utf8_lossy(&buffer[..size]);

    println!("✅ RPC server responded: {}", response);
    assert!(response.contains("result") || response.contains("error"));
}
