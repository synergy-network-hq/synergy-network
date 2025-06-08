
use synergy_testnet::consensus::consensus_algorithm::ProofOfSynergy;
use synergy_testnet::rpc;
use std::env;
use std::fs;
use std::path::PathBuf;
use std::process;

fn main() {
    println!("Synergy Testnet Node Starting...");

    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: synergy-testnet <subcommand>");
        process::exit(1);
    }

    let subcommand = &args[1];

    match subcommand.as_str() {
        "init" => {
            let config_dir = PathBuf::from("config");
            if !config_dir.exists() {
                fs::create_dir_all(&config_dir).expect("Failed to create config directory");
                println!("Created config directory.");
            } else {
                println!("Config directory already exists.");
            }
        }

        "start" => {
            println!("Starting the node...");

            // Start RPC server in a new thread and keep the handle
            let rpc_handle = std::thread::spawn(|| {
                rpc::rpc_server::start_rpc_server();
            });

            let mut consensus = ProofOfSynergy::new();
            consensus.initialize();
            consensus.execute();

            // Keep the main thread alive after consensus by joining the RPC thread
            rpc_handle.join().unwrap();
        }

        "status" => {
            println!("Node status: Online");
        }

        _ => {
            eprintln!("Unknown subcommand: {}", subcommand);
            process::exit(1);
        }
    }
}
