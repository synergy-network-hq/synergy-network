use synergy_testnet::consensus::consensus_algorithm::ProofOfSynergy;
use synergy_testnet::rpc::rpc_server::{start_rpc_server, CHAIN};
use std::env;
use std::fs;
use std::path::PathBuf;
use std::process::{self, Command};

fn main() {
    println!("🚀 Synergy Testnet Node Booting...");

    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("❌ Usage: synergy-testnet <init|start|status|mine>");
        process::exit(1);
    }

    let subcommand = &args[1];

    match subcommand.as_str() {
        "init" => {
            let config_dir = PathBuf::from("config");
            if !config_dir.exists() {
                fs::create_dir_all(&config_dir).expect("Failed to create config directory");
                println!("✅ Created 'config' directory.");
            } else {
                println!("ℹ️ 'config' directory already exists.");
            }

            let default_files = vec![
                ("consensus-config.toml", include_str!("../config/consensus-config.toml")),
                ("network-config.toml", include_str!("../config/network-config.toml")),
                ("node_config.toml", include_str!("../config/node_config.toml")),
                ("token_metadata.json", include_str!("../config/token_metadata.json")),
                ("genesis.json", include_str!("../config/genesis.json")),
            ];

            for (file, content) in default_files {
                let file_path = config_dir.join(file);
                if !file_path.exists() {
                    fs::write(&file_path, content).expect("Failed to write default config file");
                    println!("✅ Wrote default {}", file);
                } else {
                    println!("ℹ️ {} already exists", file);
                }
            }
        }

        "start" => {
            println!("🟢 Starting Synergy Node Components...");

            let rpc_handle = std::thread::spawn(|| {
                start_rpc_server();
            });

            let mut consensus = ProofOfSynergy::new();
            consensus.initialize();
            consensus.execute();

            rpc_handle.join().expect("RPC server thread panicked");
        }

        "status" => {
            let output = Command::new("curl")
                .arg("-s")
                .arg("-X")
                .arg("POST")
                .arg("--data")
                .arg(r#"{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}"#)
                .arg("http://127.0.0.1:8545")
                .output();

            match output {
                Ok(result) => {
                    if result.status.success() {
                        println!("✅ Node status: Online");
                        println!("⛓️ Latest block: {}", String::from_utf8_lossy(&result.stdout));
                    } else {
                        println!("⚠️ Node status: RPC offline or unreachable");
                    }
                }
                Err(_) => {
                    println!("❌ Could not determine status. Is the node running?");
                }
            }
        }

        "mine" => {
            println!("🔨 Attempting to mine pending transactions...");
            let mut chain = CHAIN.lock().unwrap();
            chain.mine_pending_block("validator_1");
        }

        _ => {
            eprintln!("❌ Unknown subcommand: '{}'", subcommand);
            eprintln!("Usage: synergy-testnet <init|start|status|mine>");
            process::exit(1);
        }
    }
}
